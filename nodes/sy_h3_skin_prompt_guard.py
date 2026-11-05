"""H3 Skin Prompt Guard SY: cleans a video prompt of words that make skin look shiny or plastic, and puts the LoRA trigger words first."""
import os
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

WORDS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sy_skin_words.txt")
MAX_WORDS_BYTES = 1024 * 1024
STYLES = ("photoreal deep focus", "none")
MODES = ("clean", "warn")

DEFAULT_LISTS = {
    "shine": ["flawless", "glow", "glowing", "glowy", "shimmer", "shimmering", "shiny", "shine", "highlighter", "wet skin",
              "wet look", "dewy", "glossy", "oily", "sheen", "luminous skin", "radiant skin", "porcelain skin", "airbrushed"],
    "skin_detail": ["pores", "visible pores", "skin pores", "peach fuzz", "vellus hair", "freckles", "faint freckles",
                    "skin texture", "fine lines", "matte skin", "natural skin texture", "imperfections"],
    "negation": ["no", "not", "without", "avoid", "never", "free of"],
    "opening": {"photoreal deep focus": "A photoreal video, deep focus, natural soft light."},
}
_SECTIONS = ("shine", "skin_detail", "negation", "opening")
_QUOTE = re.compile(r'"[^"]*"|“[^”]*”')
_HOLD = "\x00"


def default_lists():
    return {"shine": list(DEFAULT_LISTS["shine"]), "skin_detail": list(DEFAULT_LISTS["skin_detail"]),
            "negation": list(DEFAULT_LISTS["negation"]), "opening": dict(DEFAULT_LISTS["opening"])}


def parse_word_list(text):
    """Pure function. Reads the word list text. Sections missing from the text keep the built-in default."""
    lists = default_lists()
    section = None
    seen = set()
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().lower()
            if section not in _SECTIONS:
                raise ValueError("unknown section [%s] in the skin word list. Allowed: %s" % (section, ", ".join(_SECTIONS)))
            if section not in seen:
                seen.add(section)
                lists[section] = {} if section == "opening" else []
            continue
        if section is None:
            raise ValueError("the skin word list has a line before any [section]: %r" % line)
        if section == "opening":
            if "=" not in line:
                raise ValueError("an [opening] line must look like: name = sentence (got %r)" % line)
            name, sentence = line.split("=", 1)
            lists["opening"][name.strip().lower()] = " ".join(sentence.split())
        else:
            word = " ".join(line.lower().split())
            if word not in lists[section]:
                lists[section].append(word)
    return lists


def load_word_list(path=None):
    """Reads the word list file (the default one next to the nodes). A missing file gives the built-in lists."""
    path = path or WORDS_FILE
    if not os.path.isfile(path):
        return default_lists()
    if os.path.getsize(path) > MAX_WORDS_BYTES:
        raise ValueError("the skin word list file is bigger than 1 MB: %s" % os.path.basename(path))
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_word_list(f.read())


def _phrase_regex(phrases):
    """Regex that matches any phrase as whole words, longest first, any spacing between words, ignoring case."""
    parts = []
    for p in sorted({" ".join(str(x).lower().split()) for x in phrases if str(x).strip()}, key=lambda s: (-len(s), s)):
        parts.append(r"\s+".join(re.escape(w) for w in p.split()))
    if not parts:
        return None
    return re.compile(r"(?<!\w)(?:%s)(?!\w)" % "|".join(parts), re.IGNORECASE)


def split_quotes(text):
    """Pure function. Replaces every quoted passage by a hold mark. Returns (text_with_marks, [quoted passages])."""
    held = []

    def hold(m):
        held.append(m.group(0))
        return "%s%d%s" % (_HOLD, len(held) - 1, _HOLD)
    return _QUOTE.sub(hold, text), held


def restore_quotes(text, held):
    """Pure function. Puts the quoted passages back."""
    return re.sub("%s(\\d+)%s" % (_HOLD, _HOLD), lambda m: held[int(m.group(1))], text)


def tidy(text):
    """Pure function. Fixes doubled spaces and commas left behind by removals."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+([,.;])", r"\1", text)
    text = re.sub(r"([,;])(?:[ \t]*[,;])+", r"\1", text)
    text = re.sub(r",[ \t]*\.", ".", text)
    text = re.sub(r"^[\s,;]+", "", text)
    text = re.sub(r"[\s,;]+$", "", text)
    return text


_BOUNDARY = re.compile(r"[,.;\n\x00]|(?<!\w)and(?!\w)", re.IGNORECASE)
_WORD = re.compile(r"\w+")


def find_negated_clauses(text, negation_words, skin_words):
    """Pure function. Spans (start, end) of clauses like 'no oily skin': a negation word with a skin or shine word within 4 words.
    A clause ends at the next comma, full stop or 'and'. Spans do not overlap and are in order."""
    neg = _phrase_regex(negation_words)
    skin = _phrase_regex(skin_words)
    if neg is None or skin is None:
        return []
    spans = []
    pos = 0
    while True:
        m = neg.search(text, pos)
        if not m:
            break
        tail = text[m.end():]
        b = _BOUNDARY.search(tail)
        clause_end = b.start() if b else len(tail)
        clause = tail[:clause_end]
        words = list(_WORD.finditer(clause))
        window_end = words[3].end() if len(words) >= 4 else len(clause)
        hit = skin.search(clause)
        if words and hit and hit.start() < window_end:
            spans.append((m.start(), m.end() + clause_end))
            pos = m.end() + clause_end
        else:
            pos = m.end()
    return spans


def _cut(text, spans):
    for s, e in reversed(spans):
        text = text[:s] + text[e:]
    return text


def has_prefix(text, prefix):
    """Pure function. True when text starts with prefix (ignoring case) and the prefix ends at a word end."""
    if not prefix or not text.lower().startswith(prefix.lower()):
        return False
    rest = text[len(prefix):]
    return rest == "" or not (rest[0].isalnum() or rest[0] == "_") or not (prefix[-1].isalnum() or prefix[-1] == "_")


def guard_prompt(prompt, lists, mode="clean", add_opening_line=True, opening_text="", keep_skin_words=False, trigger_text=""):
    """Pure function. Returns (new_prompt, report, changed). See the node description for the rules."""
    if mode not in MODES:
        raise ValueError("mode must be clean or warn, not %r" % (mode,))
    original = str(prompt if prompt is not None else "")
    if not original.strip():
        return "", "The prompt is empty.", False
    trigger = " ".join(str(trigger_text or "").split())

    # keep a trigger that is already at the start exactly as it is
    head, sep, body = "", "", original.strip()
    if trigger and has_prefix(body, trigger):
        head = body[:len(trigger)]
        rest = body[len(trigger):]
        sep = re.match(r"[\s.,;]*", rest).group(0)
        body = rest[len(sep):]

    text, held = split_quotes(body)
    shine_re = _phrase_regex(lists["shine"])
    detail_re = _phrase_regex(lists["skin_detail"])
    removed_words, removed_clauses, dropped = [], [], []

    # b) negation clauses about skin
    skin_words = list(lists["shine"]) + ([] if keep_skin_words else list(lists["skin_detail"]))
    spans = find_negated_clauses(text, lists["negation"], skin_words)
    for s, e in spans:
        removed_clauses.append(restore_quotes(text[s:e], held).strip())
    if mode == "clean":
        text = _cut(text, spans)

    # c) shine words
    if shine_re is not None:
        scan = text if mode == "clean" else _cut(text, spans)
        found = [m.group(0).lower() for m in shine_re.finditer(scan)]
        removed_words.extend(" ".join(w.split()) for w in found)
        if mode == "clean":
            text = shine_re.sub("", text)

    # d) too many skin detail words: keep the first one only
    if detail_re is not None and not keep_skin_words:
        scan = text if mode == "clean" else _cut(text, spans)
        ms = list(detail_re.finditer(scan))
        if len(ms) >= 3:
            dropped = [" ".join(m.group(0).lower().split()) for m in ms[1:]]
            if mode == "clean":
                out, last = [], 0
                for m in ms[1:]:
                    out.append(scan[last:m.start()])
                    last = m.end()
                out.append(scan[last:])
                text = "".join(out)

    count = len(removed_words) + len(removed_clauses) + len(dropped)
    if mode == "clean" and count:
        text = tidy(text)
    body = restore_quotes(text, held)

    # e) trigger words first, then the opening line, then the prompt
    opening = " ".join(str(opening_text or "").split()) if add_opening_line else ""
    if opening and body.lower().startswith(opening.lower()):
        opening = ""
    pieces = []
    if head:
        sep = sep or " "
    elif trigger:
        head = trigger if trigger[-1] in ".!?" else trigger + "."
        sep = " "
    if opening and body:
        body = opening + " " + body
    elif opening:
        body = opening
    result = (head + (sep if body else "") + body) if head else body

    # report
    lines = []
    if removed_words:
        lines.append(("Shine words %s: " % ("removed" if mode == "clean" else "found, not removed")) + ", ".join(removed_words) + ".")
    if removed_clauses:
        lines.append(("Skin clauses %s: " % ("removed" if mode == "clean" else "found, not removed")) + "; ".join('"%s"' % c for c in removed_clauses) + ".")
    if dropped:
        lines.append(("Extra skin detail words %s (kept the first): " % ("dropped" if mode == "clean" else "found, not dropped")) + ", ".join(dropped) + ".")
    if count:
        lines.append("%d change%s %s." % (count, "" if count == 1 else "s", "made" if mode == "clean" else "needed"))
    report = " ".join(lines) if lines else "Nothing to change."
    if result != original.strip() and not count:
        report = "Only the trigger words or opening line were added."
    return result, report, result != original.strip()


class SYH3SkinPromptGuard:
    DESCRIPTION = ("Cleans a video prompt for realistic skin. Removes shine and glow words and clauses like 'no oily skin', keeps only the first "
                   "skin detail word when there are three or more, and puts the LoRA trigger words and a short photoreal opening line first. "
                   "Text in double quotes is never touched.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "BOOLEAN")
    RETURN_NAMES = ("prompt", "report", "changed")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "The video prompt to clean. Text inside double quotes is left alone."}),
                "mode": (list(MODES), {"default": "clean", "tooltip": "clean removes the words. warn only lists them and leaves the text as it is."}),
                "add_opening_line": ("BOOLEAN", {"default": True, "tooltip": "Put a short photoreal opening sentence in front of the prompt."}),
                "opening_style": (list(STYLES), {"default": "photoreal deep focus", "tooltip": "Which opening sentence to use. none adds no sentence."}),
                "keep_skin_words": ("BOOLEAN", {"default": False, "tooltip": "Off keeps only the first skin detail word when there are three or more."}),
            },
            "optional": {
                "trigger_text": ("STRING", {"default": "", "forceInput": False, "tooltip": "LoRA trigger words to put first, for example from H3 Skin Recipe."}),
            },
        }

    def run(self, prompt, mode="clean", add_opening_line=True, opening_style="photoreal deep focus", keep_skin_words=False, trigger_text=""):
        if opening_style not in STYLES:
            raise ValueError("opening_style must be one of: %s" % ", ".join(STYLES))
        lists = load_word_list()
        opening = lists["opening"].get(opening_style, DEFAULT_LISTS["opening"].get(opening_style, "")) if opening_style != "none" else ""
        text, report, changed = guard_prompt(prompt, lists, mode, bool(add_opening_line) and opening_style != "none", opening,
                                             bool(keep_skin_words), trigger_text)
        return (text, report, changed)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3 Skin Prompt Guard", SYH3SkinPromptGuard)
