"""Coalesce Text SY: gives the first piece of text that is not empty."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def coalesce(values, treat_spaces_as_empty=True, fallback=""):
    """Pure function. Returns (value, slot): the first non-empty value and its place (1 = first), or (fallback, 0)."""
    for slot, v in enumerate(values, 1):
        if v is None:
            continue
        if not isinstance(v, str):
            raise ValueError("slot %d is not text (got %r): connect a text output" % (slot, v))
        if (v.strip() if treat_spaces_as_empty else v) != "":
            return (v, slot)
    return (fallback, 0)


class SYCoalesceText:
    DESCRIPTION = ("Gives the first piece of text that is not empty out of up to five, so optional inputs "
                   "fall back cleanly. Tells you which slot won (0 means the fallback).")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "used_slot")

    @classmethod
    def INPUT_TYPES(cls):
        opt = {"multiline": False, "default": "", "forceInput": True}
        return {
            "required": {
                "text_1": ("STRING", {"default": "", "tooltip": "Checked first. Used if it is not empty."}),
            },
            "optional": {
                "text_2": ("STRING", dict(opt, tooltip="Checked second.")),
                "text_3": ("STRING", dict(opt, tooltip="Checked third.")),
                "text_4": ("STRING", dict(opt, tooltip="Checked fourth.")),
                "text_5": ("STRING", dict(opt, tooltip="Checked fifth.")),
                "treat_spaces_as_empty": ("BOOLEAN", {"default": True, "tooltip": "On: text with only spaces or line breaks counts as empty."}),
                "fallback": ("STRING", {"default": "", "tooltip": "Given back when every slot is empty."}),
            },
        }

    def run(self, text_1, text_2=None, text_3=None, text_4=None, text_5=None, treat_spaces_as_empty=True, fallback=""):
        return coalesce([text_1, text_2, text_3, text_4, text_5], treat_spaces_as_empty, fallback)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CoalesceText", SYCoalesceText)
NODE_DISPLAY_NAME_MAPPINGS["SYCoalesceText"] = "Coalesce Text SY"
