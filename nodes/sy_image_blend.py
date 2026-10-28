"""Image Blend SY: lays a second picture over the first with a blend mode and an opacity."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, resize_tensor
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, resize_tensor

MODES = ("normal", "multiply", "screen", "overlay", "add", "difference")


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


def blend_tensors(a, b, mode, opacity):
    import torch

    if mode not in MODES:
        raise ValueError("unknown blend mode %r, pick one of: %s" % (mode, ", ".join(MODES)))
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("opacity must be between 0 and 1, got %s" % opacity)
    if b.shape[0] != a.shape[0]:
        b = b[[i % b.shape[0] for i in range(a.shape[0])]]
    if b.shape[1:3] != a.shape[1:3]:
        b = resize_tensor(b, a.shape[1], a.shape[2], "bilinear")
    c = min(a.shape[3], b.shape[3])
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
    return (a * (1.0 - opacity) + mixed * opacity).clamp(0.0, 1.0)


class SYImageBlend:
    DESCRIPTION = "Lays one picture over another. Pick a blend mode and how strong the top picture is. A smaller top picture is stretched to fit."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base": ("IMAGE", {"tooltip": "The bottom picture. The result has its size."}),
                "top": ("IMAGE", {"tooltip": "The picture laid over the base. It is resized to the base size when needed."}),
                "mode": (list(MODES), {"default": "normal", "tooltip": "How the two pictures mix. Normal just shows the top picture."}),
                "opacity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the top picture is. 0 shows only the base, 1 the full mix."}),
            }
        }

    def run(self, base, top, mode, opacity):
        need_image(base)
        need_image(top)
        return (blend_tensors(base, top, mode, float(opacity)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageBlend", SYImageBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYImageBlend"] = "Image Blend SY"
