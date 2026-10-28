"""Load Text SY: reads a .txt file from the ComfyUI input folder."""
import os

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register

MAX_BYTES = 2_000_000


def read_text_file(base, relative):
    """Read a .txt file under `base`. Refuses other extensions, paths outside `base` and big files."""
    rel = str(relative).strip()
    if not rel:
        raise ValueError("file is empty: type the name of a .txt file in the input folder")
    if not rel.lower().endswith(".txt"):
        raise ValueError("only .txt files can be loaded, got %r" % rel)
    path = safe_join(base, rel)
    if not os.path.isfile(path):
        raise ValueError("text file not found in the input folder: %s" % rel)
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError("text file is too big (%d bytes, max %d)" % (size, MAX_BYTES))
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


class SYLoadText:
    DESCRIPTION = "Loads the text of a .txt file from the ComfyUI input folder. Other file types are refused."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"file": ("STRING", {"default": "notes.txt", "tooltip": "Path of a .txt file inside the input folder, like notes.txt or a/b.txt."})}}

    @classmethod
    def IS_CHANGED(cls, file):
        try:
            return os.path.getmtime(safe_join(root_folder("input"), file))
        except Exception:
            return float("nan")

    def run(self, file):
        return (read_text_file(root_folder("input"), file),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadText", SYLoadText)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadText"] = "Load Text SY"
