"""Audio Beat Finder SY: finds loud hits (drum beats) in a sound and lists their times."""
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

# How much louder than its surroundings a hit must be. A window counts as a beat when its energy is above
# (running average) * (1 + (1 - sensitivity) * K). Sensitivity 1 -> factor 1 (anything above average),
# sensitivity 0 -> factor 1 + K = 5 (only very strong hits).
K = 4.0
AVERAGE_SECONDS = 1.0   # the running average looks this far to each side
QUIET = 1e-4            # windows below this energy are never beats (silence has no beats)


def energy_envelope(samples, rate, window_ms):
    """Pure function. Loudness (RMS) of consecutive, non-overlapping windows of a mono list."""
    if rate <= 0:
        raise ValueError("sample rate is %s: it must be above zero" % rate)
    if window_ms <= 0:
        raise ValueError("window is %s ms: it must be above zero" % window_ms)
    w = max(1, int(round(rate * window_ms / 1000.0)))
    env = []
    for start in range(0, len(samples), w):
        chunk = samples[start:start + w]
        env.append(math.sqrt(sum(v * v for v in chunk) / len(chunk)))
    return env


def running_average(env, half_width):
    """Pure function. Average of each value and its neighbours up to half_width windows away."""
    n = len(env)
    prefix = [0.0]
    for v in env:
        prefix.append(prefix[-1] + v)
    out = []
    for i in range(n):
        lo = max(0, i - half_width)
        hi = min(n, i + half_width + 1)
        out.append((prefix[hi] - prefix[lo]) / float(hi - lo))
    return out


def pick_peaks(env, threshold_ratio, min_gap_windows, half_width=None):
    """Pure function. Indices of beats: local maxima above running_average * threshold_ratio and above QUIET.
    The very first window counts too (a click at time 0 is a beat). Beats closer than min_gap_windows
    are merged: the stronger one stays."""
    if threshold_ratio < 1.0:
        raise ValueError("threshold ratio is %s: it must be 1 or more" % threshold_ratio)
    n = len(env)
    if n == 0:
        return []
    if half_width is None:
        half_width = max(1, n // 2)
    avg = running_average(env, half_width)
    gap = max(1, int(min_gap_windows))
    kept = []
    for i in range(n):
        v = env[i]
        left = env[i - 1] if i > 0 else -1.0
        right = env[i + 1] if i < n - 1 else -1.0
        if v < QUIET or v < left or v <= right or v <= avg[i] * threshold_ratio:
            continue
        if kept and i - kept[-1] < gap:
            if v > env[kept[-1]]:
                kept[-1] = i
            continue
        kept.append(i)
    return kept


def threshold_for(sensitivity):
    """Pure function. The ratio used by pick_peaks for a sensitivity of 0..1."""
    if sensitivity < 0 or sensitivity > 1:
        raise ValueError("sensitivity is %s: use a number from 0 to 1" % sensitivity)
    return 1.0 + (1.0 - sensitivity) * K


def times_to_frames(times, fps):
    """Pure function. Seconds to frame numbers (rounded to the nearest frame)."""
    if fps <= 0:
        raise ValueError("fps is %s: it must be above zero" % fps)
    return [int(round(t * fps)) for t in times]


def find_beats(env, rate, window_ms, sensitivity, min_gap_seconds, max_beats):
    """Pure function. Beat times in seconds from an energy envelope."""
    window_s = window_ms / 1000.0
    half = max(1, int(round(AVERAGE_SECONDS / window_s)))
    gap = max(1, int(math.ceil(min_gap_seconds / window_s)))
    idx = pick_peaks(env, threshold_for(sensitivity), gap, half)
    return [i * window_s for i in idx[:max_beats]]


class SYAudioBeatFinder:
    DESCRIPTION = ("Finds loud hits in a sound, such as drum beats, and lists their times in seconds and as video frame "
                   "numbers. Stereo is mixed to mono first. A hit in the very first window is counted.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("beat_times", "beat_frames", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to search for beats."}),
                "sensitivity": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Higher finds more, weaker beats. Lower finds only the strongest hits."}),
                "min_gap_seconds": ("FLOAT", {"default": 0.25, "min": 0.05, "max": 5.0, "step": 0.01, "tooltip": "Beats closer together than this are counted once."}),
                "window_ms": ("INT", {"default": 20, "min": 5, "max": 200, "step": 1, "tooltip": "Size of each listening slice in milliseconds. Smaller is more exact in time."}),
                "max_beats": ("INT", {"default": 1000, "min": 1, "max": 10000, "step": 1, "tooltip": "Stop after this many beats."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 240.0, "step": 0.01, "tooltip": "Frames per second of your video. Used to turn beat times into frame numbers."}),
            }
        }

    def run(self, audio, sensitivity, min_gap_seconds, window_ms, max_beats, fps):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if min_gap_seconds < 0.05:
            raise ValueError("min_gap_seconds is %s: use 0.05 or more" % min_gap_seconds)
        mono = audio["waveform"][0].float().mean(dim=0)
        w = max(1, int(round(rate * window_ms / 1000.0)))
        pad = (-n) % w
        if pad:
            # the last short window is averaged over its real length only
            body = mono[: n - (n % w)]
            tail = mono[n - (n % w):]
            parts = []
            if body.numel():
                parts.append(body.reshape(-1, w).pow(2).mean(dim=1).sqrt())
            parts.append(tail.pow(2).mean().sqrt().reshape(1))
            env = torch.cat(parts)
        else:
            env = mono.reshape(-1, w).pow(2).mean(dim=1).sqrt()
        times = find_beats(env.tolist(), rate, w * 1000.0 / rate, sensitivity, min_gap_seconds, max_beats)
        frames = times_to_frames(times, fps)
        return (", ".join("%.3f" % t for t in times), ", ".join(str(f) for f in frames), len(times))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioBeatFinder", SYAudioBeatFinder)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioBeatFinder"] = "Audio Beat Finder SY"
