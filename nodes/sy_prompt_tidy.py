"""Prompt Tidy SY: joins two texts and tidies a prompt in one step (spaces, repeats, weights, trigger words, token limit)."""
import re

try:
    from ._sy_common import category, register
    from .sy_prompt_cleaner import split_tags, tag_key
    from .sy_prompt_emphasis_strip import strip_emphasis_ex, _tidy
    from .sy_prompt_weight_wrap import _WEIGHTED
    from .sy_text_join import join_texts
    from .sy_text_trim_to_tokens import estimate_tokens as _chars_tokens
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from sy_prompt_cleaner import split_tags, tag_key
    from sy_prompt_emphasis_strip import strip_emphasis_ex, _tidy
    from sy_prompt_weight_wrap import _WEIGHTED
    from sy_text_join import join_texts
    from sy_text_trim_to_tokens import estimate_tokens as _chars_tokens

MAX_INPUT = 2000000
SEPARATORS = {"comma": ", ", "new line": "\n", "space": " ", "period": ". "}
WEIGHT_CHOICES = ["keep", "strip all", "normalise to 1 decimal"]
TOKEN_STYLES = ["words*1.3 estimate", "characters/4 estimate"]
_ANY_WEIGHT = re.compile(r"\(([^()]*?):\s*([-+]?\d*\.?\d+)\s*\)")
_ANGLE = re.compile(r"(<[^<>]*>)")


def _text_arg(name, value):
    value = "" if value is None else value
    if not isinstance(value, str):
        raise ValueError("%s must be text, got %s" % (name, type(value).__name__))
    if len(value) > MAX_INPUT:
        raise ValueError("%s is too long: %d characters (limit %d)" % (name, len(value), MAX_INPUT))
    return value


def estimate_tokens(text, style=TOKEN_STYLES[0]):
    """Pure function. A rough token count (about): words*1.3 rounded up, or characters/4 rounded up. No real tokenizer."""
    if style not in TOKEN_STYLES:
        raise ValueError("token_style must be one of: %s (got %r)" % (", ".join(TOKEN_STYLES), style))
    if style == TOKEN_STYLES[1]:
        return _chars_tokens(text)
    return (len(text.split()) * 13 + 9) // 10


def lower_keep_tags(text):
    """Pure function. Lowercases the text but leaves <lora:Name:1> style parts alone (file names are case sensitive)."""
    return "".join(p if p.startswith("<") and p.endswith(">") else p.lower() for p in _ANGLE.split(text))


def normalise_weights(text):
    """Pure function. Returns (text, changed) where every (word:1.234) becomes (word:1.2). Other weights stay."""
    changed = [0]

    def fix(m):
        new = "(%s:%.1f)" % (m.group(1), float(m.group(2)))
        if new != m.group(0):
            changed[0] += 1
        return new
    return _ANY_WEIGHT.sub(fix, text), changed[0]


def _tags(text):
    return [t for t in (" ".join(x.split()) for x in split_tags(text)) if t]


def _weight_of(tag):
    m = _WEIGHTED.match(tag)
    return float(m.group(2)) if m else 1.0


def dedupe_tags(tags):
    """Pure function. Returns (tags, removed). Same tag twice (case ignored, (cat:1.2) = cat): the first place stays,
    with the text of the strongest (highest weight) copy."""
    index, out, best, removed = {}, [], {}, 0
    for tag in tags:
        key = tag_key(tag, True, True)
        if key not in index:
            index[key] = len(out)
            best[key] = tag
            out.append(tag)
            continue
        removed += 1
        if _weight_of(tag) > _weight_of(best[key]):
            best[key] = tag
            out[index[key]] = tag
    return out, removed


def _keys(text):
    return {tag_key(t, True, True) for t in _tags(text)}


def _plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def _apply_weights(parts, mode):
    """Returns (parts, note) for the weights step."""
    if mode == WEIGHT_CHOICES[1]:
        w = b = 0
        res = []
        for p in parts:
            s, counts = strip_emphasis_ex(p)
            w += counts["weights"]
            b += counts["brackets"]
            res.append(s)
        bits = []
        if w:
            bits.append(_plural(w, "weight"))
        if b:
            bits.append(_plural(b, "bracket"))
        return [r for r in res if r != ""], ("stripped " + " and ".join(bits)) if bits else ""
    n = 0
    res = []
    for p in parts:
        s, k = normalise_weights(p)
        n += k
        res.append(s)
    return res, ("rounded %s to 1 decimal" % _plural(n, "weight")) if n else ""


def tidy_prompt(text, extra_text="", separator="comma", clean=True, remove_duplicates=False, weights="keep", lowercase=False,
                trigger_words="", remove_words="", max_tokens=0, token_style=TOKEN_STYLES[0]):
    """Pure function. Returns (text, token_estimate, info).
    Order of steps: 1 join text + extra_text with the separator, 2 clean spaces and commas, 3 lowercase,
    4 remove_words, 5 remove duplicates (keeps the strongest weight), 6 weights (keep / strip all / normalise),
    7 trigger words first, 8 cut whole tags from the end to fit max_tokens, 9 count tokens (about)."""
    text = _text_arg("text", text)
    extra_text = _text_arg("extra_text", extra_text)
    trigger_words = _text_arg("trigger_words", trigger_words)
    remove_words = _text_arg("remove_words", remove_words)
    if separator not in SEPARATORS:
        raise ValueError("separator must be one of: %s (got %r)" % (", ".join(SEPARATORS), separator))
    if weights not in WEIGHT_CHOICES:
        raise ValueError("weights must be one of: %s (got %r)" % (", ".join(WEIGHT_CHOICES), weights))
    if token_style not in TOKEN_STYLES:
        raise ValueError("token_style must be one of: %s (got %r)" % (", ".join(TOKEN_STYLES), token_style))
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):
        raise ValueError("max_tokens must be a whole number, got %r" % (max_tokens,))
    if max_tokens < 0 or max_tokens > 4096:
        raise ValueError("max_tokens must be between 0 and 4096 (0 = no limit), got %d" % max_tokens)
    trig, seen = [], set()
    for t in _tags(trigger_words):
        k = tag_key(t, True, True)
        if k not in seen:
            seen.add(k)
            trig.append(t)
    drop = _keys(remove_words)
    clash = [t for t in trig if tag_key(t, True, True) in drop]
    if clash:
        raise ValueError("'%s' is in both trigger_words and remove_words: pick one" % clash[0])

    notes = []
    out = text
    if extra_text.strip():
        head = text.strip(" ,\t\r\n") if separator == "comma" else text.rstrip()
        out = join_texts([head, extra_text.strip()], SEPARATORS[separator], True, True)
        if separator == "period":
            out = re.sub(r"\.\.\s", ". ", out)
        notes.append("joined the extra text")
    if clean:
        tidy = _tidy(out)
        if tidy != out.strip():
            notes.append("cleaned spaces and commas")
        out = tidy
    if lowercase:
        low = lower_keep_tags(out)
        if low != out:
            notes.append("lowercased")
        out = low

    cut = 0
    if remove_duplicates or drop or trig or max_tokens:
        tags = _tags(out)
        if drop:
            kept = [t for t in tags if tag_key(t, True, True) not in drop]
            if len(tags) != len(kept):
                notes.append("removed %s" % _plural(len(tags) - len(kept), "listed tag"))
            tags = kept
        if remove_duplicates:
            tags, n = dedupe_tags(tags)
            if n:
                notes.append("removed %s" % _plural(n, "duplicate"))
        if weights != "keep":
            tags, note = _apply_weights(tags, weights)
            if note:
                notes.append(note)
            weights = "keep"
        if trig:
            tl = [lower_keep_tags(t) if lowercase else t for t in trig]
            tkeys = {tag_key(t, True, True) for t in tl}
            rest = [t for t in tags if tag_key(t, True, True) not in tkeys]
            if tags[:len(tl)] != tl:
                notes.append("put %s first" % _plural(len(tl), "trigger word"))
            tags = tl + rest
        if max_tokens and tags:
            lo, hi = 1, len(tags)  # largest number of tags that fits; at least one stays
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if estimate_tokens(", ".join(tags[:mid]), token_style) <= max_tokens:
                    lo = mid
                else:
                    hi = mid - 1
            cut = len(tags) - lo
            tags = tags[:lo]
        out = ", ".join(tags)
    if weights != "keep":
        parts, note = _apply_weights([out], weights)
        out = parts[0] if parts else ""
        if note:
            notes.append(note)

    count = estimate_tokens(out, token_style)
    if max_tokens and count > max_tokens:
        notes.append("WARNING: still over the limit of %d" % max_tokens)
    info = list(notes) if notes else ["no changes"]
    info.append("%d tokens (about)" % count)
    if cut:
        info.append("cut %s at the end" % _plural(cut, "tag"))
    line = ", ".join(info)
    return out, count, line[0].upper() + line[1:]


class SYPromptTidy:
    DESCRIPTION = ("Joins a prompt with extra text and tidies it in one node. Steps run in this order: join, clean spaces and commas, lowercase, "
                   "remove listed tags, remove duplicates (keeps the strongest weight), weights (keep, strip or round to 1 decimal), "
                   "trigger words first, cut whole tags from the end to fit a token limit. Token counts are only about right. "
                   "Tag steps treat the prompt as a comma list. Info says what changed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "token_estimate", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt to tidy."}),
            },
            "optional": {
                "extra_text": ("STRING", {"multiline": True, "default": "", "tooltip": "Added after the text. Empty means nothing is added."}),
                "separator": (list(SEPARATORS), {"default": "comma", "tooltip": "What goes between the text and the extra text."}),
                "clean": ("BOOLEAN", {"default": True, "tooltip": "On: remove stray spaces, doubled commas and a trailing comma."}),
                "remove_duplicates": ("BOOLEAN", {"default": False, "tooltip": "On: a tag written twice stays once, with the strongest weight."}),
                "weights": (WEIGHT_CHOICES, {"default": "keep", "tooltip": "Keep the (word:1.2) weights, strip them all, or round them to 1 decimal."}),
                "lowercase": ("BOOLEAN", {"default": False, "tooltip": "On: write the prompt in lowercase. <lora:...> tags stay as they are."}),
                "trigger_words": ("STRING", {"default": "", "tooltip": "Words to put first, separated by commas. Not repeated."}),
                "remove_words": ("STRING", {"default": "", "tooltip": "Whole tags to remove, separated by commas. Case and weights are ignored."}),
                "max_tokens": ("INT", {"default": 0, "min": 0, "max": 4096, "tooltip": "0 = no limit. Otherwise whole tags are cut from the end to fit."}),
                "token_style": (TOKEN_STYLES, {"default": TOKEN_STYLES[0], "tooltip": "How tokens are guessed. Both are rough."}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off: the text passes through unchanged."}),
            },
        }

    def run(self, text, extra_text="", separator="comma", clean=True, remove_duplicates=False, weights="keep", lowercase=False,
            trigger_words="", remove_words="", max_tokens=0, token_style=TOKEN_STYLES[0], enabled=True):
        if not enabled:
            text = _text_arg("text", text)
            n = estimate_tokens(text, token_style)
            return text, n, "Off: text passed through unchanged, %d tokens (about)" % n
        return tidy_prompt(text, extra_text, separator, clean, remove_duplicates, weights, lowercase,
                           trigger_words, remove_words, max_tokens, token_style)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptTidy", SYPromptTidy)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptTidy"] = "Prompt Tidy SY"
