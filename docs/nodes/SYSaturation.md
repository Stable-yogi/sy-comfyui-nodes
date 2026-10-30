# Saturation SY (`SYSaturation`)

Source: `nodes/sy_saturation.py`

**What it does:** Makes colours stronger or weaker. Vibrance mostly lifts dull colours and leaves strong ones alone.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| amount | FLOAT | yes | Below 0 fades the colour, -100 is grey. Above 0 makes colours stronger. | -100.0 to 100.0, step 1.0, default 0.0 |
| mode | COMBO | yes | saturation changes every colour the same; vibrance moves dull colours more than strong ones. | one of: saturation, vibrance |

Outputs: `IMAGE`
