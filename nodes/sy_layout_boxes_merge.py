"""Layout Boxes Merge SY: joins up to four box texts into one list."""
try:
    from ._sy_common import category, register
    from ._sy_layout import MAX_BOXES, boxes_to_json, parse_boxes
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import MAX_BOXES, boxes_to_json, parse_boxes


def merge_boxes(texts):
    """Pure function. texts is a list of strings (blank ones are skipped). Returns one JSON list in the same order."""
    merged = []
    used = 0
    for n, text in enumerate(texts):
        if text is None or not str(text).strip():
            continue
        used += 1
        try:
            merged += parse_boxes(text)
        except ValueError as e:
            raise ValueError("input %d: %s" % (n + 1, e))
    if used == 0:
        raise ValueError("all four inputs are empty; connect at least one Layout Box node")
    if len(merged) > MAX_BOXES:
        raise ValueError("together the inputs hold %d boxes; the most allowed is %d" % (len(merged), MAX_BOXES))
    return boxes_to_json(merged)


class SYLayoutBoxesMerge:
    DESCRIPTION = "Joins up to four box lists into one list, keeping the order. Empty inputs are skipped."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("layout_boxes",)

    @classmethod
    def INPUT_TYPES(cls):
        tip = "Box text from a Layout Box node or another merge. Leave empty to skip."
        return {
            "required": {},
            "optional": {
                "boxes_1": ("STRING", {"default": "", "forceInput": True, "tooltip": tip}),
                "boxes_2": ("STRING", {"default": "", "forceInput": True, "tooltip": tip}),
                "boxes_3": ("STRING", {"default": "", "forceInput": True, "tooltip": tip}),
                "boxes_4": ("STRING", {"default": "", "forceInput": True, "tooltip": tip}),
            },
        }

    def run(self, boxes_1="", boxes_2="", boxes_3="", boxes_4=""):
        return (merge_boxes([boxes_1, boxes_2, boxes_3, boxes_4]),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBoxesMerge", SYLayoutBoxesMerge)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesMerge"] = "Layout Boxes Merge SY"
