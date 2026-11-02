"""Audio Loop To Length SY: repeats, cuts or pads a sound to an exact length."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("loop", "loop then fade out", "cut or pad with silence")
FINAL_FADE_SECONDS = 1.0


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


def loop_plan(clip_len, target_len, crossfade_len):
    """Pure function. Segments (src_start, src_end, dst_start, fade_len) that build `target_len` samples.
    fade_len = how many samples at the start of the segment blend with what is already there.
    The crossfade is limited to half the clip."""
    if clip_len < 1:
        raise ValueError("audio is empty: it needs at least one sample")
    if target_len < 1:
        raise ValueError("target length must be at least 1 sample: raise seconds")
    if crossfade_len < 0:
        raise ValueError("crossfade cannot be negative: use 0 or more seconds")
    cf = min(int(crossfade_len), clip_len // 2)
    if target_len <= clip_len:
        return [(0, target_len, 0, 0)]
    step = clip_len - cf
    plan = [(0, clip_len, 0, 0)]
    dst = 0
    covered = clip_len
    while covered < target_len:
        dst += step
        seg = min(clip_len, target_len - dst)
        plan.append((0, seg, dst, cf))
        covered = dst + seg
    return plan


def final_fade_len(target_len, rate):
    """Pure function. Length in samples of the closing fade: 1 second, at most half the result."""
    return min(int(round(FINAL_FADE_SECONDS * rate)), target_len // 2)


class SYAudioLoopToLength:
    DESCRIPTION = ("Makes a sound exactly as long as you ask: repeats it with a soft crossfade, optionally fades the end, "
                   "or simply cuts / pads with silence.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to repeat, cut or pad."}),
                "seconds": ("FLOAT", {"default": 10.0, "min": 0.1, "max": 3600.0, "step": 0.1, "tooltip": "Exact length of the result in seconds."}),
                "crossfade_seconds": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 5.0, "step": 0.01, "tooltip": "Overlap blended at each loop join. Limited to half the clip."}),
                "mode": (list(MODES), {"default": "loop", "tooltip": "Loop repeats the sound. Loop then fade out closes with a 1 s fade. The last cuts or pads with silence."}),
            }
        }

    def run(self, audio, seconds, crossfade_seconds, mode):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if seconds <= 0 or crossfade_seconds < 0:
            raise ValueError("seconds must be above 0 and crossfade_seconds 0 or more")
        if mode not in MODES:
            raise ValueError("unknown mode %r: pick one of %s" % (mode, ", ".join(MODES)))
        wave = audio["waveform"]
        target = max(1, int(round(seconds * rate)))
        out = torch.zeros(wave.shape[0], wave.shape[1], target, dtype=wave.dtype, device=wave.device)
        if mode == "cut or pad with silence":
            plan = loop_plan(n, min(n, target), 0)
        else:
            plan = loop_plan(n, target, int(round(crossfade_seconds * rate)))
        for s0, s1, d0, fade in plan:
            piece = wave[..., s0:s1]
            length = s1 - s0
            if fade > 0:
                f = min(fade, length)
                ramp = torch.linspace(0.0, 1.0, f + 2, dtype=wave.dtype, device=wave.device)[1:-1]
                out[..., d0:d0 + f] = out[..., d0:d0 + f] * (1.0 - ramp) + piece[..., :f] * ramp
                out[..., d0 + f:d0 + length] = piece[..., f:]
            else:
                out[..., d0:d0 + length] = piece
        if mode == "loop then fade out":
            f = final_fade_len(target, rate)
            if f > 0:
                ramp = torch.linspace(1.0, 0.0, f, dtype=wave.dtype, device=wave.device)
                out[..., target - f:] = out[..., target - f:] * ramp
        return ({"waveform": out.clamp(-1.0, 1.0), "sample_rate": rate},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioLoopToLength", SYAudioLoopToLength)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioLoopToLength"] = "Audio Loop To Length SY"
