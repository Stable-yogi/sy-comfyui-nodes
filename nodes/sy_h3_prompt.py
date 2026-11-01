"""H3 Prompt SY: one box for the video prompt. Text, reference pictures, video length and acting clip are checked together."""
import re

try:
    from ._sy_common import category, register
    from .sy_h3_prompt_builder import build_prompt
    from .sy_h3_length import frames_for
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from sy_h3_prompt_builder import build_prompt
    from sy_h3_length import frames_for

SLOTS = 4
DEFAULT_SECONDS = 5.0
_PIC = re.compile(r"picture\s*(\d+)", re.IGNORECASE)
_TIME = re.compile(r"^(\d+(?:\.\d+)?)s?\s*-\s*(\d+(?:\.\d+)?)s?\s*:")


def picture_numbers(text):
    """Pure function. The picture numbers a text points at (Picture 2 gives 2), sorted, no repeats."""
    return sorted({int(m.group(1)) for m in _PIC.finditer(str(text or ""))})


def connected_slots(flags):
    """Pure function. flags: True/False per slot (is a picture wired in). Returns the slot numbers (1..4) that are wired."""
    return [i for i, f in enumerate(flags, 1) if f]


def slot_to_picture(slots):
    """Pure function. Slot numbers that are wired -> {slot: Picture number}. Empty slots are skipped, so numbers have no gaps."""
    return {s: n for n, s in enumerate(slots, 1)}


def check_pictures(text, count):
    """Pure function. Plain warnings: text names a picture that is not connected, or a connected picture the text never names."""
    nums = picture_numbers(text)
    out = []
    missing = [n for n in nums if n > count or n < 1]
    if missing:
        out.append("WARNING: the text mentions %s but only %d reference picture%s connected."
                   % (", ".join("Picture %d" % n for n in missing), count, " is" if count == 1 else "s are"))
    unused = [n for n in range(1, count + 1) if n not in nums]
    if unused:
        if len(unused) == 1:
            out.append("WARNING: Picture %d is connected but the text never mentions it." % unused[0])
        else:
            out.append("WARNING: Pictures %s are connected but the text never mentions them." % ", ".join(str(n) for n in unused))
    return out


def picture_lines(notes, slots):
    """Pure function. notes: texts per slot (slot 1..4). Returns (lines, warnings). A line is made only when the note is written."""
    mapping = slot_to_picture(slots)
    lines, warns = [], []
    for slot, note in enumerate(notes, 1):
        note = " ".join(str(note or "").split())
        if not note:
            continue
        if slot not in mapping:
            warns.append("WARNING: ref_note_%d is written but ref_image_%d is not connected, so the note was left out." % (slot, slot))
            continue
        lines.append("Picture %d is %s." % (mapping[slot], note.rstrip(".")))
    gaps = [s for s in slots if mapping[s] != s]
    if gaps:
        warns.append("Note: an empty slot comes before ref_image_%d, so the model sees it as Picture %d." % (gaps[0], mapping[gaps[0]]))
    return lines, warns


def time_code_ends(time_codes):
    """Pure function. End time in seconds of every time code line that is like 0-4s: text."""
    ends = []
    for line in str(time_codes or "").splitlines():
        m = _TIME.match(line.strip())
        if m:
            ends.append(float(m.group(2)))
    return ends


def check_time_codes(time_codes, clip_seconds):
    """Pure function. Warns when a time code ends after the clip does."""
    ends = time_code_ends(time_codes)
    if ends and max(ends) > clip_seconds + 0.05:
        return ["WARNING: the time codes run to %.1f s but the clip is only %.2f s long." % (max(ends), clip_seconds)]
    return []


def plan_length(seconds, fps, acting_frames):
    """Pure function. Returns (frames, real_seconds, lines). seconds 0 = take it from the acting video, or 5 s when there is none."""
    fps = int(round(float(fps)))
    if fps < 1:
        raise ValueError("fps must be at least 1")
    seconds = float(seconds)
    if seconds < 0:
        raise ValueError("seconds cannot be negative")
    acting_frames = int(acting_frames or 0)
    if seconds > 0:
        source = "seconds you set"
    elif acting_frames > 0:
        seconds, source = acting_frames / float(fps), "acting video"
    else:
        seconds, source = DEFAULT_SECONDS, "default"
    frames, real, _ = frames_for(seconds, fps, "up")
    lines = ["Length: %.2f s at %d fps (from %s) -> %d frames (%.2f s)." % (seconds, fps, source, frames, real)]
    if acting_frames:
        lines.append("Acting video: %d frames = %.2f s." % (acting_frames, acting_frames / float(fps)))
        if acting_frames > frames:
            lines.append("WARNING: the acting video has more frames (%d) than the clip (%d). Only the first %d are used." % (acting_frames, frames, frames))
    return frames, real, lines


def make_info(lines):
    """Pure function. Joins the lines; says everything is fine when there is no warning."""
    lines = [l for l in lines if l]
    if not any(l.startswith("WARNING") for l in lines):
        lines.append("All checks passed.")
    return "\n".join(lines)


def _reference_batch(images):
    """images: list of tensors or None. First frame of each, size of the first, 3 colour channels. Empty = black 64x64."""
    import torch
    import torch.nn.functional as F
    got = []
    for img in images:
        if img is None:
            continue
        if getattr(img, "ndim", 0) != 4:
            raise ValueError("a reference picture must be shaped [batch, height, width, channels]")
        got.append(img[:1, :, :, :3])
    if not got:
        return torch.zeros((1, 64, 64, 3), dtype=torch.float32)
    h, w = int(got[0].shape[1]), int(got[0].shape[2])
    out = []
    for g in got:
        if (int(g.shape[1]), int(g.shape[2])) != (h, w):
            g = F.interpolate(g.movedim(-1, 1), size=(h, w), mode="bilinear", align_corners=False).movedim(1, -1)
        out.append(g)
    return torch.cat(out, dim=0)


class SYH3Prompt:
    DESCRIPTION = ("One box for the video prompt. Builds the text, checks that Picture 1, Picture 2 match the reference pictures you connected, "
                   "turns seconds into a frame count the model accepts, and checks the time codes against the acting video.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "IMAGE", "STRING")
    RETURN_NAMES = ("prompt", "frames", "references", "info")

    @classmethod
    def INPUT_TYPES(cls):
        opt = {
            "dialogue": ("STRING", {"default": "", "multiline": True, "tooltip": "Spoken lines, one per line. Each line gets its own speech tag."}),
            "dialogue_language": ("STRING", {"default": "", "multiline": False, "tooltip": "Language of the spoken lines, for example Japanese. Leave empty for none."}),
            "time_codes": ("STRING", {"default": "", "multiline": True, "tooltip": "One line per moment, like 0-4s: she turns round."}),
        }
        for i in range(1, SLOTS + 1):
            opt["ref_image_%d" % i] = ("IMAGE", {"tooltip": "Reference picture %d. Leave empty if not used. Only its first frame is used." % i})
        opt["acting_video"] = ("IMAGE", {"tooltip": "The acting video as frames. Gives the clip length and checks the time codes."})
        opt["fps"] = ("FLOAT", {"default": 24.0, "min": 1.0, "max": 60.0, "step": 1.0, "tooltip": "Frames per second of the clip."})
        opt["seconds"] = ("FLOAT", {"default": 0.0, "min": 0.0, "max": 60.0, "step": 0.1, "tooltip": "Clip length. 0 = take it from the acting video, or 5 seconds if none."})
        opt["label_pictures"] = ("BOOLEAN", {"default": True, "tooltip": "Add a 'Picture 1 is ...' line for each note you wrote below."})
        for i in range(1, SLOTS + 1):
            opt["ref_note_%d" % i] = ("STRING", {"default": "", "multiline": False, "tooltip": "What reference picture %d shows, for example the hero in a red coat." % i})
        return {
            "required": {
                "style": ("STRING", {"default": "", "multiline": True, "tooltip": "The look of the clip, for example soft film light."}),
                "world": ("STRING", {"default": "", "multiline": True, "tooltip": "Where the scene happens and who is in it."}),
                "action": ("STRING", {"default": "", "multiline": True, "tooltip": "What happens in the clip. Write Picture 1, Picture 2 to point at input pictures."}),
            },
            "optional": opt,
        }

    def run(self, style, world, action, dialogue="", dialogue_language="", time_codes="", acting_video=None,
            fps=24.0, seconds=0.0, label_pictures=True, ref_image_1=None, ref_image_2=None, ref_image_3=None,
            ref_image_4=None, ref_note_1="", ref_note_2="", ref_note_3="", ref_note_4=""):
        images = [ref_image_1, ref_image_2, ref_image_3, ref_image_4]
        slots = connected_slots([im is not None for im in images])
        count = len(slots)
        if acting_video is not None and getattr(acting_video, "ndim", 0) != 4:
            raise ValueError("acting_video must be video frames shaped [frames, height, width, channels]")
        acting_frames = int(acting_video.shape[0]) if acting_video is not None else 0
        lines = []
        # check the words the user wrote, before any label line is added
        written = "\n".join([str(style), str(world), str(action), str(time_codes)])
        lines.extend(check_pictures(written, count))
        world_text = str(world or "")
        if label_pictures:
            pl, pw = picture_lines([ref_note_1, ref_note_2, ref_note_3, ref_note_4], slots)
            lines.extend(pw)
            if pl:
                world_text = (world_text.strip() + "\n" if world_text.strip() else "") + "\n".join(pl)
        # picture_count is set to the maximum: the clearer picture check above replaces the builder's own one
        prompt, notes = build_prompt(style, world_text, action, dialogue, dialogue_language, SLOTS, time_codes)
        frames, real, length_lines = plan_length(seconds, fps, acting_frames)
        lines.extend(length_lines)
        lines.extend(check_time_codes(time_codes, real))
        for note in notes.splitlines():
            if note:
                lines.append("WARNING: " + note)
        lines.insert(0, "%d reference picture%s connected." % (count, "" if count == 1 else "s"))
        return (prompt, frames, _reference_batch(images), make_info(lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3Prompt", SYH3Prompt)
NODE_DISPLAY_NAME_MAPPINGS["SYH3Prompt"] = "H3 Prompt SY"
