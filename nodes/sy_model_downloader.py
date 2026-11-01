"""Model Downloader SY: a list of models (folder, file name, link) with a button that downloads the missing ones.

The list lives in the node properties (key sy_models, a JSON text), so it travels inside the workflow file.
The node does nothing when a workflow runs. Downloads start ONLY when the user presses a button in the node.
"""
import json

try:
    from ._sy_common import category, register
    from ._sy_download import validate_row
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_download import validate_row

PROPERTY = "sy_models"


def clean_models(props):
    """Pure function. Reads node.properties['sy_models'] (JSON text or a list) and returns (good_rows, problems).
    A bad row is dropped and named in the problems list; nothing is ever raised."""
    raw = (props or {}).get(PROPERTY, "[]")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw.strip() else []
        except ValueError:
            return [], ["The saved model list is damaged and was ignored."]
    if not isinstance(raw, list):
        return [], ["The saved model list is damaged and was ignored."]
    rows, problems, seen = [], [], set()
    for i, item in enumerate(raw, 1):
        clean, why = validate_row(item)
        if not clean:
            problems.append("Row %d: %s" % (i, why))
            continue
        key = (clean["dir"], clean["file"].lower())
        if key in seen:
            problems.append("Row %d: %s is in the list twice." % (i, clean["file"]))
            continue
        seen.add(key)
        row = {"folder": clean["folder"], "file": clean["file"], "url": clean["url"], "note": clean["note"]}
        if clean.get("sha256"):
            row["sha256"] = clean["sha256"]
        rows.append(row)
    return rows, problems


class SYModelDownloader:
    DESCRIPTION = "Keeps a list of models for this workflow (folder, file name and link) and shows which ones are missing. Press Download on a row to fetch it into the right ComfyUI models folder. Nothing is ever downloaded by itself: only when you press a button, and you confirm the size first. Only Hugging Face, Civitai and GitHub links work, only .safetensors and .gguf files, and an existing file is never overwritten. It does nothing when the workflow runs."
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ()

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    def run(self):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ModelDownloader", SYModelDownloader)
NODE_DISPLAY_NAME_MAPPINGS["SYModelDownloader"] = "Model Downloader SY"
