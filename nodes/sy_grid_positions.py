"""Grid Positions SY: works out where each cell of a grid sits, for placing pictures or labels."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ORDERS = ["row by row", "column by column"]


def grid_cells(columns, rows, cw, ch, gap=0, margin=0, order="row by row"):
    """Pure function. Returns (cells, total_width, total_height).
    cells is a list of (index, x, y, w, h) sorted by index. The margin surrounds the grid, the gap sits between cells."""
    columns, rows, cw, ch, gap, margin = (int(v) for v in (columns, rows, cw, ch, gap, margin))
    if columns < 1 or rows < 1:
        raise ValueError("columns and rows must be at least 1 (got %d and %d)" % (columns, rows))
    if cw < 1 or ch < 1:
        raise ValueError("cell_width and cell_height must be at least 1 (got %d and %d)" % (cw, ch))
    if gap < 0 or margin < 0:
        raise ValueError("gap and margin must be 0 or more (got %d and %d)" % (gap, margin))
    if order not in ORDERS:
        raise ValueError("order must be one of: %s (got %r)" % (", ".join(ORDERS), order))
    cells = []
    for r in range(rows):
        for c in range(columns):
            index = r * columns + c if order == ORDERS[0] else c * rows + r
            cells.append((index, margin + c * (cw + gap), margin + r * (ch + gap), cw, ch))
    cells.sort(key=lambda t: t[0])
    total_w = 2 * margin + columns * cw + (columns - 1) * gap
    total_h = 2 * margin + rows * ch + (rows - 1) * gap
    return cells, total_w, total_h


def cells_to_text(cells):
    return "\n".join("%d,%d,%d,%d,%d" % c for c in cells)


class SYGridPositions:
    DESCRIPTION = ("Works out where every cell of a grid sits, so you can place pictures or labels. "
                   "Gives one line per cell as index,x,y,width,height plus the total size of the grid.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("positions", "total_width", "total_height", "cell_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "columns": ("INT", {"default": 3, "min": 1, "max": 64, "tooltip": "How many cells across."}),
                "rows": ("INT", {"default": 3, "min": 1, "max": 64, "tooltip": "How many cells down."}),
                "cell_width": ("INT", {"default": 512, "min": 1, "max": 16384, "tooltip": "Width of one cell in pixels."}),
                "cell_height": ("INT", {"default": 512, "min": 1, "max": 16384, "tooltip": "Height of one cell in pixels."}),
                "gap": ("INT", {"default": 16, "min": 0, "max": 1024, "tooltip": "Space between neighbouring cells in pixels."}),
                "margin": ("INT", {"default": 0, "min": 0, "max": 4096, "tooltip": "Empty border around the whole grid in pixels."}),
                "order": (ORDERS, {"default": "row by row", "tooltip": "Number the cells along the rows or down the columns."}),
            }
        }

    def run(self, columns, rows, cell_width, cell_height, gap, margin, order):
        cells, tw, th = grid_cells(columns, rows, cell_width, cell_height, gap, margin, order)
        return (cells_to_text(cells), tw, th, len(cells))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GridPositions", SYGridPositions)
NODE_DISPLAY_NAME_MAPPINGS["SYGridPositions"] = "Grid Positions SY"
