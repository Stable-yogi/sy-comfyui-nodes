"""Free VRAM SY: passes any value through and, when enabled, asks ComfyUI to unload models and clears the GPU cache."""
import gc

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class AnyType(str):
    """ComfyUI any-type trick: never reports a type mismatch."""

    def __ne__(self, other):
        return False


ANY = AnyType("*")


def describe_status(freed_before, freed_after):
    """Pure function. Inputs are free VRAM in MiB before and after. Returns e.g. 'freed 1234 MiB'."""
    gained = int(freed_after) - int(freed_before)
    if gained <= 0:
        return "nothing freed"
    return "freed %d MiB" % gained


def _free_mib(torch):
    if torch is not None and torch.cuda.is_available():
        free, _total = torch.cuda.mem_get_info()
        return int(free // (1024 * 1024))
    return 0


def free_vram():
    """Does the work. Returns a status string. All heavy imports happen here."""
    try:
        import comfy.model_management as mm
    except Exception:
        return "comfy not available"
    try:
        import torch
    except Exception:
        torch = None
    before = _free_mib(torch)
    mm.unload_all_models()
    mm.soft_empty_cache()
    gc.collect()
    if torch is not None and torch.cuda.is_available():
        torch.cuda.empty_cache()
    return describe_status(before, _free_mib(torch))


class SYFreeVRAM:
    DESCRIPTION = "Passes any value through. When enabled, unloads models and clears the GPU memory cache so the next step has more room."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = (ANY, "STRING")
    RETURN_NAMES = ("value", "status")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": (ANY,), "enabled": ("BOOLEAN", {"default": True})}}

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("nan")

    def run(self, value, enabled=True):
        status = free_vram() if enabled else "disabled"
        return (value, status)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FreeVRAM", SYFreeVRAM)
NODE_DISPLAY_NAME_MAPPINGS["SYFreeVRAM"] = "Free VRAM SY"
