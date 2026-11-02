"""Audio Reverse SY: plays a sound backwards."""

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

def reverse_list(samples):
    """Pure function. A list backwards (the node does the same along the sample axis)."""
    return list(samples)[::-1]


class SYAudioReverse:
    DESCRIPTION = "Plays a sound backwards. The length and sample rate stay the same."
    CATEGORY = category("Audio")
    FUNCTION = "run"
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio": ("AUDIO", {"tooltip": "The sound to turn around."})}}

    def run(self, audio):
        check_audio(audio)
        wave = audio["waveform"].flip(-1).contiguous()
        return ({"waveform": wave, "sample_rate": int(audio["sample_rate"])},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AudioReverse", SYAudioReverse)
NODE_DISPLAY_NAME_MAPPINGS["SYAudioReverse"] = "Audio Reverse SY"
