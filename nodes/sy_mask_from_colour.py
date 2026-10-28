"""Mask From Colour SY: makes a mask from the pixels of a picture that match a colour."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm


def colour_mask(img, red, green, blue, tolerance):
    """Pure function on a nested-list image [H][W][C] of floats 0..1. Returns a mask [H][W]."""
    if tolerance < 0 or tolerance > 255:
        raise ValueError("tolerance must be between 0 and 255")
    return mm.colour_mask_list(img, (red, green, blue), tolerance)


class SYMaskFromColour:
    DESCRIPTION = "Makes a mask from every pixel that is close to a chosen colour. Tolerance sets how close."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to pick the colour from."}),
                "red": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Red part of the wanted colour, 0 to 255."}),
                "green": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1, "tooltip": "Green part of the wanted colour, 0 to 255."}),
                "blue": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Blue part of the wanted colour, 0 to 255."}),
                "tolerance": ("INT", {"default": 20, "min": 0, "max": 255, "step": 1, "tooltip": "How far each colour part may differ and still count. 0 is an exact match."}),
            }
        }

    def run(self, image, red, green, blue, tolerance):
        import torch
        if tolerance < 0 or tolerance > 255:
            raise ValueError("tolerance must be between 0 and 255")
        if image.shape[-1] < 3:
            raise ValueError("the picture needs at least 3 colour channels")
        col = torch.tensor([red, green, blue], dtype=torch.float32, device=image.device)
        diff = torch.abs(image[..., :3].float() * 255.0 - col).amax(dim=-1)
        return ((diff <= tolerance + 1e-4).float(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFromColour", SYMaskFromColour)
