"""Save Image To Folder SY: saves pictures into a sub folder of the ComfyUI output folder with a name pattern.

The browser part (js/sy_save.js) adds token buttons, the live 'Will save as' line, Open / Copy / Folder, a format switch,
a Save / Preview switch and a picture grid. The node itself works without it.
"""
import os
from datetime import datetime

try:
    from ._sy_safe_paths import date_subfolder, save_images
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import date_subfolder, save_images
    from _sy_common import category, register

MODES = ["save", "preview"]
SIDECARS = ["off", "settings", "custom text"]
MAX_SIDECAR_CHARS = 100000


def check_batch(shape):
    """Pure function. Plain refusal for an empty or wrong-shaped image batch."""
    if len(shape) != 4:
        raise ValueError("the images input is not a picture batch (expected 4 dimensions, got %d)" % len(shape))
    if int(shape[0]) < 1:
        raise ValueError("nothing to save: the images input is empty")


def sidecar_texts(kind, custom_text, count, seed, model, input_name, width, height, fmt, quality, now=None):
    """Pure function. The text for the same-name .txt file next to each picture, or None when the sidecar is off."""
    if kind not in SIDECARS:
        raise ValueError("sidecar must be one of: %s" % ", ".join(SIDECARS))
    if kind == "off":
        return None
    count = int(count)
    if kind == "custom text":
        text = str(custom_text)
        if not text.strip():
            raise ValueError("sidecar is set to custom text but the sidecar text is empty: type the text or switch the sidecar off")
        if len(text) > MAX_SIDECAR_CHARS:
            raise ValueError("sidecar text is too long (%d characters, max %d)" % (len(text), MAX_SIDECAR_CHARS))
        return [text] * count
    now = now or datetime.now()
    out = []
    for i in range(count):
        lines = ["saved: " + now.strftime("%Y-%m-%d %H:%M:%S"), "seed: %d" % int(seed),
                 "size: %dx%d" % (int(width), int(height)), "format: %s" % fmt]
        if fmt != "png":
            lines.append("quality: %d" % int(quality))
        if str(model).strip():
            lines.append("model: " + " ".join(str(model).split()))
        if str(input_name).strip():
            lines.append("input: " + " ".join(str(input_name).split()))
        lines.append("picture: %d of %d" % (i + 1, count))
        out.append(chr(10).join(lines))
    return out


def save_info(ui, width, height, fmt, channels, embed_workflow, sidecars, preview):
    """Pure function. A plain line (plus notes) telling what was saved and where."""
    n = len(ui)
    if n == 0:
        return "nothing was saved"
    where = ui[0].get("subfolder", "") or "(output folder)"
    names = ui[0]["filename"] if n == 1 else "%s ... %s" % (ui[0]["filename"], ui[-1]["filename"])
    if preview:
        return "Preview only: %d picture%s shown, nothing kept in the output folder." % (n, "" if n == 1 else "s")
    lines = ["Saved %d picture%s (%s, %dx%d) to %s: %s" % (n, "" if n == 1 else "s", fmt, width, height, where, names)]
    if sidecars:
        lines.append("Wrote %d text file%s with the same names." % (sidecars, "" if sidecars == 1 else "s"))
    if channels == 4 and fmt == "jpg":
        lines.append("Note: jpg cannot hold transparency, so the alpha channel was dropped. Use png or webp to keep it.")
    if embed_workflow and fmt != "png":
        lines.append("Note: the workflow is only embedded in png files, so %s files have none." % fmt)
    return chr(10).join(lines)


def saved_summary(ui, width, height):
    """Pure function. The line under the picture grid: '960x1440 saved 4 images'."""
    n = len(ui)
    return "%dx%d saved %d image%s" % (width, height, n, "" if n == 1 else "s")


class SYSaveImageToFolder:
    DESCRIPTION = ("Saves pictures into a folder inside the ComfyUI output folder. The name can use {date} {time} {seed} {counter} {width} {height} {batch} {model} {input}. "
                   "Never overwrites: a taken name gets the next number. Optional text file next to each picture with the seed, model and size. "
                   "Gives the saved paths, a plain info line (with notes such as jpg losing transparency) and the folder. Preview mode saves nothing in the output folder.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("saved_paths", "info", "folder")
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
                "sidecar": (SIDECARS, {"default": "off", "tooltip": "Also write a .txt next to each picture: settings = seed, size, model. custom text = your own text."}),
                "sidecar_text": ("STRING", {"default": "", "multiline": True, "tooltip": "Text for the .txt files when sidecar is custom text, for example the prompt."}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def run(self, images, subfolder, filename_pattern, format, quality, seed, embed_workflow=True, output_mode="save",
            date_folder=False, model_name="", input_name="", sidecar="off", sidecar_text="", prompt=None, extra_pnginfo=None):
        check_batch(tuple(images.shape))
        preview = output_mode == "preview"
        height, width = int(images.shape[1]), int(images.shape[2])
        captions = None if preview else sidecar_texts(sidecar, sidecar_text, images.shape[0], seed, model_name, input_name,
                                                      width, height, format, quality)
        sub = "sy_preview" if preview else (date_subfolder(subfolder) if date_folder else subfolder)
        paths, ui = save_images(images, sub, filename_pattern, format, quality, seed,
                                prompt=prompt if embed_workflow else None,
                                extra_pnginfo=extra_pnginfo if embed_workflow else None,
                                root="temp" if preview else "output",
                                extra={"model": model_name, "input": input_name}, captions=captions)
        for item in ui:
            item["width"], item["height"] = width, height
        summary = saved_summary(ui, width, height)
        if preview:
            summary = summary.replace(" saved ", " shown ")
        info = save_info(ui, width, height, format, int(images.shape[3]), bool(embed_workflow), len(ui) if captions else 0, preview)
        folder = "" if preview or not paths else os.path.dirname(paths[0])
        return {"ui": {"images": ui, "sy_saved": ui, "sy_summary": [summary]},
                "result": ("" if preview else "\n".join(paths), info, folder)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveImageToFolder", SYSaveImageToFolder)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveImageToFolder"] = "Save Image To Folder SY"
