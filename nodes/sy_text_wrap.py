"""Text Wrap SY: breaks long lines of text at a chosen width."""
import re
import textwrap

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def wrap_text(text, width, keep_paragraphs):
    """Pure function. Returns (wrapped_text, line_count).
    keep_paragraphs True: each paragraph (blocks split by blank lines) is wrapped on its own and one blank line is kept between them.
    False: everything is joined into one paragraph first."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    if width < 4 or width > 1000:
        raise ValueError("width must be between 4 and 1000, got %s" % width)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if keep_paragraphs:
        blocks = [b for b in re.split(r"\n[ \t]*\n", text)]
    else:
        blocks = [text]
    out_blocks = []
    for block in blocks:
        flat = " ".join(block.split())
        if not flat:
            if keep_paragraphs and block == "" and len(blocks) > 1:
                continue
            out_blocks.append([])
            continue
        out_blocks.append(textwrap.wrap(flat, width=width, break_long_words=True, break_on_hyphens=False))
    lines = []
    for i, b in enumerate(out_blocks):
        if i > 0 and b:
            lines.append("")
        lines.extend(b)
    while lines and lines[0] == "":
        lines.pop(0)
    result = "\n".join(lines)
    return (result, len(lines))


class SYTextWrap:
    DESCRIPTION = "Breaks long lines of text at a chosen width. Long words are split, and paragraphs can be kept apart."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "line_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to wrap."}),
                "width": ("INT", {"default": 40, "min": 4, "max": 1000, "step": 1, "tooltip": "Most characters allowed on one line."}),
                "keep_paragraphs": ("BOOLEAN", {"default": True, "tooltip": "On keeps a blank line between paragraphs. Off joins all the text into one block."}),
            }
        }

    def run(self, text, width, keep_paragraphs):
        return wrap_text(text, width, keep_paragraphs)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextWrap", SYTextWrap)
NODE_DISPLAY_NAME_MAPPINGS["SYTextWrap"] = "Text Wrap SY"
