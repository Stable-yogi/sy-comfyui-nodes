"""Folder Image Count SY: counts the pictures in a sub folder of the input or output folder."""
try:
    from ._sy_safe_paths import IMAGE_EXTENSIONS, list_files, root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import IMAGE_EXTENSIONS, list_files, root_folder, safe_join
    from _sy_common import category, register


class SYFolderImageCount:
    DESCRIPTION = "Counts the picture files (png, jpg, jpeg, webp, bmp, gif, tif) in a folder inside the input or output folder."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("count",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root": (["input", "output"], {"default": "input", "tooltip": "Which ComfyUI folder to look in."}),
                "subfolder": ("STRING", {"default": "", "tooltip": "Folder inside it. Empty means the folder itself."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, root, subfolder):
        return float("nan")

    def run(self, root, subfolder):
        folder = safe_join(root_folder(root), subfolder)
        return (len(list_files(folder, IMAGE_EXTENSIONS)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FolderImageCount", SYFolderImageCount)
NODE_DISPLAY_NAME_MAPPINGS["SYFolderImageCount"] = "Folder Image Count SY"
