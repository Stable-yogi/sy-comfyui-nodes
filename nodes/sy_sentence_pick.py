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


_INTRO = re.compile(r"^(sure|certainly|of course|absolutely|no problem|here(?:'s|’s| is| are)|i hope)\b", re.I)
_HERE_NOUN = re.compile(r"\b(caption|prompt|description|version|result|story|answer|list|text|revised|rewritten|translation|summary|tags|json)\b", re.I)
_OUTRO = re.compile(r"^(let me know|i hope this|hope this|feel free|is there anything|if you (?:need|want|would like)|would you like)\b", re.I)


def strip_chatter(sentences):
    """Pure function. Removes helper chatter around an answer: 'Sure! Here is the caption:' at the start and
    'Let me know if...' at the end. Text after a colon in the first sentence is kept. Returns (sentences, removed_count)."""
    items = list(sentences)
    removed = 0
    while items and _INTRO.match(items[0]):
        first = items[0]
        if ":" in first and first.split(":", 1)[1].strip():
            items[0] = first.split(":", 1)[1].strip()
            removed += 1
            break
        short_ack = len(first.split()) <= 3 and not first.lower().startswith(("here", "i "))
        here_label = first.lower().startswith("here") and _HERE_NOUN.search(first)
        if first.rstrip().endswith((":", "!")) or short_ack or here_label:
            items.pop(0)
            removed += 1
            continue
        break
    while len(items) > 1 and _OUTRO.match(items[-1]):
        items.pop()
        removed += 1
    return items, removed


def sentence_pick(text, mode="first_n", n=1, index=0, skip_chatter=False):
    """Pure function. Returns (picked_text, total_sentences). skip_chatter first removes 'Sure! Here is...' style lines."""
    return sentence_pick_info(text, mode, n, index, skip_chatter)[:2]


def sentence_pick_info(text, mode="first_n", n=1, index=0, skip_chatter=False):
    """Pure function. Returns (picked_text, total_sentences, info)."""
    if mode not in MODES:
        raise ValueError("unknown mode %r: choose one of %s" % (mode, ", ".join(MODES)))
    n = int(n)
    index = int(index)
    if n < 1:
        raise ValueError("n must be at least 1, got %d" % n)
    sentences = split_sentences(text)
    removed = 0
    if skip_chatter:
        sentences, removed = strip_chatter(sentences)
    total = len(sentences)
    note = "; removed %d chatter sentence(s)" % removed if removed else ""
    if total == 0:
        note += "; WARNING: the text has no sentences"
    if mode == "first_n":
        return " ".join(sentences[:n]), total, "Took the first %d of %d sentence(s)%s" % (min(n, total), total, note)
    if mode == "last_n":
        return " ".join(sentences[-n:]), total, "Took the last %d of %d sentence(s)%s" % (min(n, total), total, note)
    if mode == "index":
        if index < 0 or index >= total:
            raise ValueError("index %d is out of range: the text has %d sentence(s), so use 0 to %d" % (index, total, max(total - 1, 0)))
        return sentences[index], total, "Took sentence %d (counting from 0) of %d%s" % (index, total, note)
    return "\n".join("%d. %s" % (i + 1, s) for i, s in enumerate(sentences)), total, "Listed all %d sentence(s) numbered%s" % (total, note)


class SYSentencePick:
    DESCRIPTION = ("Splits text into sentences and picks the first few, the last few, one by number, or lists them all numbered. "
                   "Can drop helper chatter such as 'Sure! Here is...' and 'Let me know if...', and the info line says what was taken.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "total", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to split into sentences."}),
                "mode": (list(MODES), {"default": "first_n", "tooltip": "first_n and last_n take n sentences. index takes one. all_numbered lists all."}),
                "n": ("INT", {"default": 1, "min": 1, "max": 100000, "tooltip": "How many sentences to take in first_n or last_n mode."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which sentence to take in index mode, counting from 0."}),
            },
            "optional": {
                "skip_chatter": ("BOOLEAN", {"default": False, "tooltip": "On: first drop helper lines like 'Sure! Here is the caption:' and 'Let me know if...'."}),
            },
        }

    def run(self, text, mode="first_n", n=1, index=0, skip_chatter=False):
        return sentence_pick_info(text, mode, n, index, skip_chatter)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SentencePick", SYSentencePick)
NODE_DISPLAY_NAME_MAPPINGS["SYSentencePick"] = "Sentence Pick SY"
