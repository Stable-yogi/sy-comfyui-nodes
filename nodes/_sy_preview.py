"""Result preview for SY nodes: a small picture or text of what a node made, sent to the browser with the run.

Applied once at start-up by __init__.py (wrap_all). It never changes what a node returns as its result: it only adds
the "ui" part that ComfyUI sends to the browser. A node that already returns its own ui is left alone.
Works without the browser: a run through the API gives the same result. Set SY_NO_PREVIEW=1 to switch it off.
"""
import functools
import hashlib
import inspect
import os

MAX_TEXT = 1200       # characters kept per text output
MAX_TEXT_ITEMS = 4    # text outputs shown per node
MAX_FRAMES = 4        # pictures shown per node
THUMB = 320           # longest side of a thumbnail in pixels
TEXT_TYPES = ("STRING", "INT", "FLOAT", "BOOLEAN")
SKIP_CLASSES = ("SYWorkflowHeader", "SYNote", "SYSystemInfo")  # nodes with nothing to show
_warned = set()


def clip_text(text, limit=MAX_TEXT):
    """Pure function. Cut a long text and say how much was cut."""
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... (%d more characters)" % (len(text) - limit)


def format_value(value):
    """Pure function. Plain text for one output value."""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return "%.6g" % value
    return clip_text(value)


def plan_outputs(return_types):
    """Pure function. Which outputs can be shown: {"image": index or None, "mask": index or None, "text": [index...]}."""
    plan = {"image": None, "mask": None, "text": []}
    for i, t in enumerate(return_types or ()):
        if t == "IMAGE" and plan["image"] is None:
            plan["image"] = i
        elif t == "MASK" and plan["mask"] is None:
            plan["mask"] = i
        elif t in TEXT_TYPES and len(plan["text"]) < MAX_TEXT_ITEMS:
            plan["text"].append(i)
    return plan


def text_items(plan, names, result):
    """Pure function. [{"name", "text"}] for the text outputs of one result tuple."""
    items = []
    for i in plan["text"]:
        if i >= len(result):
            continue
        v = result[i]
        if v is None or isinstance(v, (list, tuple, dict)):
            continue
        name = names[i] if names and i < len(names) else "out%d" % i
        items.append({"name": str(name), "text": format_value(v)})
    return items


def can_wrap(cls):
    """Pure function. True when the class has a plain method to wrap and something to show."""
    if getattr(cls, "SY_NO_PREVIEW", False) or cls.__name__ in SKIP_CLASSES:
        return False
    if getattr(cls, "INPUT_IS_LIST", False) or any(getattr(cls, "OUTPUT_IS_LIST", ()) or ()):
        return False
    fn = cls.__dict__.get(getattr(cls, "FUNCTION", ""))
    if not inspect.isfunction(fn) or inspect.iscoroutinefunction(fn) or inspect.isgeneratorfunction(fn):
        return False
    plan = plan_outputs(getattr(cls, "RETURN_TYPES", ()))
    return plan["image"] is not None or plan["mask"] is not None or bool(plan["text"])


def image_input_names(cls):
    """Names of the IMAGE inputs of a node, in order."""
    try:
        spec = cls.INPUT_TYPES()
    except Exception:
        return []
    names = []
    for section in ("required", "optional"):
        for name, defn in (spec.get(section) or {}).items():
            if isinstance(defn, tuple) and defn and defn[0] == "IMAGE":
                names.append(name)
    return names


def _to_pil(tensor, index):
    """One frame of a picture tensor [B,H,W,C] as a small RGB picture."""
    from PIL import Image
    frame = tensor[index]
    arr = (frame.clamp(0, 1) * 255).round().byte().cpu().numpy()
    if arr.ndim == 2:
        arr = arr[:, :, None]
    if arr.shape[2] == 1:
        img = Image.fromarray(arr[:, :, 0], "L").convert("RGB")
    else:
        img = Image.fromarray(arr[:, :, :3], "RGB")
    img.thumbnail((THUMB, THUMB))
    return img


def _mask_to_pil(mask, index, size):
    from PIL import Image
    m = mask if mask.ndim == 3 else mask[None]
    frame = m[min(index, m.shape[0] - 1)]
    arr = (frame.clamp(0, 1) * 255).round().byte().cpu().numpy()
    return Image.fromarray(arr, "L").resize(size)


def _save_jpeg(img):
    import io
    import folder_paths
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    data = buf.getvalue()
    name = "sy_pv_%s.jpg" % hashlib.md5(data).hexdigest()[:14]
    path = os.path.join(folder_paths.get_temp_directory(), name)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(data)
    return name


def picture_files(plan, result, before):
    """Save thumbnails of the first output picture (and mask) next to the input picture. Returns (files, info)."""
    from PIL import Image
    files, info = [], ""
    after = result[plan["image"]] if plan["image"] is not None and plan["image"] < len(result) else None
    mask = result[plan["mask"]] if plan["mask"] is not None and plan["mask"] < len(result) else None
    if after is not None and hasattr(after, "shape") and len(after.shape) == 4:
        n = int(after.shape[0])
        info = "%d picture%s, %d x %d" % (n, "" if n == 1 else "s", int(after.shape[2]), int(after.shape[1]))
        for i in range(min(n, MAX_FRAMES)):
            files.append({"filename": _save_jpeg(_to_pil(after, i)), "subfolder": "", "type": "temp", "role": "after"})
    elif mask is not None and hasattr(mask, "shape"):
        n = int(mask.shape[0]) if mask.ndim == 3 else 1
        h, w = int(mask.shape[-2]), int(mask.shape[-1])
        info = "%d mask%s, %d x %d" % (n, "" if n == 1 else "s", w, h)
        for i in range(min(n, MAX_FRAMES)):
            base = None
            if before is not None and len(before.shape) == 4:
                base = _to_pil(before, min(i, int(before.shape[0]) - 1))
            if base is None:
                base = Image.new("RGB", (min(w, THUMB), min(h, THUMB)), (20, 20, 20))
                base.thumbnail((THUMB, THUMB))
            m = _mask_to_pil(mask, i, base.size)
            tint = Image.new("RGB", base.size, (255, 40, 40))
            shown = Image.composite(tint, base, m.point(lambda v: int(v * 0.6)))
            files.append({"filename": _save_jpeg(shown), "subfolder": "", "type": "temp", "role": "after"})
    if files and before is not None and after is not None and len(before.shape) == 4:
        for i in range(min(int(before.shape[0]), MAX_FRAMES, len(files))):
            files.append({"filename": _save_jpeg(_to_pil(before, i)), "subfolder": "", "type": "temp", "role": "before"})
    return files, info


def add_preview(cls, image_names, out, kwargs):
    """Return `out` with a "ui" part added. `out` is the result tuple of the node."""
    if not isinstance(out, tuple):
        return out
    plan = plan_outputs(cls.RETURN_TYPES)
    ui = {}
    items = text_items(plan, getattr(cls, "RETURN_NAMES", None), out)
    if items:
        ui["sy_text"] = items
    before = next((kwargs[n] for n in image_names if kwargs.get(n) is not None), None)
    if plan["image"] is not None or plan["mask"] is not None:
        files, info = picture_files(plan, out, before)
        if files:
            ui["sy_preview"] = files
        if info:
            ui["sy_info"] = [info]
    if not ui:
        return out
    return {"ui": ui, "result": out}


def wrap_class(cls):
    """Wrap the run method of one node class. Returns True when it was wrapped."""
    if getattr(cls, "_sy_preview_wrapped", False) or not can_wrap(cls):
        return False
    fn_name = cls.FUNCTION
    orig = cls.__dict__[fn_name]
    image_names = image_input_names(cls)

    @functools.wraps(orig)
    def wrapper(self, *args, **kwargs):
        out = orig(self, *args, **kwargs)
        if os.environ.get("SY_NO_PREVIEW"):
            return out
        try:
            return add_preview(cls, image_names, out, kwargs)
        except Exception as e:  # the preview must never break the node; say it once in the console
            if cls.__name__ not in _warned:
                _warned.add(cls.__name__)
                print("[SY] result preview skipped for %s: %s" % (cls.__name__, e))
            return out

    setattr(cls, fn_name, wrapper)
    cls._sy_preview_wrapped = True
    return True


def wrap_all(mappings):
    """Wrap every class in a NODE_CLASS_MAPPINGS dict. Returns how many were wrapped."""
    return sum(1 for cls in mappings.values() if wrap_class(cls))
