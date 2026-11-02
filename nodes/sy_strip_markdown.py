"""Strip Markdown SY: turns reply text with markdown marks into clean plain text."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_RULE = re.compile(r"\s*([-*_])(\s*\1){2,}\s*")
_HEADING = re.compile(r"^\s{0,3}#{1,6}(\s+|$)")
_HEADING_TAIL = re.compile(r"\s+#+\s*$")
_QUOTE = re.compile(r"^\s*(>\s?)+")
_BULLET = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_CODE = re.compile(r"(`+)(.+?)\1")
_BOLD = re.compile(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1")
_STAR = re.compile(r"\*(?=\S)(.+?)(?<=\S)\*")
_UNDER = re.compile(r"(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)")
_STRIKE = re.compile(r"~~(?=\S)(.+?)(?<=\S)~~")


def _clean_line(line, keep_bullets, keep_link_text):
    if _RULE.fullmatch(line):
        return ""
    line = _HEADING.sub("", line, count=1)
    line = _HEADING_TAIL.sub("", line) if line != line.strip() or "#" in line else line
    line = _QUOTE.sub("", line, count=1)
    m = _BULLET.match(line)
    if m:
        line = (m.group(1) + "- " + m.group(2)) if keep_bullets else m.group(2)
    codes = []

    def hold(match):
        codes.append(match.group(2))
        return "\x00%d\x00" % (len(codes) - 1)

    line = _CODE.sub(hold, line)
    line = _IMAGE.sub((lambda mm: mm.group(1)) if keep_link_text else "", line)
    line = _LINK.sub((lambda mm: mm.group(1)) if keep_link_text else "", line)
    line = _BOLD.sub(lambda mm: mm.group(2), line)
    line = _STAR.sub(lambda mm: mm.group(1), line)
    line = _UNDER.sub(lambda mm: mm.group(1), line)
    line = _STRIKE.sub(lambda mm: mm.group(1), line)
    return re.sub("\x00(\\d+)\x00", lambda mm: codes[int(mm.group(1))], line)


def strip_markdown(text, keep_bullets=False, keep_link_text=True):
    """Pure function. Removes markdown marks and keeps the words. Code content is kept as it is."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    out = []
    in_fence = False
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        out.append(line.rstrip() if in_fence else _clean_line(line, keep_bullets, keep_link_text).rstrip())
    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


class SYStripMarkdown:
    DESCRIPTION = ("Turns reply text with markdown marks (stars, hashes, backticks, bullets, links) into clean plain text. "
                   "Words inside code are kept.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text that has markdown marks in it."}),
                "keep_bullets": ("BOOLEAN", {"default": False, "tooltip": "On: list lines keep a plain dash in front. Off: the dash is removed."}),
                "keep_link_text": ("BOOLEAN", {"default": True, "tooltip": "On: a link becomes its label. Off: links are dropped completely."}),
            },
        }

    def run(self, text, keep_bullets=False, keep_link_text=True):
        return (strip_markdown(text, keep_bullets, keep_link_text),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "StripMarkdown", SYStripMarkdown)
NODE_DISPLAY_NAME_MAPPINGS["SYStripMarkdown"] = "Strip Markdown SY"
