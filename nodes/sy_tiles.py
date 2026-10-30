"""Tile Split SY and Tile Merge SY: cut a big picture into equal tiles, then join processed tiles back with a soft blend."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

INFO_KEYS = ("width", "height", "tile_w", "tile_h", "overlap", "xs", "ys", "cols", "rows")


def tile_starts(side, tile, overlap):
    """Pure function. Start positions of tiles along one axis. The last tile is shifted back so it keeps the full size."""
    side = int(side)
    tile = int(tile)
    overlap = int(overlap)
    if side < 1:
        raise ValueError("picture side must be at least 1 pixel, got %d" % side)
    if tile < 1:
        raise ValueError("tile size must be at least 1 pixel, got %d" % tile)
    if overlap < 0:
        raise ValueError("overlap cannot be negative, got %d" % overlap)
    if overlap >= tile:
        raise ValueError("overlap (%d) must be smaller than the tile size (%d). Lower the overlap." % (overlap, tile))
    length = min(tile, side)
    if side <= length:
        return [0]
    ov = min(overlap, length - 1)
    step = length - ov
    last = side - length
    starts = []
    pos = 0
    while pos < last:
        starts.append(pos)
        pos += step
    starts.append(last)
    return starts


def ramp_1d(length, lead, trail):
    """Pure function. Weights along one tile side: rise over `lead` at the start, fall over `trail` at the end, 1 between."""
    length = int(length)
    lead = int(lead)
    trail = int(trail)
    if length < 1:
        raise ValueError("tile length must be at least 1, got %d" % length)
    if lead < 0 or trail < 0:
        raise ValueError("ramp lengths cannot be negative")
    out = []
    for i in range(length):
        w = 1.0
        if lead > 0 and i < lead:
            w = min(w, (i + 1) / (lead + 1.0))
        if trail > 0 and i >= length - trail:
            w = min(w, (length - i) / (trail + 1.0))
        out.append(w)
    return out


def make_info(width, height, tile_size, overlap):
    """Pure function. Describes how a picture is cut. This dict is saved as JSON text."""
    width = int(width)
    height = int(height)
    xs = tile_starts(width, tile_size, overlap)
    ys = tile_starts(height, tile_size, overlap)
    return {
        "width": width,
        "height": height,
        "tile_w": min(int(tile_size), width),
        "tile_h": min(int(tile_size), height),
        "overlap": int(overlap),
        "xs": xs,
        "ys": ys,
        "cols": len(xs),
        "rows": len(ys),
    }


def parse_info(text):
    """Pure function. Reads and checks the tile_info text."""
    try:
        info = json.loads(text)
    except (TypeError, ValueError):
        raise ValueError("tile_info is not valid JSON text. Connect the tile_info output of Tile Split SY.")
    if not isinstance(info, dict):
        raise ValueError("tile_info must be a JSON object. Connect the tile_info output of Tile Split SY.")
    for key in INFO_KEYS:
        if key not in info:
            raise ValueError("tile_info is missing the key '%s'. Connect the tile_info output of Tile Split SY." % key)
    for key in INFO_KEYS:
        val = info[key]
        if key in ("xs", "ys"):
            if not isinstance(val, list) or not val or not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in val):
                raise ValueError("tile_info key '%s' must be a list of whole numbers" % key)
        elif not isinstance(val, int) or isinstance(val, bool) or val < 0:
            raise ValueError("tile_info key '%s' must be a whole number" % key)
    for key in ("width", "height", "tile_w", "tile_h", "cols", "rows"):
        if info[key] < 1:
            raise ValueError("tile_info key '%s' must be at least 1" % key)
    if info["cols"] != len(info["xs"]) or info["rows"] != len(info["ys"]):
        raise ValueError("tile_info cols/rows do not match the start lists (xs, ys)")
    if max(info["xs"]) + info["tile_w"] > info["width"] or max(info["ys"]) + info["tile_h"] > info["height"]:
        raise ValueError("tile_info tiles reach outside the picture (xs, ys, tile_w, tile_h, width, height)")
    return info


def scale_factor(info, tiles_w, tiles_h):
    """Pure function. Whole-number size change between the split tiles and the processed tiles."""
    tiles_w = int(tiles_w)
    tiles_h = int(tiles_h)
    tw = info["tile_w"]
    th = info["tile_h"]
    if tiles_w < tw or tiles_h < th or tiles_w % tw != 0 or tiles_h % th != 0:
        raise ValueError("the tiles were resized by a non-whole factor (%dx%d tiles from %dx%d). Resize by 1, 2, 4 and so on." % (tiles_w, tiles_h, tw, th))
    sx = tiles_w // tw
    sy = tiles_h // th
    if sx != sy:
        raise ValueError("the tiles were resized by a different factor in width (%d) and height (%d). Use the same factor." % (sx, sy))
    return sx


def merge_plan(info, scale):
    """Pure function. For each tile in order: (x0, y0, wx_list, wy_list) in output pixels."""
    scale = int(scale)
    if scale < 1:
        raise ValueError("scale must be at least 1, got %d" % scale)
    tw = info["tile_w"] * scale
    th = info["tile_h"] * scale
    ov_x = min(info["overlap"], info["tile_w"] - 1) * scale
    ov_y = min(info["overlap"], info["tile_h"] - 1) * scale
    cols = info["cols"]
    rows = info["rows"]
    plan = []
    for r in range(rows):
        wy = ramp_1d(th, ov_y if r > 0 else 0, ov_y if r < rows - 1 else 0)
        for c in range(cols):
            wx = ramp_1d(tw, ov_x if c > 0 else 0, ov_x if c < cols - 1 else 0)
            plan.append((info["xs"][c] * scale, info["ys"][r] * scale, wx, wy))
    return plan


class SYTileSplit:
    DESCRIPTION = "Cuts one big picture into equal tiles that overlap a little. Process the tiles, then join them with Tile Merge SY."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("tiles", "tile_info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to cut. If you give a batch, only the first picture is used."}),
                "tile_size": ("INT", {"default": 1024, "min": 64, "max": 8192, "tooltip": "Width and height of one tile in pixels."}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 2048, "tooltip": "How many pixels neighbouring tiles share. Must be smaller than the tile size."}),
            }
        }

    def run(self, image, tile_size, overlap):
        import torch
        height = int(image.shape[1])
        width = int(image.shape[2])
        info = make_info(width, height, tile_size, overlap)
        pic = image[0]
        tw = info["tile_w"]
        th = info["tile_h"]
        tiles = []
        for y in info["ys"]:
            for x in info["xs"]:
                tiles.append(pic[y:y + th, x:x + tw, :])
        return (torch.stack(tiles, dim=0), json.dumps(info))


class SYTileMerge:
    DESCRIPTION = "Joins tiles from Tile Split SY back into one picture. Works after an upscale of a whole-number factor."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tiles": ("IMAGE", {"tooltip": "The processed tiles, in the same count and order as Tile Split SY gave them."}),
                "tile_info": ("STRING", {"default": "", "forceInput": True, "tooltip": "The tile_info text from Tile Split SY."}),
                "blend": (["linear", "none"], {"default": "linear", "tooltip": "linear fades the shared edges softly. none lets later tiles cover earlier ones."}),
            }
        }

    def run(self, tiles, tile_info, blend):
        import torch
        info = parse_info(tile_info)
        expected = info["cols"] * info["rows"]
        got = int(tiles.shape[0])
        if got != expected:
            raise ValueError("expected %d tiles, got %d" % (expected, got))
        th_in = int(tiles.shape[1])
        tw_in = int(tiles.shape[2])
        channels = int(tiles.shape[3])
        s = scale_factor(info, tw_in, th_in)
        out_w = info["width"] * s
        out_h = info["height"] * s
        plan = merge_plan(info, s)
        dev = tiles.device
        tiles = tiles.to(torch.float32)
        acc = torch.zeros((out_h, out_w, channels), dtype=torch.float32, device=dev)
        if blend == "none":
            for i, (x0, y0, wx, wy) in enumerate(plan):
                acc[y0:y0 + th_in, x0:x0 + tw_in, :] = tiles[i]
            return (acc.clamp(0.0, 1.0).unsqueeze(0),)
        wsum = torch.zeros((out_h, out_w, 1), dtype=torch.float32, device=dev)
        for i, (x0, y0, wx, wy) in enumerate(plan):
            wxt = torch.tensor(wx, dtype=torch.float32, device=dev)
            wyt = torch.tensor(wy, dtype=torch.float32, device=dev)
            w = (wyt[:, None] * wxt[None, :]).unsqueeze(-1)
            acc[y0:y0 + th_in, x0:x0 + tw_in, :] += tiles[i] * w
            wsum[y0:y0 + th_in, x0:x0 + tw_in, :] += w
        out = acc / wsum.clamp(min=1e-12)
        return (out.clamp(0.0, 1.0).unsqueeze(0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TileSplit", SYTileSplit)
NODE_DISPLAY_NAME_MAPPINGS["SYTileSplit"] = "Tile Split SY"
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TileMerge", SYTileMerge)
NODE_DISPLAY_NAME_MAPPINGS["SYTileMerge"] = "Tile Merge SY"
