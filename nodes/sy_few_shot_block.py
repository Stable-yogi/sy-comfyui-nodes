"""Few Shot Block SY: builds a text block with a task, worked examples and the new input."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
MAX_PAIRS = 4


def few_shot_block(task, pairs, new_input, input_label="Input", output_label="Output"):
    """Pure function. pairs is a list of (example_in, example_out). Returns the block text."""
    task = "" if task is None else str(task).strip()
    new_input = "" if new_input is None else str(new_input).strip()
    input_label = "Input" if input_label is None or str(input_label).strip() == "" else str(input_label).strip()
    output_label = "Output" if output_label is None or str(output_label).strip() == "" else str(output_label).strip()
    if new_input == "":
        raise ValueError("new_input is empty: type the text the examples should be applied to")
    total = len(task) + len(new_input)
    blocks = []
    if task:
        blocks.append(task)
    for ex_in, ex_out in pairs:
        ex_in = "" if ex_in is None else str(ex_in).strip()
        ex_out = "" if ex_out is None else str(ex_out).strip()
        total += len(ex_in) + len(ex_out)
        if ex_in == "" or ex_out == "":
            continue
        blocks.append("%s: %s\n%s: %s" % (input_label, ex_in, output_label, ex_out))
    if total > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (total, MAX_INPUT))
    blocks.append("%s: %s\n%s:" % (input_label, new_input, output_label))
    return "\n\n".join(blocks)


class SYFewShotBlock:
    DESCRIPTION = "Builds a few-shot text: your task, up to 4 worked examples, then the new input with an empty output line."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "task": ("STRING", {"default": "", "multiline": True, "tooltip": "What the examples teach, in plain words."}),
            "new_input": ("STRING", {"default": "", "multiline": True, "tooltip": "The new text that should be answered like the examples."}),
            "input_label": ("STRING", {"default": "Input", "tooltip": "The word printed before each example input."}),
            "output_label": ("STRING", {"default": "Output", "tooltip": "The word printed before each example output."}),
        }
        optional = {}
        for i in range(1, MAX_PAIRS + 1):
            optional["example_in_%d" % i] = ("STRING", {"default": "", "multiline": True, "tooltip": "Example %d: the input. Empty skips the pair." % i})
            optional["example_out_%d" % i] = ("STRING", {"default": "", "multiline": True, "tooltip": "Example %d: the answer you want. Empty skips the pair." % i})
        return {"required": required, "optional": optional}

    def run(self, task, new_input, input_label="Input", output_label="Output", **kw):
        pairs = [(kw.get("example_in_%d" % i, ""), kw.get("example_out_%d" % i, "")) for i in range(1, MAX_PAIRS + 1)]
        return (few_shot_block(task, pairs, new_input, input_label, output_label),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FewShotBlock", SYFewShotBlock)
NODE_DISPLAY_NAME_MAPPINGS["SYFewShotBlock"] = "Few Shot Block SY"
