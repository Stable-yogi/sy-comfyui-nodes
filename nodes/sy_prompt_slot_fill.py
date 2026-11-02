"""Prompt Slot Fill SY: fills named slots like [subject] in a template and drops empty ones cleanly."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DEFAULT_NAMES = ("subject", "place", "light", "style", "mood", "extra")
_SLOT = re.compile(r"\[([^\[\]]+)\]")


def clean_commas(text):
    """Pure function. Removes ', ,' runs, leading and trailing commas and double spaces."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r"(,\s*){2,}", ", ", text)
    text = re.sub(r"^[\s,]+|[\s,]+$", "", text)
    return text


def fill_slots(template, values):
    """Pure function. Returns (text, unused). `unused` lists slot names in the template with no value."""
    values = {str(k).strip(): str(v).strip() for k, v in (values or {}).items() if str(k).strip()}
    unused = []

    def sub(m):
        name = m.group(1).strip()
        val = values.get(name, "")
        if not val and name not in unused:
            unused.append(name)
        return val

    out = _SLOT.sub(sub, str(template or ""))
    return clean_commas(out), unused


class SYPromptSlotFill:
    DESCRIPTION = ("Fills named slots like [subject] or [place] in a template from up to six text inputs. "
                   "Empty slots disappear together with their stray comma.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "unused")

    @classmethod
    def INPUT_TYPES(cls):
        req = {"template": ("STRING", {"multiline": True, "default": "[subject], [place], [light], [style]", "tooltip": "Prompt with slots in square brackets, like [subject]."})}
        opt = {}
        for i, name in enumerate(DEFAULT_NAMES, 1):
            req["slot_%d_name" % i] = ("STRING", {"default": name, "tooltip": "Slot %d name. It matches [name] in the template." % i})
        for i in range(1, 7):
            opt["slot_%d" % i] = ("STRING", {"multiline": True, "default": "", "tooltip": "Text for slot %d. Leave empty to drop the slot." % i})
        return {"required": req, "optional": opt}

    def run(self, template, **kw):
        values = {}
        for i in range(1, 7):
            name = str(kw.get("slot_%d_name" % i, DEFAULT_NAMES[i - 1])).strip()
            if not name:
                continue
            if name in values:
                raise ValueError("slot name %r is used twice. Give every slot its own name" % name)
            values[name] = kw.get("slot_%d" % i, "")
        text, unused = fill_slots(template, values)
        return (text, ", ".join(unused))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptSlotFill", SYPromptSlotFill)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptSlotFill"] = "Prompt Slot Fill SY"
