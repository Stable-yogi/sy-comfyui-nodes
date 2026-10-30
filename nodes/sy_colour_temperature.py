"""Colour Temperature SY: makes a picture warmer or cooler, and shifts it towards magenta or green."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def check_params(warmth, tint):
    if not -100.0 <= warmth <= 100.0:
        raise ValueError("warmth must be between -100 and 100, got %s" % warmth)
    if not -100.0 <= tint <= 100.0:
        raise ValueError("tint must be between -100 and 100, got %s" % tint)


def temperature_gains(warmth, tint):
    """Pure function. Returns (gain_red, gain_green, gain_blue).
    warmth > 0: red up, blue down. tint > 0: green down (towards magenta); tint < 0: green up."""
    check_params(warmth, tint)
    gr = 1.0 + 0.2 * warmth / 100.0
    gb = 1.0 - 0.2 * warmth / 100.0
    gg = 1.0 - 0.15 * tint / 100.0
    return (gr, gg, gb)


def apply_gains(rgb, gains):
    return tuple(min(1.0, max(0.0, rgb[i] * gains[i])) for i in range(3))


class SYColourTemperature:
    DESCRIPTION = "Makes a picture warmer (orange) or cooler (blue), and can push it towards magenta or green."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to adjust."}),
                "warmth": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Above 0 is warmer (more red, less blue). Below 0 is cooler."}),
                "tint": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Above 0 pushes towards magenta. Below 0 pushes towards green."}),
            }
        }

    def run(self, image, warmth, tint):
        import torch

        need_image(image)
        check_params(warmth, tint)
        if warmth == 0.0 and tint == 0.0:
            return (image,)
        gains = torch.tensor(temperature_gains(warmth, tint), dtype=torch.float32, device=image.device)
        rgb = image[..., :3].to(torch.float32)
        out = image.clone()
        out[..., :3] = (rgb * gains).clamp(0.0, 1.0).to(image.dtype)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourTemperature", SYColourTemperature)
NODE_DISPLAY_NAME_MAPPINGS["SYColourTemperature"] = "Colour Temperature SY"
