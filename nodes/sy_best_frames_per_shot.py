"""Best Frames Per Shot SY: picks the best still frames from every shot of a clip with hard cuts."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ["sharpest", "middle"]


def parse_starts(text, total):
    """Pure function. Shot start frames from text like "0,30,61". Frame 0 is always a start.
    Returns (starts, notes). Numbers at or past the end of the clip are left out with a note."""
    total = int(total)
    if total < 1:
        raise ValueError("the clip is empty: there are no frames to pick from")
    notes = []
    starts = {0}
    for part in str(text or "").replace(";", ",").replace("\n", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            v = int(float(part))
        except ValueError:
            raise ValueError("shot_starts must be frame numbers split by commas, got %r" % part)
        if v < 0:
            raise ValueError("shot start %d is below 0" % v)
        if v >= total:
            notes.append("shot start %d is past the last frame (%d), left out" % (v, total - 1))
            continue
        starts.add(v)
    return sorted(starts), notes


def merge_short(starts, min_shot):
    """Pure function. Drops every shot start that comes less than `min_shot` frames after the last kept start,
    so a cut finder that fires many times in a row (flashes, moving titles) gives one shot. 0 or 1 keeps all."""
    min_shot = int(min_shot)
    if min_shot < 0:
        raise ValueError("min_shot must be 0 or more, got %d" % min_shot)
    kept = []
    for s in starts:
        if not kept or s - kept[-1] >= min_shot:
            kept.append(s)
    return kept


def shot_ranges(starts, total, edge):
    """Pure function. One (first, last) frame range per shot, with `edge` frames trimmed at both ends
    (cut frames are often blurred). A shot too short to trim keeps its middle frame."""
    edge = int(edge)
    if edge < 0:
        raise ValueError("edge must be 0 or more, got %d" % edge)
    ranges = []
    for i, s in enumerate(starts):
        e = (starts[i + 1] if i + 1 < len(starts) else int(total)) - 1
        a, b = s + edge, e - edge
        if a > b:
            mid = (s + e) // 2
            a = b = mid
        ranges.append((a, b))
    return ranges


def pick_frames(ranges, per_shot, mode="sharpest", scores=None):
    """Pure function. Returns a list of (shot_number_from_0, frame) in clip order.
    sharpest: the `per_shot` highest scores in each range (ties go to the earlier frame).
    middle: `per_shot` frames spread evenly inside each range."""
    per_shot = int(per_shot)
    if per_shot < 1:
        raise ValueError("frames_per_shot must be at least 1, got %d" % per_shot)
    if mode not in MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(MODES))
    out = []
    for n, (a, b) in enumerate(ranges):
        frames = list(range(a, b + 1))
        if mode == "sharpest":
            if scores is None:
                raise ValueError("sharpest needs a score for every frame")
            chosen = sorted(sorted(frames, key=lambda f: (-scores[f], f))[:per_shot])
        else:
            k = min(per_shot, len(frames))
            chosen = sorted({a + int(round((b - a) * (j + 1) / float(k + 1))) for j in range(k)})
        out.extend((n, f) for f in chosen)
    return out


def apply_drop(picks, drop_text):
    """Pure function. Leaves out picks by their number in the result (1 = first), like "2, 5".
    Returns (kept_picks, notes)."""
    drop = set()
    notes = []
    for part in str(drop_text or "").replace(";", ",").replace("\n", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit() or int(part) < 1:
            raise ValueError("drop must be picture numbers from 1, split by commas, got %r" % part)
        if int(part) > len(picks):
            notes.append("drop %s: there are only %d pictures" % (part, len(picks)))
        drop.add(int(part))
    kept = [p for i, p in enumerate(picks, 1) if i not in drop]
    if not kept:
        raise ValueError("drop leaves no pictures: keep at least one")
    return kept, notes


def labels_for(picks, label_text):
    """Pure function. One label line per kept picture: the shot's name, or "shot N"."""
    names = [l.strip() for l in str(label_text or "").splitlines() if l.strip()]
    return "\n".join(names[n] if n < len(names) else "shot %d" % (n + 1) for n, _ in picks)


class SYBestFramesPerShot:
    DESCRIPTION = ("Picks the best still frames from every shot of a clip with hard cuts (a look sheet or turnaround video). "
                   "Give it the shot start frames from H3 Look Sheet Prompt SY or Scene Cut Finder SY. "
                   "It skips the blurred frames next to each cut, keeps the sharpest (or middle) frames per shot, "
                   "and can leave out pictures you do not want. Feed the result and labels into Image Grid SY for a datasheet.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("images", "labels", "picked_frames", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "All frames of the clip, in order."}),
                "shot_starts": ("STRING", {"default": "0", "multiline": False, "tooltip": "Frame where each shot starts, split by commas (0 is added for you). Connect shot_starts or cut_indices here."}),
                "frames_per_shot": ("INT", {"default": 1, "min": 1, "max": 16, "tooltip": "How many stills to keep from each shot."}),
                "mode": (MODES, {"default": "sharpest", "tooltip": "sharpest: the least blurry frames of each shot. middle: frames spread evenly through each shot."}),
                "edge": ("INT", {"default": 3, "min": 0, "max": 48, "tooltip": "Frames to skip at the start and end of each shot (cuts often blur these)."}),
            },
            "optional": {
                "shot_labels": ("STRING", {"default": "", "multiline": True, "tooltip": "Shot names, one per line (from H3 Look Sheet Prompt SY). Empty gives shot 1, shot 2 ..."}),
                "drop": ("STRING", {"default": "", "multiline": False, "tooltip": "Picture numbers to leave out after a look, like 2, 5 (1 = first picture)."}),
                "min_shot": ("INT", {"default": 8, "min": 0, "max": 240, "tooltip": "Shots shorter than this many frames join the shot before (stops false cuts from titles or flashes). 0 keeps all."}),
            },
        }

    def run(self, images, shot_starts, frames_per_shot, mode, edge, shot_labels="", drop="", min_shot=8):
        total = int(images.shape[0])
        starts, notes = parse_starts(shot_starts, total)
        merged = merge_short(starts, min_shot)
        if len(merged) < len(starts):
            notes.append("%d short shots joined the shot before (min_shot %d)" % (len(starts) - len(merged), int(min_shot)))
        ranges = shot_ranges(merged, total, edge)
        scores = None
        if mode == "sharpest":
            h, w = images.shape[1], images.shape[2]
            if h < 3 or w < 3:
                raise ValueError("the pictures are too small to measure sharpness: they need at least 3 x 3 pixels, got %d x %d" % (w, h))
            c = images.shape[-1]
            rgb = images[..., :3] if c >= 3 else images[..., :1].expand(-1, -1, -1, 3)
            grey = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
            lap = (4.0 * grey[:, 1:-1, 1:-1] - grey[:, :-2, 1:-1] - grey[:, 2:, 1:-1]
                   - grey[:, 1:-1, :-2] - grey[:, 1:-1, 2:])
            scores = [float(v) for v in lap.reshape(lap.shape[0], -1).double().var(dim=1, unbiased=False).tolist()]
        picks = pick_frames(ranges, frames_per_shot, mode, scores)
        picks, drop_notes = apply_drop(picks, drop)
        frames = [f for _, f in picks]
        info = ["%d shots, %d pictures kept" % (len(ranges), len(frames))] + notes + drop_notes
        return (images[frames], labels_for(picks, shot_labels), ",".join(str(f) for f in frames), len(frames), "\n".join(info))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BestFramesPerShot", SYBestFramesPerShot)
NODE_DISPLAY_NAME_MAPPINGS["SYBestFramesPerShot"] = "Best Frames Per Shot SY"
