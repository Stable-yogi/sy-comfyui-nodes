"""Audio Normalise SY: makes a sound louder or quieter so it reaches a target level."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("peak", "average (RMS)")


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


def peak_of(values):
    """Pure function. Loudest absolute value in a flat list."""
    return max((abs(v) for v in values), default=0.0)


def rms_of(values):
    """Pure function. Root-mean-square level of a flat list."""
    if not values:
        return 0.0
    return math.sqrt(sum(v * v for v in values) / len(values))


def gain_for(measure_linear, target_db, max_gain_db):
    """Pure function. Gain in dB that brings `measure_linear` to `target_db`, never above `max_gain_db`.
    Silent audio (measure 0) gets 0 dB."""
    if measure_linear < 0:
        raise ValueError("level cannot be negative")
    if max_gain_db < 0:
        raise ValueError("max_gain_db cannot be negative: use 0 or more")
    if measure_linear <= 0.0:
        return 0.0
    gain = target_db - 20.0 * math.log10(measure_linear)
    return min(gain, float(max_gain_db))


class SYAudioNormalise:
    DESCRIPTION = ("Makes a sound louder or quieter so its loudest point (peak) or its average loudness (RMS) hits a target. "
                   "Silent sound is left alone. Nothing is ever pushed past full scale.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "gain_db")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to adjust."}),
                "target_db": ("FLOAT", {"default": -1.0, "min": -60.0, "max": 0.0, "step": 0.1, "tooltip": "Level to reach in dB. 0 is the loudest possible; -1 leaves a little room."}),
                "mode": (list(MODES), {"default": "peak", "tooltip": "Peak aims the loudest moment at the target. Average (RMS) aims the overall loudness."}),
                "max_gain_db": ("FLOAT", {"default": 30.0, "min": 0.0, "max": 60.0, "step": 0.5, "tooltip": "Most the sound may be made louder, so quiet hiss is not blown up."}),
            }
        }

    def run(self, audio, target_db, mode, max_gain_db):
        import torch
        check_audio(audio)
        if mode not in MODES:
            raise ValueError("unknown mode %r: pick one of %s" % (mode, ", ".join(MODES)))
        wave = audio["waveform"]
        rate = int(audio["sample_rate"])
        if mode == "peak":
            measure = float(wave.abs().max())
        else:
            measure = float(torch.sqrt((wave.double() ** 2).mean()))
        gain_db = gain_for(measure, target_db, max_gain_db)
        if measure <= 0.0:
            return ({"waveform": wave.clone(), "sample_rate": rate}, 0.0)
        out = (wave * (10.0 ** (gain_db / 20.0))).clamp(-1.0, 1.0)
        return ({"waveform": out, "sample_rate": rate}, float(gain_db))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioNormalise", SYAudioNormalise)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioNormalise"] = "Audio Normalise SY"
