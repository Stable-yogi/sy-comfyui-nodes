"""Sharpen SY: unsharp mask. Adds back the difference between the picture and a blurred copy."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import blur_1d, blur_tensor, need_image
    from ._sy_d3_info import need_nonempty
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import blur_1d, blur_tensor, need_image
    from _sy_d3_info import need_nonempty


def unsharp_value(original, blurred, amount, threshold=0.0):
    """Pure function. original + amount * (original - blurred), kept inside 0..1.
    A difference smaller than `threshold` is ignored, so smooth areas and noise are not sharpened."""
    diff = original - blurred
    if threshold > 0.0 and abs(diff) < threshold:
        diff = 0.0
    v = original + amount * diff
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def sharpen_line(values, radius, amount, threshold=0.0):
    """Pure function on one row of numbers: the same maths the node uses, along one direction."""
    if radius < 0 or amount < 0:
        raise ValueError("radius and amount cannot be negative")
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    blurred = blur_1d(values, radius)
    return [unsharp_value(o, bl, amount, threshold) for o, bl in zip(values, blurred)]


def sharpen_info(radius, amount, threshold=0.0):
    """Pure function. Plain sentence: what was done, with a hint when the setting is too weak or too harsh."""
    if radius < 0 or amount < 0:
        raise ValueError("radius and amount cannot be negative")
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    if amount == 0:
        return "Amount is 0: nothing was sharpened."
    text = "Sharpened edges about %.1f px wide, strength %.2f" % (radius, amount)
    if threshold > 0:
        text += ", ignoring brightness differences below %.2f (smooth areas and noise stay untouched)" % threshold
    text += "."
    if amount > 2.0:
        text += " Strength above 2 can leave bright halos along edges: try a lower amount."
    return text


class SYSharpen:
    DESCRIPTION = "Makes a picture crisper with an unsharp mask. Radius sets how wide the edges are, amount sets how strong, and the optional threshold keeps smooth areas and noise from being sharpened. The info output says what was done."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to sharpen."}),
                "radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 32.0, "step": 0.1, "tooltip": "Width of the edges to sharpen, in pixels. Small is fine detail."}),
                "amount": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0, "step": 0.05, "tooltip": "How strong the sharpening is. 0 changes nothing, above 2 is harsh."}),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.005, "tooltip": "Ignore brightness changes smaller than this, so noise is not sharpened. 0 sharpens everything; try 0.02."}),
            },
        }

    def run(self, image, radius, amount, threshold=0.0):
        need_image(image)
        need_nonempty(image.shape)
        if radius < 0 or amount < 0:
            raise ValueError("radius and amount cannot be negative")
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
        rgb = min(image.shape[3], 3)
        soft = blur_tensor(image[..., :rgb], radius)
        out = image.clone()
        diff = image[..., :rgb] - soft
        if threshold > 0.0:
            diff = diff * (diff.abs() >= threshold).to(diff.dtype)
        out[..., :rgb] = (image[..., :rgb] + amount * diff).clamp(0.0, 1.0)
        return (out, sharpen_info(float(radius), float(amount), float(threshold)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Sharpen", SYSharpen)
NODE_DISPLAY_NAME_MAPPINGS["SYSharpen"] = "Sharpen SY"
