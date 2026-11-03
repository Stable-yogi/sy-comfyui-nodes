"""Overlap Window Planner SY: cuts a long clip into overlapping windows (start and end frame numbers)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LAST_MODES = ("shift back so it is full", "keep it short")


def plan_windows(total, window, overlap, last_mode="shift back so it is full"):
    """Pure function. Returns a list of (start, end_exclusive) windows that cover frames 0..total-1."""
    total = int(total)
    window = int(window)
    overlap = int(overlap)
    if total < 1:
        raise ValueError("total_frames must be at least 1, got %d" % total)
    if window < 2:
        raise ValueError("window_frames must be at least 2, got %d" % window)
    if overlap < 0:
        raise ValueError("overlap_frames cannot be negative, got %d" % overlap)
    if overlap >= window:
        raise ValueError("overlap must be smaller than the window: overlap is %d, window is %d. "
                         "Lower overlap_frames or raise window_frames" % (overlap, window))
    if last_mode not in LAST_MODES:
        raise ValueError("last_window must be one of: %s" % ", ".join(LAST_MODES))
    if total <= window:
        return [(0, total)]
    step = window - overlap
    out = []
    start = 0
    while True:
        end = start + window
        if end >= total:
            if end > total and last_mode == LAST_MODES[0]:
                start = total - window
            out.append((start, total))
            break
        out.append((start, end))
        start += step
    return out


def plan_text(windows):
    """Pure function. One line per window; the second number is the last frame (inclusive)."""
    return "\n".join("%d: %d-%d (%d frames)" % (i + 1, s, e - 1, e - s) for i, (s, e) in enumerate(windows))


def pick_window(windows, pick):
    """Pure function. Returns (start, end_exclusive, length) of the 1-based window, or zeros when pick is 0."""
    pick = int(pick)
    if pick < 0:
        raise ValueError("pick cannot be negative, got %d" % pick)
    if pick == 0:
        return (0, 0, 0)
    if pick > len(windows):
        raise ValueError("pick is %d but there are only %d windows. Lower pick (0 means none)" % (pick, len(windows)))
    s, e = windows[pick - 1]
    return (s, e, e - s)


class SYOverlapWindowPlanner:
    DESCRIPTION = ("Cuts a long clip into overlapping windows so a long video can be made or processed in pieces "
                   "and joined later. Gives one line per window and can read out one window.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("plan", "window_count", "start", "end_exclusive", "length")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_frames": ("INT", {"default": 200, "min": 1, "max": 100000, "tooltip": "How many frames the whole clip has."}),
                "window_frames": ("INT", {"default": 56, "min": 2, "max": 10000, "tooltip": "How many frames each piece holds."}),
                "overlap_frames": ("INT", {"default": 5, "min": 0, "max": 5000, "tooltip": "How many frames two neighbouring pieces share. Must be smaller than the window."}),
                "last_window": (list(LAST_MODES), {"default": LAST_MODES[0], "tooltip": "Last piece: move it back so it is full (more overlap), or let it be shorter."}),
                "pick": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Window number to read out, counting from 1. 0 means none."}),
            },
        }

    def run(self, total_frames, window_frames, overlap_frames, last_window, pick):
        windows = plan_windows(total_frames, window_frames, overlap_frames, last_window)
        s, e, n = pick_window(windows, pick)
        return (plan_text(windows), len(windows), s, e, n)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "OverlapWindowPlanner", SYOverlapWindowPlanner)
NODE_DISPLAY_NAME_MAPPINGS["SYOverlapWindowPlanner"] = "Overlap Window Planner SY"
