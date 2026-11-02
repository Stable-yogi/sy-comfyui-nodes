"""Audio Fade SY: fades a sound in at the start and out at the end."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CURVES = ("linear", "smooth", "exponential")


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


def _shape(x, curve):
    """x in 0..1 -> 0..1 rising."""
    x = min(1.0, max(0.0, x))
    if curve == "linear":
        return x
    if curve == "smooth":
        return x * x * (3.0 - 2.0 * x)
    if curve == "exponential":
        k = 5.0
        return (math.exp(k * x) - 1.0) / (math.exp(k) - 1.0)
    raise ValueError("unknown curve %r: pick one of %s" % (curve, ", ".join(CURVES)))


def effective_fades(total_seconds, fade_in, fade_out):
    """Pure function. Limits fades to the clip; if they overlap, scales both down in proportion."""
    if fade_in < 0 or fade_out < 0:
        raise ValueError("fade times cannot be negative: use 0 or more seconds")
    fi = float(fade_in)
    fo = float(fade_out)
    if fi + fo > total_seconds and fi + fo > 0:
        s = total_seconds / (fi + fo)
        fi *= s
        fo *= s
    return fi, fo


def fade_gain(position_seconds, total_seconds, fade_in, fade_out, curve):
    """Pure function. Gain 0..1 at one moment of the clip."""
    if curve not in CURVES:
        raise ValueError("unknown curve %r: pick one of %s" % (curve, ", ".join(CURVES)))
    if total_seconds <= 0:
        return 1.0
    fi, fo = effective_fades(total_seconds, fade_in, fade_out)
    g = 1.0
    if fi > 0 and position_seconds < fi:
        g *= _shape(position_seconds / fi, curve)
    if fo > 0 and position_seconds > total_seconds - fo:
        g *= _shape((total_seconds - position_seconds) / fo, curve)
    return min(1.0, max(0.0, g))


def fade_regions(n, rate, fade_in, fade_out, curve):
    """Pure function. Returns (head, tail_start, tail): gains for the first samples and for the last ones.
    First and last sample sit at 0 and (n-1)/rate, so a fade really reaches silence."""
    if n < 1 or rate <= 0:
        raise ValueError("audio is empty or its sample rate is zero")
    total = (n - 1) / float(rate)
    fi, fo = effective_fades(total, fade_in, fade_out)
    head_len = min(n, int(math.ceil(fi * rate)) + 1) if fi > 0 else 0
    tail_len = min(n, int(math.ceil(fo * rate)) + 1) if fo > 0 else 0
    head = [fade_gain(i / float(rate), total, fade_in, fade_out, curve) for i in range(head_len)]
    tail_start = n - tail_len
    tail = [fade_gain(i / float(rate), total, fade_in, fade_out, curve) for i in range(tail_start, n)]
    return head, tail_start, tail


class SYAudioFade:
    DESCRIPTION = ("Fades a sound in at the start and out at the end. Pick a straight, smooth or fast-rising curve. "
                   "If the two fades would overlap they shrink in proportion.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to fade."}),
                "fade_in_seconds": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 60.0, "step": 0.01, "tooltip": "How long the sound takes to rise from silence. 0 = no fade in."}),
                "fade_out_seconds": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 60.0, "step": 0.01, "tooltip": "How long the sound takes to sink to silence at the end. 0 = no fade out."}),
                "curve": (list(CURVES), {"default": "smooth", "tooltip": "Shape of the fade. Smooth eases at both ends; exponential rises slowly then quickly."}),
            }
        }

    def run(self, audio, fade_in_seconds, fade_out_seconds, curve):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if fade_in_seconds < 0 or fade_out_seconds < 0:
            raise ValueError("fade times cannot be negative: use 0 or more seconds")
        wave = audio["waveform"].clone()
        if n > 1:
            head, tail_start, tail = fade_regions(n, rate, fade_in_seconds, fade_out_seconds, curve)
            if head:
                h = torch.tensor(head, dtype=wave.dtype, device=wave.device)
                wave[..., :len(head)] = wave[..., :len(head)] * h
            if tail:
                t = torch.tensor(tail, dtype=wave.dtype, device=wave.device)
                wave[..., tail_start:] = wave[..., tail_start:] * t
        wave = wave.clamp(-1.0, 1.0)
        return ({"waveform": wave, "sample_rate": rate},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioFade", SYAudioFade)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioFade"] = "Audio Fade SY"
