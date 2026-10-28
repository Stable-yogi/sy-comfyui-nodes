"""Save With Caption SY: saves a picture and a same-name .txt caption next to it, for making training sets."""
try:
    from ._sy_safe_paths import save_images
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import save_images
    from _sy_common import category, register


def caption_list(caption, count):
    """Pure function. One caption text per picture. A single caption is used for every picture."""
    count = int(count)
    if count < 1:
        raise ValueError("nothing to save: no pictures")
    text = str(caption)
    if not text.strip():
        raise ValueError("the caption is empty: type the caption text")
    return [text] * count


class SYSaveWithCaption:
    DESCRIPTION = "Saves each picture plus a text file with the same name holding the caption. Good for making training datasets."
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
                "caption": ("STRING", {"default": "", "multiline": True, "tooltip": "Text written to the .txt file next to each picture."}),
                "subfolder": ("STRING", {"default": "SY/dataset", "tooltip": "Folder inside the output folder. It is created if missing."}),
                "filename_pattern": ("STRING", {"default": "img_{counter}", "tooltip": "File name without extension. Tokens: {date} {time} {seed} {counter}."}),
                "format": (["png", "jpg", "webp"], {"default": "png", "tooltip": "Picture file type."}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "tooltip": "Quality for jpg and webp. Png ignores it."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
            }
        }

    def run(self, images, caption, subfolder, filename_pattern, format, quality, seed):
        caps = caption_list(caption, images.shape[0])
        paths, ui = save_images(images, subfolder, filename_pattern, format, quality, seed, captions=caps)
        return {"ui": {"images": ui}, "result": ("\n".join(paths),)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveWithCaption", SYSaveWithCaption)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveWithCaption"] = "Save With Caption SY"
