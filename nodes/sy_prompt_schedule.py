"""Prompt Schedule SY: picks the prompt that is active at a given frame from lines like "24: a dog"."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_schedule(text):
    """Pure function. Returns a list of (frame, prompt) sorted by frame.
    Blank lines and lines starting with # are skipped. Anything else must look like "frame: prompt"."""
    keys = {}
    for number, raw in enumerate(str(text).splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        head, sep, prompt = line.partition(":")
        head = head.strip()
        prompt = prompt.strip()
        if not sep or not head.isascii() or not head.isdigit() or not prompt:
            raise ValueError("line %d is not in the form 'frame: prompt': %r" % (number, raw))
        frame = int(head)
        if frame in keys:
            raise ValueError("line %d repeats frame %d: %r" % (number, frame, raw))
        keys[frame] = prompt
    return sorted(keys.items())


def prompt_at(keys, frame):
    """Returns (prompt, next_key_frame, key_count). Before the first key the prompt is empty; no next key gives -1."""
    frame = int(frame)
    if frame < 0:
        raise ValueError("frame must not be negative, got %d" % frame)
    active = ""
    nxt = -1
    for k, p in keys:
        if k <= frame:
            active = p
        else:
            nxt = k
            break
    return active, nxt, len(keys)


class SYPromptSchedule:
    DESCRIPTION = "Reads lines like '0: a cat' and '24: a dog' and gives the prompt that is active at the frame you choose."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("prompt", "next_key_frame", "key_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "0: a cat\n24: a dog", "tooltip": "One line per key, written as frame: prompt. Blank lines and # lines are skipped."}),
                "frame": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "The frame to look up."}),
            }
        }

    def run(self, text, frame):
        return prompt_at(parse_schedule(text), frame)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptSchedule", SYPromptSchedule)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptSchedule"] = "Prompt Schedule SY"
