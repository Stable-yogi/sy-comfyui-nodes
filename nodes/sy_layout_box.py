"""Layout Box SY: one named box (x, y, width, height, label, colour) written as box text for the layout nodes."""
try:
    from ._sy_common import category, register
    from ._sy_layout import COLOUR_NAMES, MAX_LABEL, MAX_SIDE, boxes_to_json, make_box
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import COLOUR_NAMES, MAX_LABEL, MAX_SIDE, boxes_to_json, make_box


def layout_box_text(x, y, w, h, label, colour):
    """Pure function. Returns a JSON list holding one box."""
    return boxes_to_json([make_box(x, y, w, h, label, colour)])


class SYLayoutBox:
    DESCRIPTION = "Makes one named box for a picture layout. Join several with Layout Boxes Merge, then check or preview them."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("layout_boxes",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x": ("INT", {"default": 0, "min": 0, "max": MAX_SIDE, "tooltip": "Distance of the box left edge from the left of the picture, in pixels."}),
                "y": ("INT", {"default": 0, "min": 0, "max": MAX_SIDE, "tooltip": "Distance of the box top edge from the top of the picture, in pixels."}),
                "w": ("INT", {"default": 256, "min": 1, "max": MAX_SIDE, "tooltip": "Width of the box in pixels."}),
                "h": ("INT", {"default": 256, "min": 1, "max": MAX_SIDE, "tooltip": "Height of the box in pixels."}),
                "label": ("STRING", {"default": "box", "tooltip": "Short name shown on the box, up to %d characters." % MAX_LABEL}),
                "colour": (list(COLOUR_NAMES), {"default": COLOUR_NAMES[0], "tooltip": "Colour the preview uses to draw this box."}),
            }
        }

    def run(self, x, y, w, h, label, colour):
        return (layout_box_text(x, y, w, h, label, colour),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBox", SYLayoutBox)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBox"] = "Layout Box SY"
