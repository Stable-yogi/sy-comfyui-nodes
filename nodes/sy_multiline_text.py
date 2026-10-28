"""Multiline Text SY: a big text box. Lines that start with # are comments and are left out."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def strip_comments(text, keep_empty_lines=True):
    """Pure function. Removes lines whose first non-space character is #. A line starting with \\# keeps a literal #."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    out = []
    for line in text.split("\n"):
        line = line.rstrip("\r")
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("\\#"):
            line = line.replace("\\#", "#", 1)
        if not keep_empty_lines and line.strip() == "":
            continue
        out.append(line)
    return "\n".join(out)


class SYMultilineText:
    DESCRIPTION = "A big text box. Lines starting with # are notes to yourself and are left out. Start a line with \\# to keep a #."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "Your text. Lines that start with # are ignored."}),
                "keep_empty_lines": ("BOOLEAN", {"default": True, "tooltip": "Off: also remove empty lines from the result."}),
            }
        }

    def run(self, text, keep_empty_lines=True):
        return (strip_comments(text, keep_empty_lines),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MultilineText", SYMultilineText)
NODE_DISPLAY_NAME_MAPPINGS["SYMultilineText"] = "Multiline Text SY"
