"""Tag Frequency SY: counts how often each tag appears in a list of captions."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def count_tags(captions_text, separator=",", lowercase=True):
    """Pure function. One caption per line. Returns (caption_count, {tag: count}). A tag counts once per caption."""
    if not separator:
        raise ValueError("separator must not be empty; use a comma for normal tag captions")
    counts = {}
    n = 0
    for line in (captions_text or "").split("\n"):
        if not line.strip():
            continue
        n += 1
        seen = set()
        for tag in line.split(separator):
            tag = " ".join(tag.split())
            if lowercase:
                tag = tag.lower()
            if tag and tag not in seen:
                seen.add(tag)
                counts[tag] = counts.get(tag, 0) + 1
    return n, counts


def frequency_report(captions_text, separator=",", lowercase=True, min_count=1, top_n=0):
    """Pure function. Returns (report_text, unique_tag_count). Sorted by count, then by name. top_n 0 means all."""
    if min_count < 1:
        raise ValueError("min_count must be at least 1 (got %s)" % min_count)
    if top_n < 0:
        raise ValueError("top_n must be 0 (all) or more (got %s)" % top_n)
    n, counts = count_tags(captions_text, separator, lowercase)
    if n == 0:
        raise ValueError("no captions found; put one caption on each line")
    rows = sorted(((c, t) for t, c in counts.items() if c >= min_count), key=lambda r: (-r[0], r[1]))
    shown = rows[:top_n] if top_n else rows
    lines = ["captions: %d" % n, "different tags: %d" % len(counts)]
    if len(shown) < len(counts):
        lines.append("showing: %d" % len(shown))
    lines.append("")
    lines += ["%d  %s" % (c, t) for c, t in shown]
    return "\n".join(lines), len(counts)


def _norm(tag, lowercase):
    tag = " ".join(tag.split())
    return tag.lower() if lowercase else tag


def caption_problems(captions_text, separator=",", lowercase=True, trigger_word="", banned_words="", max_listed=8):
    """Pure function. Checks every caption for the usual training mistakes.
    Returns (report_text, problem_count). Line numbers count from 1 and include blank lines."""
    if not separator:
        raise ValueError("separator must not be empty; use a comma for normal tag captions")
    trigger = _norm(trigger_word or "", lowercase)
    banned = [_norm(b, True) for b in (banned_words or "").replace("\n", ",").split(",") if b.strip()]
    dup, missing, not_first, hits = [], [], [], {}
    total = 0
    for number, line in enumerate((captions_text or "").split("\n"), start=1):
        if not line.strip():
            continue
        total += 1
        tags = [_norm(t, lowercase) for t in line.split(separator)]
        tags = [t for t in tags if t]
        seen, twice = set(), set()
        for t in tags:
            (twice if t in seen else seen).add(t)
        if twice:
            dup.append((number, sorted(twice)))
        if trigger:
            if trigger not in tags:
                missing.append(number)
            elif tags[0] != trigger:
                not_first.append(number)
        for word in banned:
            for t in tags:
                if re.search(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(word), t.lower()):
                    hits.setdefault(word, []).append(number)
                    break

    def lines_of(numbers):
        shown = ", ".join(str(x) for x in numbers[:max_listed])
        return shown + (" ... (%d more)" % (len(numbers) - max_listed) if len(numbers) > max_listed else "")
    out = []
    count = 0
    if dup:
        count += len(dup)
        out.append("Same tag twice in one caption (%d caption(s)): " % len(dup)
                   + "; ".join("line %d: %s" % (n, ", ".join(t)) for n, t in dup[:max_listed])
                   + (" ... (%d more)" % (len(dup) - max_listed) if len(dup) > max_listed else ""))
    if missing:
        count += len(missing)
        out.append("Trigger word '%s' is missing in %d caption(s): lines %s" % (trigger_word.strip(), len(missing), lines_of(missing)))
    if not_first:
        count += len(not_first)
        out.append("Trigger word '%s' is not the first tag in %d caption(s): lines %s" % (trigger_word.strip(), len(not_first), lines_of(not_first)))
    for word, numbers in hits.items():
        count += len(numbers)
        out.append("Banned word '%s' found in %d caption(s): lines %s" % (word, len(numbers), lines_of(numbers)))
    if total == 0:
        return "No captions to check: put one caption on each line", 0
    if not out:
        return "No problems found in %d caption(s)" % total, 0
    return "Problems found: %d in %d caption(s)\n" % (count, total) + "\n".join(out), count


class SYTagFrequency:
    DESCRIPTION = ("Counts how many captions use each tag and lists them from the most common to the rarest. Also checks the captions for "
                   "training mistakes: a tag twice in one caption, a trigger word that is missing or not first, and banned words.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING", "INT")
    RETURN_NAMES = ("report", "unique_tags", "problems", "problem_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "captions": ("STRING", {"default": "", "multiline": True, "tooltip": "All captions, one caption per line."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next. Usually a comma."}),
                "lowercase": ("BOOLEAN", {"default": True, "tooltip": "On: Dog and dog count as the same tag."}),
                "min_count": ("INT", {"default": 1, "min": 1, "max": 1000000, "tooltip": "Hide tags that appear in fewer captions than this."}),
                "top_n": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Show only the most common tags. 0 shows all of them."}),
            },
            "optional": {
                "trigger_word": ("STRING", {"default": "", "tooltip": "Your LoRA trigger word, for example 'ohwx'. Every caption should start with it. Empty skips this check."}),
                "banned_words": ("STRING", {"multiline": True, "default": "", "tooltip": "Words that must not appear in any caption, separated by commas, for example 'watermark, text'."}),
            },
        }

    def run(self, captions, separator, lowercase, min_count, top_n, trigger_word="", banned_words=""):
        report, unique = frequency_report(captions, separator, lowercase, min_count, top_n)
        problems, count = caption_problems(captions, separator, lowercase, trigger_word, banned_words)
        return (report, unique, problems, count)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TagFrequency", SYTagFrequency)
NODE_DISPLAY_NAME_MAPPINGS["SYTagFrequency"] = "Tag Frequency SY"
