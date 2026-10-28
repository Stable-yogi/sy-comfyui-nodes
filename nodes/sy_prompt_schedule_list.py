"""Prompt Schedule List SY: expands a prompt schedule into one prompt per frame."""
try:
    from ._sy_common import category, register
    from .sy_prompt_schedule import parse_schedule
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from sy_prompt_schedule import parse_schedule

MAX_FRAMES = 2000


def expand_schedule(text, total_frames):
    """Pure function. Returns (joined_text, segment_count). Frames before the first key get an empty line.
    Segments are the keys that start inside the range."""
    total_frames = int(total_frames)
    if total_frames < 1:
        raise ValueError("total_frames must be at least 1, got %d" % total_frames)
    if total_frames > MAX_FRAMES:
        raise ValueError("total_frames is capped at %d, got %d" % (MAX_FRAMES, total_frames))
    keys = parse_schedule(text)
    lines = []
    idx = 0
    active = ""
    for frame in range(total_frames):
        while idx < len(keys) and keys[idx][0] <= frame:
            active = keys[idx][1]
            idx += 1
        lines.append(active)
    segments = sum(1 for k, _ in keys if k < total_frames)
    return "\n".join(lines), segments


class SYPromptScheduleList:
    DESCRIPTION = "Turns a prompt schedule into a list with one prompt per frame, one per line. Also tells how many segments it has."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompts", "segments")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "0: a cat\n24: a dog", "tooltip": "One line per key, written as frame: prompt. Blank lines and # lines are skipped."}),
                "total_frames": ("INT", {"default": 48, "min": 1, "max": MAX_FRAMES, "tooltip": "How many frames to list. The most allowed is 2000."}),
            }
        }

    def run(self, text, total_frames):
        return expand_schedule(text, total_frames)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptScheduleList", SYPromptScheduleList)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptScheduleList"] = "Prompt Schedule List SY"
