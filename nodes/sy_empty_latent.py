"""Empty Latent SY: a blank latent of the right shape for the model family."""
try:
    from ._sy_common import category, register
    from ._sy_a1_sizes import SNAP_CHOICES, SNAP_DIRECTIONS, snap_choice, snap_value, ratio_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_a1_sizes import SNAP_CHOICES, SNAP_DIRECTIONS, snap_choice, snap_value, ratio_text

# latent type -> channel count. Both use 8x smaller height and width than the picture.
LATENT_TYPES = {
    "standard 4ch /8": 4,
    "flux 16ch /8": 16,
}
DOWNSCALE = 8
MAX_SIDE = 16384
MAX_BATCH = 4096


def latent_shape(width, height, batch, latent_type):
    """Pure function. Returns (batch, channels, height//8, width//8), like the stock empty latent."""
    if latent_type not in LATENT_TYPES:
        raise ValueError("unknown latent_type %r, pick one of: %s" % (latent_type, ", ".join(LATENT_TYPES)))
    width, height, batch = int(width), int(height), int(batch)
    if width < DOWNSCALE or height < DOWNSCALE:
        raise ValueError("width and height must be at least %d, got %dx%d" % (DOWNSCALE, width, height))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("width and height must be at most %d, got %dx%d" % (MAX_SIDE, width, height))
    if batch < 1 or batch > MAX_BATCH:
        raise ValueError("batch must be between 1 and %d, got %d" % (MAX_BATCH, batch))
    return (batch, LATENT_TYPES[latent_type], height // DOWNSCALE, width // DOWNSCALE)


BIG_MEGAPIXELS = 4.0


def plan_latent(width, height, batch, latent_type, snap_to="off", snap_direction="nearest"):
    """Pure function. Returns (shape, picture_width, picture_height, info).

    snap_to off keeps the old behaviour: sizes are cut down to a multiple of 8. A number (8, 16, 32, 64) rounds
    the size to that multiple first (nearest, down or up). picture_width/height is the size the picture really gets.
    """
    multiple = snap_choice(snap_to)
    width, height = int(width), int(height)
    notes = []
    if multiple:
        # check the raw numbers first so a refusal talks about what the user typed
        latent_shape(max(width, DOWNSCALE), max(height, DOWNSCALE), batch, latent_type)
        if width < DOWNSCALE or height < DOWNSCALE:
            raise ValueError("width and height must be at least %d, got %dx%d" % (DOWNSCALE, width, height))
        w2 = snap_value(width, multiple, snap_direction, minimum=max(multiple, DOWNSCALE), maximum=MAX_SIDE)
        h2 = snap_value(height, multiple, snap_direction, minimum=max(multiple, DOWNSCALE), maximum=MAX_SIDE)
        if (w2, h2) != (width, height):
            notes.append("Snapped %dx%d to %dx%d (multiple of %d, %s)." % (width, height, w2, h2, multiple, snap_direction))
        width, height = w2, h2
    shape = latent_shape(width, height, batch, latent_type)
    pw, ph = shape[3] * DOWNSCALE, shape[2] * DOWNSCALE
    if (pw, ph) != (width, height):
        notes.append("%dx%d is not a multiple of %d, so the picture will be %dx%d. Use snap_to to round it instead." % (width, height, DOWNSCALE, pw, ph))
    mp = pw * ph / 1_000_000
    head = "Latent %s: %d x %d channels x %d x %d. Picture %dx%d (%.2f MP, %s)." % (latent_type, shape[0], shape[1], shape[2], shape[3], pw, ph, mp, ratio_text(pw, ph))
    if mp > BIG_MEGAPIXELS:
        notes.append("Warning: %.1f MP is large; many cards run out of memory above %d MP." % (mp, int(BIG_MEGAPIXELS)))
    if shape[0] > 1 and mp * shape[0] > 8:
        notes.append("Warning: %d pictures at once at this size need a lot of memory. Lower the batch if it fails." % shape[0])
    return shape, pw, ph, " ".join([head] + notes)


class SYEmptyLatent:
    DESCRIPTION = ("Makes a blank latent to start a render from. 'standard 4ch /8' has 4 channels "
                   "(SD 1.5, SDXL). 'flux 16ch /8' has 16 channels (Flux, SD3 style). Both are 8 times smaller than the picture. "
                   "Adds a snap_to option (round the size to 8, 16, 32 or 64 instead of silently cutting it), the real picture "
                   "width and height as outputs, and an info text with warnings for sizes that are odd or very large.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("latent", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "step": 8, "tooltip": "Picture width in pixels."}),
                "height": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "step": 8, "tooltip": "Picture height in pixels."}),
                "batch": ("INT", {"default": 1, "min": 1, "max": MAX_BATCH, "tooltip": "How many blank latents to make at once."}),
                "latent_type": (list(LATENT_TYPES), {"default": "standard 4ch /8", "tooltip": "4 channels for SD 1.5 and SDXL. 16 channels for Flux style models."}),
            },
            "optional": {
                "snap_to": (SNAP_CHOICES, {"default": "off", "tooltip": "off cuts the size to a multiple of 8. 16, 32 or 64 round it to that multiple."}),
                "snap_direction": (SNAP_DIRECTIONS, {"default": "nearest", "tooltip": "How snap_to rounds: to the nearest multiple, always down, or always up."}),
            },
        }

    def run(self, width, height, batch, latent_type, snap_to="off", snap_direction="nearest"):
        import torch
        shape, pw, ph, info = plan_latent(width, height, batch, latent_type, snap_to, snap_direction)
        try:
            import comfy.model_management as mm
            device = mm.intermediate_device()
        except Exception:
            device = "cpu"
        return ({"samples": torch.zeros(list(shape), device=device)}, pw, ph, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EmptyLatent", SYEmptyLatent)
NODE_DISPLAY_NAME_MAPPINGS["SYEmptyLatent"] = "Empty Latent SY"
