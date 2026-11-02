"""Audio High Low Pass SY: removes low rumble (high-pass) or high hiss (low-pass) with an FFT filter."""
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

MODES = ("high-pass (cut lows)", "low-pass (cut highs)")
SLOPES = {"gentle (6 dB)": 1, "normal (12 dB)": 2, "steep (24 dB)": 4}


def butterworth_gain(f, fc, order, kind):
    """Pure function. Butterworth filter strength 0..1 at frequency f for cutoff fc.
    kind 'high' = 1/sqrt(1+(fc/f)^(2n)); kind 'low' = 1/sqrt(1+(f/fc)^(2n)). The gain at fc is 0.7071 for any order."""
    if fc <= 0:
        raise ValueError("cutoff is %s Hz: it must be above zero" % fc)
    if order < 1:
        raise ValueError("order is %s: it must be 1 or more" % order)
    if kind not in ("high", "low"):
        raise ValueError("kind %r is unknown: use 'high' or 'low'" % (kind,))
    f = abs(float(f))
    if kind == "high":
        if f == 0.0:
            return 0.0
        ratio = fc / f
    else:
        ratio = f / fc
    try:
        return 1.0 / math.sqrt(1.0 + ratio ** (2 * order))
    except OverflowError:
        return 0.0


def check_cutoff(cutoff_hz, rate):
    """Pure function. Refuses a cutoff at or above half the sample rate."""
    if cutoff_hz <= 0:
        raise ValueError("cutoff is %s Hz: it must be above zero" % cutoff_hz)
    if cutoff_hz >= rate / 2.0:
        raise ValueError("cutoff %.0f Hz is too high for this sound: its sample rate is %d Hz, so the cutoff must stay below %.0f Hz"
                         % (cutoff_hz, rate, rate / 2.0))


class SYAudioHighLowPass:
    DESCRIPTION = ("Removes low rumble (high-pass) or high hiss (low-pass). Pick the cutoff frequency and how steep the "
                   "cut is. The sound keeps its length and sample rate.")
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", {"tooltip": "The sound to filter."}),
                "mode": (list(MODES), {"default": "high-pass (cut lows)", "tooltip": "High-pass removes the low sounds below the cutoff. Low-pass removes the high sounds above it."}),
                "cutoff_hz": ("FLOAT", {"default": 120.0, "min": 20.0, "max": 20000.0, "step": 1.0, "tooltip": "The pitch where the cut starts, in Hz. At this pitch the sound is about 30 percent quieter."}),
                "slope": (list(SLOPES.keys()), {"default": "normal (12 dB)", "tooltip": "How sharply the cut bites. Steeper cuts leave less of the unwanted sound."}),
            }
        }

    def run(self, audio, mode, cutoff_hz, slope):
        import torch
        _b, _c, n, rate = check_audio(audio)
        if mode not in MODES:
            raise ValueError("unknown mode %r: pick one of %s" % (mode, ", ".join(MODES)))
        if slope not in SLOPES:
            raise ValueError("unknown slope %r: pick one of %s" % (slope, ", ".join(SLOPES)))
        check_cutoff(cutoff_hz, rate)
        order = SLOPES[slope]
        wave = audio["waveform"].float()
        spec = torch.fft.rfft(wave, dim=-1)
        freqs = torch.fft.rfftfreq(n, d=1.0 / rate).to(device=wave.device, dtype=torch.float64)
        if mode.startswith("high"):
            ratio = torch.where(freqs > 0, cutoff_hz / freqs.clamp_min(1e-12), torch.full_like(freqs, float("inf")))
        else:
            ratio = freqs / cutoff_hz
        gain = 1.0 / torch.sqrt(1.0 + ratio.pow(2 * order))
        out = torch.fft.irfft(spec * gain.to(torch.float32), n=n, dim=-1)
        out = out.clamp(-1.0, 1.0).to(audio["waveform"].dtype).contiguous()
        return ({"waveform": out, "sample_rate": rate},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioHighLowPass", SYAudioHighLowPass)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioHighLowPass"] = "Audio High Low Pass SY"
