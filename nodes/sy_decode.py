"""Decode SY: turns a latent into a picture, video frames or sound, and retries in smaller tiles when the memory runs out."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core, is_out_of_memory
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core, is_out_of_memory

MODES = ["Picture or video", "Sound"]
TILED = ["Auto (retry in tiles)", "Always tiles", "Never tiles"]
MIN_TILE = 64


def tile_ladder(start, minimum=MIN_TILE):
    """Pure function. The tile sizes tried in order after a memory error: start, start/2, ... down to the minimum."""
    start, minimum = int(start), int(minimum)
    if start < minimum:
        raise ValueError("tile size must be at least %d, got %d" % (minimum, start))
    sizes = []
    size = start
    while size >= minimum:
        sizes.append(size)
        size //= 2
    return sizes


def plan_decode(mode, tiled, tile_size):
    """Pure function. Returns the list of attempts as (use_tiles, tile_size). Raises ValueError on a bad choice."""
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (MODES, mode))
    if tiled not in TILED:
        raise ValueError("tiles must be one of %s, got %r" % (TILED, tiled))
    ladder = tile_ladder(tile_size)
    if tiled == TILED[2]:
        return [(False, 0)]
    if tiled == TILED[1]:
        return [(True, s) for s in ladder]
    return [(False, 0)] + [(True, s) for s in ladder]


def info_text(mode, attempts_used, used, shape_text):
    """Pure function. One line telling what was decoded and how."""
    how = "in one piece" if not used[0] else "in tiles of %d" % used[1]
    extra = "" if attempts_used <= 1 else " (memory ran short, %d tries)" % attempts_used
    return "%s: %s, %s%s" % (mode, shape_text, how, extra)


def _blank_image():
    import torch
    return torch.zeros((1, 64, 64, 3), dtype=torch.float32)


def _silent_audio():
    import torch
    return {"waveform": torch.zeros((1, 2, 1), dtype=torch.float32), "sample_rate": 44100}


def _run_once(mode, samples, vae, use_tiles, tile, overlap):
    if mode == MODES[0]:
        if use_tiles:
            temporal = max(8, min(4096, tile // 8 * 2))
            return core("VAEDecodeTiled", "Decode SY", samples=samples, vae=vae, tile_size=tile,
                        overlap=min(overlap, tile // 2), temporal_size=temporal, temporal_overlap=8)[0]
        return core("VAEDecode", "Decode SY", samples=samples, vae=vae)[0]
    if use_tiles:
        return core("VAEDecodeAudioTiled", "Decode SY", samples=samples, vae=vae, tile_size=max(32, tile),
                    overlap=min(overlap, 1024))[0]
    return core("VAEDecodeAudio", "Decode SY", samples=samples, vae=vae)[0]


class SYDecode:
    DESCRIPTION = ("Turns a latent into a picture, video frames or sound. If the graphics card runs out of memory it "
                   "retries by itself in smaller and smaller tiles instead of stopping, and tells you what it used.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "AUDIO", "STRING")
    RETURN_NAMES = ("image", "audio", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "samples": ("LATENT", {"tooltip": "The latent to turn into a picture, video or sound."}),
                "vae": ("VAE", {"tooltip": "The VAE that matches the model (for sound: the audio VAE)."}),
                "mode": (MODES, {"default": MODES[0], "tooltip": "Picture or video frames come out on image. Sound comes out on audio."}),
                "tiles": (TILED, {"default": TILED[0], "tooltip": "Auto: one piece first, tiles if memory runs out. Always: tiles from the start. Never: one piece only."}),
                "tile_size": ("INT", {"default": 512, "min": MIN_TILE, "max": 4096, "step": 32, "tooltip": "First tile size in pixels. Each retry halves it."}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 1024, "step": 8, "tooltip": "How much neighbouring tiles share, so no seams show."}),
            }
        }

    def run(self, samples, vae, mode, tiles, tile_size, overlap):
        attempts = plan_decode(mode, tiles, tile_size)
        last_error = None
        for n, (use_tiles, tile) in enumerate(attempts, start=1):
            try:
                out = _run_once(mode, samples, vae, use_tiles, tile, overlap)
            except Exception as e:  # only a memory shortage is retried, anything else is a real error
                if not is_out_of_memory(e):
                    raise
                last_error = e
                try:
                    import comfy.model_management as mm
                    mm.soft_empty_cache()
                except Exception:
                    pass
                continue
            if mode == MODES[0]:
                shape = "%d frame(s) of %dx%d" % (out.shape[0], out.shape[2], out.shape[1])
                return (out, _silent_audio(), info_text(mode, n, (use_tiles, tile), shape))
            wave = out["waveform"]
            shape = "%.2f s at %d Hz" % (wave.shape[-1] / float(out["sample_rate"]), int(out["sample_rate"]))
            return (_blank_image(), out, info_text(mode, n, (use_tiles, tile), shape))
        raise ValueError("decode ran out of memory even in tiles of %d (last error: %s). Use a smaller picture or free the card."
                         % (attempts[-1][1], last_error))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Decode", SYDecode)
NODE_DISPLAY_NAME_MAPPINGS["SYDecode"] = "Decode SY"
