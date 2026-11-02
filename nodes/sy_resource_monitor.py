"""Resource Monitor SY: small live meters on screen for CPU, RAM, GPU, VRAM and GPU temperature.
The meters are drawn in the browser (js/sy_resource_monitor.js) from one read-only route (nodes/_sy_resource_api.py).
This file holds the node shell and the plain rules (the same rules are in js/sy_resource_monitor_logic.js)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CORNERS = ["top right", "top left", "bottom right", "bottom left"]
WARN_AT = 70.0
HOT_AT = 90.0
GB = 1024.0 ** 3


def percent(used, total):
    """Used as a percent of total, 0 to 100, one decimal. Zero, unknown or bad numbers give 0."""
    try:
        u, t = float(used), float(total)
    except (TypeError, ValueError):
        return 0.0
    if not (t > 0) or u != u or t != t:
        return 0.0
    return round(min(100.0, max(0.0, u / t * 100.0)) * 10) / 10.0


def level(pct):
    """ok under 70 percent, warn from 70, hot from 90. Used for the meter colour."""
    try:
        p = float(pct)
    except (TypeError, ValueError):
        return "ok"
    return "hot" if p >= HOT_AT else "warn" if p >= WARN_AT else "ok"


def temp_level(celsius):
    """A GPU temperature as a meter level: warn from 75 C, hot from 85 C."""
    try:
        c = float(celsius)
    except (TypeError, ValueError):
        return "ok"
    return "hot" if c >= 85 else "warn" if c >= 75 else "ok"


def format_gb(num_bytes):
    """Bytes as gigabytes with one decimal, for example 11.9 GB."""
    try:
        b = max(0.0, float(num_bytes))
    except (TypeError, ValueError):
        b = 0.0
    return "%.1f GB" % (b / GB)


def clean_interval(seconds):
    """How often the meters refresh: 0.5 to 10 seconds."""
    try:
        s = float(seconds)
    except (TypeError, ValueError):
        return 1.0
    if s != s:
        return 1.0
    return min(10.0, max(0.5, s))


def build_snapshot(cpu_percent, ram_used, ram_total, gpus):
    """One reading as a plain dict. gpus is a list of dicts with name, util, vram_used, vram_total, temp (None when unknown).
    A missing source stays None so the page can hide that meter instead of showing a wrong 0."""
    out = {
        "cpu": None if cpu_percent is None else round(min(100.0, max(0.0, float(cpu_percent))) * 10) / 10.0,
        "ram": None if not ram_total else {"used": int(ram_used), "total": int(ram_total), "percent": percent(ram_used, ram_total)},
        "gpus": [],
    }
    for g in gpus or []:
        total = g.get("vram_total")
        out["gpus"].append({
            "name": str(g.get("name") or "GPU"),
            "util": None if g.get("util") is None else round(min(100.0, max(0.0, float(g["util"]))) * 10) / 10.0,
            "vram": None if not total else {"used": int(g.get("vram_used") or 0), "total": int(total), "percent": percent(g.get("vram_used"), total)},
            "temp": None if g.get("temp") is None else int(g["temp"]),
        })
    return out


class SYResourceMonitor:
    DESCRIPTION = ("Shows small live meters in a corner of the screen: CPU, RAM, GPU load, VRAM and GPU temperature. "
                   "Good for videos that show how much memory a model takes while it loads. Put one in the workflow; it has no wires.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "Off hides the meters and stops reading."}),
                "corner": (CORNERS, {"default": "top right", "tooltip": "Which corner of the screen holds the meters."}),
                "interval": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 10.0, "step": 0.5, "tooltip": "Seconds between two readings."}),
            },
        }

    def run(self, enabled=True, corner="top right", interval=1.0):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ResourceMonitor", SYResourceMonitor)
NODE_DISPLAY_NAME_MAPPINGS["SYResourceMonitor"] = "Resource Monitor SY"
