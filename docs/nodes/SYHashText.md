# Hash Text SY (`SYHashText`)

Source: `nodes/sy_hash_text.py`

**What it does:** Turns a text into a fingerprint code. The same text always gives the same code. Handy for file names. Can ignore capital letters and extra spaces, so two nearly equal prompts get the same code, and an info line says what was made.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to fingerprint. | default '', multiline |
| algorithm | COMBO | yes | Which fingerprint method to use. sha256 is a good default. | one of: sha256, sha1, md5, sha512 |
| length | INT | yes | Keep only this many characters of the code. 0 keeps all of it. | 0 to 128, default 0 |
| strip | BOOLEAN | yes | On: remove spaces and new lines around the text first. | default False |
| normalize | BOOLEAN | no | On: ignore capital letters and extra spaces, so 'A Cat' and 'a cat' give the same code. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Type or connect the text. Pick algorithm (sha256 is a good default).
2. Set length to keep only that many characters of the code. 0 keeps all.
3. Turn on strip to remove spaces and new lines around the text, and normalize to ignore capitals and extra spaces.
4. The same text always gives the same code, which suits file names. An info line comes out too.
