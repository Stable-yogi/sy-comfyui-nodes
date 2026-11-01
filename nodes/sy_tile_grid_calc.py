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


MAX_LISTED = 4096


def tile_starts(length, tile, overlap):
    """Pure function. Where each tile starts along one side. The last tile is moved back so it ends exactly at the edge."""
    n = _tiles_along(length, tile, overlap)
    if n == 1:
        return [0]
    step = tile - overlap
    return [min(i * step, length - tile) for i in range(n)]


def tile_positions(width, height, tile_size, overlap):
    """Pure function. Text with one 'x,y' line per tile (top left corner), row by row. Too many tiles gives a short note."""
    cols, rows, count, _ = tile_grid(width, height, tile_size, overlap)
    if count > MAX_LISTED:
        return "%d tiles is too many to list (the limit is %d)" % (count, MAX_LISTED)
    xs = tile_starts(int(width), int(tile_size), int(overlap))
    ys = tile_starts(int(height), int(tile_size), int(overlap))
    return "\n".join("%d,%d" % (x, y) for y in ys for x in xs)


def tile_notes(width, height, tile_size, overlap):
    """Pure function. Plain notes and warnings for a tile plan (one sentence per line, may be one 'looks fine' line)."""
    width, height, tile_size, overlap = int(width), int(height), int(tile_size), int(overlap)
    cols, rows, count, _ = tile_grid(width, height, tile_size, overlap)
    notes = []
    if count == 1:
        notes.append("The picture fits in one tile, so no tiling is needed.")
    if 0 < overlap < 8 and count > 1:
        notes.append("Overlap %d is very small and seams may show. 32 to 128 is common." % overlap)
    if overlap == 0 and count > 1:
        notes.append("No overlap: seams between tiles are likely.")
    if overlap * 2 > tile_size:
        notes.append("Overlap is more than half the tile, so many pixels are processed twice.")
    if tile_size % 8:
        notes.append("Tile size %d is not a multiple of 8. Most models want 8, 16 or 64." % tile_size)
    if count > 64:
        notes.append("%d tiles will take a long time. A bigger tile size means fewer tiles." % count)
    for label, length, n in (("column", width, cols), ("row", height, rows)):
        if n > 1:
            starts = tile_starts(length, tile_size, overlap)
            shared = starts[-2] + tile_size - starts[-1]
            if shared > overlap:
                notes.append("The last %s is moved back to fit the edge, so it shares %d pixels with its neighbour instead of %d." % (label, shared, overlap))
    return notes or ["Looks fine."]


class SYTileGridCalc:
    DESCRIPTION = ("Counts the tiles needed to cover a picture for a tile size and overlap. "
                   "Gives columns, rows, the total and a text line, plus the step between tiles, the top left corner of every tile, "
                   "and plain warnings (tiny overlap, tile size not a multiple of 8, too many tiles). Can stop the run if there would be too many tiles.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("columns", "rows", "count", "report", "step", "positions", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 2048, "min": 1, "max": MAX_SIDE, "tooltip": "Picture width in pixels."}),
                "height": ("INT", {"default": 2048, "min": 1, "max": MAX_SIDE, "tooltip": "Picture height in pixels."}),
                "tile_size": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Width and height of one square tile in pixels."}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": MAX_SIDE, "tooltip": "Pixels shared by neighbour tiles. Must be less than the tile size."}),
            },
            "optional": {
                "max_tiles": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Stop with a message if more tiles than this are needed, for example 16. 0 turns the limit off."}),
            },
        }

    def run(self, width, height, tile_size, overlap, max_tiles=0):
        cols, rows, count, report = tile_grid(width, height, tile_size, overlap)
        if int(max_tiles) > 0 and count > int(max_tiles):
            raise ValueError("this needs %d tiles, more than your limit of %d. Raise the tile size or lower the overlap" % (count, int(max_tiles)))
        return (cols, rows, count, report, int(tile_size) - int(overlap), tile_positions(width, height, tile_size, overlap),
                "\n".join(tile_notes(width, height, tile_size, overlap)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TileGridCalc", SYTileGridCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYTileGridCalc"] = "Tile Grid Calc SY"
