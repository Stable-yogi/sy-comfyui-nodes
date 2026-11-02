"""Strobe Flash SY: flashes the picture to white, black or a colour on a beat pattern."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ["white", "black", "invert", "colour"]


def flash_amount(frame_index, every_n, flash_frames, fade_frames, offset=0):
    """Pure function. 0..1: 1 inside a flash, then fading down over fade_frames, 0 otherwise.
    Frame 0 is the first frame. Nothing flashes before `offset`."""
    frame_index, every_n, flash_frames = int(frame_index), int(every_n), int(flash_frames)
    fade_frames, offset = int(fade_frames), int(offset)
    if every_n < 1:
        raise ValueError("every_n_frames must be at least 1 (got %d)" % every_n)
    if flash_frames < 1:
        raise ValueError("flash_frames must be at least 1 (got %d)" % flash_frames)
    if fade_frames < 0 or offset < 0:
        raise ValueError("fade_out_frames and offset cannot be negative")
    if frame_index < offset:
        return 0.0
    k = (frame_index - offset) % every_n
    if k < flash_frames:
        return 1.0
    if k < flash_frames + fade_frames:
        return 1.0 - (k - flash_frames + 1) / (fade_frames + 1.0)
    return 0.0


class SYStrobeFlash:
    DESCRIPTION = ("Flashes the clip to white, black, a colour, or inverted colours on a steady beat. "
                   "Each flash then fades back over a few frames. Frames are processed one at a time.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "every_n_frames": ("INT", {"default": 12, "min": 1, "max": 1000, "tooltip": "A new flash starts every this many frames."}),
                "flash_frames": ("INT", {"default": 1, "min": 1, "max": 100, "tooltip": "How many frames each flash stays at full strength."}),
                "mode": (MODES, {"default": "white", "tooltip": "Flash to white, to black, to the colour below, or to inverted colours."}),
                "strength": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How far the picture goes towards the flash. 1 is complete."}),
                "fade_out_frames": ("INT", {"default": 3, "min": 0, "max": 100, "tooltip": "The flash fades back to the normal picture over this many frames."}),
                "colour_r": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Red part of the flash colour. Used only by mode colour."}),
                "colour_g": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Green part of the flash colour. Used only by mode colour."}),
                "colour_b": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Blue part of the flash colour. Used only by mode colour."}),
                "offset": ("INT", {"default": 0, "min": 0, "max": 1000, "tooltip": "The frame where the first flash happens. 0 is the first frame."}),
            }
        }

    def run(self, images, every_n_frames, flash_frames, mode, strength, fade_out_frames,
            colour_r, colour_g, colour_b, offset):
        import torch

        if mode not in MODES:
            raise ValueError("mode must be one of: %s (got %r)" % (", ".join(MODES), mode))
        if not 0.0 <= float(strength) <= 1.0:
            raise ValueError("strength must be between 0 and 1 (got %s)" % strength)
        chans = int(images.shape[3])
        rgb = min(chans, 3)
        if mode == "white":
            target = torch.ones(rgb)
        elif mode == "black":
            target = torch.zeros(rgb)
        elif mode == "colour":
            target = torch.tensor([float(colour_r), float(colour_g), float(colour_b)])[:rgb]
        else:
            target = None
        out = torch.empty_like(images)
        for i in range(images.shape[0]):
            amount = flash_amount(i, every_n_frames, flash_frames, fade_out_frames, offset) * float(strength)
            frame = images[i]
            if amount <= 0.0:
                out[i] = frame
                continue
            colour = frame[..., :rgb].to(torch.float32)
            goal = (1.0 - colour) if target is None else target.to(colour.device)
            mixed = colour + (goal - colour) * amount
            result = frame.clone()
            result[..., :rgb] = mixed.clamp(0.0, 1.0).to(frame.dtype)
            out[i] = result
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "StrobeFlash", SYStrobeFlash)
NODE_DISPLAY_NAME_MAPPINGS["SYStrobeFlash"] = "Strobe Flash SY"
