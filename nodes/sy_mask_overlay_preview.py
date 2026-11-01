"""Mask Overlay Preview SY: tints the masked area of a picture so you can see the mask."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from ._sy_d3_info import pct_text, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    from _sy_d3_info import pct_text, size_text


def overlay_info(img_w, img_h, mask_w, mask_h, img_count, mask_count, covered, total, inverted=False):
    """Pure function. Plain sentence: what the tint covers and what was adjusted to make the mask fit."""
    parts = ["The tint covers %s of the picture%s." % (pct_text(covered, total), " (mask flipped first)" if inverted else "")]
    if (mask_w, mask_h) != (img_w, img_h):
        parts.append("The mask is %s and was stretched to the picture size %s." % (size_text(mask_w, mask_h), size_text(img_w, img_h)))
    if mask_count != img_count:
        parts.append("The mask batch has %d and the picture batch %d, so masks were repeated or cut to fit." % (mask_count, img_count))
    if covered == 0:
        parts.append("The mask is empty, so you see no tint.")
    return " ".join(parts)


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
    DESCRIPTION = "Shows a mask on top of a picture as a coloured tint, so you can check what it covers. A mask of another size is stretched to fit, and the info output says so. Can also tint the outside of the mask."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

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
            },
            "optional": {
                "invert_mask": ("BOOLEAN", {"default": False, "tooltip": "On: tint everything outside the mask instead. Handy to check what a mask protects."}),
            },
        }

    def run(self, image, mask, red, green, blue, opacity, invert_mask=False):
        import torch
        if image.dim() != 4 or image.shape[0] < 1:
            raise ValueError("the picture batch is empty: connect at least 1 picture")
        m0 = mm.t_mask3(mask)
        if m0.shape[0] < 1:
            raise ValueError("the mask batch is empty: connect at least 1 mask")
        m = mm.t_match_batch(mm.t_resize_mask(m0, image.shape[1], image.shape[2]), image.shape[0])
        if invert_mask:
            m = 1.0 - m
        a = (m * float(opacity)).unsqueeze(-1).to(image.device)
        col = torch.tensor([red, green, blue], dtype=image.dtype, device=image.device) / 255.0
        out = image.clone()
        out[..., :3] = image[..., :3] * (1.0 - a) + col * a
        info = overlay_info(int(image.shape[2]), int(image.shape[1]), int(m0.shape[2]), int(m0.shape[1]),
                            int(image.shape[0]), int(m0.shape[0]), int((m >= 0.5).sum()), int(m.numel()), bool(invert_mask))
        return (out, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskOverlayPreview", SYMaskOverlayPreview)
