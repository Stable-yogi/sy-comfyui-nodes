"""Image Blend SY: lays a second picture over the first with a blend mode and an opacity."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, resize_tensor
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, resize_tensor
    import _sy_d2_common as d2

MODES = ("normal", "multiply", "screen", "overlay", "add", "difference")
FITS = ("stretch", "fill and crop")


def check_fit(top_fit):
    if top_fit not in FITS:
        raise ValueError("top_fit must be one of: %s, got %r" % (", ".join(FITS), top_fit))


def blend_info(mode, opacity, base_size, top_size, top_fit, used_alpha, mask_given, top_has_alpha, base_batch, top_batch):
    """Pure function. One plain line about the blend, including a warning when the top picture was reshaped."""
    parts = ["Blended with %s at opacity %g" % (mode, opacity)]
    if top_size != base_size:
        bw, bh = base_size
        tw, th = top_size
        distorted = abs(tw / float(th) - bw / float(bh)) > 0.01
        if top_fit == "fill and crop":
            parts.append("top %s was scaled to cover %s and the overhang was cut off" % (d2.size_text(tw, th), d2.size_text(bw, bh)))
        else:
            parts.append("top %s was stretched to %s%s" % (d2.size_text(tw, th), d2.size_text(bw, bh),
                                                           " (its shape changed; try top_fit fill and crop)" if distorted else ""))
    if used_alpha:
        parts.append("the top picture's transparency was used")
    elif top_has_alpha:
        parts.append("the top picture has transparency that was ignored (turn on use_top_alpha)")
    if mask_given:
        parts.append("only inside the mask")
    if top_batch != base_batch:
        parts.append("top has %d picture(s) and base %d, so the top ones were repeated or trimmed" % (top_batch, base_batch))
    return "; ".join(parts) + "."


def blend_value(a, b, mode):
    """Pure function. a is the base value, b the top value, both 0..1. Returns the mixed value before opacity."""
    if mode == "normal":
        return b
    if mode == "multiply":
        return a * b
    if mode == "screen":
        return 1.0 - (1.0 - a) * (1.0 - b)
    if mode == "overlay":
        return 2.0 * a * b if a < 0.5 else 1.0 - 2.0 * (1.0 - a) * (1.0 - b)
    if mode == "add":
        return min(1.0, a + b)
    if mode == "difference":
        return abs(a - b)
    raise ValueError("unknown blend mode %r, pick one of: %s" % (mode, ", ".join(MODES)))


def blend_with_opacity(a, b, mode, opacity):
    """Pure function. Result = base * (1 - opacity) + mixed * opacity, kept inside 0..1."""
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("opacity must be between 0 and 1, got %s" % opacity)
    v = a * (1.0 - opacity) + blend_value(a, b, mode) * opacity
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def blend_tensors(a, b, mode, opacity, top_fit="stretch", use_top_alpha=False, mask=None):
    import torch

    if mode not in MODES:
        raise ValueError("unknown blend mode %r, pick one of: %s" % (mode, ", ".join(MODES)))
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("opacity must be between 0 and 1, got %s" % opacity)
    check_fit(top_fit)
    if b.shape[0] != a.shape[0]:
        b = b[[i % b.shape[0] for i in range(a.shape[0])]]
    if b.shape[1:3] != a.shape[1:3]:
        if top_fit == "fill and crop":
            sw, sh, cx, cy = d2.cover_crop_plan(b.shape[2], b.shape[1], a.shape[2], a.shape[1])
            b = resize_tensor(b, sh, sw, "bilinear")[:, cy:cy + a.shape[1], cx:cx + a.shape[2], :]
        else:
            b = resize_tensor(b, a.shape[1], a.shape[2], "bilinear")
    weight = opacity
    if use_top_alpha and b.shape[3] == 4:
        weight = weight * b[..., 3:4]
    if mask is not None:
        weight = weight * d2.t_mask_for_image(mask, a.shape[0], a.shape[1], a.shape[2]).to(a.device, a.dtype)
    base_alpha = a[..., 3:4] if a.shape[3] == 4 else None
    c = min(a.shape[3], b.shape[3], 3)
    a, b = a[..., :c], b[..., :c]
    if mode == "normal":
        mixed = b
    elif mode == "multiply":
        mixed = a * b
    elif mode == "screen":
        mixed = 1.0 - (1.0 - a) * (1.0 - b)
    elif mode == "overlay":
        mixed = torch.where(a < 0.5, 2.0 * a * b, 1.0 - 2.0 * (1.0 - a) * (1.0 - b))
    elif mode == "add":
        mixed = a + b
    else:
        mixed = torch.abs(a - b)
    out = (a * (1.0 - weight) + mixed * weight).clamp(0.0, 1.0)
    if base_alpha is not None:  # keep the base picture's transparency
        out = torch.cat([out, base_alpha], dim=3)
    return out


class SYImageBlend:
    DESCRIPTION = ("Lays one picture over another. Pick a blend mode and how strong the top picture is. A top picture of another size is "
                   "stretched, or scaled to cover and cropped. A mask limits where it shows, and the top picture's transparency can be used.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base": ("IMAGE", {"tooltip": "The bottom picture. The result has its size."}),
                "top": ("IMAGE", {"tooltip": "The picture laid over the base. It is resized to the base size when needed."}),
                "mode": (list(MODES), {"default": "normal", "tooltip": "How the two pictures mix. Normal just shows the top picture."}),
                "opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the top picture is. 0 shows only the base, 1 the full mix."}),
            },
            "optional": {
                "top_fit": (list(FITS), {"default": "stretch", "tooltip": "If the top picture has another size: stretch it, or fill and crop (keeps its shape)."}),
                "use_top_alpha": ("BOOLEAN", {"default": False, "tooltip": "On: transparent parts of the top picture (if it has transparency) let the base show through."}),
                "mask": ("MASK", {"tooltip": "Optional. The top picture shows only where this mask is white. A different size is stretched to fit."}),
            },
        }

    def run(self, base, top, mode, opacity, top_fit="stretch", use_top_alpha=False, mask=None):
        need_image(base)
        need_image(top)
        out = blend_tensors(base, top, mode, float(opacity), top_fit, bool(use_top_alpha), mask)
        info = blend_info(mode, float(opacity), (base.shape[2], base.shape[1]), (top.shape[2], top.shape[1]), top_fit,
                          bool(use_top_alpha) and top.shape[3] == 4, mask is not None, top.shape[3] == 4,
                          base.shape[0], top.shape[0])
        return (out, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageBlend", SYImageBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYImageBlend"] = "Image Blend SY"
