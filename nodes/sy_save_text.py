"""Save Text SY: writes text to a .txt file in a sub folder of the ComfyUI output folder."""
import os
from datetime import datetime

try:
    from ._sy_safe_paths import check_filename, expand_pattern, list_files, plan_names, root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import check_filename, expand_pattern, list_files, plan_names, root_folder, safe_join
    from _sy_common import category, register

MAX_CHARS = 5_000_000


EXTENSIONS = ["txt", "md", "csv", "json", "log"]
ON_EMPTY = ["save anyway", "skip", "error"]


def text_file_name(existing, pattern, append, seed=0, now=None, ext=".txt"):
    """Pure function. The file name to write (.txt unless `ext` says otherwise). Append mode needs a fixed name (no {counter}) and reuses it."""
    ext = ext if str(ext).startswith(".") else "." + str(ext)
    if str(ext)[1:] not in EXTENSIONS:
        raise ValueError("extension must be one of: %s" % ", ".join(EXTENSIONS))
    if append:
        if "{counter}" in str(pattern):
            raise ValueError("append needs a fixed file name: remove {counter} from the pattern")
        if not str(pattern).strip():
            raise ValueError("file name pattern is empty: type a name such as notes")
        return check_filename(expand_pattern(pattern, seed, now) + ext)
    return plan_names(existing, pattern, ext, 1, seed, now)[0]


def prepare_text(text, on_empty="save anyway", stamp=False, append=False, now=None):
    """Pure function. Returns the text to write, or None when an empty text should be skipped.

    stamp puts the date and time in square brackets in front of the entry (it is meant for append mode, a running log).
    """
    if on_empty not in ON_EMPTY:
        raise ValueError("on_empty must be one of: %s" % ", ".join(ON_EMPTY))
    text = str(text)
    if len(text) > MAX_CHARS:
        raise ValueError("text is too long (%d characters, max %d)" % (len(text), MAX_CHARS))
    if not text.strip():
        if on_empty == "skip":
            return None
        if on_empty == "error":
            raise ValueError("the text is empty: nothing to save. Connect a text or switch on_empty to save anyway")
    if stamp and text.strip():
        text = "[%s] %s" % ((now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), text)
    return text


def save_info(rel_path, chars, append, existed, size_after=None):
    """Pure function. A plain line telling what was written."""
    if append and existed:
        return "Added %d characters to the end of %s%s" % (chars, rel_path, "" if size_after is None else " (file is now %d bytes)" % size_after)
    return "Saved %d characters to %s (%s)" % (chars, rel_path, "new file" if not append else "new file, more will be added to it")


class SYSaveText:
    DESCRIPTION = ("Saves text to a file inside the ComfyUI output folder and never overwrites: a taken name gets the next number. "
                   "Can add to the end of one file for a running log (with a time stamp per entry), pick txt, md, csv, json or log, "
                   "and skip empty texts. Gives the saved path and a plain info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("saved_path", "info")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to save."}),
                "subfolder": ("STRING", {"default": "SY", "tooltip": "Folder inside the output folder. It is created if missing."}),
                "filename_pattern": ("STRING", {"default": "text_{counter}", "tooltip": "File name without the extension. Tokens: {date} {time} {seed} {counter}."}),
                "append": ("BOOLEAN", {"default": False, "tooltip": "Add the text to the end of the file instead of making a new one. No {counter}."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
            },
            "optional": {
                "extension": (EXTENSIONS, {"default": "txt", "tooltip": "File type to write. The text is saved as it is, nothing is converted."}),
                "on_empty": (ON_EMPTY, {"default": "save anyway", "tooltip": "When the text is empty: save an empty file, skip saving, or stop with a message."}),
                "time_stamp": ("BOOLEAN", {"default": False, "tooltip": "Put [date time] in front of the text. Handy with append for a running log."}),
            },
        }

    def run(self, text, subfolder, filename_pattern, append, seed, extension="txt", on_empty="save anyway", time_stamp=False):
        text = prepare_text(text, on_empty, bool(time_stamp), bool(append))
        if text is None:
            return ("", "Skipped: the text was empty, so no file was written.")
        root = root_folder("output")
        folder = safe_join(root, subfolder)
        os.makedirs(folder, exist_ok=True)
        name = text_file_name(list_files(folder), filename_pattern, append, seed, ext="." + extension)
        path = os.path.join(folder, name)
        existed = os.path.isfile(path)
        try:
            with open(path, "a" if append else "x", encoding="utf-8", newline="\n") as f:
                f.write(text + ("\n" if append else ""))
        except FileExistsError:
            raise ValueError("a file with this name appeared while saving: %s. Run it again." % name)
        rel = os.path.relpath(path, os.path.realpath(root)).replace(os.sep, "/")
        size = os.path.getsize(path) if append else None
        return (path, save_info(rel, len(text), bool(append), existed, size))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveText", SYSaveText)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveText"] = "Save Text SY"
