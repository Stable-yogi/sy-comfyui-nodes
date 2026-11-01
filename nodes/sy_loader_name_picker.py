"""Loader Name Picker SY: pick a model file name from a list and pass the name on as text. Loads nothing."""
import os

try:
    from ._sy_common import category, register
    from ._sy_loaders import MODEL_FOLDERS, folder_key, pick_name
    from ._sy_model_files import list_names
    from ._sy_a1_files import pick_with_filter, folders_holding, match_names, file_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import MODEL_FOLDERS, folder_key, pick_name
    from _sy_model_files import list_names
    from _sy_a1_files import pick_with_filter, folders_holding, match_names, file_facts


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


def wrong_folder_message(folder, name, by_folder):
    """Pure function. Plain sentence when the name exists, but in another folder. '' when it exists nowhere."""
    others = [f for f in folders_holding(name, by_folder) if f != folder]
    if not others:
        return ""
    return "%r is not in the %s list, but it is in the %s list. Change folder to %s." % (name, folder, " and ".join(others), others[0])


def resolve(folder, name, name_filter, by_folder):
    """Pure function. Returns (name, info). by_folder = {folder: [names]} for every supported folder.

    With name_filter text the first match in the chosen folder wins and the list pick is ignored.
    """
    folder_key(folder)
    names = by_folder.get(folder, [])
    chosen, note = pick_with_filter(names, name, name_filter, folder)
    if chosen not in names:
        hint = wrong_folder_message(folder, chosen, by_folder)
        if hint:
            raise ValueError(hint)
    pick_name(folder, chosen, names)
    count = len(match_names(names, name_filter)) if str(name_filter).strip() else 1
    lines = ["%s: %s" % (folder, chosen)]
    if note:
        lines.append(note)
    return chosen, "\n".join(lines), count


class SYLoaderNamePicker:
    DESCRIPTION = ("Pick a model file from the list and get its name as text. Nothing is loaded. The folder is checked against "
                   "the name. Adds: a name_filter box (words instead of scrolling), a plain message when the file is in a "
                   "different folder (for example a LoRA picked under checkpoints), the match count and an info text with the size.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("name", "name_no_ext", "match_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (list(MODEL_FOLDERS), {"default": "checkpoints", "tooltip": "Which model folder the name must come from."}),
                "name": (all_names(), {"tooltip": "The file name to pass on. It must exist in the chosen folder."}),
            },
            "optional": {
                "name_filter": ("STRING", {"default": "", "tooltip": "Optional. Words like 'flux dev': uses the first matching file of the folder and ignores the list."}),
            },
        }

    def run(self, folder, name, name_filter=""):
        by_folder = {f: list_names(folder_key(f)) for f in MODEL_FOLDERS}
        chosen, info, count = resolve(folder, name, name_filter, by_folder)
        try:
            from ._sy_model_files import find_file
        except ImportError:
            from _sy_model_files import find_file
        try:
            size = os.path.getsize(find_file(folder_key(folder), chosen))
            info = file_facts(chosen, size) + ("\n" + info.split("\n", 1)[1] if "\n" in info else "")
        except (ValueError, OSError):
            pass  # the facts are a bonus; the name itself was already checked against the list
        return split_name(chosen) + (count, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoaderNamePicker", SYLoaderNamePicker)
NODE_DISPLAY_NAME_MAPPINGS["SYLoaderNamePicker"] = "Loader Name Picker SY"
