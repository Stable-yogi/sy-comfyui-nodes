"""Tag Frequency SY: counts how often each tag appears in a list of captions."""
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


class SYTagFrequency:
    DESCRIPTION = "Counts how many captions use each tag and lists them from the most common to the rarest."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("report", "unique_tags")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "captions": ("STRING", {"default": "", "multiline": True, "tooltip": "All captions, one caption per line."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next. Usually a comma."}),
                "lowercase": ("BOOLEAN", {"default": True, "tooltip": "On: Dog and dog count as the same tag."}),
                "min_count": ("INT", {"default": 1, "min": 1, "max": 1000000, "tooltip": "Hide tags that appear in fewer captions than this."}),
                "top_n": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Show only the most common tags. 0 shows all of them."}),
            }
        }

    def run(self, captions, separator, lowercase, min_count, top_n):
        return frequency_report(captions, separator, lowercase, min_count, top_n)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TagFrequency", SYTagFrequency)
NODE_DISPLAY_NAME_MAPPINGS["SYTagFrequency"] = "Tag Frequency SY"
