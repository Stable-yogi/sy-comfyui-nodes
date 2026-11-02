"""Crossfade Slideshow SY: turns a batch of pictures into video frames. Each picture holds, then fades into the next."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_plan_args(n, hold, fade):
    if int(n) < 1:
        raise ValueError("need at least 1 picture, got %d" % int(n))
    if int(hold) < 1:
        raise ValueError("hold_frames must be at least 1, got %d" % int(hold))
    if int(fade) < 0:
        raise ValueError("fade_frames cannot be negative, got %d" % int(fade))
    if int(fade) > int(hold):
        raise ValueError("fade_frames (%d) must not be bigger than hold_frames (%d). Lower the fade or raise the hold" % (int(fade), int(hold)))


def plan_frames(n, hold, fade, loop=False):
    """Pure function. List of (index_a, index_b, mix 0..1). mix 0 = all a, 1 = all b. Fade frames never reach 0 or 1."""
    check_plan_args(n, hold, fade)
    n, hold, fade = int(n), int(hold), int(fade)
    out = []
    for i in range(n):
        out.extend([(i, i, 0.0)] * hold)
        last = i == n - 1
        if last and not loop:
            break
        nxt = (i + 1) % n
        for k in range(fade):
            out.append((i, nxt, (k + 1) / float(fade + 1)))
    return out


def frame_count(n, hold, fade, loop=False):
    """Pure function. How many frames plan_frames makes."""
    check_plan_args(n, hold, fade)
    return int(n) * int(hold) + (int(n) if loop else int(n) - 1) * int(fade)


def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def eased_mix(mix, ease=True):
    """Pure function. Smoothstep curve on the mix when ease is on."""
    return smoothstep(mix) if ease else mix


def slideshow_info(n, hold, fade, loop, total):
    return "Crossfade Slideshow: %d pictures, hold %d, fade %d%s -> %d frames" % (n, hold, fade, ", looping" if loop else "", total)


class SYCrossfadeSlideshow:
    DESCRIPTION = ("Turns a batch of same-sized pictures into video frames. Every picture stays still for a while, "
                   "then melts into the next one. Optionally melts from the last back to the first for a seamless loop.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("frames", "frame_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The slides. Each picture in the batch is one slide. They must all be the same size."}),
                "hold_frames": ("INT", {"default": 24, "min": 1, "max": 10000, "tooltip": "How many frames each slide stays still."}),
                "fade_frames": ("INT", {"default": 12, "min": 0, "max": 10000, "tooltip": "Frames of cross-fade between two slides. Not more than hold_frames."}),
                "loop": ("BOOLEAN", {"default": False, "tooltip": "On: also fade from the last slide back to the first."}),
            },
            "optional": {
                "ease": ("BOOLEAN", {"default": True, "tooltip": "On: the fade starts and ends gently instead of at a steady speed."}),
            },
        }

    def run(self, images, hold_frames, fade_frames, loop, ease=True):
        import torch

        if images.ndim != 4:
            raise ValueError("images must be shaped [batch, height, width, channels], got %s" % (tuple(images.shape),))
        n = int(images.shape[0])
        plan = plan_frames(n, hold_frames, fade_frames, loop)
        frames = []
        for a, b, mix in plan:
            if a == b:
                frames.append(images[a])
            else:
                m = eased_mix(mix, ease)
                frames.append(images[a].to(torch.float32) * (1.0 - m) + images[b].to(torch.float32) * m)
        out = torch.stack(frames, 0).to(images.dtype)
        return (out, len(plan), slideshow_info(n, hold_frames, fade_frames, loop, len(plan)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CrossfadeSlideshow", SYCrossfadeSlideshow)
NODE_DISPLAY_NAME_MAPPINGS["SYCrossfadeSlideshow"] = "Crossfade Slideshow SY"
