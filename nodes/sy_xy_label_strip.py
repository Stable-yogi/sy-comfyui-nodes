"""XY Label Strip SY: a text table of the grid values, handy for notes and captions."""
try:
    from ._sy_common import category, register
    from ._sy_xy import markdown_table, parse_axis
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_xy import markdown_table, parse_axis


def make_table(x_values, y_values, x_name, y_name):
    """Pure function. Returns the Markdown table text."""
    xs, ys = parse_axis(x_values), parse_axis(y_values)
    if not xs and not ys:
        raise ValueError("both lists are empty: give at least one X or Y value")
    return markdown_table(xs, ys, str(x_name).strip() or "X", str(y_name).strip() or "Y")


class SYXYLabelStrip:
    DESCRIPTION = "Writes the XY grid as a Markdown table. Each cell shows its picture number, so you can match it to the batch."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("table",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The X list, one value per line."}),
                "y_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The Y list, one value per line. Empty means a single row."}),
                "x_name": ("STRING", {"default": "X", "tooltip": "Name of the X axis, shown in the table corner."}),
                "y_name": ("STRING", {"default": "Y", "tooltip": "Name of the Y axis, shown in the table corner."}),
            }
        }

    def run(self, x_values, y_values, x_name, y_name):
        return (make_table(x_values, y_values, x_name, y_name),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYLabelStrip", SYXYLabelStrip)
NODE_DISPLAY_NAME_MAPPINGS["SYXYLabelStrip"] = "XY Label Strip SY"
