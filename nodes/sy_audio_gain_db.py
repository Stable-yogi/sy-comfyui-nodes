"""Audio Gain dB SY: makes a sound louder or quieter by a number of decibels, never clipping silently."""
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

LIMITS = ("clamp", "soft limit")
SILENCE_DB = -120.0
KNEE = 0.5


def db_to_gain(db):
    """Pure function. Decibels to a plain multiplier (0 dB = 1.0, +6 dB about 2.0)."""
    return 10.0 ** (float(db) / 20.0)


def gain_to_db(x):
    """Pure function. Plain level (0..) to decibels. Silence and anything below -120 dB gives -120."""
    x = abs(float(x))
    if x <= 1e-6:
        return SILENCE_DB
    return max(SILENCE_DB, 20.0 * math.log10(x))


def soft_limit(x):
    """Pure function. Squeezes peaks smoothly. Up to 0.5 the sound is left exactly as it is; above that
    the level bends towards 1 along a tanh curve, so the result is always below 1. Odd and rising."""
    a = abs(x)
    if a <= KNEE:
        return x
    y = KNEE + (1.0 - KNEE) * math.tanh((a - KNEE) / (1.0 - KNEE))
    return y if x > 0 else -y


class SYAudioGainDb:
    DESCRIPTION = ("Makes a sound louder or quieter in decibels. Peaks above full scale are either cut flat (clamp) "
                   "or squeezed gently (soft limit). Also tells you the loudest peak of the result.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "peak_after_db")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to change."}),
                "gain_db": ("FLOAT", {"default": 0.0, "min": -60.0, "max": 60.0, "step": 0.1, "tooltip": "Change in loudness. +6 is about twice as loud, -6 about half. 0 = unchanged."}),
                "limit": (list(LIMITS), {"default": "clamp", "tooltip": "What happens to peaks above full scale. Clamp cuts them flat; soft limit rounds them off gently."}),
            }
        }

    def run(self, audio, gain_db, limit):
        import torch
        check_audio(audio)
        if limit not in LIMITS:
            raise ValueError("unknown limit %r: pick one of %s" % (limit, ", ".join(LIMITS)))
        wave = audio["waveform"] * db_to_gain(gain_db)
        if limit == "soft limit":
            a = wave.abs()
            squeezed = KNEE + (1.0 - KNEE) * torch.tanh((a - KNEE) / (1.0 - KNEE))
            wave = torch.where(a <= KNEE, wave, torch.sign(wave) * squeezed)
        wave = wave.clamp(-1.0, 1.0).contiguous()
        peak = float(wave.abs().max().item())
        return ({"waveform": wave, "sample_rate": int(audio["sample_rate"])}, gain_to_db(peak))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioGainDb", SYAudioGainDb)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioGainDb"] = "Audio Gain dB SY"
