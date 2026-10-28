"""Gaussian Blur SY: soft blur of a picture with a chosen radius."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import blur_1d, blur_tensor, gaussian_kernel, need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import blur_1d, blur_tensor, gaussian_kernel, need_image


def blur_line(values, radius):
    """Pure function on one row of numbers. Radius 0 returns the row unchanged."""
    if radius < 0:
        raise ValueError("radius cannot be negative, got %s" % radius)
    return list(values) if radius == 0 else blur_1d(values, radius)


def kernel_width(radius):
    """Pure function. How many pixels wide the blur window is."""
    return len(gaussian_kernel(radius))


class SYGaussianBlur:
    DESCRIPTION = "Blurs a picture softly. A bigger radius gives a stronger blur. Radius 0 leaves the picture as it is."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to blur."}),
                "radius": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 64.0, "step": 0.1, "tooltip": "How far the blur reaches, in pixels. 0 does nothing."}),
            }
        }

    def run(self, image, radius):
        need_image(image)
        if radius < 0:
            raise ValueError("radius cannot be negative, got %s" % radius)
        return (blur_tensor(image, radius).clamp(0.0, 1.0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GaussianBlur", SYGaussianBlur)
NODE_DISPLAY_NAME_MAPPINGS["SYGaussianBlur"] = "Gaussian Blur SY"
