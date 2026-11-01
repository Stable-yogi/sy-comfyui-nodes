"""Filename Builder SY: turns a name pattern with tokens into a file name text."""
import os
import re

try:
    from ._sy_safe_paths import check_filename, clean_extension, expand_pattern, MAX_NAME_LENGTH
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import check_filename, clean_extension, expand_pattern, MAX_NAME_LENGTH
    from _sy_common import category, register

NEW_TOKENS = ("model", "width", "height")
SAVE_ONLY_TOKENS = ("batch", "input")


def tidy_name(text, limit):
    """Pure function. Turns a free text into a safe plain name: spaces become _, forbidden characters become _,
    no leading or trailing space or dot, cut to `limit` characters."""
    out = re.sub(r"\s+", "_", str(text))
    out = "".join("_" if (c in '<>:"/\\|?*' or ord(c) < 32) else c for c in out)
    out = out.strip(" .") or "file"
    return out[:max(1, limit)].rstrip(" .") or "file"


def build_parts(pattern, seed=0, counter=1, extension="", now=None, model="", width=0, height=0, auto_clean=False):
    """Pure function. Returns (filename, stem). Same rules as build_filename plus {model} {width} {height}.

    {batch} and {input} belong to the Save Image node and are refused here with a plain message.
    auto_clean tidies the result (spaces, forbidden characters, too long) instead of refusing it.
    """
    text = str(pattern)
    if not text.strip():
        raise ValueError("pattern is empty: type a name such as shot_{counter}")
    if int(counter) < 0:
        raise ValueError("counter must be 0 or more")
    for tok in SAVE_ONLY_TOKENS:
        if "{%s}" % tok in text:
            raise ValueError("{%s} only works in the Save Image node (it needs a picture). Use {model}, {width} or {height} here." % tok)
    used = [t for t in NEW_TOKENS if "{%s}" % t in text]
    extra = None
    if used:
        if "model" in used and not str(model).strip():
            raise ValueError("the pattern uses {model} but the model box is empty: type a model name")
        if ("width" in used and int(width) < 1) or ("height" in used and int(height) < 1):
            raise ValueError("the pattern uses {width} or {height}: set width and height above 0")
        extra = {"model": model, "width": width, "height": height, "batch": 0, "input": ""}
    ext = clean_extension(extension)
    name = expand_pattern(text, seed, now, counter=counter, extra=extra)
    if auto_clean:
        name = tidy_name(name, MAX_NAME_LENGTH - len(ext))
    full = check_filename(name + ext)
    return full, (full[:-len(ext)] if ext else full)


def build_filename(pattern, seed=0, counter=1, extension="", now=None):
    """Pure function. Fills {date} {time} {seed} {counter} and adds the extension. Checks the result is a plain name."""
    if not str(pattern).strip():
        raise ValueError("pattern is empty: type a name such as shot_{counter}")
    if int(counter) < 0:
        raise ValueError("counter must be 0 or more")
    name = expand_pattern(pattern, seed, now, counter=counter)
    return check_filename(name + clean_extension(extension))


def name_info(filename, stem):
    note = "File name: %s (%d characters)." % (filename, len(filename))
    if len(filename) > 100:
        note += " Long names can fail on some systems."
    if " " in filename:
        note += " It contains spaces; turn on auto_clean to use _ instead."
    return note


class SYFilenameBuilder:
    DESCRIPTION = ("Builds a file name from a pattern. Tokens: {date} {time} {seed} {counter}, and {model} {width} {height} "
                   "when you fill those boxes. Optional auto_clean tidies spaces and forbidden characters instead of failing. "
                   "Also gives the name without its ending (stem) and an info line. Only makes text, saves nothing.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("filename", "stem", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pattern": ("STRING", {"default": "shot_{date}_{counter}", "tooltip": "Name with tokens: {date} {time} {seed} {counter}. No slashes."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
                "counter": ("INT", {"default": 1, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Number used for the {counter} token, shown with 5 digits."}),
                "extension": ("STRING", {"default": "", "tooltip": "Optional ending such as png or .txt. Leave empty for none."}),
            },
            "optional": {
                "model": ("STRING", {"default": "", "tooltip": "Text for the {model} token. A path or ending is cut off."}),
                "width": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Number for the {width} token."}),
                "height": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Number for the {height} token."}),
                "auto_clean": ("BOOLEAN", {"default": False, "tooltip": "On: spaces become _ and forbidden characters are replaced instead of an error."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, pattern, seed, counter, extension, **kw):
        return float("nan") if "{time}" in str(pattern) else None

    def run(self, pattern, seed, counter, extension, model="", width=0, height=0, auto_clean=False):
        if not (model or width or height or auto_clean):
            filename, stem = build_parts(pattern, seed, counter, extension)
        else:
            filename, stem = build_parts(pattern, seed, counter, extension, None, model, width, height, auto_clean)
        return (filename, stem, name_info(filename, stem))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FilenameBuilder", SYFilenameBuilder)
NODE_DISPLAY_NAME_MAPPINGS["SYFilenameBuilder"] = "Filename Builder SY"
