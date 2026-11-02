"""Deflicker SY: evens out brightness jumps between frames."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def smooth_targets(means, window):
    """Pure function. Moving average of `means`, using `window` frames each side (fewer at the ends)."""
    window = int(window)
    if window < 1:
        raise ValueError("window must be at least 1, got %d" % window)
    n = len(means)
    out = []
    for i in range(n):
        lo, hi = max(0, i - window), min(n, i + window + 1)
        seg = means[lo:hi]
        out.append(sum(seg) / len(seg))
    return out


def gains_for(means, window, strength):
    """Pure function. Per-frame brightness factor: target/mean, clamped to 0.5..2, blended by strength."""
    s = float(strength)
    if not (0.0 <= s <= 1.0):
        raise ValueError("strength must be between 0 and 1, got %r" % strength)
    if int(window) == 1:
        return [1.0 for _ in means]
    targets = smooth_targets(means, window)
    gains = []
    for m, t in zip(means, targets):
        g = 1.0 if m <= 1e-6 else min(2.0, max(0.5, t / m))
        gains.append(1.0 + (g - 1.0) * s)
    return gains


def deflicker_info(gains):
    biggest = max((abs(g - 1.0) for g in gains), default=0.0) * 100.0
    return "Biggest correction: %.1f percent" % biggest


class SYDeflicker:
    DESCRIPTION = ("Evens out brightness jumps between frames. Each frame is pulled toward the "
                   "smoothed average brightness of its neighbours.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The clip as a batch of frames."}),
                "window": ("INT", {"default": 5, "min": 1, "max": 31, "tooltip": "Frames on each side used for the smooth average. 1 changes nothing."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "How far to move toward the smooth value. 0 changes nothing."}),
                "keep_colour": ("BOOLEAN", {"default": True, "tooltip": "On: all colours change by the same factor. Off: each colour is evened out alone."}),
            }
        }

    def run(self, images, window, strength, keep_colour=True):
        import torch
        n = int(images.shape[0])
        if n < 1:
            raise ValueError("the batch is empty: connect at least one frame")
        rgb = min(int(images.shape[3]), 3)
        out = images.clone()
        all_gains = []
        if keep_colour:
            means = images[..., :rgb].reshape(n, -1).mean(dim=1).tolist()
            all_gains = gains_for(means, window, strength)
            g = torch.tensor(all_gains, dtype=images.dtype, device=images.device).view(n, 1, 1, 1)
            out[..., :rgb] = (images[..., :rgb] * g).clamp(0.0, 1.0)
        else:
            for ch in range(rgb):
                means = images[..., ch].reshape(n, -1).mean(dim=1).tolist()
                gl = gains_for(means, window, strength)
                all_gains.extend(gl)
                g = torch.tensor(gl, dtype=images.dtype, device=images.device).view(n, 1, 1)
                out[..., ch] = (images[..., ch] * g).clamp(0.0, 1.0)
        return (out, deflicker_info(all_gains))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Deflicker", SYDeflicker)
