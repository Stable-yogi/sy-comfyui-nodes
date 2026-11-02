"""Audio Speed Change SY: plays a sound faster or slower by resampling (pitch follows speed, like a tape)."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_audio(audio):
    """Pure function. Returns (batch, channels, samples, sample_rate) or raises ValueError."""
    if not isinstance(audio, dict) or "waveform" not in audio or "sample_rate" not in audio:
        raise ValueError("audio input is not a sound: connect an AUDIO output (for example from a Load Audio node)")
    shape = tuple(audio["waveform"].shape)
    rate = int(audio["sample_rate"])
    if len(shape) != 3:
        raise ValueError("audio has an odd shape %s: expected batch, channels, samples" % (shape,))
    if rate <= 0:
        raise ValueError("sample rate is %d: it must be above zero" % rate)
    if shape[0] < 1 or shape[1] < 1 or shape[2] < 1:
        raise ValueError("audio is empty: it needs at least one sample. Check the node that makes the sound")
    return shape[0], shape[1], shape[2], rate

METHODS = ("linear", "cubic")


def new_length(n, speed):
    """Pure function. Number of samples after the speed change (rounded, at least 1)."""
    if n < 1:
        raise ValueError("audio is empty: it needs at least one sample")
    if speed <= 0:
        raise ValueError("speed is %s: it must be above zero" % speed)
    return max(1, int(round(n / float(speed))))


def interpolate_at(samples, position, method):
    """Pure function. Value of a list of samples at a fractional position (0 = first sample).
    Positions outside the list use the nearest end sample. cubic = Catmull-Rom."""
    if method not in METHODS:
        raise ValueError("unknown method %r: pick one of %s" % (method, ", ".join(METHODS)))
    n = len(samples)
    if n == 0:
        raise ValueError("no samples to read from")
    pos = min(float(n - 1), max(0.0, float(position)))
    i1 = int(math.floor(pos))
    t = pos - i1

    def at(i):
        return samples[min(n - 1, max(0, i))]

    p1 = at(i1)
    p2 = at(i1 + 1)
    if method == "linear":
        return p1 * (1.0 - t) + p2 * t
    p0 = at(i1 - 1)
    p3 = at(i1 + 2)
    return 0.5 * (2.0 * p1 + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t
                  + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t)


def resample_list(samples, speed, method):
    """Pure function. The same job as the node, on a plain list (used by the test)."""
    m = new_length(len(samples), speed)
    return [interpolate_at(samples, i * speed, method) for i in range(m)]


class SYAudioSpeedChange:
    DESCRIPTION = ("Plays a sound faster or slower. The pitch changes with the speed, like a tape machine. "
                   "Speed 1 gives back an identical copy.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "seconds")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to speed up or slow down."}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.25, "max": 4.0, "step": 0.01, "tooltip": "2 = twice as fast and one octave higher; 0.5 = half speed and lower. 1 = unchanged."}),
                "method": (list(METHODS), {"default": "linear", "tooltip": "How in-between values are worked out. Cubic is smoother and a little slower."}),
            }
        }

    def run(self, audio, speed, method):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if method not in METHODS:
            raise ValueError("unknown method %r: pick one of %s" % (method, ", ".join(METHODS)))
        wave = audio["waveform"]
        if speed == 1.0:
            return ({"waveform": wave.clone(), "sample_rate": rate}, n / float(rate))
        m = new_length(n, speed)
        pos = (torch.arange(m, dtype=torch.float64, device=wave.device) * float(speed)).clamp(0.0, float(n - 1))
        i1 = pos.floor().long()
        t = (pos - i1.to(torch.float64)).to(wave.dtype)
        last = n - 1

        def at(k):
            return wave[..., (i1 + k).clamp(0, last)]

        p1 = at(0)
        p2 = at(1)
        if method == "linear":
            out = p1 * (1.0 - t) + p2 * t
        else:
            p0 = at(-1)
            p3 = at(2)
            out = 0.5 * (2.0 * p1 + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t
                         + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t)
        out = out.clamp(-1.0, 1.0).contiguous()
        return ({"waveform": out, "sample_rate": rate}, m / float(rate))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioSpeedChange", SYAudioSpeedChange)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioSpeedChange"] = "Audio Speed Change SY"
