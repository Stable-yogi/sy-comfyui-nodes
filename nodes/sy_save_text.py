"""Save Text SY: writes text to a .txt file in a sub folder of the ComfyUI output folder."""
import os

try:
    from ._sy_safe_paths import check_filename, expand_pattern, list_files, plan_names, root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import check_filename, expand_pattern, list_files, plan_names, root_folder, safe_join
    from _sy_common import category, register

MAX_CHARS = 5_000_000


def text_file_name(existing, pattern, append, seed=0, now=None):
    """Pure function. The .txt name to write. Append mode needs a fixed name (no {counter}) and reuses it."""
    if append:
        if "{counter}" in str(pattern):
            raise ValueError("append needs a fixed file name: remove {counter} from the pattern")
        if not str(pattern).strip():
            raise ValueError("file name pattern is empty: type a name such as notes")
        return check_filename(expand_pattern(pattern, seed, now) + ".txt")
    return plan_names(existing, pattern, ".txt", 1, seed, now)[0]


class SYSaveText:
    DESCRIPTION = "Saves text to a .txt file inside the ComfyUI output folder. Can add to the end of an existing file."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to save."}),
                "subfolder": ("STRING", {"default": "SY", "tooltip": "Folder inside the output folder. It is created if missing."}),
                "filename_pattern": ("STRING", {"default": "text_{counter}", "tooltip": "File name without .txt. Tokens: {date} {time} {seed} {counter}."}),
                "append": ("BOOLEAN", {"default": False, "tooltip": "Add the text to the end of the file instead of making a new one. No {counter}."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
            }
        }

    def run(self, text, subfolder, filename_pattern, append, seed):
        text = str(text)
        if len(text) > MAX_CHARS:
            raise ValueError("text is too long (%d characters, max %d)" % (len(text), MAX_CHARS))
        folder = safe_join(root_folder("output"), subfolder)
        os.makedirs(folder, exist_ok=True)
        name = text_file_name(list_files(folder), filename_pattern, append, seed)
        path = os.path.join(folder, name)
        with open(path, "a" if append else "x", encoding="utf-8", newline="\n") as f:
            f.write(text + ("\n" if append else ""))
        return (path,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveText", SYSaveText)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveText"] = "Save Text SY"
