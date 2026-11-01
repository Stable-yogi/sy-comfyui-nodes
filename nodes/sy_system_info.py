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


def read_gpu_name():
    """Name of the current GPU, or '' when torch or a GPU is missing."""
    try:
        import torch
        return torch.cuda.get_device_name() if torch.cuda.is_available() else ""
    except Exception:
        return ""


def check_needs(vram_free_mb, ram_free_mb, need_vram_gb=0.0, need_ram_gb=0.0):
    """Pure function. Returns (enough, text). A need of 0 is not checked. An unknown value (-1) is not checked either."""
    need_v, need_r = float(need_vram_gb), float(need_ram_gb)
    if need_v < 0 or need_r < 0:
        raise ValueError("the memory you need cannot be negative")
    problems, notes = [], []
    for label, free, need, advice in (
            ("VRAM", vram_free_mb, need_v, "Close other programs, unload models, or pick a smaller model."),
            ("RAM", ram_free_mb, need_r, "Close other programs or lower the batch size.")):
        if need <= 0:
            continue
        if free is None or free < 0:
            notes.append("%s could not be read, so it was not checked." % label)
        elif free / 1024.0 < need:
            problems.append("Not enough %s: %.1f GB free, %g GB needed. %s" % (label, free / 1024.0, need, advice))
        else:
            notes.append("%s ok: %.1f GB free, %g GB needed." % (label, free / 1024.0, need))
    if problems:
        return False, " ".join(problems)
    if notes:
        return True, " ".join(notes)
    return True, "No memory need was given, so nothing was checked."


class SYSystemInfo:
    DESCRIPTION = ("Reports free video memory and free system memory as a short text and numbers. Shows -1 if unknown. "
                   "Type how much memory your next step needs and it says if there is enough, or stops the run early with a plain message.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "INT", "INT", "BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("report", "vram_free_mb", "ram_free_mb", "vram_total_mb", "ram_total_mb", "enough", "check", "gpu_name")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}, "optional": {
            "need_vram_gb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.5, "tooltip": "VRAM the next step needs, for example 12. 0 means do not check."}),
            "need_ram_gb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10000.0, "step": 0.5, "tooltip": "System RAM the next step needs, for example 32. 0 means do not check."}),
            "stop_if_short": ("BOOLEAN", {"default": False, "tooltip": "On: stop the run with a plain message when there is not enough memory."}),
        }}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # memory changes all the time, so run every time

    def run(self, need_vram_gb=0.0, need_ram_gb=0.0, stop_if_short=False):
        vt, vf = read_vram_mb()
        rt, rf = read_ram_mb()
        enough, check = check_needs(vf, rf, need_vram_gb, need_ram_gb)
        if stop_if_short and not enough:
            raise ValueError(check)
        return (format_report(vt, vf, rt, rf), int(vf), int(rf), int(vt), int(rt), enough, check, read_gpu_name())


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SystemInfo", SYSystemInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYSystemInfo"] = "System Info SY"
