"""Mask Overlay Preview SY: tints the masked area of a picture so you can see the mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm


def overlay(img, mask, red, green, blue, opacity):
    """Pure function: image [H][W][C], mask [H][W]. A mask of another size is stretched to the image."""
    if opacity < 0.0 or opacity > 1.0:
        raise ValueError("opacity must be between 0 and 1")
    if any(c < 0 or c > 255 for c in (red, green, blue)):
        raise ValueError("colour values must be between 0 and 255")
    if len(mask) != len(img) or len(mask[0]) != len(img[0]):
        mask = mm.resize_nearest_mask(mask, len(img), len(img[0]))
    return mm.overlay_list(img, mask, (red, green, blue), opacity)


class SYMaskOverlayPreview:
    DESCRIPTION = "Shows a mask on top of a picture as a coloured tint, so you can check what it covers."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to show the mask on."}),
                "mask": ("MASK", {"tooltip": "The mask to show. It is stretched to the picture size if needed."}),
                "red": ("INT", {"default": 255, "min": 0, "max": 255, "step": 1, "tooltip": "Red part of the tint colour, 0 to 255."}),
                "green": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Green part of the tint colour, 0 to 255."}),
                "blue": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Blue part of the tint colour, 0 to 255."}),
                "opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the tint is. 0 shows no tint, 1 covers the picture."}),
            }
        }

    def run(self, image, mask, red, green, blue, opacity):
        import torch
        m = mm.t_match_batch(mm.t_resize_mask(mm.t_mask3(mask), image.shape[1], image.shape[2]), image.shape[0])
        a = (m * float(opacity)).unsqueeze(-1).to(image.device)
        col = torch.tensor([red, green, blue], dtype=image.dtype, device=image.device) / 255.0
        out = image.clone()
        out[..., :3] = image[..., :3] * (1.0 - a) + col * a
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskOverlayPreview", SYMaskOverlayPreview)
