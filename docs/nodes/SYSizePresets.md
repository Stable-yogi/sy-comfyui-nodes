# Size Presets SY (`SYSizePresets`)

Source: `nodes/sy_size_presets.py`

**What it does:** Pick a common picture size by name, like 1024x1024 square or 2048x1152 wide. Gives a width and a height.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | A common picture size. Portrait is taller than wide. | one of: 512x512 square, 512x768 portrait, 768x512 landscape, 768x768 square, 768x1024 portrait, 1024x768 landscape, 832x1216 portrait, 1216x832 landscape, 896x1152 portrait, 1152x896 landscape, 1024x1024 square, 1024x1536 portrait ... |

Outputs: `INT`, `INT`
