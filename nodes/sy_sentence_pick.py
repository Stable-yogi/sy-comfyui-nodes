"""Sentence Pick SY: splits text into sentences and picks the first, the last, one by number, or all numbered."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
MODES = ("first_n", "last_n", "index", "all_numbered")
_ABBR = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "e.g", "i.e", "no", "fig", "inc", "ltd", "co"}
_END = re.compile("[.!?]+[\"'”’)\\]]*(?=\\s|$)")


def split_sentences(text):
    """Pure function. Simple rule-based split on . ! ? followed by space or the end. No ML."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    sentences = []
    start = 0
    for m in _END.finditer(text):
        if m.group(0) == ".":
            words = text[start:m.start()].split()
            last = words[-1].lower() if words else ""
            if last in _ABBR or (len(last) == 1 and last.isalpha() and words[-1].isupper()):
                continue
        piece = text[start:m.end()].strip()
        if piece:
            sentences.append(piece)
        start = m.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def sentence_pick(text, mode="first_n", n=1, index=0):
    """Pure function. Returns (picked_text, total_sentences)."""
    if mode not in MODES:
        raise ValueError("unknown mode %r: choose one of %s" % (mode, ", ".join(MODES)))
    n = int(n)
    index = int(index)
    if n < 1:
        raise ValueError("n must be at least 1, got %d" % n)
    sentences = split_sentences(text)
    total = len(sentences)
    if mode == "first_n":
        return " ".join(sentences[:n]), total
    if mode == "last_n":
        return " ".join(sentences[-n:]), total
    if mode == "index":
        if index < 0 or index >= total:
            raise ValueError("index %d is out of range: the text has %d sentence(s), so use 0 to %d" % (index, total, max(total - 1, 0)))
        return sentences[index], total
    return "\n".join("%d. %s" % (i + 1, s) for i, s in enumerate(sentences)), total


class SYSentencePick:
    DESCRIPTION = "Splits text into sentences and picks the first few, the last few, one by number, or lists them all numbered."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "total")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to split into sentences."}),
                "mode": (list(MODES), {"default": "first_n", "tooltip": "first_n and last_n take n sentences. index takes one. all_numbered lists all."}),
                "n": ("INT", {"default": 1, "min": 1, "max": 100000, "tooltip": "How many sentences to take in first_n or last_n mode."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which sentence to take in index mode, counting from 0."}),
            }
        }

    def run(self, text, mode="first_n", n=1, index=0):
        return sentence_pick(text, mode, n, index)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SentencePick", SYSentencePick)
NODE_DISPLAY_NAME_MAPPINGS["SYSentencePick"] = "Sentence Pick SY"
