"""Dataset Pair Check SY: checks that a set of pictures and a set of captions have the same count."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def caption_lines(text, skip_blank=False):
    """Pure function. One caption per line. A final empty line from a trailing new line is not a caption."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if skip_blank:
        lines = [l for l in lines if l.strip()]
    return lines


def repeated_lines(lines):
    """Pure function. Returns [(line_number, first_line_number)] for every caption that repeats an earlier one (ignores capitals and spaces)."""
    seen = {}
    out = []
    for i, l in enumerate(lines, start=1):
        key = " ".join(l.lower().split())
        if not key:
            continue
        if key in seen:
            out.append((i, seen[key]))
        else:
            seen[key] = i
    return out


def pair_report(image_count, captions_text, skip_blank=False, warn_duplicates=False):
    """Pure function. Returns (match, report). Empty caption lines are listed so you can fix them."""
    if image_count < 0:
        raise ValueError("image_count must be 0 or more (got %s)" % image_count)
    lines = caption_lines(captions_text, skip_blank)
    n = len(lines)
    blanks = [i + 1 for i, l in enumerate(lines) if not l.strip()]
    match = (n == image_count)
    out = []
    if match:
        out.append("MATCH: %d pictures and %d captions." % (image_count, n))
    elif n > image_count:
        out.append("MISMATCH: %d pictures but %d captions. %d caption%s too many; remove them or add pictures."
                   % (image_count, n, n - image_count, "" if n - image_count == 1 else "s"))
    else:
        out.append("MISMATCH: %d pictures but %d captions. %d caption%s missing; write them or remove pictures."
                   % (image_count, n, image_count - n, "" if image_count - n == 1 else "s"))
    if not match:
        if n < image_count:
            first, last = n + 1, image_count
            out.append("Picture %s %s no caption." % (("%d" % first) if first == last else "%d to %d" % (first, last), "has" if first == last else "have"))
        else:
            first, last = image_count + 1, n
            out.append("Caption line %s %s no picture." % (("%d" % first) if first == last else "%d to %d" % (first, last), "has" if first == last else "have"))
    if blanks:
        shown = ", ".join(str(b) for b in blanks[:20]) + (" ..." if len(blanks) > 20 else "")
        out.append("WARNING: %d caption line%s empty (line %s)." % (len(blanks), " is" if len(blanks) == 1 else "s are", shown))
    if warn_duplicates:
        dup = repeated_lines(lines)
        if dup:
            shown = "; ".join("line %d repeats line %d" % d for d in dup[:5]) + (" ..." if len(dup) > 5 else "")
            out.append("WARNING: %d caption%s repeated (%s)." % (len(dup), " is" if len(dup) == 1 else "s are", shown))
    return match, "\n".join(out)


class SYDatasetPairCheck:
    DESCRIPTION = ("Checks that the number of pictures equals the number of caption lines, says which pictures or lines are left over, "
                   "lists empty caption lines and can warn about repeated captions. Also gives the caption count.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "INT")
    RETURN_NAMES = ("match", "report", "caption_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "captions": ("STRING", {"default": "", "multiline": True, "tooltip": "All captions, one caption per line."}),
                "image_count": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "Number of pictures. Ignored when a picture batch is connected."}),
                "skip_blank_lines": ("BOOLEAN", {"default": False, "tooltip": "On: empty caption lines are not counted. Off: each one counts as a caption."}),
            },
            "optional": {
                "images": ("IMAGE", {"tooltip": "Optional picture batch. When connected, its size is used as the picture count."}),
                "warn_duplicates": ("BOOLEAN", {"default": False, "tooltip": "On: also warn when two captions are the same (capitals and spaces ignored)."}),
            },
        }

    def run(self, captions, image_count, skip_blank_lines, images=None, warn_duplicates=False):
        if images is not None:
            image_count = int(images.shape[0])
        match, report = pair_report(image_count, captions, skip_blank_lines, warn_duplicates)
        return match, report, len(caption_lines(captions, skip_blank_lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DatasetPairCheck", SYDatasetPairCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYDatasetPairCheck"] = "Dataset Pair Check SY"
