"""Seed Vault SY: a keep-the-good-ones notebook for seeds, with star ratings and a ranked list."""
import datetime

try:
    from ._sy_common import category, register
    from . import _sy_seed_vault as H
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_seed_vault as H


def vault_run(path, action, collection, seed, rating, max_entries, keep_best, pick_rank,
              prompt="", note="", tags="", now_text=None):
    """Pure-ish core (takes a path). Returns (best_seed, ranking, count, info). 'show' never writes."""
    if action not in ("save", "show"):
        raise ValueError("action must be 'save' or 'show', got %r" % (action,))
    name = H.validate_inputs(collection, seed, rating, max_entries, prompt)
    if not 0 <= int(pick_rank) <= 50:
        raise ValueError("pick_rank must be from 0 to 50, got %s" % (pick_rank,))
    entries = H.load_vault(path)
    if action == "save":
        if now_text is None:
            now_text = datetime.datetime.now().isoformat(timespec="seconds")
        entries = H.add_entry(entries, name, seed, rating, prompt, note, tags, now_text, max_entries, keep_best)
        H.save_vault(path, entries)
    ranked = H.rank_entries(entries, name)
    best = H.seed_at_rank(ranked, pick_rank)
    md = H.ranking_markdown(ranked, name)
    if action == "save":
        info = "Saved seed %d in '%s' with %d star(s). %d saved in this collection." % (int(seed), name, int(rating), len(ranked))
    else:
        info = "Showing '%s': %d saved. Nothing was written." % (name, len(ranked))
    return best, md, len(ranked), info


class SYSeedVault:
    DESCRIPTION = ("A notebook for good seeds. Save a seed with a star rating, a note and tags, see the ranked list as "
                   "Markdown, and hand back the best seed again. Keep it at the end of a workflow.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("INT", "STRING", "INT", "STRING")
    RETURN_NAMES = ("best_seed", "ranking", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["save", "show"], {"default": "save", "tooltip": "Save adds or updates this seed. Show only reads the vault."}),
                "collection": ("STRING", {"default": "my seeds", "multiline": False, "tooltip": "Name of the group this seed belongs to, for example a look or a motion."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": H.MAX_SEED, "tooltip": "The seed to keep."}),
                "rating": ("INT", {"default": 3, "min": 0, "max": 5, "tooltip": "Stars from 0 to 5. Higher stars rank first."}),
                "max_entries": ("INT", {"default": 500, "min": 10, "max": 5000, "tooltip": "Most entries kept in the whole vault. Extra ones are dropped."}),
                "keep_best": ("BOOLEAN", {"default": True, "tooltip": "On drops the lowest rated, oldest entries when full. Off drops the oldest."}),
                "pick_rank": ("INT", {"default": 0, "min": 0, "max": 50, "tooltip": "0 gives the best seed. 2 gives the second best, and so on."}),
            },
            "optional": {
                "prompt": ("STRING", {"default": "", "multiline": True, "forceInput": False, "tooltip": "The prompt used with this seed. Different prompts are kept apart."}),
                "note": ("STRING", {"default": "", "multiline": True, "tooltip": "A short note. Left empty on a re-save keeps the old note."}),
                "tags": ("STRING", {"default": "", "multiline": False, "tooltip": "Words separated by commas. Left empty on a re-save keeps the old tags."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("nan")

    def run(self, action, collection, seed, rating, max_entries, keep_best, pick_rank, prompt="", note="", tags=""):
        path = H.vault_path()
        return vault_run(path, action, collection, seed, rating, max_entries, keep_best, pick_rank, prompt, note, tags)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeedVault", SYSeedVault)
