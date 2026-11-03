"""Colour Drift Check SY: shows how much brightness and colour strength crept along a clip."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def drift_percent(first, last):
    """Pure function. Change from first to last in percent (+ = went up)."""
    return (last - first) / max(first, 1e-6) * 100.0


def mean(values):
    values = list(values)
    return sum(values) / len(values)


def pixel_saturation(r, g, b):
    """Pure function. (max-min)/max for one pixel."""
    hi = max(r, g, b)
    lo = min(r, g, b)
    return (hi - lo) / max(hi, 1e-6)


def frame_stats(pixels):
    """Pure function. pixels = list of (r, g, b) in 0..1. Returns (brightness, saturation)."""
    if not pixels:
        raise ValueError("a frame has no pixels")
    bright = sum(r + g + b for r, g, b in pixels) / (3.0 * len(pixels))
    sat = mean(pixel_saturation(r, g, b) for r, g, b in pixels)
    return bright, sat


def check_counts(frame_count, compare_frames):
    frame_count = int(frame_count)
    compare_frames = int(compare_frames)
    if frame_count < 2:
        raise ValueError("need at least 2 frames to compare, got %d. Connect a clip, not a single picture" % frame_count)
    if compare_frames * 2 > frame_count:
        raise ValueError("compare_frames is %d but the clip has %d frames. The most you can use is %d"
                         % (compare_frames, frame_count, frame_count // 2))


def evenly_spaced(count, limit=12):
    """Pure function. Up to `limit` frame indexes spread from first to last."""
    if count <= limit:
        return list(range(count))
    return sorted(set(int(round(i * (count - 1) / (limit - 1))) for i in range(limit)))


def build_report(brightness, saturation, compare_frames, warn_percent):
    """Pure function. Returns (report, brightness_change, saturation_change, warning)."""
    n = int(compare_frames)
    check_counts(len(brightness), n)
    b_first, b_last = mean(brightness[:n]), mean(brightness[-n:])
    s_first, s_last = mean(saturation[:n]), mean(saturation[-n:])
    b_ch = drift_percent(b_first, b_last)
    s_ch = drift_percent(s_first, s_last)
    b_big = abs(b_ch) > warn_percent
    s_big = abs(s_ch) > warn_percent
    notes = []
    if b_big:
        notes.append("got brighter" if b_ch > 0 else "got darker")
    if s_big:
        notes.append("got more colourful" if s_ch > 0 else "got less colourful")
    verdict = "Verdict: " + (" and ".join(notes) if notes else "steady")
    lines = [
        "Compared the first %d with the last %d of %d frames." % (n, n, len(brightness)),
        "Brightness: %.3f -> %.3f (%+.1f%%)" % (b_first, b_last, b_ch),
        "Colour strength: %.3f -> %.3f (%+.1f%%)" % (s_first, s_last, s_ch),
        verdict,
        "",
        "frame | brightness | saturation",
    ]
    for i in evenly_spaced(len(brightness)):
        lines.append("%d | %.3f | %.3f" % (i + 1, brightness[i], saturation[i]))
    return "\n".join(lines), b_ch, s_ch, (b_big or s_big)


class SYColourDriftCheck:
    DESCRIPTION = ("Shows how much brightness and colour strength crept up or down along a clip. "
                   "Chained clips often get more saturated; this tells you by how much.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("report", "brightness_change", "saturation_change", "drift_warning")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "compare_frames": ("INT", {"default": 3, "min": 1, "max": 50, "tooltip": "Compare the first this-many frames with the last this-many."}),
                "warn_percent": ("INT", {"default": 5, "min": 1, "max": 100, "tooltip": "Warn when brightness or colour changed by more than this many percent."}),
            },
        }

    def run(self, images, compare_frames, warn_percent):
        check_counts(images.shape[0], compare_frames)
        rgb = images[..., :3].float()
        bright = rgb.mean(dim=(1, 2, 3))
        hi = rgb.max(dim=3).values
        lo = rgb.min(dim=3).values
        sat = ((hi - lo) / hi.clamp(min=1e-6)).mean(dim=(1, 2))
        report, b_ch, s_ch, warn = build_report(bright.tolist(), sat.tolist(), compare_frames, warn_percent)
        return (report, float(b_ch), float(s_ch), bool(warn))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourDriftCheck", SYColourDriftCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYColourDriftCheck"] = "Colour Drift Check SY"
