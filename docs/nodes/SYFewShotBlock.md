# Few Shot Block SY (`SYFewShotBlock`)

Source: `nodes/sy_few_shot_block.py`

**What it does:** Builds a few-shot text: your task, up to 4 worked examples, then the new input with an empty output line. An info line counts the examples used, warns about a half-filled example that was skipped, and gives a rough token count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| task | STRING | yes | What the examples teach, in plain words. | default '', multiline |
| new_input | STRING | yes | The new text that should be answered like the examples. | default '', multiline |
| input_label | STRING | yes | The word printed before each example input. | default 'Input' |
| output_label | STRING | yes | The word printed before each example output. | default 'Output' |
| example_in_1 | STRING | no | Example 1: the input. Empty skips the pair. | default '', multiline |
| example_out_1 | STRING | no | Example 1: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_2 | STRING | no | Example 2: the input. Empty skips the pair. | default '', multiline |
| example_out_2 | STRING | no | Example 2: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_3 | STRING | no | Example 3: the input. Empty skips the pair. | default '', multiline |
| example_out_3 | STRING | no | Example 3: the answer you want. Empty skips the pair. | default '', multiline |
| example_in_4 | STRING | no | Example 4: the input. Empty skips the pair. | default '', multiline |
| example_out_4 | STRING | no | Example 4: the answer you want. Empty skips the pair. | default '', multiline |

Outputs: `STRING`, `STRING`

## How to use

1. Write the job in task and the new item in new_input.
2. Fill example_in_1 and example_out_1 and so on, up to 4 pairs. A half-filled pair is skipped.
3. input_label and output_label name the lines (default Input and Output).
4. The text ends with an empty output line. info counts the examples and gives a rough token count.
