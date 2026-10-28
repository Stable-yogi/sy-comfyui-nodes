"""Tile Grid Calc SY: how many tiles cover a picture for a tile size and overlap."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 1_000_000


def _tiles_along(length, tile, overlap):
    if length <= tile:
        return 1
    step = tile - overlap
    return -(-(length - overlap) // step)


def tile_grid(width, height, tile_size, overlap):
    """Pure function. Returns (columns, rows, count, report_text)."""
    width, height, tile_size, overlap = int(width), int(height), int(tile_size), int(overlap)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (width, height))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("width and height must be at most %d, got %dx%d" % (MAX_SIDE, width, height))
    if tile_size < 1:
        raise ValueError("tile_size must be at least 1, got %d" % tile_size)
    if overlap < 0:
        raise ValueError("overlap cannot be negative, got %d" % overlap)
    if overlap >= tile_size:
        raise ValueError("overlap (%d) must be smaller than tile_size (%d)" % (overlap, tile_size))
    cols = _tiles_along(width, tile_size, overlap)
    rows = _tiles_along(height, tile_size, overlap)
    count = cols * rows
    text = "%dx%d picture, tile %d, overlap %d: %d columns x %d rows = %d tiles" % (
        width, height, tile_size, overlap, cols, rows, count)
    return (cols, rows, count, text)


class SYTileGridCalc:
    DESCRIPTION = ("Counts the tiles needed to cover a picture for a tile size and overlap. "
                   "Gives columns, rows, the total and a text line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("columns", "rows", "count", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 2048, "min": 1, "max": MAX_SIDE, "tooltip": "Picture width in pixels."}),
                "height": ("INT", {"default": 2048, "min": 1, "max": MAX_SIDE, "tooltip": "Picture height in pixels."}),
                "tile_size": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Width and height of one square tile in pixels."}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": MAX_SIDE, "tooltip": "Pixels shared by neighbour tiles. Must be less than the tile size."}),
            }
        }

    def run(self, width, height, tile_size, overlap):
        return tile_grid(width, height, tile_size, overlap)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TileGridCalc", SYTileGridCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYTileGridCalc"] = "Tile Grid Calc SY"
