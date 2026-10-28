"""Loader Name Picker SY: pick a model file name from a list and pass the name on as text. Loads nothing."""
import os

try:
    from ._sy_common import category, register
    from ._sy_loaders import MODEL_FOLDERS, folder_key, pick_name
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import MODEL_FOLDERS, folder_key, pick_name
    from _sy_model_files import list_names


def all_names():
    """Every file name of every supported folder, without doubles, in a fixed order."""
    seen, out = set(), []
    for folder in MODEL_FOLDERS:
        for n in list_names(folder_key(folder)):
            if n not in seen:
                seen.add(n)
                out.append(n)
    return out


def split_name(name):
    """Pure function. Returns (name, name_without_extension)."""
    return (name, os.path.splitext(name.replace("\\", "/").split("/")[-1])[0])


class SYLoaderNamePicker:
    DESCRIPTION = "Pick a model file from the list and get its name as text. Nothing is loaded. The folder is checked against the name."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("name", "name_no_ext")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (list(MODEL_FOLDERS), {"default": "checkpoints", "tooltip": "Which model folder the name must come from."}),
                "name": (all_names(), {"tooltip": "The file name to pass on. It must exist in the chosen folder."}),
            }
        }

    def run(self, folder, name):
        pick_name(folder, name, list_names(folder_key(folder)))
        return split_name(name)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoaderNamePicker", SYLoaderNamePicker)
NODE_DISPLAY_NAME_MAPPINGS["SYLoaderNamePicker"] = "Loader Name Picker SY"
