"""Mask From Colour SY: makes a mask from the pixels of a picture that match a colour."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from ._sy_hexcolour import parse_hex
    from ._sy_d3_info import pct_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    from _sy_hexcolour import parse_hex
    from _sy_d3_info import pct_text


def pick_colour(red, green, blue, hex_colour=""):
    """Pure function. Returns (r, g, b) as whole numbers 0..255. A hex text (like 'ff8800') wins over the three numbers."""
    if isinstance(hex_colour, str) and hex_colour.strip():
        return tuple(int(round(v * 255.0)) for v in parse_hex(hex_colour, "hex_colour"))
    return (int(red), int(green), int(blue))


def colour_info(white, total, rgb, tolerance, inverted=False):
    """Pure function. One plain sentence about the result. `white` is the count of white mask pixels (after any flip)."""
    text = "Colour %d,%d,%d with tolerance %d: %s of the pixels are white (%d of %d)%s." % (
        rgb[0], rgb[1], rgb[2], tolerance, pct_text(white, total), white, total, ", mask flipped" if inverted else "")
    if white == 0:
        text += " The mask is empty: raise the tolerance or pick the colour again."
    elif white == total:
        text += " The mask covers the whole picture: lower the tolerance."
    return text


def colour_mask(img, red, green, blue, tolerance):
    """Pure function on a nested-list image [H][W][C] of floats 0..1. Returns a mask [H][W]."""
    if tolerance < 0 or tolerance > 255:
        raise ValueError("tolerance must be between 0 and 255")
    return mm.colour_mask_list(img, (red, green, blue), tolerance)


class SYMaskFromColour:
    DESCRIPTION = "Makes a mask from every pixel close to a chosen colour (type numbers or paste a hex colour). Tolerance sets how close. The info output says how much matched, and warns when nothing did."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to pick the colour from."}),
                "red": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Red part of the wanted colour, 0 to 255."}),
                "green": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1, "tooltip": "Green part of the wanted colour, 0 to 255."}),
                "blue": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Blue part of the wanted colour, 0 to 255."}),
                "tolerance": ("INT", {"default": 20, "min": 0, "max": 255, "step": 1, "tooltip": "How far each colour part may differ and still count. 0 is an exact match."}),
            },
            "optional": {
                "hex_colour": ("STRING", {"default": "", "multiline": False, "tooltip": "Optional web colour such as ff8800 or #f80. When filled it replaces red, green and blue."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "On: white becomes everything that does NOT match the colour."}),
            },
        }

    def run(self, image, red, green, blue, tolerance, hex_colour="", invert=False):
        import torch
        if tolerance < 0 or tolerance > 255:
            raise ValueError("tolerance must be between 0 and 255")
        if image.shape[-1] < 3:
            raise ValueError("the picture needs at least 3 colour channels")
        if image.dim() != 4 or image.shape[0] < 1:
            raise ValueError("the picture batch is empty: connect at least 1 picture")
        rgb = pick_colour(red, green, blue, hex_colour)
        col = torch.tensor(rgb, dtype=torch.float32, device=image.device)
        diff = torch.abs(image[..., :3].float() * 255.0 - col).amax(dim=-1)
        mask = (diff <= tolerance + 1e-4).float()
        if invert:
            mask = 1.0 - mask
        total = int(mask.numel())
        matched = int(round(float(mask.sum())))
        return (mask, colour_info(matched, total, rgb, int(tolerance), bool(invert)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFromColour", SYMaskFromColour)
