"""LLM Reply Clean SY: tidy a chatty text reply (fences, intro line, quotes, extra paragraphs)."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
_PREAMBLE = re.compile(r"^\s*(here|sure|certainly|okay|ok|of course|absolutely|alright)\b[^\n]*:\s*$", re.I)
_QUOTE_PAIRS = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"), ("`", "`"))


def _drop_preamble(text):
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and _PREAMBLE.match(lines[i]):
        return "\n".join(lines[i + 1:]).strip()
    return text


def _drop_fences(text):
    kept = [ln for ln in text.split("\n") if not ln.strip().startswith("```")]
    return "\n".join(kept).strip()


def _drop_quotes(text):
    for left, right in _QUOTE_PAIRS:
        if len(text) >= 2 and text[0] == left and text[-1] == right:
            inner = text[1:-1]
            if left not in inner and right not in inner:
                return inner.strip()
    return text


def reply_clean(text, strip_code_fences=True, strip_preamble=True, strip_wrapping_quotes=True,
                first_paragraph_only=False, collapse_blank_lines=True):
    """Pure function. Returns the cleaned text."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if strip_preamble:
        text = _drop_preamble(text)
    if strip_code_fences:
        text = _drop_fences(text)
    if first_paragraph_only:
        parts = re.split(r"\n[ \t]*\n", text, maxsplit=1)
        text = parts[0].strip()
    if strip_wrapping_quotes:
        text = _drop_quotes(text)
    if collapse_blank_lines:
        text = re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", text)
    return text.strip()


class SYLLMReplyClean:
    DESCRIPTION = "Cleans a chatty text reply: removes code fences, an intro line like 'Here is...:', wrapping quotes and extra blank lines."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The reply text you want to clean."}),
                "strip_code_fences": ("BOOLEAN", {"default": True, "tooltip": "On: remove the ``` lines and keep what is inside."}),
                "strip_preamble": ("BOOLEAN", {"default": True, "tooltip": "On: drop a first line like 'Here is your prompt:' that ends with a colon."}),
                "strip_wrapping_quotes": ("BOOLEAN", {"default": True, "tooltip": "On: remove quote marks that wrap the whole text."}),
                "first_paragraph_only": ("BOOLEAN", {"default": False, "tooltip": "On: keep only the first paragraph and drop the rest."}),
                "collapse_blank_lines": ("BOOLEAN", {"default": True, "tooltip": "On: turn several empty lines in a row into one."}),
            }
        }

    def run(self, text, strip_code_fences=True, strip_preamble=True, strip_wrapping_quotes=True,
            first_paragraph_only=False, collapse_blank_lines=True):
        return (reply_clean(text, strip_code_fences, strip_preamble, strip_wrapping_quotes,
                            first_paragraph_only, collapse_blank_lines),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LLMReplyClean", SYLLMReplyClean)
NODE_DISPLAY_NAME_MAPPINGS["SYLLMReplyClean"] = "LLM Reply Clean SY"
