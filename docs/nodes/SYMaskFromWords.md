# Mask From Words SY (`SYMaskFromWords`)

Source: `nodes/sy_mask_from_words.py`

**What it does:** Selects things in a picture from words you type, for example 'person' or 'the red dress'. Gives a mask (1 = selected), a cut-out picture with a see-through background, how many separate things were found and a short note. Nothing found gives an empty mask, not an error. Needs a SAM3 model file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch) to select things in. | picture batch [B,H,W,3] |
| words | STRING | yes | What to select, in plain words. Example: the red dress. Commas look for several things. | default 'person' |
| model | COMBO | yes | SAM3 model file from models/sam3. | one of: (no model installed: use Model Downloader SY) |
| threshold | FLOAT | yes | How sure it must be. Lower finds more. Finds things that are not there? Raise it to 0.8. | 0.0 to 1.0, step 0.01, default 0.5 |
| which | COMBO | yes | Join everything found, keep the biggest, or give one mask per find. | one of: all matches together, biggest one, one at a time (batch of masks) |
| grow | INT | yes | Pixels to widen the selection. Negative numbers shrink it. | -64 to 64, default 0 |
| feather | INT | yes | Soft edge in pixels. 0 = off. | 0 to 64, default 0 |

Outputs: `MASK`, `IMAGE`, `INT`, `STRING`

## How to use

1. Connect your picture to image and pick a model file in model. If none is listed, get one with Model Downloader SY.
2. Type what to select in words, for example person or the red dress. Commas look for several things.
3. Raise threshold (try 0.8) if it finds things that are not there. Lower it to find more.
4. In which, choose to join all finds, keep the biggest one, or get one mask per find.
5. Outputs: the mask, a cut-out picture with a see-through background, the number of finds and a note. Nothing found gives an empty mask, not an error.
