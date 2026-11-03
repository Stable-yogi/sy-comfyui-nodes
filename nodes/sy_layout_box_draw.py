"""Layout Box Draw SY: draw boxes with the mouse on a small canvas; the boxes come out as box text for the layout nodes."""
try:
    from ._sy_common import category, register
    from ._sy_layout import COLOUR_NAMES, MAX_BOXES, MAX_SIDE, boxes_to_json, make_box, parse_boxes
    from ._sy_e_layout import check_fits, snap_box_numbers
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import COLOUR_NAMES, MAX_BOXES, MAX_SIDE, boxes_to_json, make_box, parse_boxes
    from _sy_e_layout import check_fits, snap_box_numbers


def _whole(v):
    """Panel numbers are whole pixels; a decimal from pasted text is rounded. Anything else is left for make_box to refuse."""
    if isinstance(v, float) and v == v and v not in (float("inf"), float("-inf")):
        return int(round(v))
    return v


def draw_boxes_details(boxes_text, canvas_width, canvas_height, snap_to=1):
    """Pure function. Returns (json_text, info). An empty list is fine (nothing drawn yet).
    Every box must fit the canvas; snap_to rounds the numbers to a multiple (1 = off)."""
    if canvas_width < 1 or canvas_height < 1:
        raise ValueError("canvas_width and canvas_height must be 1 or more (got %sx%s)" % (canvas_width, canvas_height))
    text = "" if boxes_text is None else str(boxes_text).strip()
    if not text:
        return "[]", "No boxes drawn yet. Drag on the canvas to draw one."
    raw = parse_boxes(text)
    if len(raw) > MAX_BOXES:
        raise ValueError("there are %d boxes; the most allowed is %d. Delete some." % (len(raw), MAX_BOXES))
    boxes = []
    for i, item in enumerate(raw):
        for key in ("x", "y", "w", "h"):
            if key not in item:
                raise ValueError("box %d is missing \"%s\"" % (i + 1, key))
        colour = item.get("colour", item.get("color"))
        if colour is None:
            colour = COLOUR_NAMES[i % len(COLOUR_NAMES)]
        label = item.get("label", "")
        x, y, w, h = (_whole(item[k]) for k in ("x", "y", "w", "h"))
        make_box(x, y, w, h, label, colour)            # refuses bad numbers, labels and colours first
        if snap_to > 1:
            x, y, w, h = snap_box_numbers(x, y, w, h, snap_to)
        box = make_box(x, y, w, h, label, colour)
        check_fits(box["label"], x, y, w, h, canvas_width, canvas_height)
        boxes.append(box)
    names = ", ".join(('"%s"' % b["label"]) if b["label"] else "(no label)" for b in boxes[:6])
    more = "" if len(boxes) <= 6 else " and %d more" % (len(boxes) - 6)
    info = "%d box%s on a %dx%d canvas: %s%s." % (len(boxes), "" if len(boxes) == 1 else "es", canvas_width, canvas_height, names, more)
    return boxes_to_json(boxes), info


class SYLayoutBoxDraw:
    DESCRIPTION = "Draw layout boxes with the mouse on a small canvas inside the node. The boxes come out as box text for Layout Boxes Merge, Preview and Check, and for a MOSS layout prompt."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("layout_boxes", "info", "box_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "canvas_width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Width of the picture the boxes are for, in pixels. The canvas keeps this shape."}),
                "canvas_height": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Height of the picture the boxes are for, in pixels."}),
                "boxes": ("STRING", {"default": "[]", "multiline": True, "tooltip": "The boxes as a JSON list. The canvas writes this for you; you can also paste a list here."}),
            },
            "optional": {
                "snap_to": ("INT", {"default": 1, "min": 1, "max": 512, "tooltip": "Round every box to a multiple of this, for example 8 or 64. 1 keeps your numbers."}),
            },
        }

    def run(self, canvas_width, canvas_height, boxes, snap_to=1):
        text, info = draw_boxes_details(boxes, canvas_width, canvas_height, snap_to)
        return (text, info, len(parse_boxes(text)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBoxDraw", SYLayoutBoxDraw)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxDraw"] = "Layout Box Draw SY"
