"""Show SY: one preview box that shows text, numbers, pictures, masks, latents and sound facts, and passes the value on."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_PICTURES = 6
MAX_CHARS = 20000


class AnyType(str):
    """ComfyUI any-type trick: never reports a type mismatch."""

    def __ne__(self, other):
        return False


ANY = AnyType("*")


def _shape(value):
    try:
        return tuple(int(s) for s in value.shape)
    except Exception:
        return None


def kind_of(value):
    """Pure function. 'image', 'mask', 'latent', 'audio', 'tensor', 'text', 'number', 'list', 'dict' or 'other'."""
    if value is None or isinstance(value, str):
        return "text"
    if isinstance(value, (bool, int, float)):
        return "number"
    if isinstance(value, (list, tuple)):
        return "list"
    if isinstance(value, dict):
        if "samples" in value:
            return "latent"
        if "waveform" in value:
            return "audio"
        return "dict"
    shape = _shape(value)
    if shape is not None:
        if len(shape) == 4 and shape[-1] in (1, 3, 4):
            return "image"
        if len(shape) in (2, 3):
            return "mask"
        return "tensor"
    return "other"


def pick_frames(count, limit=MAX_PICTURES):
    """Pure function. Which frame numbers to show: all if few, else evenly spaced including the first and last."""
    count, limit = int(count), int(limit)
    if count <= 0:
        return []
    if count <= limit:
        return list(range(count))
    return sorted({round(i * (count - 1) / float(limit - 1)) for i in range(limit)})


def describe(value):
    """Pure function. A plain-words description of the value."""
    kind = kind_of(value)
    if kind == "text":
        return "" if value is None else value
    if kind == "number":
        return str(value)
    if kind == "list":
        return "\n".join(describe(v) for v in value)
    if kind == "image":
        s = _shape(value)
        return "Picture: %d frame(s), %dx%d, %d channel(s)" % (s[0], s[2], s[1], s[3])
    if kind == "mask":
        s = _shape(value)
        return "Mask: %s" % "x".join(str(v) for v in s)
    if kind == "latent":
        s = _shape(value["samples"])
        return "Latent: shape %s" % "x".join(str(v) for v in s) if s else "Latent"
    if kind == "audio":
        s = _shape(value["waveform"])
        rate = int(value.get("sample_rate", 0) or 0)
        if s and rate:
            return "Sound: %.2f s, %d channel(s), %d Hz" % (s[-1] / float(rate), s[-2] if len(s) > 1 else 1, rate)
        return "Sound"
    if kind == "tensor":
        return "Tensor: shape %s" % "x".join(str(v) for v in _shape(value))
    if kind == "dict":
        return json.dumps(value, ensure_ascii=False, default=str, indent=2)
    return "%s: %s" % (type(value).__name__, value)


def clip_text(text, limit=MAX_CHARS):
    """Pure function. Cuts very long text and says so."""
    text = str(text)
    return text if len(text) <= limit else text[:limit] + "\n... (%d more characters)" % (len(text) - limit)


def _save_previews(images):
    import os
    import uuid
    import numpy as np
    import folder_paths
    from PIL import Image
    out = []
    folder = folder_paths.get_temp_directory()
    os.makedirs(folder, exist_ok=True)
    for i in pick_frames(images.shape[0]):
        arr = np.clip(255.0 * images[i].cpu().numpy(), 0, 255).astype(np.uint8)
        if arr.shape[-1] == 1:
            arr = np.repeat(arr, 3, axis=-1)
        name = "sy_show_%s.png" % uuid.uuid4().hex[:12]
        Image.fromarray(arr).save(os.path.join(folder, name), compress_level=1)
        out.append({"filename": name, "subfolder": "", "type": "temp"})
    return out


class SYShow:
    DESCRIPTION = ("One preview box for anything: shows text and numbers, previews pictures and video frames, and describes "
                   "masks, latents and sound in plain words. The value passes through unchanged, so you can leave it in place.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("value",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": (ANY, {"tooltip": "Anything you want to look at. It also comes out unchanged on the output."})}}

    def run(self, value):
        kind = kind_of(value)
        text = clip_text(describe(value))
        ui = {"text": [text]}
        if kind == "image":
            ui["images"] = _save_previews(value)
        elif kind == "mask":
            m = value if len(value.shape) == 3 else value.unsqueeze(0)
            ui["images"] = _save_previews(m.unsqueeze(-1))
        return {"ui": ui, "result": (value,)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Show", SYShow)
NODE_DISPLAY_NAME_MAPPINGS["SYShow"] = "Show SY"
