"""Checkpoint Loader Info SY: loads a checkpoint and also tells you its file name and size."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import info_line, embedding_dirs, listed_path
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import info_line, embedding_dirs, listed_path
    from _sy_model_files import list_names


class SYCheckpointLoaderInfo:
    DESCRIPTION = "Loads a checkpoint from your checkpoints folder. Also gives a text line with the file name and size."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": (list_names("checkpoints"), {"tooltip": "The checkpoint file to load from the checkpoints folder."}),
            }
        }

    def run(self, ckpt_name):
        path = listed_path("checkpoints", ckpt_name)
        import os
        import comfy.sd
        info = info_line(ckpt_name, os.path.getsize(path))
        out = comfy.sd.load_checkpoint_guess_config(path, output_vae=True, output_clip=True, embedding_directory=embedding_dirs())
        return (out[0], out[1], out[2], info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CheckpointLoaderInfo", SYCheckpointLoaderInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointLoaderInfo"] = "Checkpoint Loader Info SY"
