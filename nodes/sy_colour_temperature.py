"""Colour Temperature SY: makes a picture warmer or cooler, and shifts it towards magenta or green."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d1_finish import MASK_TIP, MIX_TIP, ENABLED_TIP, finish_rgb, info_line


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
    DESCRIPTION = ("Makes a picture warmer (orange) or cooler (blue), and can push it towards magenta or green. Adds a mask, a mix slider "
                   "to blend with the original, an on/off switch and an info line, and keeps transparency.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to adjust."}),
                "warmth": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Above 0 is warmer (more red, less blue). Below 0 is cooler."}),
                "tint": ("FLOAT", {"default": 0.0, "min": -100.0, "max": 100.0, "step": 1.0, "tooltip": "Above 0 pushes towards magenta. Below 0 pushes towards green."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": MASK_TIP}),
                "mix": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": MIX_TIP}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": ENABLED_TIP}),
            },
        }

    def run(self, image, warmth, tint, mask=None, mix=1.0, enabled=True):
        import torch

        need_image(image)
        check_params(warmth, tint)
        detail = "warmth %g, tint %g" % (warmth, tint)
        if not enabled or (warmth == 0.0 and tint == 0.0):
            return (image, info_line("Colour Temperature", enabled, mix, mask is not None, detail if enabled else ""))
        gains = torch.tensor(temperature_gains(warmth, tint), dtype=torch.float32, device=image.device)
        rgb = image[..., :3].to(torch.float32)
        out = finish_rgb(image, rgb * gains, mask, mix, True)
        return (out, info_line("Colour Temperature", True, mix, mask is not None, detail))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourTemperature", SYColourTemperature)
NODE_DISPLAY_NAME_MAPPINGS["SYColourTemperature"] = "Colour Temperature SY"
