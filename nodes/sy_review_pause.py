"""Review Pause SY: stops the workflow half-way so you can look at the pictures, keep the good ones, fix the text, maybe paint a mask, then press Continue or Stop."""
import os
import secrets
import time

try:
    from ._sy_common import category, register, safe_join
    from . import _sy_pause_api as api
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join
    import _sy_pause_api as api

DEFAULT_MESSAGE = "Look at the result, then press Continue."
PREVIEW_SIDE = 512
PREVIEW_FOLDER = "sy_review"
EVENT_NAME = "sy.review.open"
CLOSE_EVENT_NAME = "sy.review.close"
NEED_SOMETHING = "Connect a picture, a text or a mask so there is something to review."


def check_inputs(image, text, mask, allow_mask_draw):
    """Pure function. Plain refusal when there is nothing to review, or when mask drawing has no picture to draw on."""
    has_text = isinstance(text, str) and text != ""
    if image is None and mask is None and not has_text:
        raise ValueError(NEED_SOMETHING)
    if allow_mask_draw and image is None:
        raise ValueError("Drawing a mask needs a picture to draw on. Connect a picture or switch allow_mask_draw off.")
    return has_text


def review_count(image_count):
    """Pure function. How many pictures are shown in the window (the rest cannot be shown and are always kept)."""
    return min(int(image_count), api.MAX_PREVIEWS)


def final_kept(chosen, shown, total):
    """Pure function. The picture numbers that go on: the ones picked in the window plus every picture too far down to be shown."""
    return sorted(set(chosen) | set(range(shown, total)))


def open_message(message, shown, previews, text, has_mask, draw, size, mask_preview=None):
    """Pure function. What the browser receives to open the window."""
    return {
        "message": (message or DEFAULT_MESSAGE)[:2000],
        "count": shown,
        "images": previews,
        "text": text if isinstance(text, str) else "",
        "has_text": isinstance(text, str) and text != "",
        "mask": bool(has_mask),
        "draw": bool(draw),
        "size": list(size),
        "mask_preview": mask_preview,
    }


def _preview_dir():
    import folder_paths
    return safe_join(folder_paths.get_temp_directory(), PREVIEW_FOLDER)


def _to_pil(frame):
    """One picture [H, W, C] tensor -> PIL."""
    from PIL import Image
    arr = (frame.detach().cpu().float().clamp(0, 1) * 255.0).round().byte().numpy()
    if arr.shape[-1] >= 3:
        return Image.fromarray(arr[..., :3], "RGB")
    return Image.fromarray(arr[..., 0], "L")


def save_previews(image, shown):
    """Save small copies of the first `shown` pictures in ComfyUI's temp folder. Returns (file refs, file paths)."""
    folder = _preview_dir()
    os.makedirs(folder, exist_ok=True)
    tag = secrets.token_hex(6)
    refs, paths = [], []
    for i in range(shown):
        pic = _to_pil(image[i])
        pic.thumbnail((PREVIEW_SIDE, PREVIEW_SIDE))
        name = "sy_review_%s_%d.png" % (tag, i)
        path = safe_join(folder, name)
        pic.save(path, "PNG")
        refs.append({"filename": name, "subfolder": PREVIEW_FOLDER, "type": "temp"})
        paths.append(path)
    return refs, paths


def save_mask_preview(mask, side_size):
    """Save the starting mask as a small grey picture so the window can start from it. Returns (ref, path)."""
    from PIL import Image
    m = mask[0] if getattr(mask, "ndim", 3) == 3 else mask
    arr = (m.detach().cpu().float().clamp(0, 1) * 255.0).round().byte().numpy()
    pic = Image.fromarray(arr, "L")
    pic.thumbnail((PREVIEW_SIDE, PREVIEW_SIDE))
    folder = _preview_dir()
    os.makedirs(folder, exist_ok=True)
    name = "sy_review_mask_%s.png" % secrets.token_hex(6)
    path = safe_join(folder, name)
    pic.save(path, "PNG")
    return {"filename": name, "subfolder": PREVIEW_FOLDER, "type": "temp"}, path


def send_close(token):
    """Tell the browser to close the window of this pause (time-out). Tests replace this function."""
    try:
        from server import PromptServer
    except ImportError:  # no server (a script test): there is no browser window to close
        return
    PromptServer.instance.send_sync(CLOSE_EVENT_NAME, {"id": token})


def send_open(info):
    """Tell the browser to open the window. Tests replace this function."""
    from server import PromptServer
    PromptServer.instance.send_sync(EVENT_NAME, info)


def check_interrupt():
    """Raise the same way ComfyUI does when the Cancel button was pressed."""
    import comfy.model_management as mm
    mm.throw_exception_if_processing_interrupted()


def _empty_mask(w, h):
    import torch
    return torch.zeros((1, int(h), int(w)), dtype=torch.float32)


def _pil_to_mask(pic):
    import numpy as np
    import torch
    arr = np.asarray(pic, dtype=np.float32) / 255.0
    return torch.from_numpy(arr.copy()).unsqueeze(0)


class SYReviewPause:
    DESCRIPTION = ("Stops the workflow half-way and opens a window. Look at the pictures, untick the bad ones, fix the text, "
                   "paint a mask if you switched that on, then press Continue or Stop. Only the ticked pictures go on, in their "
                   "old order. Shows at most 16 pictures; any further ones are always kept. Switch it off to run without stopping.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING", "MASK", "STRING", "STRING")
    RETURN_NAMES = ("image", "text", "mask", "kept", "answer")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off = pass everything through without stopping, for runs without a person."}),
                "message": ("STRING", {"default": DEFAULT_MESSAGE, "multiline": True, "tooltip": "The note shown at the top of the window."}),
                "allow_mask_draw": ("BOOLEAN", {"default": False, "tooltip": "On = the window lets you paint a mask on the first picture."}),
                "wait_limit_minutes": ("INT", {"default": 0, "min": 0, "max": api.MAX_LIMIT_MINUTES, "tooltip": "How long to wait for you. 0 = wait until you answer."}),
                "on_timeout": (list(api.TIMEOUT_MODES), {"default": api.TIMEOUT_MODES[0], "tooltip": "What happens when the waiting time runs out."}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "The pictures to look at. You choose which ones to keep."}),
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "A text you may change in the window before it goes on."}),
                "mask": ("MASK", {"tooltip": "A mask to start from. You can change it if drawing is on."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def run(self, enabled=True, message=DEFAULT_MESSAGE, allow_mask_draw=False, wait_limit_minutes=0,
            on_timeout=api.TIMEOUT_MODES[0], image=None, text="", mask=None, unique_id=None):
        if on_timeout not in api.TIMEOUT_MODES:
            raise ValueError("on_timeout must be one of: %s, got %r" % (", ".join(api.TIMEOUT_MODES), on_timeout))
        check_inputs(image, text, mask, bool(allow_mask_draw) and bool(enabled))
        total = 0 if image is None else int(image.shape[0])
        if image is not None:
            w, h = int(image.shape[2]), int(image.shape[1])
        elif mask is not None:
            w, h = int(mask.shape[-1]), int(mask.shape[-2])
        else:
            w, h = 64, 64
        text_in = text if isinstance(text, str) else ""

        def start_mask():
            if mask is None:
                return _empty_mask(w, h)
            return mask if getattr(mask, "ndim", 3) == 3 else mask.unsqueeze(0)

        if not enabled:
            return (image, text_in, start_mask(), kept_all(total), "passed through")

        shown = review_count(total)
        draw = bool(allow_mask_draw)
        files = []
        try:
            refs = []
            if shown:
                refs, paths = save_previews(image, shown)
                files.extend(paths)
            mask_ref = None
            if mask is not None and draw:
                mask_ref, mpath = save_mask_preview(mask, (w, h))
                files.append(mpath)
            info = open_message(message, shown, refs, text_in, mask is not None, draw, (w, h), mask_ref)
            rec = api.STORE.create(unique_id if unique_id is not None else "0", info)
            try:
                send_open(rec.info)
                kind, result = api.wait_for_answer(rec, int(wait_limit_minutes), on_timeout, check_interrupt)
            finally:
                api.STORE.remove(rec.token)
                send_close(rec.token)
        finally:
            for p in files:
                try:
                    os.remove(p)
                except OSError:
                    pass

        if kind == "timeout":
            if result == "stop":
                raise ValueError("Review Pause SY waited %d minutes and was set to stop the workflow." % int(wait_limit_minutes))
            return (image, text_in, start_mask(), kept_all(total), "timed out")
        if result["action"] == "stop":
            raise ValueError("You pressed Stop in Review Pause SY.")

        out_text = result["text"] if result.get("text") is not None else text_in
        kept = final_kept(result["kept"], shown, total)
        out_image = image
        if image is not None:
            if not kept:
                raise ValueError("You kept no pictures. Keep at least one or press Stop.")
            if len(kept) != total:
                import torch
                out_image = image[torch.tensor(kept, dtype=torch.long, device=image.device)]
        drawn = result.get("mask")
        out_mask = _pil_to_mask(drawn) if drawn is not None else start_mask()
        return (out_image, out_text, out_mask, api.kept_text(kept), "continue")


def kept_all(total):
    """Pure function. The kept text when nothing is removed."""
    return api.kept_text(range(int(total)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ReviewPause", SYReviewPause)
NODE_DISPLAY_NAME_MAPPINGS["SYReviewPause"] = "Review Pause SY"
