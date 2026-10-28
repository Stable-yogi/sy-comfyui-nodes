"""3D Scene SY: arrange simple 3D shapes in a small editor on the node. Gives a shaded picture, a depth picture and a text summary."""
try:
    from ._sy_common import category, register
    from . import _sy_scene3d as sc
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_scene3d as sc


def load_picture(text, width, height, what):
    """Stored PNG text -> a PIL RGB picture of width x height, or None when the text is empty. PIL is imported here."""
    raw = sc.decode_png_bytes(text, what)
    if not raw:
        return None
    import io
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:
        raise ValueError("the stored %s cannot be read; clear it and use the editor again" % what)
    if im.width > sc.MAX_PICTURE_SIDE or im.height > sc.MAX_PICTURE_SIDE:
        raise ValueError("the stored %s is larger than %d pixels; clear it and use the editor again" % (what, sc.MAX_PICTURE_SIDE))
    im = im.convert("RGB")
    if im.size != (width, height):
        im = im.resize((width, height), Image.BILINEAR)
    return im


def picture_tensor(text, width, height, empty_value, what):
    """Stored PNG text -> torch tensor [1,H,W,3] of 0..1. Empty text gives a plain picture of empty_value."""
    import numpy as np
    import torch
    im = load_picture(text, width, height, what)
    if im is None:
        return torch.full((1, height, width, 3), float(empty_value), dtype=torch.float32)
    arr = np.asarray(im, dtype=np.float32) / 255.0
    return torch.from_numpy(arr.copy()).unsqueeze(0)


class SYScene3D:
    DESCRIPTION = "Place cubes, spheres, cylinders, planes and loaded .glb models in a small 3D editor. Gives a shaded picture, a depth picture and a text list of the objects."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("image", "depth", "summary")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_json": ("STRING", {"default": "", "multiline": False, "tooltip": "Filled in by the editor on the node: the objects and camera. Leave it alone."}),
                "render_data": ("STRING", {"default": "", "multiline": False, "tooltip": "Filled in by the editor: the shaded picture of the scene. Leave it alone."}),
                "depth_data": ("STRING", {"default": "", "multiline": False, "tooltip": "Filled in by the editor: the depth picture (near is white). Leave it alone."}),
                "width": ("INT", {"default": 768, "min": 64, "max": 2048, "step": 8, "tooltip": "Width in pixels of both output pictures."}),
                "height": ("INT", {"default": 768, "min": 64, "max": 2048, "step": 8, "tooltip": "Height in pixels of both output pictures."}),
            }
        }

    def run(self, scene_json, render_data, depth_data, width, height):
        width, height = sc.check_size(width, height)
        summary = sc.summary_from_text(scene_json)
        shaded = picture_tensor(render_data, width, height, sc.SHADED_EMPTY, "shaded picture")
        depth = picture_tensor(depth_data, width, height, sc.DEPTH_EMPTY, "depth picture")
        return (shaded, depth, summary)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
# The id starts with a letter after SY on purpose (the selftest wants SY + capital letter).
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Scene3D", SYScene3D)
NODE_DISPLAY_NAME_MAPPINGS["SYScene3D"] = "3D Scene SY"
