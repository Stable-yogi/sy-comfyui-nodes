# Filename Builder SY (`SYFilenameBuilder`)

Source: `nodes/sy_filename_builder.py`

**What it does:** Builds a file name from a pattern. Tokens: {date} {time} {seed} {counter}, and {model} {width} {height} when you fill those boxes. Optional auto_clean tidies spaces and forbidden characters instead of failing. Also gives the name without its ending (stem) and an info line. Only makes text, saves nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| pattern | STRING | yes | Name with tokens: {date} {time} {seed} {counter}. No slashes. | default 'shot_{date}_{counter}' |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| counter | INT | yes | Number used for the {counter} token, shown with 5 digits. | 0 to 2147483647, default 1 |
| extension | STRING | yes | Optional ending such as png or .txt. Leave empty for none. | default '' |
| model | STRING | no | Text for the {model} token. A path or ending is cut off. | default '' |
| width | INT | no | Number for the {width} token. | 0 to 100000, default 0 |
| height | INT | no | Number for the {height} token. | 0 to 100000, default 0 |
| auto_clean | BOOLEAN | no | On: spaces become _ and forbidden characters are replaced instead of an error. | default False |

Outputs: `STRING`, `STRING`, `STRING`

## How to use

1. Write a pattern. Tokens: {date} {time} {seed} {counter}, and {model} {width} {height} when you fill those boxes.
2. Set seed, counter and extension.
3. Turn on auto_clean to tidy spaces and forbidden characters instead of failing.
4. Outputs: filename, stem (without the ending) and info. It only makes text and saves nothing.
