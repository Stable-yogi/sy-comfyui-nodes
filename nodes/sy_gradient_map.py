"""Gradient Map SY: recolours a picture by turning its brightness into a colour from a 2 or 3 colour gradient."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

DEFAULT_DARK = "#" + "000000"
DEFAULT_LIGHT = "#" + "ffffff"
LUT_SIZE = 1024


def luma(r, g, b):
    """Pure function. Rec.709 brightness of a colour with values 0..1."""
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def gradient_color(t, stops):
    """Pure function. Colour at t (0..1) along evenly spaced stops, each stop an (r, g, b) tuple."""
    if len(stops) < 2:
        raise ValueError("a gradient needs at least 2 colours, got %d" % len(stops))
    t = min(1.0, max(0.0, float(t)))
    pos = t * (len(stops) - 1)
    i = min(int(pos), len(stops) - 2)
    f = pos - i
    return tuple(stops[i][c] * (1.0 - f) + stops[i + 1][c] * f for c in range(3))


def build_stops(color_1, color_2, color_3=""):
    """Pure function. Reads the typed hex colours. An empty color_3 means two stops; otherwise it is the middle stop."""
    a = parse_hex(color_1, "color_1")
    b = parse_hex(color_2, "color_2")
    if color_3 is not None and str(color_3).strip():
        return [a, parse_hex(color_3, "color_3"), b]
    return [a, b]


def check_strength(strength):
    if not 0.0 <= float(strength) <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)


def map_pixel(rgb, stops, strength=1.0, invert=False, mask=1.0):
    """Pure function. One pixel through the gradient map. mask 1 applies it, 0 keeps the pixel."""
    check_strength(strength)
    t = luma(*rgb)
    if invert:
        t = 1.0 - t
    g = gradient_color(t, stops)
    w = float(strength) * float(mask)
    return tuple(rgb[i] + (g[i] - rgb[i]) * w for i in range(3))


class SYGradientMap:
    DESCRIPTION = ("Recolours a picture by mapping its brightness to a colour gradient: darks get the first colour, lights the last. "
                   "Add a middle colour for three tones. Type colours as web hex like fa0 or ffaa00.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to recolour."}),
                "color_1": ("STRING", {"default": DEFAULT_DARK, "multiline": False, "tooltip": "Colour for the darkest parts, 3 or 6 hex digits."}),
                "color_2": ("STRING", {"default": DEFAULT_LIGHT, "multiline": False, "tooltip": "Colour for the lightest parts, 3 or 6 hex digits."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 keeps the original picture, 1 uses only the gradient."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "On: swap which parts get the first and last colour."}),
            },
            "optional": {
                "color_3": ("STRING", {"default": "", "multiline": False, "tooltip": "Optional middle colour. Leave empty for a plain two colour gradient."}),
                "mask": ("MASK", {"tooltip": "White recolours, black keeps the picture. A different size is stretched to fit."}),
            },
        }

    def run(self, image, color_1, color_2, strength, invert, color_3="", mask=None):
        import torch

        if image.ndim != 4 or image.shape[-1] < 3:
            raise ValueError("image must be shaped [batch, height, width, 3 or 4], got %s" % (tuple(image.shape),))
        check_strength(strength)
        stops = build_stops(color_1, color_2, color_3)
        lut = torch.tensor([gradient_color(i / float(LUT_SIZE - 1), stops) for i in range(LUT_SIZE)], dtype=torch.float32, device=image.device)
        rgb = image[..., :3].to(torch.float32)
        y = (rgb * torch.tensor([0.2126, 0.7152, 0.0722], dtype=torch.float32, device=image.device)).sum(-1).clamp(0.0, 1.0)
        if invert:
            y = 1.0 - y
        mapped = lut[(y * (LUT_SIZE - 1)).round().long()]
        w = float(strength)
        if mask is not None:
            m = mask if mask.ndim == 3 else mask.unsqueeze(0)
            if m.shape[0] not in (1, image.shape[0]):
                raise ValueError("mask batch %s does not match image batch %s (use 1 or the same count)" % (m.shape[0], image.shape[0]))
            if tuple(m.shape[1:]) != tuple(image.shape[1:3]):
                import torch.nn.functional as F
                m = F.interpolate(m.to(torch.float32).unsqueeze(1), size=(image.shape[1], image.shape[2]), mode="bilinear", align_corners=False).squeeze(1)
            w = (m.to(torch.float32).clamp(0.0, 1.0) * w).unsqueeze(-1).to(image.device)
        res = (rgb + (mapped - rgb) * w).clamp(0.0, 1.0)
        out = image.clone()
        out[..., :3] = res.to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GradientMap", SYGradientMap)
NODE_DISPLAY_NAME_MAPPINGS["SYGradientMap"] = "Gradient Map SY"
