# Coalesce Text SY (`SYCoalesceText`)

Source: `nodes/sy_coalesce_text.py`

**What it does:** Gives the first piece of text that is not empty out of up to five, so optional inputs fall back cleanly. Tells you which slot won (0 means the fallback).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_1 | STRING | yes | Checked first. Used if it is not empty. | default '' |
| text_2 | STRING | no | Checked second. | default '' |
| text_3 | STRING | no | Checked third. | default '' |
| text_4 | STRING | no | Checked fourth. | default '' |
| text_5 | STRING | no | Checked fifth. | default '' |
| treat_spaces_as_empty | BOOLEAN | no | On: text with only spaces or line breaks counts as empty. | default True |
| fallback | STRING | no | Given back when every slot is empty. | default '' |

Outputs: `STRING`, `INT`

## How to use

1. Connect your texts to **text_1** to **text_5**, in the order you want them tried.
2. Leave **treat_spaces_as_empty** on so text with only spaces or line breaks is skipped.
3. Type a **fallback** to use when every slot is empty.
4. The outputs give the first non-empty **text** and **used_slot**, which slot won (0 means the fallback).
