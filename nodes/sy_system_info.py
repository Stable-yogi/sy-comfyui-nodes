"""System Info SY: reports free graphics memory (VRAM) and free system memory (RAM) as text and numbers."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

WARN_PERCENT = 85.0
HIGH_PERCENT = 95.0
MB = 1024 * 1024


def level_word(percent):
    """Pure function. ok below 85 percent, warn from 85, high from 95."""
    if percent >= HIGH_PERCENT:
        return "high"
    if percent >= WARN_PERCENT:
        return "warn"
    return "ok"


def _line(label, total, free):
    if total is None or free is None or total <= 0 or free < 0:
        return "%s: unavailable" % label
    used = max(0.0, 100.0 * (total - free) / total)
    return "%s: %.0f%% used, %d of %d MB free (%s)" % (label, used, free, total, level_word(used))


def format_report(vram_total, vram_free, ram_total, ram_free):
    """Pure function. Sizes are in MB; use -1 when a value is unknown. Returns a short two-line text."""
    return _line("VRAM", vram_total, vram_free) + "\n" + _line("RAM", ram_total, ram_free)


def read_vram_mb():
    """Returns (total_mb, free_mb) of the current GPU, or (-1, -1) when torch or a GPU is missing."""
    try:
        import torch
        if not torch.cuda.is_available():
            return -1, -1
        free, total = torch.cuda.mem_get_info()
        return int(total // MB), int(free // MB)
    except Exception:
        return -1, -1


def read_ram_mb():
    """Returns (total_mb, free_mb) of system memory, or (-1, -1) when psutil is missing."""
    try:
        import psutil
        vm = psutil.virtual_memory()
        return int(vm.total // MB), int(vm.available // MB)
    except Exception:
        return -1, -1


class SYSystemInfo:
    DESCRIPTION = "Reports free video memory and free system memory as a short text and two numbers. Shows -1 if unknown."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("report", "vram_free_mb", "ram_free_mb")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # memory changes all the time, so run every time

    def run(self):
        vt, vf = read_vram_mb()
        rt, rf = read_ram_mb()
        return (format_report(vt, vf, rt, rf), int(vf), int(rf))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SystemInfo", SYSystemInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYSystemInfo"] = "System Info SY"
