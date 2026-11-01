# Review Pause SY (`SYReviewPause`)

Source: `nodes/sy_review_pause.py`

**What it does:** Stops the workflow half-way and opens a window. Look at the pictures, untick the bad ones, fix the text, paint a mask if you switched that on, then press Continue or Stop. Only the ticked pictures go on, in their old order. Shows at most 16 pictures; any further ones are always kept. Switch it off to run without stopping.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| enabled | BOOLEAN | yes | Off = pass everything through without stopping, for runs without a person. | default True |
| message | STRING | yes | The note shown at the top of the window. | default 'Look at the result, then press Continue.', multiline |
| allow_mask_draw | BOOLEAN | yes | On = the window lets you paint a mask on the first picture. | default False |
| wait_limit_minutes | INT | yes | How long to wait for you. 0 = wait until you answer. | 0 to 1440, default 0 |
| on_timeout | COMBO | yes | What happens when the waiting time runs out. | one of: continue with everything, stop the workflow |
| image | IMAGE | no | The pictures to look at. You choose which ones to keep. | picture batch [B,H,W,3] |
| text | STRING | no | A text you may change in the window before it goes on. | default '', multiline |
| mask | MASK | no | A mask to start from. You can change it if drawing is on. | mask [B,H,W] |

Outputs: `IMAGE`, `STRING`, `MASK`, `STRING`, `STRING`
