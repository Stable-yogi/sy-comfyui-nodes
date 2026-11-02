"""Audio Mix SY: lays one sound over another."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LENGTHS = ("longest", "length of A", "length of B placed")


def check_audio(audio, label="audio"):
    """Pure function. Returns (batch, channels, samples, sample_rate) or raises ValueError."""
    if not isinstance(audio, dict) or "waveform" not in audio or "sample_rate" not in audio:
        raise ValueError("%s is not a sound: connect an AUDIO output (for example from a Load Audio node)" % label)
    shape = tuple(audio["waveform"].shape)
    rate = int(audio["sample_rate"])
    if len(shape) != 3:
        raise ValueError("%s has an odd shape %s: expected batch, channels, samples" % (label, (shape,)))
    if rate <= 0:
        raise ValueError("%s has sample rate %d: it must be above zero" % (label, rate))
    if shape[0] < 1 or shape[1] < 1 or shape[2] < 1:
        raise ValueError("%s is empty: it needs at least one sample. Check the node that makes the sound" % label)
    if shape[1] > 2:
        raise ValueError("%s has %d channels: only mono and stereo can be mixed. Convert it to stereo first" % (label, shape[1]))
    return shape[0], shape[1], shape[2], rate


def mix_plan(len_a, len_b, b_start, mode):
    """Pure function. Returns (total_len, b_offset) in samples."""
    if len_a < 1 or len_b < 1:
        raise ValueError("audio is empty: both sounds need at least one sample")
    if b_start < 0:
        raise ValueError("b_start_seconds cannot be negative: use 0 or more")
    if mode not in LENGTHS:
        raise ValueError("unknown length %r: pick one of %s" % (mode, ", ".join(LENGTHS)))
    end_b = b_start + len_b
    if mode == "longest":
        return (max(len_a, end_b), b_start)
    if mode == "length of A":
        return (len_a, b_start)
    return (end_b, b_start)


def batch_for(ba, bb):
    """Pure function. Batch size of the result: equal sizes, or one of them is 1."""
    if ba == bb or bb == 1:
        return ba
    if ba == 1:
        return bb
    raise ValueError("the two sounds hold %d and %d clips in a batch: use equal counts, or 1 for one of them" % (ba, bb))


def clip_scale(peak, enabled):
    """Pure function. Factor that keeps the mix inside full scale (1.0 if not needed or turned off)."""
    if enabled and peak > 1.0:
        return 1.0 / peak
    return 1.0


class SYAudioMix:
    DESCRIPTION = ("Lays sound B over sound A with a volume for each and an optional delay for B. "
                   "Different sample rates and mono / stereo are matched for you.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_a": ("AUDIO", {"tooltip": "The base sound. Its sample rate is the one used for the result."}),
                "audio_b": ("AUDIO", {"tooltip": "The sound laid over A. A different sample rate is resampled to A's rate (linear)."}),
                "volume_a": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 4.0, "step": 0.01, "tooltip": "Volume of A. 1 = unchanged, 0 = silent."}),
                "volume_b": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 4.0, "step": 0.01, "tooltip": "Volume of B. 1 = unchanged, 0 = silent."}),
                "b_start_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.01, "tooltip": "When B begins, counted from the start of A."}),
                "length": (list(LENGTHS), {"default": "longest", "tooltip": "Length of the result: the longest of the two, A's length, or until B ends."}),
                "prevent_clipping": ("BOOLEAN", {"default": True, "tooltip": "On: if the mix would pass full scale, turn the whole mix down. Off: hard limit."}),
            }
        }

    def run(self, audio_a, audio_b, volume_a, volume_b, b_start_seconds, length, prevent_clipping):
        import torch
        ba, ca, na, rate = check_audio(audio_a, "audio_a")
        bb, cb, nb, rate_b = check_audio(audio_b, "audio_b")
        if volume_a < 0 or volume_b < 0 or b_start_seconds < 0:
            raise ValueError("volumes and b_start_seconds cannot be negative")
        batch = batch_for(ba, bb)
        wa = audio_a["waveform"]
        wb = audio_b["waveform"]
        if rate_b != rate:
            new_len = max(1, int(round(nb * rate / float(rate_b))))
            flat = wb.reshape(bb * cb, 1, nb).float()
            flat = torch.nn.functional.interpolate(flat, size=new_len, mode="linear", align_corners=False)
            wb = flat.reshape(bb, cb, new_len).to(wa.dtype)
            nb = new_len
        if ca != cb:  # mono is repeated to stereo
            if ca == 1:
                wa = wa.repeat(1, 2, 1)
            else:
                wb = wb.repeat(1, 2, 1)
        channels = wa.shape[1]
        total, offset = mix_plan(na, nb, int(round(b_start_seconds * rate)), length)
        out = torch.zeros(batch, channels, total, dtype=wa.dtype, device=wa.device)
        take_a = min(na, total)
        out[..., :take_a] += wa[..., :take_a].expand(batch, channels, take_a) * volume_a
        if offset < total:
            take_b = min(nb, total - offset)
            out[..., offset:offset + take_b] += wb[..., :take_b].to(wa.device).expand(batch, channels, take_b) * volume_b
        peak = float(out.abs().max())
        out = out * clip_scale(peak, prevent_clipping)
        return ({"waveform": out.clamp(-1.0, 1.0), "sample_rate": rate},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioMix", SYAudioMix)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioMix"] = "Audio Mix SY"
