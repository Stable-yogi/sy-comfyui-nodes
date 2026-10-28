"""Save Image To Folder SY: saves pictures into a sub folder of the ComfyUI output folder with a name pattern.

The browser part (js/sy_save.js) adds token buttons, the live 'Will save as' line, Open / Copy / Folder, a format switch,
a Save / Preview switch and a picture grid. The node itself works without it.
"""
try:
    from ._sy_safe_paths import date_subfolder, save_images
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import date_subfolder, save_images
    from _sy_common import category, register

MODES = ["save", "preview"]


def saved_summary(ui, width, height):
    """Pure function. The line under the picture grid: '960x1440 saved 4 images'."""
    n = len(ui)
    return "%dx%d saved %d image%s" % (width, height, n, "" if n == 1 else "s")


class SYSaveImageToFolder:
    DESCRIPTION = "Saves pictures into a folder inside the ComfyUI output folder. The name can use {date} {time} {seed} {counter} {width} {height} {batch} {model} {input}. Preview mode saves nothing in the output folder."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_paths",)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures to save."}),
                "subfolder": ("STRING", {"default": "SY", "tooltip": "Folder inside the output folder. It is created if missing. No .. or drive letters."}),
                "filename_pattern": ("STRING", {"default": "image_{counter}", "tooltip": "File name without extension. Tokens: {date} {time} {seed} {counter} {width} {height} {batch} {model} {input}."}),
                "format": (["png", "jpg", "webp"], {"default": "png", "tooltip": "File type to save."}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "tooltip": "Quality for jpg and webp. Png ignores it."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
                "embed_workflow": ("BOOLEAN", {"default": True, "tooltip": "Store the prompt and workflow inside png files so you can reload them."}),
            },
            "optional": {
                "output_mode": (MODES, {"default": "save", "tooltip": "Save writes to the output folder. Preview only shows the pictures and keeps no copy."}),
                "date_folder": ("BOOLEAN", {"default": False, "tooltip": "Put the pictures in a folder named with today's date inside the subfolder."}),
                "model_name": ("STRING", {"default": "", "tooltip": "Text for the {model} token, for example a model file name. Folder and extension are cut off."}),
                "input_name": ("STRING", {"default": "", "tooltip": "Text for the {input} token, for example the name of the source picture."}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def run(self, images, subfolder, filename_pattern, format, quality, seed, embed_workflow=True, prompt=None, extra_pnginfo=None):
        paths, ui = save_images(images, subfolder, filename_pattern, format, quality, seed,
                                prompt=prompt if embed_workflow else None,
                                extra_pnginfo=extra_pnginfo if embed_workflow else None)
        return {"ui": {"images": ui}, "result": ("\n".join(paths),)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveImageToFolder", SYSaveImageToFolder)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveImageToFolder"] = "Save Image To Folder SY"
