"""H3 Tiled Upscale SY: enlarges a big picture or video frames with an upscale model in overlapping tiles, so memory never runs out."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core, is_out_of_memory
    from ._sy_model_files import list_names
    from .sy_tiles import tile_starts, ramp_1d
    from .sy_upscale import TARGETS, METHODS, target_size, chunk_ranges, _resize
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core, is_out_of_memory
    from _sy_model_files import list_names
    from sy_tiles import tile_starts, ramp_1d
    from sy_upscale import TARGETS, METHODS, target_size, chunk_ranges, _resize

BLENDS = ["feather", "none"]
MIN_TILE = 128


def axis_plan(side, tile, overlap):
    """Pure function. Tiles along one side: list of (start, length, lead, trail). lead/trail = pixels shared with the
    neighbour before/after (0 at the picture edge). The last tile is moved back so it ends at the edge."""
    side, tile, overlap = int(side), int(tile), int(overlap)
    starts = tile_starts(side, tile, overlap)
    length = min(tile, side)
    ov = min(overlap, length - 1)
    n = len(starts)
    plan = []
    for i, s in enumerate(starts):
        lead = 0 if i == 0 else max(ov, starts[i - 1] + length - s)
        lead = min(lead, length - 1) if lead else 0
        trail = 0 if i == n - 1 else max(ov, s + length - starts[i + 1])
        trail = min(trail, length - 1) if trail else 0
        plan.append((s, length, lead, trail))
    return plan


def tile_grid(width, height, tile, overlap):
    """Pure function. Every tile as (x, y, w, h, lead_x, trail_x, lead_y, trail_y), row by row."""
    if int(overlap) < 0:
        raise ValueError("overlap cannot be negative, got %d" % int(overlap))
    if int(overlap) >= int(tile):
        raise ValueError("overlap (%d) must be smaller than the tile size (%d)" % (int(overlap), int(tile)))
    xs = axis_plan(width, tile, overlap)
    ys = axis_plan(height, tile, overlap)
    return [(x, y, w, h, lx, tx, ly, ty) for (y, h, ly, ty) in ys for (x, w, lx, tx) in xs]


def feather_1d(length, lead, trail):
    """Pure function. Weights along one tile side: rise over `lead`, fall over `trail`, 1 between (never 0)."""
    return ramp_1d(length, lead, trail)


def halve_tile(tile):
    """Pure function. The next smaller tile size for a retry (half, multiple of 8, never under 128), or None when already 128."""
    tile = int(tile)
    if tile <= MIN_TILE:
        return None
    return max(MIN_TILE, (tile // 2) // 8 * 8)


def size_info(src, final, scale, tiles, tile, retries, frames):
    """Pure function. One plain line."""
    parts = ["%dx%d -> %dx%d" % (src[0], src[1], final[0], final[1]),
             "model scale x%s" % ("%g" % scale), "%d tile%s of %d px per frame" % (tiles, "" if tiles == 1 else "s", tile),
             "%d frame%s" % (frames, "" if frames == 1 else "s")]
    if retries:
        parts.append("memory ran short, tile size halved %d time%s" % (retries, "" if retries == 1 else "s"))
    return ", ".join(parts)


def upscale_tiled(image, model_fn, scale, tile, overlap, blend="feather"):
    """Enlarges image [B,H,W,C] tile by tile. model_fn takes a [B,h,w,C] tile and returns it enlarged by `scale`
    (scale 0 = find out from the first tile). Overlaps are mixed with soft ramps (feather) or overwritten (none).
    Returns (image, scale_used, tile_count)."""
    import torch
    if getattr(image, "ndim", 0) != 4:
        raise ValueError("expected a picture batch shaped [batch, height, width, channels]")
    if blend not in BLENDS:
        raise ValueError("blend must be one of %s, got %r" % (BLENDS, blend))
    b, h, w, c = (int(v) for v in image.shape)
    tiles = tile_grid(w, h, tile, overlap)
    out = acc = None
    s = int(scale) if scale else 0
    for (x, y, tw, th, lx, tx, ly, ty) in tiles:
        res = model_fn(image[:, y:y + th, x:x + tw, :])
        if s == 0:
            if res.shape[2] % tw or res.shape[1] % th or res.shape[2] // tw != res.shape[1] // th:
                raise ValueError("the upscale model returned %dx%d for a %dx%d tile, not a whole-number scale"
                                 % (res.shape[2], res.shape[1], tw, th))
            s = int(res.shape[2] // tw)
        if tuple(res.shape[1:3]) != (th * s, tw * s):
            raise ValueError("the upscale model returned %dx%d for a %dx%d tile, expected x%d"
                             % (res.shape[2], res.shape[1], tw, th, s))
        if out is None:
            out = torch.zeros((b, h * s, w * s, int(res.shape[3])), dtype=torch.float32)
            acc = torch.zeros((1, h * s, w * s, 1), dtype=torch.float32)
        res = res.detach().to(device="cpu", dtype=torch.float32)
        oy, ox = y * s, x * s
        if blend == "none":
            out[:, oy:oy + th * s, ox:ox + tw * s, :] = res
            acc[:, oy:oy + th * s, ox:ox + tw * s, :] = 1.0
            continue
        wy = torch.tensor(feather_1d(th * s, ly * s, ty * s), dtype=torch.float32).view(1, th * s, 1, 1)
        wx = torch.tensor(feather_1d(tw * s, lx * s, tx * s), dtype=torch.float32).view(1, 1, tw * s, 1)
        wt = wy * wx
        out[:, oy:oy + th * s, ox:ox + tw * s, :] += res * wt
        acc[:, oy:oy + th * s, ox:ox + tw * s, :] += wt
    if blend == "feather":
        out = out / acc
    return out.clamp_(0.0, 1.0), s, len(tiles)


def _free_cache():
    try:
        import comfy.model_management as mm
        mm.soft_empty_cache()
    except Exception:
        pass


class SYH3TiledUpscale:
    DESCRIPTION = ("Enlarges a big picture or video frames with an upscale model in overlapping tiles, so the card never runs out of memory. "
                   "Tiles are blended softly so no seams show. If memory still runs short, the tile size is halved by itself and the run continues.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or the video frames to enlarge."}),
                "upscale_model": (list_names("upscale_models"), {"tooltip": "The upscale model file."}),
            },
            "optional": {
                "tile_size": ("INT", {"default": 512, "min": 128, "max": 2048, "step": 8, "tooltip": "Size of one input tile in pixels. Smaller uses less memory."}),
                "overlap": ("INT", {"default": 32, "min": 0, "max": 256, "tooltip": "Pixels shared by neighbour tiles. 32 to 64 hides the seams."}),
                "blend": (BLENDS, {"default": "feather", "tooltip": "feather mixes the overlaps softly. none just pastes the tiles."}),
                "target": (TARGETS, {"default": TARGETS[0], "tooltip": "What the amount means. 'Keep the model's size' uses the size the model gives."}),
                "amount": ("FLOAT", {"default": 2048.0, "min": 0.0, "max": 32768.0, "step": 1.0, "tooltip": "Pixels for side, width and height. Megapixels for the last choice."}),
                "method": (METHODS, {"default": "lanczos", "tooltip": "How the last resize to the exact size is done."}),
                "auto_retry": ("BOOLEAN", {"default": True, "tooltip": "If memory runs out, halve the tile size (down to 128) and go on."}),
                "chunk_frames": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "Frames sent through the model at once. Lower = less memory."}),
            },
        }

    def run(self, image, upscale_model, tile_size=512, overlap=32, blend="feather", target=TARGETS[0], amount=2048.0,
            method="lanczos", auto_retry=True, chunk_frames=4):
        if getattr(image, "ndim", 0) != 4:
            raise ValueError("expected a picture batch shaped [batch, height, width, channels]")
        if not upscale_model or upscale_model not in list_names("upscale_models"):
            raise ValueError("pick an upscale model: %r was not found in the upscale_models folder" % (upscale_model,))
        import torch
        src = (int(image.shape[2]), int(image.shape[1]))
        model = core("UpscaleModelLoader", "H3 Tiled Upscale SY", model_name=upscale_model)[0]

        def model_fn(t):
            return core("ImageUpscaleWithModel", "H3 Tiled Upscale SY", upscale_model=model, image=t)[0]

        tile, retries, scale, tile_count = int(tile_size), 0, 0, 0
        pieces = []
        for a, e in chunk_ranges(image.shape[0], chunk_frames):
            while True:
                ov = min(int(overlap), tile - 1, max(0, tile // 2))
                try:
                    part, scale, tile_count = upscale_tiled(image[a:e], model_fn, scale, tile, ov, blend)
                    break
                except Exception as ex:
                    smaller = halve_tile(tile)
                    if not auto_retry or not is_out_of_memory(ex) or smaller is None:
                        raise
                    tile, retries = smaller, retries + 1
                    _free_cache()
            pieces.append(part)
        out = torch.cat(pieces, dim=0)
        model_out = (int(out.shape[2]), int(out.shape[1]))
        final = model_out if target == TARGETS[0] else target_size(src[0], src[1], target, amount)
        out = _resize(out, final[0], final[1], method)
        return (out, size_info(src, final, scale, tile_count, tile, retries, int(image.shape[0])))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3TiledUpscale", SYH3TiledUpscale)
NODE_DISPLAY_NAME_MAPPINGS["SYH3TiledUpscale"] = "H3 Tiled Upscale SY"
