"""Layout JSON Check SY: checks box text against a canvas size and says in plain words what is wrong."""
import json

try:
    from ._sy_common import category, register
    from ._sy_layout import MAX_SIDE, check_layout
    from ._sy_e_layout import clip_boxes_text, multiple_warnings
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import MAX_SIDE, check_layout
    from _sy_e_layout import clip_boxes_text, multiple_warnings


def check_with_extras(text, canvas_width, canvas_height, warn_overlap=True, multiple=1):
    """Pure function. Returns (valid, report, clipped_text). The report is the normal one, plus a WARNING line for each
    box not on a multiple (multiple 1 = off). clipped_text is the list cut to fit the canvas (broken boxes dropped);
    it is the original text when the list cannot be read."""
    checked = text
    try:  # one single box object is accepted like the other layout nodes do: check it as a list of one
        if isinstance(json.loads(text), dict):
            checked = "[%s]" % text
    except (TypeError, ValueError):
        pass
    valid, report = check_layout(checked, canvas_width, canvas_height, warn_overlap)
    lines = [report] + multiple_warnings(checked, multiple)
    clipped, dropped, changed = clip_boxes_text(text, canvas_width, canvas_height)
    if not valid and clipped != text:
        lines.append("FIX: the clipped_boxes output has the list cut to fit (%d box%s changed, %d dropped)." % (changed, "" if changed == 1 else "es", dropped))
    return valid, "\n".join(lines), (text if valid else clipped)


class SYLayoutJsonCheck:
    DESCRIPTION = "Checks a list of layout boxes: valid JSON, numbers, inside the picture, real size, short labels. Gives true or false and a report. Also hands back a fixed list (cut to fit the picture) and can warn when numbers are not a multiple of 8 or 64."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("valid", "report", "layout_boxes", "clipped_boxes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layout_boxes": ("STRING", {"default": "", "multiline": True, "tooltip": "The box list as JSON text. Connect a Layout Box or Merge node, or paste it."}),
                "canvas_width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Width of the picture the boxes must fit in, in pixels."}),
                "canvas_height": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Height of the picture the boxes must fit in, in pixels."}),
                "warn_overlap": ("BOOLEAN", {"default": True, "tooltip": "Add a warning when two boxes cover the same area. A warning does not make it invalid."}),
            },
            "optional": {
                "warn_multiple_of": ("INT", {"default": 1, "min": 1, "max": 512, "tooltip": "Warn for numbers that are not a multiple of this, for example 8 or 64. 1 turns it off."}),
            },
        }

    def run(self, layout_boxes, canvas_width, canvas_height, warn_overlap, warn_multiple_of=1):
        valid, report, clipped = check_with_extras(layout_boxes, canvas_width, canvas_height, warn_overlap, warn_multiple_of)
        return (valid, report, layout_boxes, clipped)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutJsonCheck", SYLayoutJsonCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutJsonCheck"] = "Layout JSON Check SY"
