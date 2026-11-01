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


def cell_lines(x_values, y_values, x_name="X", y_name="Y"):
    """Pure function. One line per picture in batch order: '1: X=a, Y=p'. x changes fastest."""
    xs, ys = parse_axis(x_values), parse_axis(y_values)
    if not xs and not ys:
        raise ValueError("both lists are empty: give at least one X or Y value")
    xn, yn = str(x_name).strip() or "X", str(y_name).strip() or "Y"
    out = []
    for yi in range(max(len(ys), 1)):
        for xi in range(max(len(xs), 1)):
            parts = []
            if xs:
                parts.append("%s=%s" % (xn, xs[xi]))
            if ys:
                parts.append("%s=%s" % (yn, ys[yi]))
            out.append("%d: %s" % (len(out) + 1, ", ".join(parts)))
    return out


def grid_info(x_values, y_values):
    """Pure function. A plain line: the grid size, the picture count and warnings (repeated values, many pictures)."""
    xs, ys = parse_axis(x_values), parse_axis(y_values)
    nx, ny = max(len(xs), 1), max(len(ys), 1)
    total = nx * ny
    line = "Grid %d columns x %d row%s = %d pictures." % (nx, ny, "" if ny == 1 else "s", total)
    for axis, vals in (("X", xs), ("Y", ys)):
        low = [v.lower() for v in vals]
        dups = sorted({v for v in low if low.count(v) > 1})
        if dups:
            line += " Warning: %s repeats %s, so some pictures will look the same." % (axis, ", ".join(dups[:5]))
    if total > 36:
        line += " Warning: %d pictures is a lot to render and to view in one sheet." % total
    return line


class SYXYLabelStrip:
    DESCRIPTION = ("Writes the XY grid as a Markdown table. Each cell shows its picture number, so you can match it to the batch. "
                   "Also gives the picture count, a numbered list of cells, and an info line that warns about repeated values or a very big grid.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("table", "count", "cell_list", "info")

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
        table = make_table(x_values, y_values, x_name, y_name)
        cells = cell_lines(x_values, y_values, x_name, y_name)
        return (table, len(cells), chr(10).join(cells), grid_info(x_values, y_values))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYLabelStrip", SYXYLabelStrip)
NODE_DISPLAY_NAME_MAPPINGS["SYXYLabelStrip"] = "XY Label Strip SY"
