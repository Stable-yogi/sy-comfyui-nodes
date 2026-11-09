"""H3 Tile Refine SY: runs the last sampling steps of a MiniMax H3 latent one tile at a time, which takes less graphics card memory at the peak."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core
    from .sy_tiles import ramp_1d
    from .sy_h3_tiled_upscale import axis_plan
    from ._sy_h3_windows import add_carry, audio_span, ease_in_out, frames_for_tokens, plan_windows, tokens_for_frames, window_conditioning
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core
    from sy_tiles import ramp_1d
    from sy_h3_tiled_upscale import axis_plan
    from _sy_h3_windows import add_carry, audio_span, ease_in_out, frames_for_tokens, plan_windows, tokens_for_frames, window_conditioning

GRID = 16  # one latent cell covers 16 x 16 pixels
WHO = "H3 Tile Refine SY"


def to_cells(pixels):
    """Pure function. Pixels to latent cells, rounded down to an even number (the model works in 2 x 2 patches), never under 2."""
    return max(2, int(pixels) // GRID // 2 * 2)


def tile_plan(cells_w, cells_h, tile_w, tile_h, overlap_x, overlap_y):
    """Pure function. Every tile as (x, y, w, h, lead_x, trail_x, lead_y, trail_y) in latent cells; sizes come in as pixels."""
    tw, th = to_cells(tile_w), to_cells(tile_h)
    ox, oy = int(overlap_x) // GRID, int(overlap_y) // GRID
    if ox >= tw or oy >= th:
        raise ValueError("overlap must be smaller than the tile: tile %d x %d, overlap %d / %d pixels" % (tw * GRID, th * GRID, int(overlap_x), int(overlap_y)))
    xs = axis_plan(cells_w, tw, ox)
    ys = axis_plan(cells_h, th, oy)
    return [(x, y, w, h, lx, tx, ly, ty) for (y, h, ly, ty) in ys for (x, w, lx, tx) in xs]


def plan_info(cells_w, cells_h, tiles, frames, windows=1):
    """Pure function. The line shown on the info output."""
    w, h = tiles[0][2:4]
    line = "%d x %d pixels, %d latent frames, %d tile%s of %d x %d pixels" % (
        cells_w * GRID, cells_h * GRID, frames, len(tiles), "" if len(tiles) == 1 else "s", w * GRID, h * GRID)
    return line if windows == 1 else "%s, %d time windows" % (line, windows)


def _crop(t, x, y, w, h):
    return t[..., y:y + h, x:x + w]


def fit_keyframe(latent, cells_w, cells_h):
    """A keyframe must share the target grid. One made for the small draft is stretched to the big size first."""
    if tuple(latent.shape[-2:]) == (cells_h, cells_w):
        return latent
    import torch.nn.functional as F
    b, c, t = latent.shape[:3]
    flat = latent.reshape(b * c, t, latent.shape[-2], latent.shape[-1]).float()
    return F.interpolate(flat, size=(cells_h, cells_w), mode="bilinear", align_corners=False).reshape(b, c, t, cells_h, cells_w).to(latent.dtype)


def crop_conditioning(positive, tile, cells_w, cells_h):
    """Keyframes sit on the picture grid, so each tile gets its own piece. References and words stay whole."""
    x, y, w, h = tile[:4]
    out = []
    for emb, extra in positive:
        extra = extra.copy()
        frames = extra.get("minimax_keyframes")
        if frames:
            cut = []
            for kf in frames:
                kf = dict(kf)
                if kf.get("latent") is not None:
                    kf["latent"] = _crop(fit_keyframe(kf["latent"], cells_w, cells_h), x, y, w, h).contiguous()
                cut.append(kf)
            extra["minimax_keyframes"] = cut
        out.append([emb, extra])
    return out


class _TileNoise:
    """Hands each tile its piece of ONE noise field, so neighbour tiles start from the same noise where they overlap."""

    def __init__(self, seed, noise):
        self.seed = seed
        self.noise = noise

    def generate_noise(self, input_latent):
        return self.noise


class SYH3TileRefine:
    DESCRIPTION = ("Runs the sharpening steps of a MiniMax H3 video one tile at a time and blends the tiles back, which takes less graphics card "
                   "memory at the peak. It can also split the video in time, so a long video needs no more memory than a short one. "
                   "Put it after the latent upscale, in place of the second sampler. The sound stays as it is.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "STRING")
    RETURN_NAMES = ("latent", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The H3 model."}),
                "positive": ("CONDITIONING", {"tooltip": "The same words and references the first pass used."}),
                "latent": ("LATENT", {"tooltip": "The enlarged H3 latent."}),
                "sampler": ("SAMPLER", {"tooltip": "The sampler to use on each tile."}),
                "sigmas": ("SIGMAS", {"tooltip": "The last steps only. More steps change the picture more."}),
            },
            "optional": {
                "seed": ("INT", {"default": 7, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Noise seed. Every tile shares one noise field."}),
                "tile_width": ("INT", {"default": 896, "min": 128, "max": 8192, "step": 32, "tooltip": "Tile width in pixels. Smaller uses less memory."}),
                "tile_height": ("INT", {"default": 704, "min": 128, "max": 8192, "step": 32, "tooltip": "Tile height in pixels. Smaller uses less memory."}),
                "overlap_x": ("INT", {"default": 256, "min": 0, "max": 4096, "step": 16, "tooltip": "Pixels shared by tiles side by side. More hides seams, but takes longer."}),
                "overlap_y": ("INT", {"default": 256, "min": 0, "max": 4096, "step": 16, "tooltip": "Pixels shared by tiles above each other. More hides seams, but takes longer."}),
                "window_frames": ("INT", {"default": 0, "min": 0, "max": 3600, "step": 1, "tooltip": "Video frames per time window. 0 = the whole length at once. Smaller uses less memory."}),
                "window_overlap": ("INT", {"default": 22, "min": 5, "max": 1000, "step": 1, "tooltip": "Video frames shared by neighbour windows, softly crossfaded."}),
                "carry": ("BOOLEAN", {"default": True, "tooltip": "Each window starts from the finished frames of the window before it."}),
            },
        }

    def run(self, model, positive, latent, sampler, sigmas, seed=7, tile_width=896, tile_height=704, overlap_x=256, overlap_y=256, window_frames=0, window_overlap=22, carry=True):
        import torch
        import comfy.nested_tensor
        import comfy.sample
        import comfy.utils
        samples = latent["samples"]
        nested = getattr(samples, "is_nested", False)
        video = samples.tensors[0] if nested else samples
        audio = samples.tensors[1] if nested else None
        if video.ndim != 5:
            raise ValueError("%s needs a MiniMax H3 video latent, this one has %d dimensions" % (WHO, video.ndim))
        cells_h, cells_w = int(video.shape[-2]), int(video.shape[-1])
        tiles = tile_plan(cells_w, cells_h, tile_width, tile_height, overlap_x, overlap_y)
        windows = plan_windows(int(video.shape[2]), window_frames, window_overlap)
        noise = comfy.sample.prepare_noise(video, seed)
        merged = torch.zeros(video.shape, dtype=torch.float32)
        done_t = 0
        bar = comfy.utils.ProgressBar(len(tiles) * len(windows))
        for index, (t0, tn) in enumerate(windows):
            cond = positive if len(windows) == 1 else window_conditioning(positive, t0, t0 + tn)
            sound = audio[..., slice(*audio_span(windows, index, int(audio.shape[-1])))] if nested else None
            carry_t = tokens_for_frames(frames_for_tokens(done_t - t0)) if carry and done_t > t0 else 0
            total = torch.zeros(tuple(video.shape[:2]) + (tn,) + tuple(video.shape[3:]), dtype=torch.float32)
            weight = torch.zeros((1, 1, 1, cells_h, cells_w), dtype=torch.float32)
            for tile in tiles:
                x, y, w, h, lx, tx, ly, ty = tile
                part = _crop(video[:, :, t0:t0 + tn], x, y, w, h).contiguous()
                part_noise = _crop(noise[:, :, t0:t0 + tn], x, y, w, h).contiguous()
                piece = {"samples": part}
                if nested:
                    piece["samples"] = comfy.nested_tensor.NestedTensor((part, sound))
                    piece["noise_mask"] = comfy.nested_tensor.NestedTensor((torch.ones_like(part), torch.zeros_like(sound)))
                    part_noise = comfy.nested_tensor.NestedTensor((part_noise, torch.zeros_like(sound)))
                tile_cond = crop_conditioning(cond, tile, cells_w, cells_h)
                if carry_t:
                    tile_cond = add_carry(tile_cond, _crop(merged[:, :, t0:t0 + carry_t], x, y, w, h).to(video.dtype).contiguous())
                guider = core("BasicGuider", WHO, model=model, conditioning=tile_cond)[0]
                done = core("SamplerCustomAdvanced", WHO, noise=_TileNoise(seed, part_noise), guider=guider, sampler=sampler, sigmas=sigmas, latent_image=piece)[0]["samples"]
                done = done.tensors[0] if getattr(done, "is_nested", False) else done
                ramp = torch.tensor(ramp_1d(h, ly, ty)).view(-1, 1) * torch.tensor(ramp_1d(w, lx, tx)).view(1, -1)
                total[..., y:y + h, x:x + w] += done.detach().cpu().float() * ramp
                weight[..., y:y + h, x:x + w] += ramp
                bar.update(1)
            total /= weight
            shared = max(0, done_t - t0)
            if shared:
                fade = torch.tensor(ease_in_out(shared)).view(1, 1, -1, 1, 1)
                merged[:, :, t0:done_t] = merged[:, :, t0:done_t] * (1 - fade) + total[:, :, :shared] * fade
            merged[:, :, t0 + shared:t0 + tn] = total[:, :, shared:]
            done_t = max(done_t, t0 + tn)
        merged = merged.to(video.dtype)
        out = latent.copy()
        out["samples"] = comfy.nested_tensor.NestedTensor((merged, audio)) if nested else merged
        out.pop("noise_mask", None)
        return (out, plan_info(cells_w, cells_h, tiles, int(video.shape[2]), len(windows)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3TileRefine", SYH3TileRefine)
NODE_DISPLAY_NAME_MAPPINGS["SYH3TileRefine"] = WHO
