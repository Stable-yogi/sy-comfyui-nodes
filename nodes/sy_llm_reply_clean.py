"""LLM Reply Clean SY: tidy a chatty text reply (fences, intro line, quotes, extra paragraphs)."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
_PREAMBLE = re.compile(r"^\s*(here|sure|certainly|okay|ok|of course|absolutely|alright)\b[^\n]*:\s*$", re.I)
_QUOTE_PAIRS = (('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’"), ("`", "`"))


def _drop_preamble(text):
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and _PREAMBLE.match(lines[i]):
        return "\n".join(lines[i + 1:]).strip()
    return text


def _drop_fences(text):
    kept = [ln for ln in text.split("\n") if not ln.strip().startswith("```")]
    return "\n".join(kept).strip()


def _drop_quotes(text):
    for left, right in _QUOTE_PAIRS:
        if len(text) >= 2 and text[0] == left and text[-1] == right:
            inner = text[1:-1]
            if left not in inner and right not in inner:
                return inner.strip()
    return text


_THINK = re.compile(r"<(think|thinking|reasoning)>.*?</\1>", re.S | re.I)
_THINK_END = re.compile(r"</(?:think|thinking|reasoning)>", re.I)
_CLOSING = re.compile(r"^\s*(let me know|hope this helps|i hope (this|that|it)|feel free|is there anything|would you like|if you (need|want|would like)|happy to)\b", re.I)


def _drop_thinking(text):
    text = _THINK.sub("", text)
    ends = list(_THINK_END.finditer(text))  # a reply that lost its opening tag
    if ends:
        text = text[ends[-1].end():]
    return text.strip()


def _drop_closing(text):
    lines = text.split("\n")
    kept = list(lines)
    while kept and (kept[-1].strip() == "" or _CLOSING.match(kept[-1])):
        kept.pop()
    return "\n".join(kept).strip() if kept else text


def reply_clean_steps(text, strip_code_fences=True, strip_preamble=True, strip_wrapping_quotes=True,
                      first_paragraph_only=False, collapse_blank_lines=True, strip_thinking=False, strip_closing_note=False):
    """Pure function. Returns (cleaned_text, names_of_the_steps_that_changed_something)."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    changed = []

    def step(name, fn):
        nonlocal text
        new = fn(text)
        if new != text:
            changed.append(name)
        text = new

    if strip_thinking:
        step("thinking", _drop_thinking)
    if strip_preamble:
        step("intro line", _drop_preamble)
    if strip_code_fences:
        step("code fences", _drop_fences)
    if strip_closing_note:
        step("closing note", _drop_closing)
    if first_paragraph_only:
        step("extra paragraphs", lambda t: re.split(r"\n[ \t]*\n", t, maxsplit=1)[0].strip())
    if strip_wrapping_quotes:
        step("quotes", _drop_quotes)
    if collapse_blank_lines:
        step("blank lines", lambda t: re.sub(r"\n(?:[ \t]*\n){2,}", "\n\n", t))
    return text.strip(), changed


def reply_clean(text, strip_code_fences=True, strip_preamble=True, strip_wrapping_quotes=True,
                first_paragraph_only=False, collapse_blank_lines=True, strip_thinking=False, strip_closing_note=False):
    """Pure function. Returns the cleaned text."""
    return reply_clean_steps(text, strip_code_fences, strip_preamble, strip_wrapping_quotes,
                             first_paragraph_only, collapse_blank_lines, strip_thinking, strip_closing_note)[0]


def clean_info(before, after, changed):
    """Pure function. One plain line: sizes and what was removed."""
    if not changed:
        return "Nothing to clean: the text was already tidy (%d characters)." % len(after)
    return "Cleaned %d to %d characters (removed: %s)." % (len(str(before or "")), len(after), ", ".join(changed))


class SYLLMReplyClean:
    DESCRIPTION = ("Cleans a chatty text reply: removes the model's <think> notes, code fences, an intro line like 'Here is...:', wrapping "
                   "quotes, an optional closing 'Let me know...' line and extra blank lines. An info line says what was removed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The reply text you want to clean."}),
                "strip_code_fences": ("BOOLEAN", {"default": True, "tooltip": "On: remove the ``` lines and keep what is inside."}),
                "strip_preamble": ("BOOLEAN", {"default": True, "tooltip": "On: drop a first line like 'Here is your prompt:' that ends with a colon."}),
                "strip_wrapping_quotes": ("BOOLEAN", {"default": True, "tooltip": "On: remove quote marks that wrap the whole text."}),
                "first_paragraph_only": ("BOOLEAN", {"default": False, "tooltip": "On: keep only the first paragraph and drop the rest."}),
                "collapse_blank_lines": ("BOOLEAN", {"default": True, "tooltip": "On: turn several empty lines in a row into one."}),
            },
            "optional": {
                "strip_thinking": ("BOOLEAN", {"default": True, "tooltip": "On: remove the <think>...</think> notes some models write before the answer."}),
                "strip_closing_note": ("BOOLEAN", {"default": False, "tooltip": "On: drop a last line like 'Let me know if you want changes.'"}),
            },
        }

    def run(self, text, strip_code_fences=True, strip_preamble=True, strip_wrapping_quotes=True,
            first_paragraph_only=False, collapse_blank_lines=True, strip_thinking=True, strip_closing_note=False):
        out, changed = reply_clean_steps(text, strip_code_fences, strip_preamble, strip_wrapping_quotes,
                                         first_paragraph_only, collapse_blank_lines, strip_thinking, strip_closing_note)
        return (out, clean_info(text, out, changed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LLMReplyClean", SYLLMReplyClean)
NODE_DISPLAY_NAME_MAPPINGS["SYLLMReplyClean"] = "LLM Reply Clean SY"
