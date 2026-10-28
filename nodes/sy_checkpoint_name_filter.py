"""Checkpoint Name Filter SY: finds the first checkpoint whose name contains some text."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names


def filter_names(names, contains):
    """Pure function. Case-insensitive 'contains' match. Returns matching names in sorted order."""
    needle = str(contains).strip().lower()
    return sorted(n for n in names if needle in n.lower())


def pick_first(names, contains):
    """Pure function. First match, or ValueError saying what to change."""
    if not names:
        raise ValueError("no checkpoints were found. Put a checkpoint in the ComfyUI checkpoints folder.")
    found = filter_names(names, contains)
    if not found:
        raise ValueError("no checkpoint name contains %r. Try a shorter word." % str(contains).strip())
    return found[0]


class SYCheckpointNameFilter:
    DESCRIPTION = "Looks through your checkpoint files and returns the name of the first one that contains your text."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("name", "match_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"contains": ("STRING", {"default": "", "tooltip": "Part of the checkpoint name. Capital letters do not matter."})}}

    def run(self, contains):
        names = list_names("checkpoints")
        first = pick_first(names, contains)
        return (first, len(filter_names(names, contains)))

    @classmethod
    def IS_CHANGED(cls, contains):
        return float("nan")


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CheckpointNameFilter", SYCheckpointNameFilter)
NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointNameFilter"] = "Checkpoint Name Filter SY"
