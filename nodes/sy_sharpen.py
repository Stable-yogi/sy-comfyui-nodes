"""Sharpen SY: unsharp mask. Adds back the difference between the picture and a blurred copy."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import blur_1d, blur_tensor, need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import blur_1d, blur_tensor, need_image


def unsharp_value(original, blurred, amount):
    """Pure function. original + amount * (original - blurred), kept inside 0..1."""
    v = original + amount * (original - blurred)
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def sharpen_line(values, radius, amount):
    """Pure function on one row of numbers: the same maths the node uses, along one direction."""
    if radius < 0 or amount < 0:
        raise ValueError("radius and amount cannot be negative")
    blurred = blur_1d(values, radius)
    return [unsharp_value(o, bl, amount) for o, bl in zip(values, blurred)]


class SYSharpen:
    DESCRIPTION = "Makes a picture crisper with an unsharp mask. Radius sets how wide the edges are, amount sets how strong."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to sharpen."}),
                "radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 32.0, "step": 0.1, "tooltip": "Width of the edges to sharpen, in pixels. Small is fine detail."}),
                "amount": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 5.0, "step": 0.05, "tooltip": "How strong the sharpening is. 0 changes nothing, above 2 is harsh."}),
            }
        }

    def run(self, image, radius, amount):
        need_image(image)
        if radius < 0 or amount < 0:
            raise ValueError("radius and amount cannot be negative")
        rgb = min(image.shape[3], 3)
        soft = blur_tensor(image[..., :rgb], radius)
        out = image.clone()
        out[..., :rgb] = (image[..., :rgb] + amount * (image[..., :rgb] - soft)).clamp(0.0, 1.0)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Sharpen", SYSharpen)
NODE_DISPLAY_NAME_MAPPINGS["SYSharpen"] = "Sharpen SY"
