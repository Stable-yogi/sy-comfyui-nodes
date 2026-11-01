"""LTX Latent Bridge SY: turns decoded video frames into an LTX-shaped latent in one step (fit size, fit frame count, VAE encode)."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
    from ._sy_a2_video import snap_frames
    from .sy_video_size_fit import fit_size
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape
    from _sy_a2_video import snap_frames
    from sy_video_size_fit import fit_size

POLICIES = ("exact", "trim", "pad", "nearest")
RESIZE_MODES = ("stretch", "crop")


def plan_bridge(width, height, count, max_megapixels=0.0, multiple_of=32, policy="trim", frame_step=8):
    """Pure function. Returns (new_width, new_height, frame_ids, note).
    Size: rounded to a multiple of multiple_of, and under max_megapixels when that is above 0.
    Frames: the count must be frame_step*n+1. exact refuses a wrong count, trim drops the extra frames from the end,
    pad repeats the last frame, nearest picks the closest valid count (cutting or repeating the last frame)."""
    width, height, count = int(width), int(height), int(count)
    step, m = int(frame_step), int(multiple_of)
    if min(width, height, count) < 1:
        raise ValueError("width, height and frame count must be at least 1, got %dx%d with %d frames" % (width, height, count))
    if step < 1 or m < 1:
        raise ValueError("frame_step and multiple_of must be at least 1")
    if policy not in POLICIES:
        raise ValueError("frame_policy must be one of %s, got %r" % (", ".join(POLICIES), policy))
    budget = float(max_megapixels)
    if budget > 0:
        w, h = fit_size(width, height, budget, m)
    else:
        w, h = max(m, int(round(width / float(m))) * m), max(m, int(round(height / float(m))) * m)
    valid = (count - 1) % step == 0
    if valid:
        target = count
    elif policy == "exact":
        raise ValueError("%d frames is not a %dn+1 count. Use frame_policy trim, pad or nearest, or send %d or %d frames."
                         % (count, step, snap_frames(count, step, "down"), snap_frames(count, step, "up")))
    elif policy == "trim":
        target = snap_frames(count, step, "down")
    elif policy == "pad":
        target = snap_frames(count, step, "up")
    else:
        target = snap_frames(count, step, "nearest")
    ids = [min(i, count - 1) for i in range(target)]
    parts = []
    if (w, h) != (width, height):
        parts.append("size %dx%d -> %dx%d" % (width, height, w, h))
    else:
        parts.append("size %dx%d kept" % (w, h))
    if target != count:
        parts.append("frames %d -> %d (%s, %dn+1)" % (count, target, "cut" if target < count else "last frame repeated", step))
    else:
        parts.append("%d frames kept" % count)
    return w, h, ids, ", ".join(parts)


def _resize(images, w, h, mode):
    import torch
    import torch.nn.functional as F
    _, ih, iw, _ = images.shape
    if (ih, iw) == (h, w):
        return images
    x = images.permute(0, 3, 1, 2)
    if mode == "crop":
        scale = max(w / float(iw), h / float(ih))
        nw, nh = max(w, int(round(iw * scale))), max(h, int(round(ih * scale)))
        x = F.interpolate(x, size=(nh, nw), mode="bilinear", align_corners=False, antialias=True)
        top, left = (nh - h) // 2, (nw - w) // 2
        x = x[:, :, top:top + h, left:left + w]
    else:
        x = F.interpolate(x, size=(h, w), mode="bilinear", align_corners=False, antialias=True)
    return torch.clamp(x.permute(0, 2, 3, 1), 0.0, 1.0)


class SYLtxLatentBridge:
    DESCRIPTION = ("Turns decoded video frames (for example from an H3 decode) into an LTX-shaped latent in one node. "
                   "It fits the size to a multiple of 32, fits the frame count to 8n+1, and encodes with the LTX VAE you connect. "
                   "The info line says what changed. Also gives the fitted frames, so you can preview them.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "IMAGE", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("latent", "images", "frames", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The decoded frames, for example the picture output of an H3 VAE Decode."}),
                "vae": ("VAE", {"tooltip": "The LTX VAE used to encode the frames."}),
                "frame_policy": (list(POLICIES), {"default": "trim", "tooltip": "When the count is not 8n+1: exact stops with an error, trim cuts, pad repeats the last frame, nearest picks the closest."}),
                "resize_mode": (list(RESIZE_MODES), {"default": "stretch", "tooltip": "stretch fills the new size (tiny shape change). crop keeps the shape and trims the edges."}),
            },
            "optional": {
                "max_pixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.01, "tooltip": "Pixel budget in megapixels. 0 is off: the size is only rounded to the multiple."}),
                "multiple_of": ("INT", {"default": 32, "min": 1, "max": 256, "tooltip": "Width and height are made a multiple of this number. LTX wants 32."}),
                "frame_step": ("INT", {"default": 8, "min": 1, "max": 64, "tooltip": "The n in the frame rule step*n+1. LTX wants 8."}),
            },
        }

    def run(self, images, vae, frame_policy, resize_mode, max_pixels=0.0, multiple_of=32, frame_step=8):
        n, h0, w0, _ = check_shape(images.shape)
        w, h, ids, note = plan_bridge(w0, h0, n, max_pixels, multiple_of, frame_policy, frame_step)
        frames = images[ids][:, :, :, :3]
        frames = _resize(frames, w, h, resize_mode)
        latent = vae.encode(frames)
        return ({"samples": latent}, frames, len(ids), w, h, note)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LtxLatentBridge", SYLtxLatentBridge)
NODE_DISPLAY_NAME_MAPPINGS["SYLtxLatentBridge"] = "LTX Latent Bridge SY"
