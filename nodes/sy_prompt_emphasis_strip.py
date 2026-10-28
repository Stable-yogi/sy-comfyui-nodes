"""Prompt Emphasis Strip SY: removes weights, brackets, LoRA tags and BREAK from a prompt."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
_LEFT = "\x00L"
_RIGHT = "\x00R"
_WEIGHT = re.compile(r"\(([^()]*?):\s*[-+]?\d*\.?\d+\s*\)")
_LORA = re.compile(r"<lora:[^<>]*>", re.I)
_BREAK = re.compile(r"(?<![A-Za-z0-9_])BREAK(?![A-Za-z0-9_])")


def _tidy(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ,", ",", text)
    text = re.sub(r",(?: ?,)+", ",", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"^[ ,\t]+|[ ,\t]+$", "", text)
    return text.strip()


def strip_emphasis(text, remove_lora_tags=False, remove_break=False):
    """Pure function. Returns the prompt without emphasis marks."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    text = text.replace("\\(", _LEFT).replace("\\)", _RIGHT)
    if remove_lora_tags:
        text = _LORA.sub("", text)
    if remove_break:
        text = _BREAK.sub("", text)
    while True:
        new = _WEIGHT.sub(r"\1", text)
        if new == text:
            break
        text = new
    for ch in "()[]":
        text = text.replace(ch, "")
    text = text.replace(_LEFT, "(").replace(_RIGHT, ")")
    return _tidy(text)


class SYPromptEmphasisStrip:
    DESCRIPTION = "Removes emphasis marks from a prompt: (word:1.2), ((word)) and [word] become word. Can also remove LoRA tags and BREAK."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The prompt you want to clean."}),
                "remove_lora_tags": ("BOOLEAN", {"default": False, "tooltip": "On: also remove tags like <lora:name:0.8>."}),
                "remove_break": ("BOOLEAN", {"default": False, "tooltip": "On: also remove the word BREAK when it stands alone."}),
            }
        }

    def run(self, text, remove_lora_tags=False, remove_break=False):
        return (strip_emphasis(text, remove_lora_tags, remove_break),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptEmphasisStrip", SYPromptEmphasisStrip)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptEmphasisStrip"] = "Prompt Emphasis Strip SY"
