"""Image Metadata Reader SY: reads the prompt and workflow text stored inside a png in the input folder. Read only."""
import os

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register

MAX_FILE_BYTES = 50_000_000
MAX_TEXT_CHARS = 5_000_000


def extract_metadata(info, limit=MAX_TEXT_CHARS):
    """Pure function. (prompt_text, workflow_text) from a dict of png text chunks. Missing ones give ''."""
    out = []
    for key in ("prompt", "workflow"):
        val = (info or {}).get(key, "")
        if not isinstance(val, str):
            val = ""
        if len(val) > limit:
            raise ValueError("the %s text is too big (%d characters, max %d)" % (key, len(val), limit))
        out.append(val)
    return out[0], out[1]


class SYImageMetadataReader:
    DESCRIPTION = "Reads the prompt and workflow text saved inside a png file from the input folder. It never changes the file."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_text", "workflow_json")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"file": ("STRING", {"default": "", "tooltip": "A .png file inside the input folder, like image.png or a/b.png."})}}

    @classmethod
    def IS_CHANGED(cls, file):
        try:
            return os.path.getmtime(safe_join(root_folder("input"), file))
        except Exception:
            return float("nan")

    def run(self, file):
        from PIL import Image

        rel = str(file).strip()
        if not rel.lower().endswith(".png"):
            raise ValueError("only .png files carry this metadata, got %r" % rel)
        path = safe_join(root_folder("input"), rel)
        if not os.path.isfile(path):
            raise ValueError("png file not found in the input folder: %s" % rel)
        size = os.path.getsize(path)
        if size > MAX_FILE_BYTES:
            raise ValueError("file is too big (%d bytes, max %d)" % (size, MAX_FILE_BYTES))
        with Image.open(path) as img:
            img.load()
            return extract_metadata(dict(img.info))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageMetadataReader", SYImageMetadataReader)
NODE_DISPLAY_NAME_MAPPINGS["SYImageMetadataReader"] = "Image Metadata Reader SY"
