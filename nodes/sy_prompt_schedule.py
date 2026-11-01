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


BEFORE_FIRST = ("empty", "use first prompt")


def schedule_run(keys, frame, loop_length=0, before_first="empty"):
    """Pure function. Returns (prompt, next_key_frame, key_count, next_prompt, blend, info).
    blend is how far the frame is from the active key to the next key (0 to 1). loop_length > 0 repeats the schedule every that many frames."""
    if before_first not in BEFORE_FIRST:
        raise ValueError("before_first must be one of: %s (got %r)" % (", ".join(BEFORE_FIRST), before_first))
    original = int(frame)
    loop_length = int(loop_length)
    if loop_length < 0:
        raise ValueError("loop_length must not be negative, got %d" % loop_length)
    frame = original % loop_length if loop_length > 0 and original >= 0 else original
    prompt, nxt, count = prompt_at(keys, frame)
    if not keys:
        return "", -1, 0, "", 0.0, "The schedule has no keys, so the prompt is empty."
    prev = max((k for k, _ in keys if k <= frame), default=None)
    next_prompt = dict(keys)[nxt] if nxt >= 0 else ""
    blend = round((frame - prev) / float(nxt - prev), 4) if (nxt >= 0 and prev is not None) else 0.0
    head = "Frame %d" % frame + (" (looped from %d)" % original if frame != original else "")
    if prev is None:
        if before_first == "use first prompt":
            prompt = keys[0][1]
            state = "before the first key at frame %d, so the first prompt is used" % keys[0][0]
        else:
            state = "before the first key at frame %d, so the prompt is empty" % keys[0][0]
    else:
        state = "using the key at frame %d" % prev
    tail = "next key at frame %d (%d%% of the way)" % (nxt, round(blend * 100)) if nxt >= 0 else "no later key"
    return prompt, nxt, count, next_prompt, blend, "%s: %s; %s." % (head, state, tail)


class SYPromptSchedule:
    DESCRIPTION = ("Reads lines like '0: a cat' and '24: a dog' and gives the prompt that is active at the frame you choose. "
                   "Also gives the next prompt and how far the frame is toward it (for blending), can repeat the schedule in a loop, "
                   "and an info line says which key is in use.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("prompt", "next_key_frame", "key_count", "next_prompt", "blend", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "0: a cat\n24: a dog", "tooltip": "One line per key, written as frame: prompt. Blank lines and # lines are skipped."}),
                "frame": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "The frame to look up."}),
            },
            "optional": {
                "loop_length": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "0 = no loop. Otherwise the schedule repeats every this many frames."}),
                "before_first": (list(BEFORE_FIRST), {"default": "empty", "tooltip": "What to give for frames before the first key: an empty prompt or the first prompt."}),
            },
        }

    def run(self, text, frame, loop_length=0, before_first="empty"):
        return schedule_run(parse_schedule(text), frame, loop_length, before_first)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptSchedule", SYPromptSchedule)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptSchedule"] = "Prompt Schedule SY"
