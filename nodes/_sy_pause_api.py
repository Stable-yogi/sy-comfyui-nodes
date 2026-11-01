"""Review Pause SY: the waiting room. Keeps the open pauses, checks the answers from the browser and adds the web routes.
Pure Python (PIL only inside decode_mask). Never import comfy at the top of this file."""
import base64
import binascii
import io
import itertools
import threading
import time

MAX_TEXT = 200000
MAX_MASK_BYTES = 4 * 1024 * 1024
MAX_PREVIEWS = 16
MAX_LIMIT_MINUTES = 1440
ACTIONS = ("continue", "stop")
TIMEOUT_MODES = ("continue with everything", "stop the workflow")
POLL_SECONDS = 0.25


class UnknownPause(LookupError):
    """The pause id is not waiting any more."""


def normalize_kept(kept, count):
    """Pure function. List of picture numbers (0 = first) -> sorted list without doubles. Plain refusal for anything outside 0..count-1."""
    if not isinstance(kept, (list, tuple)):
        raise ValueError("kept must be a list of picture numbers, for example [0, 2]")
    out = set()
    for v in kept:
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("picture numbers must be whole numbers, got %r" % (v,))
        if v < 0 or v >= count:
            raise ValueError("picture %d does not exist: there %s only %d picture%s to review"
                             % (v + 1, "is" if count == 1 else "are", count, "" if count == 1 else "s"))
        out.add(v)
    return sorted(out)


def kept_text(indices):
    """Pure function. [0, 2] -> '1,3' (picture numbers as people count them, from 1)."""
    return ",".join(str(int(i) + 1) for i in indices)


def check_answer(payload, pending):
    """Pure function. Check one answer from the browser against the open pause (a dict with count and draw).
    Returns a clean dict: action, kept (list), text (str or None), mask_png (bytes or None)."""
    if pending is None:
        raise UnknownPause("This pause is not waiting any more. It was answered, cancelled or the run ended.")
    if not isinstance(payload, dict):
        raise ValueError("the answer must be a JSON object")
    action = payload.get("action")
    if action not in ACTIONS:
        raise ValueError("action must be 'continue' or 'stop', got %r" % (action,))
    count = int(pending.get("count", 0))
    kept = normalize_kept(payload.get("kept", []), count)
    text = payload.get("text")
    if text is not None:
        if not isinstance(text, str):
            raise ValueError("the text must be a string")
        if len(text) > MAX_TEXT:
            raise ValueError("the text is too long: %d characters, the limit is %d" % (len(text), MAX_TEXT))
    mask_png = None
    raw = payload.get("mask_png_base64")
    if raw:
        if not pending.get("draw"):
            raise ValueError("this pause does not take a drawn mask (allow_mask_draw is off)")
        if not isinstance(raw, str):
            raise ValueError("the mask must be a base64 text")
        if len(raw) > MAX_MASK_BYTES * 4 // 3 + 8:
            raise ValueError("the mask picture is too big: the limit is 4 MB")
        try:
            mask_png = base64.b64decode(raw, validate=True)
        except (binascii.Error, ValueError):
            raise ValueError("the mask is not valid base64 text")
        if len(mask_png) > MAX_MASK_BYTES:
            raise ValueError("the mask picture is too big: the limit is 4 MB")
    return {"action": action, "kept": kept, "text": text, "mask_png": mask_png}


def decide_timeout(started, now, limit_minutes, mode):
    """Pure function. None while still waiting, else 'continue' or 'stop' (what to do after the time ran out). limit 0 = never."""
    if isinstance(limit_minutes, bool) or not isinstance(limit_minutes, int) or not 0 <= limit_minutes <= MAX_LIMIT_MINUTES:
        raise ValueError("wait_limit_minutes must be a whole number from 0 to %d, got %r" % (MAX_LIMIT_MINUTES, limit_minutes))
    if mode not in TIMEOUT_MODES:
        raise ValueError("on_timeout must be one of: %s, got %r" % (", ".join(TIMEOUT_MODES), mode))
    if limit_minutes == 0:
        return None
    if now - started < limit_minutes * 60:
        return None
    return "continue" if mode == TIMEOUT_MODES[0] else "stop"


def decode_mask(png_bytes, size):
    """Mask PNG bytes -> PIL 'L' image resized to size (w, h). White = masked. Needs PIL (imported here)."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(png_bytes))
        img.load()
    except Exception:
        raise ValueError("the drawn mask is not a readable PNG picture")
    if "A" in img.getbands():
        rgba = img.convert("RGBA")
        base = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        base.alpha_composite(rgba)
        img = base
    img = img.convert("L")
    if img.size != (int(size[0]), int(size[1])):
        img = img.resize((int(size[0]), int(size[1])), Image.BILINEAR)
    return img


class Pending:
    def __init__(self, token, unique_id, info, event, started):
        self.token = token
        self.unique_id = unique_id
        self.info = info
        self.event = event
        self.started = started
        self.answer = None


class PendingStore:
    """Open pauses, thread-safe. The worker thread waits on record.event, the web route calls answer()."""

    def __init__(self, event_factory=threading.Event, clock=time.monotonic):
        self._lock = threading.Lock()
        self._items = {}
        self._counter = itertools.count(1)
        self._event_factory = event_factory
        self._clock = clock

    def create(self, unique_id, info):
        with self._lock:
            for tok in [t for t, r in self._items.items() if r.unique_id == str(unique_id)]:
                self._items.pop(tok, None)     # the same node paused again: the old window is stale
            token = "%s-%d" % (unique_id, next(self._counter))
            data = dict(info)
            data["id"] = token
            rec = Pending(token, str(unique_id), data, self._event_factory(), self._clock())
            self._items[token] = rec
            return rec

    def get(self, token):
        with self._lock:
            return self._items.get(token)

    def answer(self, token, clean):
        """Store the answer and wake the waiting thread. False when unknown or already answered (first answer wins)."""
        with self._lock:
            rec = self._items.get(token)
            if rec is None or rec.answer is not None:
                return False
            rec.answer = clean
        rec.event.set()
        return True

    def remove(self, token):
        with self._lock:
            return self._items.pop(token, None) is not None

    def list_open(self):
        with self._lock:
            return [dict(r.info) for r in self._items.values() if r.answer is None]


STORE = PendingStore()


def wait_for_answer(rec, limit_minutes, mode, check_interrupt, poll=POLL_SECONDS, clock=time.monotonic):
    """Block until the browser answers. Returns ('answer', clean) or ('timeout', 'continue'|'stop').
    check_interrupt() is called every poll and raises when the Cancel button was pressed."""
    while True:
        if rec.event.wait(poll):
            return ("answer", rec.answer)
        check_interrupt()
        verdict = decide_timeout(rec.started, clock(), limit_minutes, mode)
        if verdict:
            return ("timeout", verdict)


_routes_done = False


def register_routes():
    """Add the /sy/pause routes to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    async def answer(request):
        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "the answer could not be read as JSON"}, status=400)
        token = body.get("id") if isinstance(body, dict) else None
        rec = STORE.get(token) if isinstance(token, str) else None
        try:
            clean = check_answer(body, rec.info if rec else None)
            if clean["mask_png"] is not None:
                size = rec.info.get("size") or [64, 64]
                clean["mask"] = decode_mask(clean["mask_png"], size)
            clean.pop("mask_png", None)
        except UnknownPause as e:
            return web.json_response({"error": str(e)}, status=404)
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)
        if not STORE.answer(token, clean):
            return web.json_response({"error": "This pause was already answered."}, status=404)
        return web.json_response({"ok": True})

    async def pending(request):
        return web.json_response({"pending": STORE.list_open()})

    routes.post("/sy/pause/answer")(answer)
    routes.get("/sy/pause/pending")(pending)
    _routes_done = True
    return True
