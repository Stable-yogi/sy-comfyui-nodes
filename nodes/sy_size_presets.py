"""Size Presets SY: pick a common picture size by name."""
try:
    from ._sy_common import category, register
    from ._sy_b_sizeinfo import size_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_b_sizeinfo import size_facts

# name -> (width, height). Twenty common sizes, landscape and portrait.
PRESETS = {
    "512x512 square": (512, 512),
    "512x768 portrait": (512, 768),
    "768x512 landscape": (768, 512),
    "768x768 square": (768, 768),
    "768x1024 portrait": (768, 1024),
    "1024x768 landscape": (1024, 768),
    "832x1216 portrait": (832, 1216),
    "1216x832 landscape": (1216, 832),
    "896x1152 portrait": (896, 1152),
    "1152x896 landscape": (1152, 896),
    "1024x1024 square": (1024, 1024),
    "1024x1536 portrait": (1024, 1536),
    "1536x1024 landscape": (1536, 1024),
    "720x1280 portrait 9:16": (720, 1280),
    "1280x720 wide 16:9": (1280, 720),
    "1080x1920 portrait 9:16": (1080, 1920),
    "1920x1080 wide 16:9": (1920, 1080),
    "1152x2048 portrait 9:16": (1152, 2048),
    "2048x1152 wide 16:9": (2048, 1152),
    "2048x2048 square": (2048, 2048),
}


# more sizes, added after the first twenty so saved workflows keep working
MORE_PRESETS = {
    "1344x768 wide": (1344, 768),
    "768x1344 portrait": (768, 1344),
    "1328x1328 square": (1328, 1328),
    "1664x928 wide": (1664, 928),
    "928x1664 portrait": (928, 1664),
}


def preset_size(name, swap=False):
    """Pure function. Returns (width, height) for a preset name. swap turns landscape into portrait and back."""
    if name in PRESETS:
        w, h = PRESETS[name]
    elif name in MORE_PRESETS:
        w, h = MORE_PRESETS[name]
    else:
        raise ValueError("unknown size preset %r, pick one from the list" % (name,))
    return (h, w) if swap else (w, h)


def preset_report(name, swap=False):
    """Pure function. Returns (width, height, info)."""
    w, h = preset_size(name, swap)
    return w, h, "%s%s: %dx%d (%s)" % (name, ", swapped" if swap else "", w, h, size_facts(w, h))


class SYSizePresets:
    DESCRIPTION = "Pick a common picture size by name, like 1024x1024 square or 2048x1152 wide. Gives a width and a height, plus an info line with the megapixels and shape. The swap switch turns any size on its side."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESETS) + list(MORE_PRESETS), {"default": "1024x1024 square", "tooltip": "A common picture size. Portrait is taller than wide."}),
            },
            "optional": {
                "swap": ("BOOLEAN", {"default": False, "tooltip": "On turns the chosen size on its side: 1216x832 becomes 832x1216."}),
            },
        }

    def run(self, preset, swap=False):
        return preset_report(preset, bool(swap))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SizePresets", SYSizePresets)
NODE_DISPLAY_NAME_MAPPINGS["SYSizePresets"] = "Size Presets SY"
