# LinePick SY (`SYLinePick`)

Source: `nodes/sy_line_pick.py`

**What it does:** Takes one line from a text. Count from the top with 0, 1, 2 or from the bottom with -1, -2. A number that is too big can wrap round to the start (handy with a counter) or stick to the last line instead of stopping, and an info line says which line was taken.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text with several lines. | default '', multiline |
| index | INT | yes | Line to take, counting from 0. Negative counts from the end. | -100000 to 100000, default 0 |
| skip_blank | BOOLEAN | yes | Ignore empty lines when counting. | default True |
| out_of_range | COMBO | no | If the index is past the last line: stop with a message, wrap round to the start, or use the nearest end. | one of: error, wrap around, clamp to ends |
| strip | BOOLEAN | no | On: remove spaces around the picked line. | default False |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Connect a text with several lines to text.
2. Set index to the line you want. 0 is the first, -1 is the last. skip_blank ignores empty lines when counting.
3. out_of_range decides what happens when index is past the end: error, wrap around to the start (handy with a counter), or clamp to ends. strip trims spaces around the line.
4. The line comes out, plus the index really used and an info line.
