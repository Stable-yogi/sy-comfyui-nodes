"""Paint Mask SY: paint a mask by hand on the node, then use it as a MASK, a cut-out preview and a coverage number."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_MASK_SIDE = 8192
MAX_DATA_CHARS = 24 * 1024 * 1024
PREVIEW_PREFIX = "sypaint_"


def strip_data_url(text):
    """Pure function. Removes a 'data:image/png;base64,' start and spaces. Returns the bare base64 text."""
    s = (text or "").strip()
    if s.startswith("data:"):
        cut = s.find(",")
        if cut < 0:
            raise ValueError("the painted mask text is damaged: a data header has no comma. Clear the mask and paint again")
        s = s[cut + 1:]
    return "".join(s.split())


def decode_mask_bytes(text):
    """Pure function. Base64 text (with or without a data header) -> PNG bytes. Empty text -> b''."""
    import base64
    import binascii
    s = strip_data_url(text)
    if not s:
        return b""
    if len(s) > MAX_DATA_CHARS:
        raise ValueError("the painted mask is too large; press Clear in the node and paint again")
    try:
        raw = base64.b64decode(s, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("the painted mask text is not valid base64; press Clear in the node and paint again")
    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError("the painted mask is not a PNG picture; press Clear in the node and paint again")
    return raw


def fit_side(width, height, max_side):
    """Pure function. Size (w, h) scaled down, keeping the shape, so the long side is at most max_side."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1 x 1")
    if max_side < 1:
        raise ValueError("max side must be 1 or more")
    longest = max(width, height)
    if longest <= max_side:
        return (int(width), int(height))
    k = max_side / float(longest)
    return (max(1, int(round(width * k))), max(1, int(round(height * k))))


def coverage_percent(rows):
    """Pure function. Share of the mask that is white, 0..100, from a nested-list mask [H][W]."""
    total = 0
    acc = 0.0
    for row in rows:
        total += len(row)
        acc += sum(row)
    if total == 0:
        return 0.0
    return 100.0 * acc / total


def check_radii(grow, feather):
    if abs(int(grow)) > mm.MAX_RADIUS:
        raise ValueError("grow must be between -%d and %d" % (mm.MAX_RADIUS, mm.MAX_RADIUS))
    if feather < 0 or feather > mm.MAX_RADIUS:
        raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)


def process_mask(rows, grow, feather, invert):
    """Pure function on a nested-list mask. Order: grow/shrink, then feather, then invert."""
    check_radii(grow, feather)
    out = rows
    if int(grow) != 0:
        out = mm.grow_shrink_list(out, int(grow))
    if int(feather) > 0:
        out = mm.blur_list(out, int(feather))
    if invert:
        out = [[1.0 - v for v in row] for row in out]
    return out


def load_band(text):
    """Stored PNG text -> a PIL 'L' picture (white = painted), or None when the text is empty. PIL is imported here."""
    raw = decode_mask_bytes(text)
    if not raw:
        return None
    import io
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:
        raise ValueError("the painted mask picture cannot be read; press Clear in the node and paint again")
    if im.width > MAX_MASK_SIDE or im.height > MAX_MASK_SIDE:
        raise ValueError("the painted mask picture is larger than %d pixels; press Clear and paint again" % MAX_MASK_SIDE)
    if "A" in im.getbands() and im.getchannel("A").getextrema()[0] < 255:
        return im.convert("RGBA").getchannel("A")
    return im.convert("L")


def decode_mask_rows(text, height=None, width=None):
    """Stored PNG text -> nested-list mask [H][W] of 0..1 (resized to height x width when given).
    Empty text gives an all-zero mask, so it needs height and width."""
    band = load_band(text)
    if band is None:
        if not height or not width:
            raise ValueError("an empty mask needs a picture size")
        return [[0.0] * width for _ in range(height)]
    if height and width and band.size != (width, height):
        from PIL import Image
        band = band.resize((width, height), Image.BILINEAR)
    w, h = band.size
    data = list(band.getdata())
    return [[data[y * w + x] / 255.0 for x in range(w)] for y in range(h)]


def mask_tensor(text, height, width):
    """Mask text -> torch tensor [1,H,W] of 0..1 at the image size. Empty text gives zeros."""
    import numpy as np
    import torch
    band = load_band(text)
    if band is None:
        return torch.zeros((1, height, width), dtype=torch.float32)
    if band.size != (width, height):
        from PIL import Image
        band = band.resize((width, height), Image.BILINEAR)
    arr = np.asarray(band, dtype=np.float32) / 255.0
    return torch.from_numpy(arr.copy()).unsqueeze(0)


def save_backdrop(image):
    """Saves the first picture as a temp file so the editor can show it. Returns the ui file list."""
    import hashlib
    import os
    import numpy as np
    import folder_paths
    from PIL import Image
    arr = (image[0].clamp(0, 1) * 255).byte().cpu().numpy()
    if arr.shape[2] == 1:
        arr = np.repeat(arr, 3, axis=2)
    arr = np.ascontiguousarray(arr[:, :, :3])
    fn = PREVIEW_PREFIX + hashlib.sha1(arr.tobytes()).hexdigest()[:16] + ".png"
    path = os.path.join(folder_paths.get_temp_directory(), fn)
    if not os.path.exists(path):
        Image.fromarray(arr).save(path, compress_level=1)
    return [{"filename": fn, "subfolder": "", "type": "temp"}]


class SYPaintMask:
    OUTPUT_NODE = True
    DESCRIPTION = "Paint a mask by hand on top of your picture. Gives the mask, a cut-out preview (the mask becomes transparency) and how much is covered."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "IMAGE", "FLOAT")
    RETURN_NAMES = ("mask", "image", "coverage_percent")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to paint on. It is shown behind the brush after a run."}),
                "mask_data": ("STRING", {"default": "", "multiline": False, "tooltip": "Filled in by the painting area on the node. Leave it alone."}),
                "grow": ("INT", {"default": 0, "min": -mm.MAX_RADIUS, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Makes the painted area bigger (plus) or smaller (minus) by this many pixels."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Softens the mask edge by this many pixels. 0 keeps it sharp."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Swap painted and unpainted areas (done last)."}),
            }
        }

    def run(self, image, mask_data, grow, feather, invert):
        import torch
        batch, height, width = int(image.shape[0]), int(image.shape[1]), int(image.shape[2])
        check_radii(grow, feather)
        mask = mask_tensor(mask_data, height, width).to(image.device)
        if int(grow) != 0:
            mask = mm.t_grow_shrink(mask, int(grow))
        if int(feather) > 0:
            mask = mm.t_blur(mask, int(feather))
        if invert:
            mask = 1.0 - mask
        mask = mask.clamp(0.0, 1.0)
        coverage = float(mask.mean().item()) * 100.0
        rgb = image[..., :3]
        if rgb.shape[3] == 1:
            rgb = rgb.expand(-1, -1, -1, 3)
        full = mask.expand(batch, -1, -1).contiguous()
        preview = torch.cat([rgb, full.unsqueeze(-1).to(rgb.dtype)], dim=3)
        return {"ui": {"sy_paint": save_backdrop(image)}, "result": (full, preview, coverage)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PaintMask", SYPaintMask)
NODE_DISPLAY_NAME_MAPPINGS["SYPaintMask"] = "Paint Mask SY"
