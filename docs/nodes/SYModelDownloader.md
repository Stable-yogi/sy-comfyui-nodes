# Model Downloader SY (`SYModelDownloader`)

Source: `nodes/sy_model_downloader.py`

**What it does:** Keeps a list of models for this workflow (folder, file name and link) and shows which ones are missing. Press Download on a row to fetch it into the right ComfyUI models folder. Nothing is ever downloaded by itself: only when you press a button, and you confirm the size first. Only Hugging Face, Civitai and GitHub links work, only .safetensors and .gguf files, and an existing file is never overwritten. It does nothing when the workflow runs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| (none) | | | | |

Outputs: none

## How to use

1. Add rows to the list on the node: the models folder, the file name and the link.
2. The node shows which files are missing.
3. Press Download on a row. You confirm the size first, and the file goes into the matching models folder.
Limits: only Hugging Face, Civitai and GitHub links work, only .safetensors and .gguf files, and an existing file is never overwritten. Nothing downloads by itself, and the node does nothing when the workflow runs.
