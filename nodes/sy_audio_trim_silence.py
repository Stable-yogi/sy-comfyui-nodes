"""Audio Trim Silence SY: cuts quiet parts off the start and/or end of a sound."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

TRIMS = ("both", "start", "end")
WINDOW_SECONDS = 0.01


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


def find_keep_range(levels, threshold_linear, pad_samples, trim, window_len=1, total_len=None):
    """Pure function. `levels` = peak level of each window (each `window_len` samples long).
    Returns (start, end) in samples to keep. All windows quiet -> (0, 0)."""
    if trim not in TRIMS:
        raise ValueError("unknown trim %r: pick one of %s" % (trim, ", ".join(TRIMS)))
    if window_len < 1:
        raise ValueError("window length must be at least 1 sample")
    if pad_samples < 0:
        raise ValueError("pad cannot be negative: use 0 or more seconds")
    if total_len is None:
        total_len = len(levels) * window_len
    loud = [i for i, v in enumerate(levels) if v > threshold_linear]
    if not loud:
        return (0, 0)
    start = max(0, loud[0] * window_len - pad_samples)
    end = min(total_len, (loud[-1] + 1) * window_len + pad_samples)
    if trim == "start":
        end = total_len
    elif trim == "end":
        start = 0
    return (start, end)


def enforce_min_keep(start, end, total_len, min_keep_len, silent):
    """Pure function. Makes sure at least `min_keep_len` samples stay (never more than the clip has).
    All-silent audio keeps that much from the start."""
    min_keep_len = min(max(1, min_keep_len), total_len)
    if silent:
        return (0, min_keep_len)
    if end - start >= min_keep_len:
        return (start, end)
    end = min(total_len, start + min_keep_len)
    start = max(0, end - min_keep_len)
    return (start, end)


class SYAudioTrimSilence:
    DESCRIPTION = ("Cuts quiet stretches off the start and/or end of a sound, keeping a little padding. "
                   "Tells you how many seconds were removed. All-silent sound keeps a short piece from the start.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO", "FLOAT")
    RETURN_NAMES = ("audio", "trimmed_seconds")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to trim."}),
                "threshold_db": ("FLOAT", {"default": -50.0, "min": -90.0, "max": -10.0, "step": 1.0, "tooltip": "Anything quieter than this counts as silence. Higher (like -30) trims more."}),
                "pad_seconds": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 5.0, "step": 0.01, "tooltip": "Silence to leave around the sound so the edges are not cut hard."}),
                "trim": (list(TRIMS), {"default": "both", "tooltip": "Cut the silence at the start, at the end, or both."}),
                "min_keep_seconds": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 10.0, "step": 0.01, "tooltip": "The result is never shorter than this, even if everything is quiet."}),
            }
        }

    def run(self, audio, threshold_db, pad_seconds, trim, min_keep_seconds):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if pad_seconds < 0 or min_keep_seconds <= 0:
            raise ValueError("pad_seconds must be 0 or more and min_keep_seconds above 0")
        wave = audio["waveform"]
        win = max(1, int(round(WINDOW_SECONDS * rate)))
        peak = wave.abs().amax(dim=(0, 1))  # per sample, loudest over batch and channels
        extra = (-n) % win
        if extra:
            peak = torch.nn.functional.pad(peak, (0, extra))
        levels = peak.reshape(-1, win).amax(dim=1).tolist()
        threshold = 10.0 ** (threshold_db / 20.0)
        start, end = find_keep_range(levels, threshold, int(round(pad_seconds * rate)), trim, win, n)
        silent = (start, end) == (0, 0)
        start, end = enforce_min_keep(start, end, n, int(round(min_keep_seconds * rate)), silent)
        out = wave[..., start:end].clone()
        return ({"waveform": out, "sample_rate": rate}, float((n - (end - start)) / rate))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioTrimSilence", SYAudioTrimSilence)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioTrimSilence"] = "Audio Trim Silence SY"
