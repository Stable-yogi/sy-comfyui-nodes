# Hash Text SY (`SYHashText`)

Source: `nodes/sy_hash_text.py`

**What it does:** Turns a text into a fingerprint code. The same text always gives the same code. Handy for file names.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to fingerprint. | default '', multiline |
| algorithm | COMBO | yes | Which fingerprint method to use. sha256 is a good default. | one of: sha256, sha1, md5, sha512 |
| length | INT | yes | Keep only this many characters of the code. 0 keeps all of it. | 0 to 128, default 0 |
| strip | BOOLEAN | yes | On: remove spaces and new lines around the text first. | default False |

Outputs: `STRING`
