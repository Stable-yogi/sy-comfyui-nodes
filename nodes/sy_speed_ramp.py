"""Speed Ramp SY: changes playback speed over time by resampling frames along a curve."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CURVES = ["linear", "ease in", "ease out", "ease in out"]


def _shape(t, curve):
    t = min(1.0, max(0.0, t))
    if curve == "linear":
        return t
    if curve == "ease in":
        return t * t
    if curve == "ease out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    if curve == "ease in out":
        return t * t * (3.0 - 2.0 * t)
    raise ValueError("curve must be one of %s, got %r" % (", ".join(CURVES), curve))


def ramp_positions(count, start_speed, end_speed, curve):
    """Pure function. Source frame positions (floats, 0..count-1) to read, one per output frame.
    The speed at each step moves from start_speed to end_speed along the curve, measured over the clip."""
    count = int(count)
    if count < 2:
        raise ValueError("Speed Ramp needs at least 2 frames, got %d" % count)
    for name, v in (("start_speed", start_speed), ("end_speed", end_speed)):
        if not (0.1 <= float(v) <= 8.0):
            raise ValueError("%s must be between 0.1 and 8, got %r" % (name, v))
    _shape(0.0, curve)
    last = count - 1
    pos = 0.0
    out = []
    while pos <= last + 1e-9 and len(out) < 100000:
        out.append(min(float(last), pos))
        speed = float(start_speed) + (float(end_speed) - float(start_speed)) * _shape(pos / last, curve)
        pos += speed
    return out


def ramp_info(count, n_out, start_speed, end_speed):
    return "%d frames -> %d frames, speed %.1f to %.1f" % (count, n_out, start_speed, end_speed)


class SYSpeedRamp:
    DESCRIPTION = ("Changes how fast a clip plays over time, for example slow motion that speeds up. "
                   "It picks frames along a speed curve and can mix the two nearest frames for smooth motion.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The clip as a batch of frames. It needs at least 2 frames."}),
                "start_speed": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 8.0, "step": 0.05, "tooltip": "Playback speed at the start. 1 is normal, 0.5 is half speed."}),
                "end_speed": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 8.0, "step": 0.05, "tooltip": "Playback speed at the end. 2 is twice as fast."}),
                "curve": (CURVES, {"default": "linear", "tooltip": "How the speed moves from the start value to the end value."}),
                "blend": ("BOOLEAN", {"default": True, "tooltip": "On: mix the two nearest frames. Off: take the nearest single frame."}),
            }
        }

    def run(self, images, start_speed, end_speed, curve, blend=True):
        import torch
        count = int(images.shape[0])
        pos = ramp_positions(count, start_speed, end_speed, curve)
        p = torch.tensor(pos, dtype=torch.float32)
        if blend:
            lo = torch.floor(p).long().clamp(0, count - 1)
            hi = (lo + 1).clamp(max=count - 1)
            w = (p - lo.to(torch.float32)).view(-1, 1, 1, 1).to(images.dtype)
            out = images[lo] * (1.0 - w) + images[hi] * w
        else:
            out = images[torch.round(p).long().clamp(0, count - 1)]
        return (out, ramp_info(count, int(out.shape[0]), start_speed, end_speed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SpeedRamp", SYSpeedRamp)
NODE_DISPLAY_NAME_MAPPINGS["SYSpeedRamp"] = "Speed Ramp SY"
