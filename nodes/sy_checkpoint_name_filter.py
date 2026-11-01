"""Checkpoint Name Filter SY: finds a checkpoint whose name contains some words, and lists every match."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names
    from ._sy_a1_files import match_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names
    from _sy_a1_files import match_names


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


def pick_match(names, contains, exclude="", index=0):
    """Pure function. Like pick_first, but with several words (all must be in the name), words to leave out,
    and an index that wraps. Returns (name, match_count, all_matches_text, info)."""
    if not names:
        raise ValueError("no checkpoints were found. Put a checkpoint in the ComfyUI checkpoints folder.")
    words = " ".join(str(contains).split())
    found = match_names(names, words, exclude)
    if not found:
        extra = (" and does not contain %r" % " ".join(str(exclude).split())) if str(exclude).strip() else ""
        raise ValueError("no checkpoint name contains %r%s. Try fewer or shorter words." % (words, extra))
    i = int(index) % len(found)
    chosen = found[i]
    info = "%d of %d checkpoints match %r: using number %d, %s" % (len(found), len(names), words, i, chosen)
    return chosen, len(found), "\n".join(found), info


class SYCheckpointNameFilter:
    DESCRIPTION = ("Looks through your checkpoint files and returns the name of the one that contains your words. "
                   "Adds over a plain search: several words at once ('flux dev'), words to leave out, an index that "
                   "wraps to step through the matches, the full list of matches and a plain info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("name", "match_count", "all_matches", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"contains": ("STRING", {"default": "", "tooltip": "Part of the checkpoint name, for example 'flux dev'. Capitals do not matter."})},
            "optional": {
                "exclude": ("STRING", {"default": "", "tooltip": "Words that must NOT be in the name, for example 'fp8 old'."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Which match to use, from 0. A too big number wraps to the start."}),
            },
        }

    def run(self, contains, exclude="", index=0):
        names = list_names("checkpoints")
        if not str(exclude).strip() and int(index) == 0 and len(str(contains).split()) <= 1:
            # the old single-word path, kept for identical results
            first = pick_first(names, contains)
            found = filter_names(names, contains)
            return (first, len(found), "\n".join(found),
                    "%d of %d checkpoints match %r: using %s" % (len(found), len(names), str(contains).strip(), first))
        name, count, all_text, info = pick_match(names, contains, exclude, index)
        return (name, count, all_text, info)

    @classmethod
    def IS_CHANGED(cls, contains, exclude="", index=0):
        return float("nan")


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CheckpointNameFilter", SYCheckpointNameFilter)
NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointNameFilter"] = "Checkpoint Name Filter SY"
