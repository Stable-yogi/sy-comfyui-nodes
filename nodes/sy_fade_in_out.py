"""Fade In Out SY: fades a clip in from and out to a colour."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

CURVES = ["linear", "ease in out"]
DEFAULT_COLOUR = "#" + "000000"


def _shape(t, curve):
    t = min(1.0, max(0.0, t))
    if curve == "linear":
        return t
    if curve == "ease in out":
        return t * t * (3.0 - 2.0 * t)
    raise ValueError("curve must be one of %s, got %r" % (", ".join(CURVES), curve))


def fade_amounts(count, fade_in, fade_out, curve):
    """Pure function. One number per frame, 0..1 (1 = fully the fade colour).
    If fade_in + fade_out is longer than the clip, both are shrunk in proportion."""
    count, fin, fout = int(count), int(fade_in), int(fade_out)
    if count < 1:
        raise ValueError("the batch is empty: connect at least one frame")
    if fin < 0 or fout < 0:
        raise ValueError("fade_in and fade_out cannot be negative, got %d and %d" % (fin, fout))
    _shape(0.0, curve)
    if fin + fout > count:
        total = fin + fout
        fin = int(fin * count / total)
        fout = int(fout * count / total)
    out = []
    for i in range(count):
        a = 0.0
        if fin > 0 and i < fin:
            a = max(a, 1.0 - _shape(i / fin, curve))
        j = count - 1 - i
        if fout > 0 and j < fout:
            a = max(a, 1.0 - _shape(j / fout, curve))
        out.append(a)
    return out


class SYFadeInOut:
    DESCRIPTION = ("Fades a clip in from a colour and out to a colour, such as black or white. "
                   "If the two fades are longer than the clip they are shortened to fit. Transparency is left alone.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The clip as a batch of frames."}),
                "fade_in": ("INT", {"default": 12, "min": 0, "max": 300, "tooltip": "Frames at the start that fade in from the colour. 0 means none."}),
                "fade_out": ("INT", {"default": 12, "min": 0, "max": 300, "tooltip": "Frames at the end that fade out to the colour. 0 means none."}),
                "colour": ("STRING", {"default": DEFAULT_COLOUR, "multiline": False, "tooltip": "Fade colour, as 3 or 6 hex digits like a web colour."}),
                "curve": (CURVES, {"default": "linear", "tooltip": "Linear fades at a steady pace. Ease in out starts and ends gently."}),
            }
        }

    def run(self, images, fade_in, fade_out, colour, curve):
        import torch
        rgb = parse_hex(colour, "colour")
        n = int(images.shape[0])
        amounts = fade_amounts(n, fade_in, fade_out, curve)
        a = torch.tensor(amounts, dtype=images.dtype, device=images.device).view(n, 1, 1, 1)
        k = min(int(images.shape[3]), 3)
        col = torch.tensor(rgb[:k], dtype=images.dtype, device=images.device).view(1, 1, 1, k)
        out = images.clone()
        out[..., :k] = images[..., :k] * (1.0 - a) + col * a
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FadeInOut", SYFadeInOut)
NODE_DISPLAY_NAME_MAPPINGS["SYFadeInOut"] = "Fade In Out SY"
