"""H3 Image Size SY: pick a picture size for MiniMax H3 Image (4, 8 or 16 MP and a shape). Width and height come out as
multiples of 32, which the H3 Image conditioning node needs. The model is tuned for 2048x2048 (4 MP)."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MULTIPLE = 32
SIZES = {"4 MP (what the model is tuned for)": 4.0, "8 MP": 8.0, "16 MP (tested, about 5x slower)": 16.0}
SHAPES = {"1:1 square": (1, 1), "4:5 portrait": (4, 5), "3:4 portrait": (3, 4), "2:3 portrait": (2, 3),
          "9:16 tall": (9, 16), "5:4 landscape": (5, 4), "4:3 landscape": (4, 3), "3:2 landscape": (3, 2),
          "16:9 wide": (16, 9), "21:9 cinema": (21, 9)}
MIN_VERSION = (0, 45, 0)


def h3_size(size, shape, multiple=MULTIPLE):
    """Pure function. (width, height) near the picked megapixels and shape, both multiples of `multiple`."""
    if size not in SIZES:
        raise ValueError("unknown size %r; pick one of: %s" % (size, ", ".join(SIZES)))
    if shape not in SHAPES:
        raise ValueError("unknown shape %r; pick one of: %s" % (shape, ", ".join(SHAPES)))
    a, b = SHAPES[shape]
    area = SIZES[size] * 1024 * 1024
    w = math.sqrt(area * a / b)
    h = w * b / a
    return max(multiple, int(round(w / multiple)) * multiple), max(multiple, int(round(h / multiple)) * multiple)


def version_tuple(text):
    """Pure function. '0.45.1' or 'v0.45.0-12' -> (0, 45, 1); unknown text -> None."""
    parts = []
    for p in str(text).lstrip("v").split("-")[0].split(".")[:3]:
        if not p.isdigit():
            return None
        parts.append(int(p))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts) if parts else None


def version_note(text):
    """Pure function. One line about the ComfyUI version: fine, too old, or unknown."""
    v = version_tuple(text)
    need = ".".join(str(x) for x in MIN_VERSION[:2])
    if v is None:
        return "ComfyUI version unknown: H3 Image needs %s or newer." % need
    if v < MIN_VERSION:
        return "ComfyUI %s is too old for H3 Image: update to %s or newer." % (text, need)
    return "ComfyUI %s is fine for H3 Image." % text


def _comfy_version():
    try:
        import comfyui_version
        return comfyui_version.__version__
    except Exception:
        return ""


class SYH3ImageSize:
    DESCRIPTION = ("Pick a size for MiniMax H3 Image: 4, 8 or 16 megapixels and a shape. Gives width and height as "
                   "multiples of 32 for the H3 Image conditioning node, and checks your ComfyUI is new enough.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "size": (list(SIZES), {"default": list(SIZES)[0], "tooltip": "How many megapixels. 4 MP is what the model is tuned for."}),
            "shape": (list(SHAPES), {"default": "1:1 square", "tooltip": "The picture shape."}),
        }}

    def run(self, size, shape):
        w, h = h3_size(size, shape)
        info = "H3 IMAGE SIZE\n%d x %d (%.1f MP), %s.\n%s" % (w, h, w * h / 1048576.0, shape, version_note(_comfy_version()))
        return (w, h, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3ImageSize", SYH3ImageSize)
