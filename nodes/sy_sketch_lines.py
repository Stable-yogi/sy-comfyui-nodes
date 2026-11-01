"""Sketch Lines SY: turns a picture into a clean black-line-on-white pen drawing."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_params(detail, sharpness, cutoff, softness):
    if not 0.3 <= float(detail) <= 4.0:
        raise ValueError("detail must be between 0.3 and 4.0, got %s" % (detail,))
    if not 1.0 <= float(sharpness) <= 50.0:
        raise ValueError("sharpness must be between 1 and 50, got %s" % (sharpness,))
    if not 0.0 <= float(cutoff) <= 1.0:
        raise ValueError("cutoff must be between 0 and 1, got %s" % (cutoff,))
    if not 1.0 <= float(softness) <= 100.0:
        raise ValueError("softness must be between 1 and 100, got %s" % (softness,))


def gaussian_kernel(sigma):
    """Pure function. Symmetric blur weights that sum to 1."""
    sigma = float(sigma)
    if sigma <= 0:
        raise ValueError("blur width must be above 0, got %s" % (sigma,))
    half = max(1, int(math.ceil(3.0 * sigma)))
    w = [math.exp(-(i * i) / (2.0 * sigma * sigma)) for i in range(-half, half + 1)]
    s = sum(w)
    return [v / s for v in w]


def xdog_value(a, b, sharpness, cutoff, softness):
    """Pure function. a = fine blur, b = wide blur of one pixel (0..1). Returns 0..1 (0 = line)."""
    check_params(1.0, sharpness, cutoff, softness)
    d = 1.0 + sharpness * (a - b)  # flat area gives 1 (paper); a dark edge pulls it down
    if d >= cutoff:
        return 1.0
    v = 1.0 + math.tanh(softness * (d - cutoff))
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def sketch_tensor(image, detail, sharpness, cutoff, softness, invert=False):
    import torch

    try:
        from ._sy_image_ops import blur_tensor, need_image
    except ImportError:
        from _sy_image_ops import blur_tensor, need_image
    need_image(image)
    check_params(detail, sharpness, cutoff, softness)
    if image.shape[3] >= 3:
        g = image[..., 0:1] * 0.299 + image[..., 1:2] * 0.587 + image[..., 2:3] * 0.114
    else:
        g = image[..., 0:1]
    g = g.float()
    a = blur_tensor(g, float(detail))
    b = blur_tensor(g, float(detail) * 1.6)
    d = 1.0 + sharpness * (a - b)
    soft = 1.0 + torch.tanh(float(softness) * (d - float(cutoff)))
    res = torch.where(d >= float(cutoff), torch.ones_like(d), soft).clamp(0.0, 1.0)
    if invert:
        res = 1.0 - res
    return res.repeat(1, 1, 1, 3).contiguous()


class SYSketchLines:
    DESCRIPTION = ("Turns a photo into a clean pen drawing: black lines on white paper. Compares a fine and a wide blur "
                   "of the picture and keeps the edges. Turn invert on for white lines on black.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The photo to turn into a line drawing."}),
                "detail": ("FLOAT", {"default": 1.0, "min": 0.3, "max": 4.0, "step": 0.05, "tooltip": "Width of the fine blur in pixels. Bigger gives fewer, thicker lines."}),
                "sharpness": ("FLOAT", {"default": 20.0, "min": 1.0, "max": 50.0, "step": 0.5, "tooltip": "How strongly the two blurs are compared. Higher picks out more edges."}),
                "cutoff": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Edge strength below this level becomes line. Raise it for more lines."}),
                "softness": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 100.0, "step": 0.5, "tooltip": "How hard the edge between line and paper is. Higher is crisper."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "On gives white lines on black. Off gives black lines on white paper."}),
            },
        }

    def run(self, image, detail, sharpness, cutoff, softness, invert):
        return (sketch_tensor(image, detail, sharpness, cutoff, softness, invert),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SketchLines", SYSketchLines)
