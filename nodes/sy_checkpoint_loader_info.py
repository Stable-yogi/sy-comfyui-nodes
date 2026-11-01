"""Checkpoint Loader Info SY: loads a checkpoint and tells you what it is: file name, size, format, precision, warnings."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import info_line, embedding_dirs, listed_path
    from ._sy_model_files import list_names
    from ._sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, checkpoint_warnings, missing_parts_note
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import info_line, embedding_dirs, listed_path
    from _sy_model_files import list_names
    from _sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, checkpoint_warnings, missing_parts_note


def build_info(name, size, filter_note="", has_clip=True, has_vae=True):
    """Pure function. The info text: facts line, then plain notes and warnings, one per line."""
    lines = [file_facts(name, size)]
    if filter_note:
        lines.append(filter_note)
    lines += precision_notes(name)
    lines += ["Warning: " + w for w in checkpoint_warnings(name)]
    lines += ["Warning: " + w for w in missing_parts_note(has_clip, has_vae)]
    return "\n".join(lines)


class SYCheckpointLoaderInfo:
    DESCRIPTION = ("Loads a checkpoint like the plain loader, and adds: a name_filter box (type part of a name instead of "
                   "scrolling a long list), a plain info text (size, format, fp8/fp16 explained), warnings for a wrong or "
                   "empty file, and the name of the file that was really loaded.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "info", "ckpt_name")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": (list_names("checkpoints"), {"tooltip": "The checkpoint file to load from the checkpoints folder."}),
            },
            "optional": {
                "name_filter": ("STRING", {"default": "", "tooltip": "Optional. Words like 'flux dev': loads the first matching file and ignores the list."}),
            },
        }

    def run(self, ckpt_name, name_filter=""):
        chosen, note = pick_with_filter(list_names("checkpoints"), ckpt_name, name_filter, "checkpoint")
        path = listed_path("checkpoints", chosen)
        import os
        import comfy.sd
        size = check_size(chosen, os.path.getsize(path))
        out = comfy.sd.load_checkpoint_guess_config(path, output_vae=True, output_clip=True, embedding_directory=embedding_dirs())
        info = build_info(chosen, size, note, has_clip=out[1] is not None, has_vae=out[2] is not None)
        return (out[0], out[1], out[2], info, chosen)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CheckpointLoaderInfo", SYCheckpointLoaderInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointLoaderInfo"] = "Checkpoint Loader Info SY"
