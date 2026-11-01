"""Layout Box SY: one named box (x, y, width, height, label, colour) written as box text for the layout nodes."""
try:
    from ._sy_common import category, register
    from ._sy_layout import COLOUR_NAMES, MAX_LABEL, MAX_SIDE, boxes_to_json, make_box
    from ._sy_e_layout import box_info, check_fits, snap_box_numbers
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import COLOUR_NAMES, MAX_LABEL, MAX_SIDE, boxes_to_json, make_box
    from _sy_e_layout import box_info, check_fits, snap_box_numbers


def layout_box_details(x, y, w, h, label, colour, canvas_width=0, canvas_height=0, snap_to=1):
    """Pure function. Returns (json_text, info). snap_to rounds x, y, w, h to a multiple (1 = off).
    A canvas side above 0 makes the box refuse to leave the picture."""
    make_box(x, y, w, h, label, colour)          # refuses bad numbers, labels and colours first
    note = ""
    if snap_to > 1:
        sx, sy, sw, sh = snap_box_numbers(x, y, w, h, snap_to)
        if (sx, sy, sw, sh) != (x, y, w, h):
            note = "Snapped to multiples of %d (was x=%s, y=%s, w=%s, h=%s)." % (snap_to, x, y, w, h)
        x, y, w, h = sx, sy, sw, sh
    box = make_box(x, y, w, h, label, colour)
    check_fits(box["label"], x, y, w, h, canvas_width, canvas_height)
    return boxes_to_json([box]), box_info(box, note)


def layout_box_text(x, y, w, h, label, colour, canvas_width=0, canvas_height=0, snap_to=1):
    """Pure function. Returns a JSON list holding one box."""
    return layout_box_details(x, y, w, h, label, colour, canvas_width, canvas_height, snap_to)[0]


class SYLayoutBox:
    DESCRIPTION = "Makes one named box for a picture layout. Can snap the numbers to a multiple of 8 or 64 and refuse a box that leaves the picture. Join several with Layout Boxes Merge, then check or preview them."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("layout_boxes", "info")

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
            },
            "optional": {
                "canvas_width": ("INT", {"default": 0, "min": 0, "max": MAX_SIDE, "tooltip": "Picture width. If above 0, a box that runs past the right edge is refused. 0 skips the check."}),
                "canvas_height": ("INT", {"default": 0, "min": 0, "max": MAX_SIDE, "tooltip": "Picture height. If above 0, a box that runs past the bottom edge is refused. 0 skips the check."}),
                "snap_to": ("INT", {"default": 1, "min": 1, "max": 512, "tooltip": "Round x, y, w and h to a multiple of this, for example 8 or 64. 1 keeps your numbers."}),
            },
        }

    def run(self, x, y, w, h, label, colour, canvas_width=0, canvas_height=0, snap_to=1):
        return layout_box_details(x, y, w, h, label, colour, canvas_width, canvas_height, snap_to)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBox", SYLayoutBox)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBox"] = "Layout Box SY"
