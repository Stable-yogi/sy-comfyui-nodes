"""Image Exists SY: checks whether a file is present in the input, output or temp folder."""
import os
import re

try:
    from ._sy_common import category, register, safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join

FOLDERS = ("input", "output", "temp")


def check_exists(base_dir, name, folder_label="input"):
    """Pure function. Returns (exists, clean_name). Only a regular file inside base_dir counts."""
    text = "" if name is None else str(name).strip()
    if text == "":
        return False, ""
    msg = "filename must stay inside the %s folder; remove '..' or the full path" % folder_label
    if "\x00" in text:
        raise ValueError(msg)
    clean = text.replace("\\", "/")
    if clean.startswith("/") or re.match(r"^[A-Za-z]:", clean):
        raise ValueError(msg)
    if ".." in clean.split("/"):
        raise ValueError(msg)
    try:
        target = safe_join(base_dir, *[p for p in clean.split("/") if p])
    except ValueError:
        raise ValueError(msg)
    return os.path.isfile(target), clean


class SYImageExists:
    DESCRIPTION = "Tells you if a file is there. Looks only inside the input, output or temp folder."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("exists", "full_name")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (list(FOLDERS), {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "filename": ("STRING", {"default": "", "multiline": False, "tooltip": "File name inside that folder, for example refs/hero.png."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, folder, filename):
        return float("nan")

    def run(self, folder, filename):
        import folder_paths
        if folder == "output":
            base = folder_paths.get_output_directory()
        elif folder == "temp":
            base = folder_paths.get_temp_directory()
        else:
            base = folder_paths.get_input_directory()
        exists, clean = check_exists(base, filename, folder)
        return (exists, clean)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageExists", SYImageExists)
