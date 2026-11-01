"""Apply Mask To Image SY: hides everything outside a mask, as see-through, black or gray."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

KEEP = ("masked", "outside")


def apply_mask(img, mask, fill, keep="masked"):
    """Pure function: image [H][W][C], mask [H][W]. alpha adds or scales a 4th channel."""
    if len(mask) != len(img) or len(mask[0]) != len(img[0]):
        mask = mm.resize_nearest_mask(mask, len(img), len(img[0]))
    return mm.apply_mask_list(img, mask, fill, keep)


def apply_info(fill, keep, feather):
    """Pure function. One plain sentence about what was hidden."""
    what = "the white part of the mask" if keep == "masked" else "the black part of the mask"
    soft = ", soft edge %d px" % feather if feather else ""
    return "Kept %s; the rest became %s%s" % (what, "see-through" if fill == "alpha" else fill, soft)


class SYApplyMaskToImage:
    DESCRIPTION = "Hides the part of a picture outside the mask. The hidden part becomes see-through (alpha), black or gray. A soft edge (feather) avoids hard cut-out lines. A mask of another size or batch is fitted for you."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to cut out."}),
                "mask": ("MASK", {"tooltip": "The mask. It is stretched to the picture size if needed."}),
                "fill": (list(mm.FILL_MODES), {"default": "alpha", "tooltip": "What the hidden part becomes: see-through (adds an alpha channel), black or gray."}),
                "keep": (list(KEEP), {"default": "masked", "tooltip": "masked keeps the white part of the mask, outside keeps the black part."}),
            },
            "optional": {
                "feather": ("INT", {"default": 0, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Softens the mask edge by this many pixels so the cut-out has no hard line. 0 = off."}),
            },
        }

    def run(self, image, mask, fill, keep, feather=0):
        import torch
        if fill not in mm.FILL_MODES:
            raise ValueError("fill must be alpha, black or gray")
        if keep not in KEEP:
            raise ValueError("keep must be masked or outside")
        if image.shape[-1] < 3:
            raise ValueError("the picture needs at least 3 colour channels")
        if not 0 <= feather <= mm.MAX_RADIUS:
            raise ValueError("feather must be between 0 and %d, got %s" % (mm.MAX_RADIUS, feather))
        m = mm.t_match_batch(mm.t_resize_mask(mm.t_mask3(mask), image.shape[1], image.shape[2]), image.shape[0])
        if feather:
            m = mm.t_blur(m, int(feather)).clamp(0.0, 1.0)
        info = apply_info(fill, keep, int(feather))
        a = (m if keep == "masked" else 1.0 - m).unsqueeze(-1).to(image.device).to(image.dtype)
        rgb = image[..., :3]
        if fill == "alpha":
            old = image[..., 3:4] if image.shape[-1] > 3 else torch.ones_like(a)
            return (torch.cat([rgb, a * old], dim=-1), info)
        f = 0.0 if fill == "black" else mm.FILL_GRAY
        return (torch.cat([rgb * a + f * (1.0 - a), image[..., 3:]], dim=-1), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ApplyMaskToImage", SYApplyMaskToImage)
