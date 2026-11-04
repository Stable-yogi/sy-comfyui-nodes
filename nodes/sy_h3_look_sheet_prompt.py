"""H3 Look Sheet Prompt SY: one video prompt with hard cuts to a still camera, one framing per shot, for character look sheets."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FRAMINGS = {
    "face front close-up": "close-up of the face, front view, looking into the lens",
    "face extreme close-up": "extreme close-up of the eyes and nose, front view",
    "face three-quarter": "close-up of the face turned three-quarters to the camera",
    "face left profile": "close-up of the face in left profile, looking to the side",
    "face right profile": "close-up of the face in right profile, looking to the side",
    "head back": "close-up of the back of the head and the hair",
    "waist up front": "medium shot from the waist up, front view",
    "waist up back": "medium shot from the waist up, seen from behind",
    "full body front": "full body shot from head to feet, front view, standing straight",
    "full body three-quarter": "full body shot from head to feet, turned three-quarters to the camera",
    "full body left side": "full body shot from head to feet, left side view",
    "full body right side": "full body shot from head to feet, right side view",
    "full body back": "full body shot from head to feet, seen from behind",
    "outfit detail": "close-up of the outfit from shoulders to waist, showing the fabric and details",
    "hands detail": "close-up of both hands held in front of the body",
    "feet detail": "close-up of the feet and shoes on the floor",
}
PRESETS = {
    "face set (6)": ["face front close-up", "face three-quarter", "face left profile", "face right profile",
                     "face extreme close-up", "head back"],
    "body set (6)": ["full body front", "full body three-quarter", "full body left side", "full body back",
                     "waist up front", "outfit detail"],
    "full set (12)": ["face front close-up", "face three-quarter", "face left profile", "face right profile",
                      "waist up front", "waist up back", "full body front", "full body three-quarter",
                      "full body left side", "full body back", "hands detail", "feet detail"],
    "custom": [],
}
HARD_ANGLES = ("worm", "bird", "from above", "from below", "top down", "top-down", "overhead", "low angle", "high angle")
MAX_SHOTS = 24
MIN_SHOT_SECONDS = 0.8


def _clean(text):
    return " ".join(str(text or "").split())


def shot_list(preset, custom_shots=""):
    """Pure function. Returns (labels, descriptions, notes) for the chosen preset or the custom lines."""
    if preset not in PRESETS:
        raise ValueError("preset must be one of: %s" % ", ".join(PRESETS))
    notes = []
    if preset == "custom":
        labels = [_clean(l) for l in str(custom_shots or "").splitlines() if _clean(l)]
        if not labels:
            raise ValueError("preset is custom but custom_shots is empty: write one framing per line, for example: full body front")
    else:
        labels = list(PRESETS[preset])
    if len(labels) > MAX_SHOTS:
        raise ValueError("%d shots is too many: at most %d fit in one clip" % (len(labels), MAX_SHOTS))
    descs = []
    for lab in labels:
        key = lab.lower()
        if key in FRAMINGS:
            descs.append(FRAMINGS[key])
        else:
            descs.append(lab)
            notes.append("'%s' is not in the framing list, used as written" % lab)
        if any(w in key for w in HARD_ANGLES):
            notes.append("'%s': views from far above or below often fail, eye level works best" % lab)
    return labels, descs, notes


def shot_plan(count, seconds, fps):
    """Pure function. Splits the clip into `count` equal shots.
    Returns (total_frames, start_frames, windows) where windows are (start_s, end_s)."""
    count = int(count)
    fps = int(fps)
    seconds = float(seconds)
    if count < 1:
        raise ValueError("there must be at least one shot")
    if fps < 1:
        raise ValueError("fps must be at least 1, got %d" % fps)
    if seconds <= 0:
        raise ValueError("seconds must be above 0, got %s" % seconds)
    total = int(round(seconds * fps)) + 1
    if total < count:
        raise ValueError("%d frames are too few for %d shots: make the clip longer" % (total, count))
    starts = [int(round(i * total / float(count))) for i in range(count)]
    step = seconds / count
    windows = [(round(i * step, 1), round((i + 1) * step, 1)) for i in range(count)]
    return total, starts, windows


def build_look_sheet(subject, setting, preset, custom_shots="", seconds=10.0, fps=24, expression=""):
    """Pure function. Returns (prompt, shot_starts, shot_labels, shot_count, notes)."""
    subject = _clean(subject)
    setting = _clean(setting)
    expression = _clean(expression)
    if not subject:
        raise ValueError("write who the look sheet is of, for example: the woman from Picture 1")
    labels, descs, notes = shot_list(preset, custom_shots)
    _total, starts, windows = shot_plan(len(labels), seconds, fps)
    if float(seconds) / len(labels) < MIN_SHOT_SECONDS:
        notes.append("each shot is %.2f s: shots under %.1f s may merge, use fewer shots or a longer clip"
                     % (float(seconds) / len(labels), MIN_SHOT_SECONDS))
    head = ["A look sheet video of %s." % subject]
    if setting:
        head.append("Setting: %s." % setting.rstrip("."))
    if expression:
        head.append("Expression: %s." % expression.rstrip("."))
    head.append("The camera is locked off on a tripod and never moves. Every shot starts with a hard cut to a new framing.")
    lines = ["%.1f-%.1fs: hard cut, %s." % (a, b, d.rstrip(".")) for (a, b), d in zip(windows, descs)]
    prompt = " ".join(head) + "\n" + "\n".join(lines)
    return prompt, ",".join(str(s) for s in starts), "\n".join(labels), len(labels), "\n".join(notes)


class SYH3LookSheetPrompt:
    DESCRIPTION = ("Writes one video prompt for a character look sheet: hard cuts to a still camera, one framing per shot "
                   "(face, profile, full body, back, details). Also gives the frame where each shot starts and the shot names, "
                   "so Best Frames Per Shot SY can pick a still from every shot and Image Grid SY can label them.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("prompt", "shot_starts", "shot_labels", "shot_count", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "subject": ("STRING", {"default": "the woman from Picture 1", "multiline": False, "tooltip": "Who the look sheet is of. Point at the reference picture."}),
                "setting": ("STRING", {"default": "a plain light grey studio wall, soft even light", "multiline": False, "tooltip": "Background and light. Plain backgrounds make clean sheets."}),
                "preset": (list(PRESETS), {"default": "full set (12)", "tooltip": "Which framings to shoot. custom uses the custom_shots lines."}),
                "seconds": ("FLOAT", {"default": 10.0, "min": 1.0, "max": 30.0, "step": 0.5, "tooltip": "Clip length. Give each shot about 0.8 s or more."}),
                "fps": ("INT", {"default": 24, "min": 1, "max": 60, "tooltip": "Frames per second of the clip. Sets the shot start frames."}),
            },
            "optional": {
                "custom_shots": ("STRING", {"default": "", "multiline": True, "tooltip": "One framing per line, for preset custom: a list name like full body front, or your own words."}),
                "expression": ("STRING", {"default": "", "multiline": False, "tooltip": "Optional face expression for every shot, for example calm and neutral."}),
            },
        }

    def run(self, subject, setting, preset, seconds, fps, custom_shots="", expression=""):
        return build_look_sheet(subject, setting, preset, custom_shots, seconds, fps, expression)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3LookSheetPrompt", SYH3LookSheetPrompt)
NODE_DISPLAY_NAME_MAPPINGS["SYH3LookSheetPrompt"] = "H3 Look Sheet Prompt SY"
