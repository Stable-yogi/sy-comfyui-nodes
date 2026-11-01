"""Layout Boxes Merge SY: joins up to eight box texts into one list."""
try:
    from ._sy_common import category, register
    from ._sy_layout import MAX_BOXES, boxes_to_json, parse_boxes
    from ._sy_e_layout import drop_duplicate_boxes
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import MAX_BOXES, boxes_to_json, parse_boxes
    from _sy_e_layout import drop_duplicate_boxes

SLOTS = 8


def merge_details(texts, drop_duplicates=False):
    """Pure function. texts is a list of strings (blank ones are skipped). Returns (json_text, count, info) in the same order."""
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
        words = "four" if len(texts) <= 4 else str(len(texts))
        raise ValueError("all %s inputs are empty; connect at least one Layout Box node" % words)
    dropped = 0
    if drop_duplicates:
        merged, dropped = drop_duplicate_boxes(merged)
    if len(merged) > MAX_BOXES:
        raise ValueError("together the inputs hold %d boxes; the most allowed is %d" % (len(merged), MAX_BOXES))
    info = "Joined %d box%s from %d input%s." % (len(merged), "" if len(merged) == 1 else "es", used, "" if used == 1 else "s")
    if dropped:
        info += " Dropped %d exact copy." % dropped if dropped == 1 else " Dropped %d exact copies." % dropped
    labels = [b["label"] for b in merged if isinstance(b.get("label"), str) and b["label"]]
    repeated = sorted({name for name in labels if labels.count(name) > 1})
    if repeated:
        info += " Same label used twice: %s." % ", ".join('"%s"' % name[:30] for name in repeated[:5])
    return boxes_to_json(merged), len(merged), info


def merge_boxes(texts, drop_duplicates=False):
    """Pure function. texts is a list of strings (blank ones are skipped). Returns one JSON list in the same order."""
    return merge_details(texts, drop_duplicates)[0]


class SYLayoutBoxesMerge:
    DESCRIPTION = "Joins up to eight box lists into one list, keeping the order. Empty inputs are skipped. Can drop exact copies, counts the boxes and warns when a label is used twice."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("layout_boxes", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        tip = "Box text from a Layout Box node or another merge. Leave empty to skip."
        optional = {"boxes_%d" % n: ("STRING", {"default": "", "forceInput": True, "tooltip": tip}) for n in range(1, SLOTS + 1)}
        optional["drop_duplicates"] = ("BOOLEAN", {"default": False, "tooltip": "On removes a box that is an exact copy of an earlier one (same place, size, label, colour)."})
        return {"required": {}, "optional": optional}

    def run(self, boxes_1="", boxes_2="", boxes_3="", boxes_4="", boxes_5="", boxes_6="", boxes_7="", boxes_8="", drop_duplicates=False):
        text, count, info = merge_details([boxes_1, boxes_2, boxes_3, boxes_4, boxes_5, boxes_6, boxes_7, boxes_8], drop_duplicates)
        return (text, count, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBoxesMerge", SYLayoutBoxesMerge)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesMerge"] = "Layout Boxes Merge SY"
