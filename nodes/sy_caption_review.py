"""Caption Review SY: flags a caption that is too short, too long, repeats words or holds banned words."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)
# small words that may repeat freely
COMMON = frozenset("a an the and or of in on at to with is are was for by as it its his her their this that from into".split())


def words_of(text):
    return [w.lower() for w in WORD.findall(text or "")]


def parse_banned(text):
    """Split a banned list on commas and new lines. Blank entries are dropped."""
    items = re.split(r"[,\n]", text or "")
    return [i.strip() for i in items if i.strip()]


def review_caption(caption, min_words=5, max_words=75, max_repeat=3, banned=""):
    """Pure function. Returns (ok, report). Every problem found is listed on its own line."""
    if min_words < 0 or max_words < 1 or min_words > max_words:
        raise ValueError("min_words must be 0 or more and not bigger than max_words (got %s and %s)" % (min_words, max_words))
    if max_repeat < 1:
        raise ValueError("max_repeat must be at least 1 (got %s)" % max_repeat)
    words = words_of(caption)
    problems = []
    if len(words) < min_words:
        problems.append("too short: %d word%s, at least %d wanted" % (len(words), "" if len(words) == 1 else "s", min_words))
    if len(words) > max_words:
        problems.append("too long: %d words, at most %d wanted" % (len(words), max_words))
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    for w in sorted(counts):
        if counts[w] > max_repeat and w not in COMMON:
            problems.append('repeated word: "%s" appears %d times (limit %d)' % (w, counts[w], max_repeat))
    doubled = []
    for a, b in zip(words, words[1:]):
        if a == b and a not in doubled:
            doubled.append(a)
    for w in doubled:
        problems.append('doubled word: "%s %s" in a row' % (w, w))
    text = " ".join(words)
    for item in parse_banned(banned):
        phrase = " ".join(words_of(item))
        if phrase and re.search(r"(?:^| )%s(?: |$)" % re.escape(phrase), text):
            problems.append('banned word: "%s" is in the caption' % item)
    if problems:
        return False, "NOT OK: %d problem%s\n%s" % (len(problems), "" if len(problems) == 1 else "s", "\n".join("- " + p for p in problems))
    return True, "OK: %d words, no problems." % len(words)


class SYCaptionReview:
    DESCRIPTION = "Reviews one caption for training: too short or long, words repeated too often, words you banned. Gives true or false and a report."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("ok", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "caption": ("STRING", {"default": "", "multiline": True, "tooltip": "The caption to review."}),
                "min_words": ("INT", {"default": 5, "min": 0, "max": 1000, "tooltip": "Fewer words than this counts as too short."}),
                "max_words": ("INT", {"default": 75, "min": 1, "max": 1000, "tooltip": "More words than this counts as too long."}),
                "max_repeat": ("INT", {"default": 3, "min": 1, "max": 100, "tooltip": "How often one word may appear. Small words like the and of are ignored."}),
                "banned_words": ("STRING", {"default": "", "multiline": True, "tooltip": "Words or phrases that must not appear. Separate with commas or new lines."}),
            }
        }

    def run(self, caption, min_words, max_words, max_repeat, banned_words):
        return review_caption(caption, min_words, max_words, max_repeat, banned_words)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CaptionReview", SYCaptionReview)
NODE_DISPLAY_NAME_MAPPINGS["SYCaptionReview"] = "Caption Review SY"
