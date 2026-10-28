"""Size Presets SY: pick a common picture size by name."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

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


def preset_size(name):
    """Pure function. Returns (width, height) for a preset name."""
    if name not in PRESETS:
        raise ValueError("unknown size preset %r, pick one from the list" % (name,))
    return PRESETS[name]


class SYSizePresets:
    DESCRIPTION = "Pick a common picture size by name, like 1024x1024 square or 2048x1152 wide. Gives a width and a height."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESETS), {"default": "1024x1024 square", "tooltip": "A common picture size. Portrait is taller than wide."}),
            }
        }

    def run(self, preset):
        return preset_size(preset)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SizePresets", SYSizePresets)
NODE_DISPLAY_NAME_MAPPINGS["SYSizePresets"] = "Size Presets SY"
