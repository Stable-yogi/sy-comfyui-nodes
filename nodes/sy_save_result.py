"""Save Result SY: saves a picture, video or sound into a folder by project and date, with the settings text beside the file."""
import datetime
import os
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

IMAGE_FORMATS = ["png", "jpg", "webp"]
BAD = re.compile(r'[<>:"|?*\x00-\x1f]')


def clean_part(text, fallback):
    """Pure function. Makes one folder or file name part safe: no slashes, dots-only, or illegal characters."""
    t = BAD.sub("", str(text or "")).replace("\\", "/")
    t = "_".join(p for p in t.split("/") if p not in ("", ".", ".."))
    t = " ".join(t.split()).strip(" .")
    return t or fallback


def build_prefix(project, name, by_date, today):
    """Pure function. 'Project/2026-11-01/name' (date folder only when asked). `today` is a date or a text."""
    parts = [clean_part(project, "SY")]
    if by_date:
        parts.append(str(today))
    parts.append(clean_part(name, "result"))
    return "/".join(parts)


def pick_kind(has_image, has_video, has_audio):
    """Pure function. What gets saved. Raises ValueError when nothing is connected."""
    kinds = [k for k, has in (("image", has_image), ("video", has_video), ("audio", has_audio)) if has]
    if not kinds:
        raise ValueError("nothing to save: connect an image, a video or an audio input")
    return kinds


def sidecar_path(file_path):
    """Pure function. The settings text sits beside the file: same name, .txt."""
    return os.path.splitext(file_path)[0] + ".txt"


def saved_text(paths):
    """Pure function. The line shown in the node after a save."""
    return "Saved " + ("\n".join(paths) if paths else "nothing")


def _out_dir():
    import folder_paths
    return folder_paths.get_output_directory()


def _write_sidecar(file_path, settings):
    if not str(settings or "").strip():
        return
    with open(sidecar_path(file_path), "w", encoding="utf-8") as f:
        f.write(str(settings))


def _save_images(images, prefix, fmt, quality, settings, prompt, extra_pnginfo):
    import json
    import numpy as np
    import folder_paths
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    out = _out_dir()
    h, w = images.shape[1], images.shape[2]
    folder, filename, counter, subfolder, _p = folder_paths.get_save_image_path(prefix, out, w, h)
    os.makedirs(folder, exist_ok=True)
    paths, shown = [], []
    for i in range(images.shape[0]):
        arr = np.clip(255.0 * images[i].cpu().numpy(), 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
        base = "%s_%05d_" % (filename, counter)
        counter += 1
        path = os.path.join(folder, base + "." + fmt)
        if fmt == "png":
            meta = PngInfo()
            if prompt is not None:
                meta.add_text("prompt", json.dumps(prompt))
            for k, v in (extra_pnginfo or {}).items():
                meta.add_text(k, json.dumps(v))
            img.save(path, pnginfo=meta, compress_level=4)
        elif fmt == "jpg":
            img.convert("RGB").save(path, quality=int(quality), optimize=True)
        else:
            img.save(path, quality=int(quality))
        _write_sidecar(path, settings)
        paths.append(path)
        shown.append({"filename": os.path.basename(path), "subfolder": subfolder, "type": "output"})
    return paths, shown


def _save_video(video, prefix, settings):
    import folder_paths
    from comfy_api.latest import Types
    w, h = video.get_dimensions()
    folder, filename, counter, subfolder, _p = folder_paths.get_save_image_path(prefix, _out_dir(), w, h)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "%s_%05d_.mp4" % (filename, counter))
    video.save_to(path, format=Types.VideoContainer.AUTO, codec=Types.VideoCodec.AUTO)
    _write_sidecar(path, settings)
    return [path], [{"filename": os.path.basename(path), "subfolder": subfolder, "type": "output"}]


def _save_audio(audio, prefix, settings):
    from comfy_api.latest._ui import AudioSaveHelper, FolderType
    saved = AudioSaveHelper.save_audio(audio, prefix, FolderType.output, None, "flac")  # None: no workflow data inside the sound file
    paths = []
    for item in saved:
        path = os.path.join(_out_dir(), item.subfolder, item.filename)
        _write_sidecar(path, settings)
        paths.append(path)
    return paths, []


class SYSaveResult:
    DESCRIPTION = ("Saves a picture, video or sound. Files go into a folder named after your project and the date, "
                   "the settings text is saved beside each file, and the saved path is shown in the node.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project": ("STRING", {"default": "SY", "tooltip": "Folder name for this project, inside the ComfyUI output folder."}),
                "name": ("STRING", {"default": "result", "tooltip": "Start of the file name. A counter is added."}),
                "folder_by_date": ("BOOLEAN", {"default": True, "tooltip": "On: a folder per day inside the project folder."}),
                "image_format": (IMAGE_FORMATS, {"default": "png", "tooltip": "File type for pictures. png keeps the workflow inside the file."}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "tooltip": "Quality for jpg and webp. png ignores it."}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Pictures or frames to save as picture files."}),
                "video": ("VIDEO", {"tooltip": "A video to save as mp4."}),
                "audio": ("AUDIO", {"tooltip": "Sound to save as flac."}),
                "settings": ("STRING", {"forceInput": True, "tooltip": "Settings text (for example from Sampler SY). Saved as a .txt beside each file."}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def run(self, project, name, folder_by_date, image_format, quality, image=None, video=None, audio=None,
            settings="", prompt=None, extra_pnginfo=None):
        kinds = pick_kind(image is not None, video is not None, audio is not None)
        prefix = build_prefix(project, name, folder_by_date, datetime.date.today().isoformat())
        paths, shown = [], []
        for kind in kinds:
            if kind == "image":
                p, s = _save_images(image, prefix, image_format, quality, settings, prompt, extra_pnginfo)
            elif kind == "video":
                p, s = _save_video(video, prefix, settings)
            else:
                p, s = _save_audio(audio, prefix, settings)
            paths += p
            shown += s
        text = saved_text(paths)
        ui = {"text": [text]}
        if shown:
            ui["images"] = [d for d in shown if d["filename"].rsplit(".", 1)[-1] in IMAGE_FORMATS]
        return {"ui": ui, "result": ("\n".join(paths),)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveResult", SYSaveResult)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveResult"] = "Save Result SY"
