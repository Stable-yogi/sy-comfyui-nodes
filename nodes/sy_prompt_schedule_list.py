"""Prompt Schedule List SY: expands a prompt schedule into one prompt per frame."""
try:
    from ._sy_common import category, register
    from .sy_prompt_schedule import parse_schedule
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from sy_prompt_schedule import parse_schedule

MAX_FRAMES = 2000


def expand_schedule(text, total_frames, fill_before_first=False):
    """Pure function. Returns (joined_text, segment_count). Frames before the first key get an empty line,
    or the first prompt when fill_before_first is on. Segments are the keys that start inside the range."""
    total_frames = int(total_frames)
    if total_frames < 1:
        raise ValueError("total_frames must be at least 1, got %d" % total_frames)
    if total_frames > MAX_FRAMES:
        raise ValueError("total_frames is capped at %d, got %d" % (MAX_FRAMES, total_frames))
    keys = parse_schedule(text)
    lines = []
    idx = 0
    active = keys[0][1] if (fill_before_first and keys) else ""
    for frame in range(total_frames):
        while idx < len(keys) and keys[idx][0] <= frame:
            active = keys[idx][1]
            idx += 1
        lines.append(active)
    segments = sum(1 for k, _ in keys if k < total_frames)
    return "\n".join(lines), segments


def schedule_info(text, total_frames, fill_before_first=False):
    """Pure function. One plain sentence: frames, segments, and the mistakes people make (late first key, keys past the end)."""
    keys = parse_schedule(text)
    total_frames = int(total_frames)
    inside = [k for k, _ in keys if k < total_frames]
    outside = len(keys) - len(inside)
    parts = ["%d frame(s), %d segment(s)" % (total_frames, len(inside))]
    if not keys:
        parts.append("WARNING: the schedule has no keys, so every line is empty")
    elif keys[0][0] > 0:
        if fill_before_first:
            parts.append("frames 0-%d use the first prompt" % (min(keys[0][0], total_frames) - 1))
        else:
            parts.append("WARNING: frames 0-%d have no prompt (first key is at frame %d; add '0: ...' or turn on fill_before_first)"
                         % (min(keys[0][0], total_frames) - 1, keys[0][0]))
    if outside:
        parts.append("%d key(s) start after frame %d and are ignored" % (outside, total_frames - 1))
    return "; ".join(parts)


class SYPromptScheduleList:
    DESCRIPTION = ("Turns a prompt schedule into one prompt per frame, one per line. Adds over a plain loop: it can fill the frames before the "
                   "first key, and the info line warns about a missing 0 key or keys past the last frame.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("prompts", "segments", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "0: a cat\n24: a dog", "tooltip": "One line per key, written as frame: prompt. Blank lines and # lines are skipped."}),
                "total_frames": ("INT", {"default": 48, "min": 1, "max": MAX_FRAMES, "tooltip": "How many frames to list. The most allowed is 2000."}),
            },
            "optional": {
                "fill_before_first": ("BOOLEAN", {"default": False, "tooltip": "On: frames before the first key use the first prompt instead of an empty line."}),
            },
        }

    def run(self, text, total_frames, fill_before_first=False):
        joined, segments = expand_schedule(text, total_frames, fill_before_first)
        return (joined, segments, schedule_info(text, total_frames, fill_before_first))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptScheduleList", SYPromptScheduleList)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptScheduleList"] = "Prompt Schedule List SY"
