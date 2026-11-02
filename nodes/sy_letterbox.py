"""Letterbox SY: adds cinema bars or crops a picture to a wanted shape, without stretching it."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

MODES = ("add bars", "crop to fit")


def parse_aspect(text):
    """Pure function. '2.39:1', '16:9', '2.35' or '1.85:1' -> width/height as a float. Bad text raises ValueError."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("aspect must be text such as '2.39:1', '16:9' or '2.35', got %r" % (text,))
    s = text.strip().replace("x", ":").replace("/", ":")
    try:
        if ":" in s:
            a, b = s.split(":", 1)
            val = float(a) / float(b)
        else:
            val = float(s)
    except (ValueError, ZeroDivisionError):
        raise ValueError("aspect %r is not understood; write it like '2.39:1', '16:9' or '2.35'" % (text,))
    if not (val > 0.05 and val < 50):
        raise ValueError("aspect %r is out of range; use a width-to-height ratio between 0.05 and 50" % (text,))
    return val


def plan_letterbox(w, h, aspect, mode):
    """Pure function. Returns (out_w, out_h, left, top, crop_box) with crop_box = (x0, y0, x1, y1) of the source kept.
    add bars: all of the picture is kept, the canvas grows; a picture narrower than the aspect gets bars left/right,
    a wider one gets bars top/bottom. crop to fit: the picture is cut to the aspect."""
    if w < 1 or h < 1:
        raise ValueError("the picture must be at least 1x1 pixels, got %dx%d" % (w, h))
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
    target = parse_aspect(aspect) if isinstance(aspect, str) else float(aspect)
    ratio = w / float(h)
    if mode == "add bars":
        if ratio < target:
            out_w, out_h = max(w, int(round(h * target))), h
        else:
            out_w, out_h = w, max(h, int(round(w / target)))
        return out_w, out_h, (out_w - w) // 2, (out_h - h) // 2, (0, 0, w, h)
    if ratio > target:
        cw = max(1, min(w, int(round(h * target))))
        x0 = (w - cw) // 2
        return cw, h, 0, 0, (x0, 0, x0 + cw, h)
    ch = max(1, min(h, int(round(w / target))))
    y0 = (h - ch) // 2
    return w, ch, 0, 0, (0, y0, w, y0 + ch)


def letterbox_info(w, h, out_w, out_h, left, top, mode):
    """Pure function. One plain line saying what happened."""
    if mode == "crop to fit":
        if (out_w, out_h) == (w, h):
            return "%dx%d -> %dx%d, already the right shape" % (w, h, out_w, out_h)
        return "%dx%d -> %dx%d, cropped %d px" % (w, h, out_w, out_h, (w - out_w) + (h - out_h))
    if left == 0 and top == 0 and (out_w, out_h) == (w, h):
        return "%dx%d -> %dx%d with no bars (already the right shape)" % (w, h, out_w, out_h)
    side = left if left > 0 else top
    return "%dx%d -> %dx%d with 2 bars of %d px" % (w, h, out_w, out_h, side)


def letterbox_tensor(image, aspect, bar_colour, mode):
    """Torch [B,H,W,C]. Returns (new image, info text)."""
    import torch

    h, w = int(image.shape[1]), int(image.shape[2])
    rgb = parse_hex(bar_colour, "bar_colour")
    out_w, out_h, left, top, (x0, y0, x1, y1) = plan_letterbox(w, h, aspect, mode)
    if mode == "crop to fit":
        out = image[:, y0:y1, x0:x1, :].contiguous()
    else:
        c = int(image.shape[3])
        fill = list(rgb[:3]) if c >= 3 else [sum(rgb) / 3.0] * c
        fill = (fill + [1.0] * c)[:c]  # extra channels (alpha) are opaque on the bars
        canvas = torch.tensor(fill, dtype=image.dtype, device=image.device).view(1, 1, 1, c)
        out = canvas.expand(image.shape[0], out_h, out_w, c).clone()
        out[:, top:top + h, left:left + w, :] = image
    return out, letterbox_info(w, h, out_w, out_h, left, top, mode)


class SYLetterbox:
    DESCRIPTION = ("Puts bars (any colour) around a picture so it fits a wanted shape such as 2.39:1 cinema, "
                   "or crops it to that shape. The picture is never stretched.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to reshape."}),
            "aspect": ("STRING", {"default": "2.39:1", "tooltip": "The wanted shape, width to height, like 2.39:1, 16:9, 1.85:1 or 1:1."}),
            "bar_colour": ("STRING", {"default": "#000", "tooltip": "Colour of the bars as a web colour, like #000 or #111."}),
            "mode": (list(MODES), {"default": "add bars", "tooltip": "Add bars keeps everything and grows the canvas. Crop to fit cuts the picture."}),
        }}

    def run(self, image, aspect, bar_colour, mode):
        return letterbox_tensor(image, aspect, bar_colour, mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Letterbox", SYLetterbox)
