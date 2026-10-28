"""Caption Prefix Suffix SY: adds a trigger word before and/or after a caption, unless it is already there."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def _clean_tag(tag):
    return (tag or "").strip().strip(",;").strip()


def _word_char(ch):
    return ch.isalnum() or ch == "_"


def starts_with_tag(text, tag):
    """True when text begins with tag as a whole word or phrase (ignores upper/lower case)."""
    t = text.lstrip()
    if not tag or not t.lower().startswith(tag.lower()):
        return False
    rest = t[len(tag):]
    return rest == "" or not _word_char(rest[0]) or not _word_char(tag[-1])


def ends_with_tag(text, tag):
    """True when text finishes with tag as a whole word or phrase (trailing commas, dots and spaces are ignored)."""
    t = text.rstrip().rstrip(",;. ").rstrip()
    if not tag or not t.lower().endswith(tag.lower()):
        return False
    before = t[:len(t) - len(tag)]
    return before == "" or not _word_char(before[-1]) or not _word_char(tag[0])


def add_prefix_suffix(caption, prefix, suffix, separator=", "):
    """Pure function. Returns the caption with prefix first and suffix last. A tag that is already there is not added twice."""
    prefix = _clean_tag(prefix)
    suffix = _clean_tag(suffix)
    sep = separator if separator is not None else ", "
    body = (caption or "").strip()
    if prefix and not starts_with_tag(body, prefix):
        body = prefix + sep + body if body else prefix
    if suffix and not ends_with_tag(body, suffix):
        body = body.rstrip().rstrip(",;").rstrip()
        body = body + sep + suffix if body else suffix
    return body


def apply_to_text(text, prefix, suffix, separator=", ", per_line=False):
    """Pure function. Works on the whole text, or on every non-empty line when per_line is true."""
    if not per_line:
        return add_prefix_suffix(text, prefix, suffix, separator)
    lines = (text or "").split("\n")
    out = []
    for line in lines:
        out.append(add_prefix_suffix(line, prefix, suffix, separator) if line.strip() else line)
    return "\n".join(out)


class SYCaptionPrefixSuffix:
    DESCRIPTION = "Adds a trigger word before and/or after a caption. Skips it when the caption already starts or ends with it."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("caption",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "caption": ("STRING", {"default": "", "multiline": True, "tooltip": "The caption text. Several captions can be given, one per line."}),
                "prefix": ("STRING", {"default": "", "tooltip": "Trigger word or phrase to put first. Leave empty for none."}),
                "suffix": ("STRING", {"default": "", "tooltip": "Trigger word or phrase to put last. Leave empty for none."}),
                "separator": ("STRING", {"default": ", ", "tooltip": "Text placed between the trigger word and the caption."}),
                "per_line": ("BOOLEAN", {"default": False, "tooltip": "On: treat every line as its own caption. Off: the whole text is one caption."}),
            }
        }

    def run(self, caption, prefix, suffix, separator, per_line):
        return (apply_to_text(caption, prefix, suffix, separator, per_line),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CaptionPrefixSuffix", SYCaptionPrefixSuffix)
NODE_DISPLAY_NAME_MAPPINGS["SYCaptionPrefixSuffix"] = "Caption Prefix Suffix SY"
