"""Text Join SY: join up to four texts with a separator."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def join_texts(parts, separator, skip_empty):
    """Pure function. Joins parts with separator. skip_empty drops parts that are empty or only spaces."""
    items = ["" if p is None else str(p) for p in parts]
    if skip_empty:
        items = [p for p in items if p.strip() != ""]
    return ("" if separator is None else str(separator)).join(items)


class SYTextJoin:
    DESCRIPTION = "Joins up to four texts into one, with a separator between them. Empty texts can be skipped."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "separator": ("STRING", {"default": ", "}),
                "skip_empty": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "text_a": ("STRING", {"default": "", "multiline": True}),
                "text_b": ("STRING", {"default": "", "multiline": True}),
                "text_c": ("STRING", {"default": "", "multiline": True}),
                "text_d": ("STRING", {"default": "", "multiline": True}),
            },
        }

    def run(self, separator=", ", skip_empty=True, text_a="", text_b="", text_c="", text_d=""):
        return (join_texts([text_a, text_b, text_c, text_d], separator, skip_empty),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextJoin", SYTextJoin)
NODE_DISPLAY_NAME_MAPPINGS["SYTextJoin"] = "Text Join SY"
