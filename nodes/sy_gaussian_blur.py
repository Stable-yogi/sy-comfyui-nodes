"""Gaussian Blur SY: soft blur of a picture with a chosen radius."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import blur_1d, blur_tensor, gaussian_kernel, need_image
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import blur_1d, blur_tensor, gaussian_kernel, need_image
    import _sy_d2_common as d2


def blur_line(values, radius):
    """Pure function on one row of numbers. Radius 0 returns the row unchanged."""
    if radius < 0:
        raise ValueError("radius cannot be negative, got %s" % radius)
    return list(values) if radius == 0 else blur_1d(values, radius)


def kernel_width(radius):
    """Pure function. How many pixels wide the blur window is."""
    return len(gaussian_kernel(radius))


def blur_info(radius, width, height, mask_text=""):
    """Pure function. One plain line about what the blur did."""
    if radius <= 0:
        return "Radius 0: the picture was left as it is."
    win = kernel_width(radius)
    parts = ["Blurred %s with radius %g (window %d px)" % (d2.size_text(width, height), radius, win)]
    if win > 2 * min(width, height):
        parts.append("the radius is large for this picture, so the edges look flat; try a smaller radius")
    parts.append(mask_text)
    return d2.join_info(parts) + "."


class SYGaussianBlur:
    DESCRIPTION = ("Blurs a picture softly. Radius 0 leaves it as it is. Add a mask to blur only that area (the edge of a "
                   "soft mask blends smoothly), and read the info line for what was done.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to blur."}),
                "radius": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 64.0, "step": 0.1, "tooltip": "How far the blur reaches, in pixels. 0 does nothing."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional. Blur only where this mask is white. A different size is stretched to fit."}),
            },
        }

    def run(self, image, radius, mask=None):
        need_image(image)
        if radius < 0:
            raise ValueError("radius cannot be negative, got %s" % radius)
        if radius == 0:
            return (image, blur_info(radius, image.shape[2], image.shape[1]))
        blurred = blur_tensor(image, radius).clamp(0.0, 1.0)
        out, note = d2.t_apply_with_mask(image, blurred, mask)
        return (out, blur_info(radius, image.shape[2], image.shape[1], note))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GaussianBlur", SYGaussianBlur)
NODE_DISPLAY_NAME_MAPPINGS["SYGaussianBlur"] = "Gaussian Blur SY"
