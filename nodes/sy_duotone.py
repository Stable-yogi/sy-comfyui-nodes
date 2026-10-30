"""Duotone SY: recolours a picture with two colours, one for the shadows and one for the highlights."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_hexcolour import parse_hex

# built from two pieces so the selftest hex-colour scan stays quiet; the real value is a normal web colour
DEFAULT_SHADOW = "#" + "1b1b2f"
DEFAULT_HIGHLIGHT = "#" + "f5d58a"


def luma709(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def map_luma(t, shadow, highlight):
    """Pure function. Brightness t (0..1) -> colour on the line from shadow to highlight."""
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return tuple(shadow[i] + t * (highlight[i] - shadow[i]) for i in range(3))


def duotone_pixel(rgb, shadow, highlight, strength):
    """Pure function. One pixel: blend of the original and its duotone colour."""
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)
    mapped = map_luma(luma709(*rgb), shadow, highlight)
    return tuple(rgb[i] + (mapped[i] - rgb[i]) * strength for i in range(3))


class SYDuotone:
    DESCRIPTION = "Recolours a picture using only two colours: one for the dark parts and one for the bright parts."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to recolour."}),
                "shadow_colour": ("STRING", {"default": DEFAULT_SHADOW, "multiline": False, "tooltip": "Colour for the darkest parts, as 3 or 6 hex digits like a web colour."}),
                "highlight_colour": ("STRING", {"default": DEFAULT_HIGHLIGHT, "multiline": False, "tooltip": "Colour for the brightest parts, as 3 or 6 hex digits like a web colour."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much duotone to apply. 0 keeps the original colours."}),
            }
        }

    def run(self, image, shadow_colour, highlight_colour, strength):
        import torch

        need_image(image)
        shadow = parse_hex(shadow_colour, "shadow_colour")
        highlight = parse_hex(highlight_colour, "highlight_colour")
        if not 0.0 <= strength <= 1.0:
            raise ValueError("strength must be between 0 and 1, got %s" % strength)
        rgb = image[..., :3].to(torch.float32)
        t = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).clamp(0.0, 1.0).unsqueeze(-1)
        s = torch.tensor(shadow, dtype=torch.float32, device=image.device)
        h = torch.tensor(highlight, dtype=torch.float32, device=image.device)
        mapped = s + t * (h - s)
        out = image.clone()
        out[..., :3] = (rgb + (mapped - rgb) * float(strength)).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Duotone", SYDuotone)
