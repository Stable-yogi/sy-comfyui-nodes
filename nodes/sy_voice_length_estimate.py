"""Voice Length Estimate SY: guesses how long a spoken line lasts and turns it into a video frame count."""
import math
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("words", "characters")
_TAG_RE = re.compile(r"</?d>|\[[^\]]*\]", re.IGNORECASE)
_SENT_RE = re.compile(r"[^.!?。！？]*[.!?。！？]+|[^.!?。！？]+$")


def strip_tags(text):
    return _TAG_RE.sub(" ", str(text or ""))


def estimate(text, mode="words", speed=150, pause_per_sentence=0.3, extra_seconds=0.5, fps=24, snap_step=16, snap_offset=1):
    """Pure function. Returns (seconds, frames, info). frames is the smallest number of the form
    snap_step * k + snap_offset (k = 0, 1, 2 ...) that holds the whole line."""
    if mode not in MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(MODES))
    clean = strip_tags(text).strip()
    if not clean:
        raise ValueError("write the line the voice will say")
    speed = int(speed)
    fps = int(fps)
    snap_step = int(snap_step)
    snap_offset = int(snap_offset)
    if speed < 1 or fps < 1 or snap_step < 1:
        raise ValueError("speed, fps and snap_step must be at least 1")
    if snap_offset < 0:
        raise ValueError("snap_offset must be 0 or more")
    if mode == "words":
        units = sum(1 for t in clean.split() if any(c.isalnum() for c in t))
    else:
        units = sum(1 for c in clean if not c.isspace())
    sentences = 0
    for piece in _SENT_RE.findall(clean):
        if any(c.isalnum() for c in piece):
            sentences += 1
    sentences = max(1, sentences)
    seconds = units / float(speed) * 60.0 + sentences * float(pause_per_sentence) + float(extra_seconds)
    steps = max(0, int(math.ceil((seconds * fps - snap_offset) / snap_step - 1e-9)))
    frames = steps * snap_step + snap_offset
    seconds = round(seconds, 2)
    info = "%d %s, %d sentences, %.2f s, %d frames at %d fps" % (units, mode, sentences, seconds, frames, fps)
    return seconds, frames, info


class SYVoiceLengthEstimate:
    DESCRIPTION = "Guesses how long a spoken line takes and gives a matching video frame count. It is an estimate, not a measurement."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("seconds", "frames", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The line the voice will say. Speech tags like <d> are ignored."}),
                "mode": (list(MODES), {"default": "words", "tooltip": "Count words or characters. Change the speed too when you switch."}),
                "speed": ("INT", {"default": 150, "min": 40, "max": 400, "tooltip": "Words per minute in words mode, characters per minute in characters mode."}),
                "pause_per_sentence": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 3.0, "step": 0.05, "tooltip": "Seconds of pause added after each sentence."}),
                "extra_seconds": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 30.0, "step": 0.1, "tooltip": "Spare seconds added at the end."}),
                "fps": ("INT", {"default": 24, "min": 1, "max": 120, "tooltip": "Frames per second of the video."}),
                "snap_step": ("INT", {"default": 16, "min": 1, "max": 64, "tooltip": "Frames grow in jumps of this size. Step 16 + offset 1 gives 17, 33, 49. Step 17 + offset 5 gives 5, 22, 39."}),
                "snap_offset": ("INT", {"default": 1, "min": 0, "max": 64, "tooltip": "Frames are step times a whole number, plus this offset. Use 5 with step 17 for the video model."}),
            }
        }

    def run(self, text, mode, speed, pause_per_sentence, extra_seconds, fps, snap_step, snap_offset=1):
        return estimate(text, mode, speed, pause_per_sentence, extra_seconds, fps, snap_step, snap_offset)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VoiceLengthEstimate", SYVoiceLengthEstimate)
