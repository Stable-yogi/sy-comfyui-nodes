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
_EMBED = re.compile(r"(?<![A-Za-z0-9_])embedding:[^\s,()\[\]<>]+", re.I)


def _tidy(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ,", ",", text)
    text = re.sub(r",(?: ?,)+", ",", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"^[ ,\t]+|[ ,\t]+$", "", text)
    return text.strip()


def strip_emphasis_ex(text, remove_lora_tags=False, remove_break=False, remove_embeddings=False):
    """Pure function. Returns (prompt without emphasis marks, counts) where counts says how many of each thing were removed."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    counts = {"weights": 0, "brackets": 0, "lora": 0, "break": 0, "embeddings": 0}
    text = text.replace("\\(", _LEFT).replace("\\)", _RIGHT)
    if remove_lora_tags:
        text, counts["lora"] = _LORA.subn("", text)
    if remove_break:
        text, counts["break"] = _BREAK.subn("", text)
    if remove_embeddings:
        text, counts["embeddings"] = _EMBED.subn("", text)
    while True:
        new, k = _WEIGHT.subn(r"\1", text)
        if new == text:
            break
        counts["weights"] += k
        text = new
    for ch in "()[]":
        counts["brackets"] += text.count(ch)
        text = text.replace(ch, "")
    text = text.replace(_LEFT, "(").replace(_RIGHT, ")")
    return _tidy(text), counts


def strip_emphasis(text, remove_lora_tags=False, remove_break=False, remove_embeddings=False):
    """Pure function. Returns the prompt without emphasis marks."""
    return strip_emphasis_ex(text, remove_lora_tags, remove_break, remove_embeddings)[0]


def strip_info(counts):
    """Pure function. One plain line saying what was removed."""
    names = (("weights", "weight"), ("brackets", "bracket"), ("lora", "LoRA tag"), ("break", "BREAK word"), ("embeddings", "embedding"))
    parts = ["%d %s%s" % (counts[k], word, "" if counts[k] == 1 else "s") for k, word in names if counts.get(k)]
    return ("Removed " + ", ".join(parts) + ".") if parts else "Nothing to strip."


class SYPromptEmphasisStrip:
    DESCRIPTION = ("Removes emphasis marks from a prompt: (word:1.2), ((word)) and [word] become word. Can also remove LoRA tags, BREAK "
                   "and embedding names. An info line counts what was removed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The prompt you want to clean."}),
                "remove_lora_tags": ("BOOLEAN", {"default": False, "tooltip": "On: also remove tags like <lora:name:0.8>."}),
                "remove_break": ("BOOLEAN", {"default": False, "tooltip": "On: also remove the word BREAK when it stands alone."}),
            },
            "optional": {
                "remove_embeddings": ("BOOLEAN", {"default": False, "tooltip": "On: also remove names like embedding:easynegative."}),
            },
        }

    def run(self, text, remove_lora_tags=False, remove_break=False, remove_embeddings=False):
        out, counts = strip_emphasis_ex(text, remove_lora_tags, remove_break, remove_embeddings)
        return out, strip_info(counts)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptEmphasisStrip", SYPromptEmphasisStrip)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptEmphasisStrip"] = "Prompt Emphasis Strip SY"
