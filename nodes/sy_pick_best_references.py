"""Pick Best References SY: hands out stills of a character datasheet as Picture 1, 2 and 3 for a video model."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SLOTS = 3
# a word that also finds a still named with another word ("back" finds "seen from behind")
ALSO = {"back": ("behind", "rear")}


def _lines(text):
    return [" ".join(t.split()) for t in str(text or "").replace(",", "\n").splitlines() if t.strip()]


def _label_lines(text):
    # one shot name per line: a name may hold commas ("full body, seen from behind")
    return [" ".join(t.split()) for t in str(text or "").splitlines() if t.strip()]


def pick_references(labels, wanted, count):
    """Pure function. labels: one name per still (newline text). wanted: up to 3 words to look for,
    for example "face\nfull body\nback". count: how many stills there are.
    Returns (list of 3 still numbers, 0-based; list of 3 names; notes)."""
    count = int(count)
    if count < 1:
        raise ValueError("there are no stills: connect the pictures from Best Frames Per Shot SY")
    names = _label_lines(labels)
    wants = _lines(wanted)[:SLOTS]
    if len(_lines(wanted)) > SLOTS:
        raise ValueError("wanted has more than 3 lines: the video model reads 3 reference pictures here")
    notes = []
    if names and len(names) != count:
        notes.append("%d labels for %d stills: missing labels read as shot N" % (len(names), count))
    names = (names + ["shot %d" % (i + 1) for i in range(len(names), count)])[:count]
    used, picks = [], []
    for want in wants:
        hit = None
        if want.isdigit():
            n = int(want)
            if not 1 <= n <= count:
                raise ValueError("wanted still %d does not exist: there are %d stills" % (n, count))
            hit = n - 1
        else:
            low = want.lower()
            for i, name in enumerate(names):
                if i not in used and any(w in name.lower() for w in (low,) + ALSO.get(low, ())):
                    hit = i
                    break
            if hit is None:
                notes.append("no still is named like %r: the next free still is used" % want)
        if hit is None:
            free = [i for i in range(count) if i not in used]
            hit = free[0] if free else used[-1]
        used.append(hit)
        picks.append(hit)
    while len(picks) < SLOTS:
        free = [i for i in range(count) if i not in used]
        nxt = free[0] if free else picks[-1] if picks else 0
        if not free:
            notes.append("only %d stills: Picture %d repeats a still" % (count, len(picks) + 1))
        used.append(nxt)
        picks.append(nxt)
    return picks, [names[i] for i in picks], notes


def prompt_line(picked_names, character):
    """Pure function. One sentence that tells the video model what each picture shows."""
    who = " ".join(str(character or "").split()) or "the character"
    parts = ["Picture %d shows %s (%s)" % (i + 1, who, n) for i, n in enumerate(picked_names)]
    return "; ".join(parts) + ". Keep the same face, hair and clothes in every shot."


class SYPickBestReferences:
    DESCRIPTION = ("Takes the stills of a character datasheet (from Best Frames Per Shot SY) and hands out three of them "
                   "as Picture 1, 2 and 3 for a video model: by name (face, full body, back) or by number. "
                   "Also writes the sentence that tells the model what each picture shows.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("picture_1", "picture_2", "picture_3", "prompt_line", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The datasheet stills, one picture per shot."}),
                "wanted": ("STRING", {"default": "face\nfull body\nback", "multiline": True, "tooltip": "Up to 3 lines: a word from the shot name, or a still number. Line 1 becomes Picture 1."}),
            },
            "optional": {
                "labels": ("STRING", {"default": "", "multiline": True, "forceInput": True, "tooltip": "Shot names, one per still (the labels output of Best Frames Per Shot SY)."}),
                "character": ("STRING", {"default": "the character", "multiline": False, "tooltip": "How the sentence names the person, for example the young woman."}),
            },
        }

    def run(self, images, wanted, labels="", character="the character"):
        picks, names, notes = pick_references(labels, wanted, images.shape[0])
        outs = [images[i:i + 1] for i in picks]
        info = "Picture 1 = still %d, Picture 2 = still %d, Picture 3 = still %d" % tuple(p + 1 for p in picks)
        if notes:
            info += "\n" + "\n".join(notes)
        return (outs[0], outs[1], outs[2], prompt_line(names, character), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PickBestReferences", SYPickBestReferences)
NODE_DISPLAY_NAME_MAPPINGS["SYPickBestReferences"] = "Pick Best References SY"
