"""Prompt Variants SY: expands {red|blue|green} choices in a template into every combination."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_template(template):
    """Pure function. Returns a list of parts: ('lit', text) or ('opt', [choices]). No nested braces."""
    template = str(template or "")
    parts, buf, i, n = [], [], 0, len(template)
    while i < n:
        ch = template[i]
        if ch == "\\" and i + 1 < n and template[i + 1] in "{}":
            buf.append(template[i + 1])
            i += 2
        elif ch == "{":
            if buf:
                parts.append(("lit", "".join(buf)))
                buf = []
            j, group, cur = i + 1, [], []
            while True:
                if j >= n:
                    raise ValueError("a { has no closing } in the template. Add the } or write \\{ for a plain brace")
                c = template[j]
                if c == "\\" and j + 1 < n and template[j + 1] in "{}":
                    cur.append(template[j + 1])
                    j += 2
                    continue
                if c == "{":
                    raise ValueError("braces inside braces are not supported. Write the choices on one level, like {a|b|c}")
                if c == "}":
                    break
                if c == "|":
                    group.append("".join(cur))
                    cur = []
                else:
                    cur.append(c)
                j += 1
            group.append("".join(cur))
            parts.append(("opt", group))
            i = j + 1
        elif ch == "}":
            raise ValueError("a } has no opening { in the template. Remove it or write \\} for a plain brace")
        else:
            buf.append(ch)
            i += 1
    if buf:
        parts.append(("lit", "".join(buf)))
    return parts


def total_count(template):
    total = 1
    for kind, val in parse_template(template):
        if kind == "opt":
            total *= len(val)
    return total


def combination(template, index):
    """Pure function. The combination at `index` (wraps around). First group changes slowest."""
    parts = parse_template(template)
    total = 1
    for kind, val in parts:
        if kind == "opt":
            total *= len(val)
    index = int(index) % total
    picks = {}
    for pos in range(len(parts) - 1, -1, -1):
        kind, val = parts[pos]
        if kind == "opt":
            index, r = divmod(index, len(val))
            picks[pos] = val[r]
    return "".join(val if kind == "lit" else picks[pos] for pos, (kind, val) in enumerate(parts))


def expand(template, cap=500):
    """Pure function. Returns up to `cap` combinations, first group changing slowest."""
    cap = int(cap)
    if cap < 1:
        raise ValueError("max_combinations must be at least 1, got %d" % cap)
    total = total_count(template)
    return [combination(template, i) for i in range(min(total, cap))]


class SYPromptVariants:
    DESCRIPTION = ("Turns a template with {red|blue|green} choices into every combination. "
                   "Returns one picked by index (wraps around) plus the full list for batch runs.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("text", "all_text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "a {red|blue|green} car", "tooltip": "Text with choices in braces, like {red|blue}. Use \\{ for a plain brace."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which combination to return. Too big a number wraps around."}),
                "max_combinations": ("INT", {"default": 500, "min": 1, "max": 10000, "tooltip": "Most combinations to list in all_text."}),
            }
        }

    def run(self, template, index, max_combinations):
        total = total_count(template)
        return (combination(template, index), "\n".join(expand(template, max_combinations)), total)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptVariants", SYPromptVariants)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptVariants"] = "Prompt Variants SY"
