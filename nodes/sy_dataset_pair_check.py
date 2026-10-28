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


def pair_report(image_count, captions_text, skip_blank=False):
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
    if blanks:
        shown = ", ".join(str(b) for b in blanks[:20]) + (" ..." if len(blanks) > 20 else "")
        out.append("WARNING: %d caption line%s empty (line %s)." % (len(blanks), " is" if len(blanks) == 1 else "s are", shown))
    return match, "\n".join(out)


class SYDatasetPairCheck:
    DESCRIPTION = "Checks that the number of pictures equals the number of caption lines, and lists empty caption lines."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("match", "report")

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
            },
        }

    def run(self, captions, image_count, skip_blank_lines, images=None):
        if images is not None:
            image_count = int(images.shape[0])
        return pair_report(image_count, captions, skip_blank_lines)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DatasetPairCheck", SYDatasetPairCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYDatasetPairCheck"] = "Dataset Pair Check SY"
