"""Audio Info SY: reads facts about a sound (length, sample rate, channels, loudness)."""
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

SILENCE_DB = -120.0


def level_to_db(x):
    """Pure function. Plain level to decibels; silence gives -120, never an error."""
    x = abs(float(x))
    if x <= 1e-6:
        return SILENCE_DB
    return max(SILENCE_DB, 20.0 * math.log10(x))


def channel_name(n):
    """Pure function. 1 = mono, 2 = stereo, anything else 'N channels'."""
    if n < 1:
        raise ValueError("channel count is %s: it must be 1 or more" % n)
    if n == 1:
        return "mono"
    if n == 2:
        return "stereo"
    return "%d channels" % n


def format_report(seconds, rate, channels, peak_db, rms_db):
    """Pure function. One readable line."""
    return "%.2f s, %d Hz, %s, peak %.1f dB, average %.1f dB" % (seconds, rate, channel_name(channels), peak_db, rms_db)


def stats_of_list(samples):
    """Pure function. (peak_db, rms_db) of a plain list of samples."""
    if not samples:
        raise ValueError("no samples to measure")
    peak = max(abs(v) for v in samples)
    rms = math.sqrt(sum(v * v for v in samples) / len(samples))
    return level_to_db(peak), level_to_db(rms)


class SYAudioInfo:
    DESCRIPTION = ("Reads facts about a sound: length in seconds, sample rate, channels, number of samples, "
                   "loudest peak and average loudness in dB. A silent sound reports -120 dB.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "INT", "INT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("seconds", "sample_rate", "channels", "samples", "peak_db", "rms_db", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO", {"tooltip": "The sound to measure."})}}

    def run(self, audio):
        _b, c, n, rate = check_audio(audio)
        wave = audio["waveform"].float()
        peak_db = level_to_db(float(wave.abs().max().item()))
        rms_db = level_to_db(float(wave.pow(2).mean().sqrt().item()))
        seconds = n / float(rate)
        return (seconds, rate, int(c), int(n), peak_db, rms_db, format_report(seconds, rate, c, peak_db, rms_db))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioInfo", SYAudioInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioInfo"] = "Audio Info SY"
