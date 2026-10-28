"""List Folder Files SY: lists the files of a sub folder of the input or output folder as text lines."""
try:
    from ._sy_safe_paths import list_files, parse_extensions, root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import list_files, parse_extensions, root_folder, safe_join
    from _sy_common import category, register

MAX_LINES = 5000


def list_text(names, limit=MAX_LINES):
    """Pure function. (text with one name per line, count). Refuses lists that are too long."""
    if len(names) > limit:
        raise ValueError("folder has %d matching files, more than the limit of %d: use an extension filter" % (len(names), limit))
    return "\n".join(names), len(names)


class SYListFolderFiles:
    DESCRIPTION = "Lists the files in a folder inside the input or output folder, one per line, with a count."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("files", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root": (["input", "output"], {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside it. Empty means the folder itself."}),
                "extensions": ("STRING", {"default": "", "tooltip": "File endings to keep, like png, jpg or txt. Empty lists every file."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, root, subfolder, extensions):
        return float("nan")

    def run(self, root, subfolder, extensions):
        folder = safe_join(root_folder(root), subfolder)
        exts = parse_extensions(extensions, default=()) or None
        return list_text(list_files(folder, exts))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ListFolderFiles", SYListFolderFiles)
NODE_DISPLAY_NAME_MAPPINGS["SYListFolderFiles"] = "List Folder Files SY"
