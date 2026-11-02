"""Progress Bar SY: a big bar at the edge of the screen with percent, step, running node and time, so screen recordings show what happens.
The bar is drawn in the browser (js/sy_progress_bar.js). This file holds the node shell and the plain rules
(the same rules are in js/sy_progress_bar_logic.js), so they can be tested without a browser."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

POSITIONS = ["top", "bottom"]


def overall_percent(total, finished, sub_value=0, sub_max=0, done=False):
    """Overall percent 0 to 100. total = nodes in the job, finished = nodes already done (cached ones count),
    sub_value/sub_max = the step counter inside the running node. Never 100 until done is True."""
    if done:
        return 100.0
    try:
        t = max(0, int(float(total)))
        f = int(float(finished))
        sm = float(sub_max)
        sv = float(sub_value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if t == 0:
        return 0.0
    f = min(t, max(0, f))
    frac = min(1.0, max(0.0, sv / sm)) if sm > 0 else 0.0
    pct = (f + (frac if f < t else 0.0)) / t * 100.0
    return min(99.0, max(0.0, round(pct * 10) / 10.0))


def format_elapsed(ms):
    """0:07, 1:05, 1:02:03. Whole seconds, never negative."""
    try:
        s = max(0, int(float(ms) // 1000))
    except (TypeError, ValueError, OverflowError):
        s = 0
    h, m, r = s // 3600, (s % 3600) // 60, s % 60
    return "%d:%02d:%02d" % (h, m, r) if h > 0 else "%d:%02d" % (m, r)


def short_title(title, max_len=32):
    """The node title on one line, cut to max_len characters with a dots mark."""
    t = " ".join(str(title or "").split())
    n = max(4, int(max_len))
    return t[:n - 1].rstrip() + "…" if len(t) > n else t


def position_style(pos):
    """top or bottom. Anything else is top."""
    return "bottom" if str(pos or "").strip().lower() == "bottom" else "top"


class SYProgressBar:
    DESCRIPTION = ("Shows a bar at the top (or bottom) of the screen while a workflow runs: percent done, the step of the running node, "
                   "which node is running and the time. Good for screen recordings. Put one in the workflow; it has no wires.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "Off hides the bar."}),
                "position": (POSITIONS, {"default": "top", "tooltip": "Show the bar at the top or the bottom of the screen."}),
                "show_node": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "Show the title of the node that is running now."}),
                "show_time": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "Show the time since the run started."}),
                "show_step": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "Show the step counter of the running node, for example step 12 of 30."}),
            },
        }

    def run(self, enabled=True, position="top", show_node=True, show_time=True, show_step=True):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ProgressBar", SYProgressBar)
NODE_DISPLAY_NAME_MAPPINGS["SYProgressBar"] = "Progress Bar SY"
