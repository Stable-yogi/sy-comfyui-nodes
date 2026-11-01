"""RTX Upscale SY: runs the NVIDIA RTX video upscaler with a simple target (2x, 1440p, 4K) and a clear message if it is not installed."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core

NODE_NAME = "RTXVideoSuperResolution"
TARGETS = ["2x bigger", "3x bigger", "4x bigger", "Height 1440 (QHD)", "Height 2160 (4K)", "Height 4320 (8K)"]
QUALITY = ["LOW", "MEDIUM", "HIGH", "ULTRA"]
MAX_SIDE = 8192  # the RTX node accepts at most this
MIN_SIDE = 64
MISSING = ("the RTX upscaler is not installed. It comes with the node pack Nvidia VFX (from Comfy-Org): "
           "install it in ComfyUI Manager (search Nvidia VFX), restart ComfyUI, and use a computer with an NVIDIA RTX card.")


def plan_target(width, height, target):
    """Pure function. Returns ('scale', factor) or ('size', width, height) for the RTX node. Raises ValueError when it cannot be done."""
    width, height = int(width), int(height)
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1, got %dx%d" % (width, height))
    if target not in TARGETS:
        raise ValueError("target must be one of %s, got %r" % (TARGETS, target))
    if target.endswith("bigger"):
        factor = float(target[0])
        out_w, out_h = int(width * factor), int(height * factor)
        plan = ("scale", factor)
    else:
        out_h = int(target.split()[1])
        out_w = int(round(width * out_h / float(height) / 8.0)) * 8  # the node steps in 8 pixels
        plan = ("size", out_w, out_h)
    if max(out_w, out_h) > MAX_SIDE:
        raise ValueError("the result would be %dx%d, bigger than the %d pixel limit. Pick a smaller target." % (out_w, out_h, MAX_SIDE))
    if min(out_w, out_h) < MIN_SIDE:
        raise ValueError("the result would be %dx%d, smaller than %d pixels" % (out_w, out_h, MIN_SIDE))
    if plan[0] == "size" and out_h <= height:
        raise ValueError("the picture is already %d pixels high, so there is nothing to upscale to %d. Pick a bigger target." % (height, out_h))
    return plan


def resize_argument(plan):
    """Pure function. The value the RTX node expects for its resize_type input."""
    if plan[0] == "scale":
        return {"resize_type": "scale by multiplier", "scale": plan[1]}
    return {"resize_type": "target dimensions", "width": plan[1], "height": plan[2]}


def info_text(src, out, quality, plan):
    """Pure function. One line telling what happened."""
    return "RTX upscale %dx%d -> %dx%d, quality %s (%s)" % (src[0], src[1], out[0], out[1], quality, plan[0])


def installed():
    import nodes as comfy_nodes
    return NODE_NAME in comfy_nodes.NODE_CLASS_MAPPINGS


class SYRtxUpscale:
    DESCRIPTION = ("Makes a picture or video bigger with the NVIDIA RTX upscaler. Pick a target like 4K instead of working out "
                   "a factor, and get a plain message if the RTX pack or card is missing instead of a red error.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or video frames to enlarge."}),
                "target": (TARGETS, {"default": TARGETS[4], "tooltip": "How big the result should be. 4K = 2160 pixels high, the width follows."}),
                "quality": (QUALITY, {"default": "ULTRA", "tooltip": "ULTRA keeps the most detail and is the slowest."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How strong the effect is. 1 is the default."}),
            }
        }

    def run(self, image, target, quality, strength):
        src = (int(image.shape[2]), int(image.shape[1]))
        plan = plan_target(src[0], src[1], target)
        if not installed():
            raise ValueError(MISSING)
        out = core(NODE_NAME, "RTX Upscale SY", images=image, resize_type=resize_argument(plan), quality=quality,
                   strength=float(strength), image_encoding="8-bit RGB")[0]
        return (out, info_text(src, (int(out.shape[2]), int(out.shape[1])), quality, plan))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RtxUpscale", SYRtxUpscale)
NODE_DISPLAY_NAME_MAPPINGS["SYRtxUpscale"] = "RTX Upscale SY"
