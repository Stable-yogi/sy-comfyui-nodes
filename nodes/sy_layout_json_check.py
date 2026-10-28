"""Layout JSON Check SY: checks box text against a canvas size and says in plain words what is wrong."""
try:
    from ._sy_common import category, register
    from ._sy_layout import MAX_SIDE, check_layout
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import MAX_SIDE, check_layout


class SYLayoutJsonCheck:
    DESCRIPTION = "Checks a list of layout boxes: valid JSON, numbers, inside the picture, real size, short labels. Gives true or false and a report."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("valid", "report", "layout_boxes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layout_boxes": ("STRING", {"default": "", "multiline": True, "tooltip": "The box list as JSON text. Connect a Layout Box or Merge node, or paste it."}),
                "canvas_width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Width of the picture the boxes must fit in, in pixels."}),
                "canvas_height": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Height of the picture the boxes must fit in, in pixels."}),
                "warn_overlap": ("BOOLEAN", {"default": True, "tooltip": "Add a warning when two boxes cover the same area. A warning does not make it invalid."}),
            }
        }

    def run(self, layout_boxes, canvas_width, canvas_height, warn_overlap):
        valid, report = check_layout(layout_boxes, canvas_width, canvas_height, warn_overlap)
        return (valid, report, layout_boxes)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutJsonCheck", SYLayoutJsonCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutJsonCheck"] = "Layout JSON Check SY"
