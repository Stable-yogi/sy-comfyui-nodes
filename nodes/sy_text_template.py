"""Text Template SY: fills {name} placeholders in a text from up to four named values."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


MISSING = ("stop with an error", "keep the {name} as it is", "use empty text")


def fill_template(template, values, missing_mode=MISSING[0]):
    """Pure function. `values` is a dict name -> text. By default every {name} in the template must be in it.
    missing_mode can instead keep the {name} written out or fill it with nothing."""
    return template_report(template, values, missing_mode)[0]


def template_report(template, values, missing_mode=MISSING[0]):
    """Pure function. Returns (text, info)."""
    if not isinstance(template, str):
        raise ValueError("template must be a string, got %s" % type(template).__name__)
    if missing_mode not in MISSING:
        raise ValueError("missing_mode must be one of: %s" % ", ".join(MISSING))
    used = []
    for name in _PLACEHOLDER.findall(template):
        if name not in used:
            used.append(name)
    missing = [name for name in used if name not in values]
    if missing and missing_mode == MISSING[0]:
        raise ValueError("the template uses {%s} but no input has that name: set a name_N field to it"
                         % "}, {".join(missing))

    def fill(m):
        name = m.group(1)
        if name in values:
            return str(values[name])
        return m.group(0) if missing_mode == MISSING[1] else ""
    text = _PLACEHOLDER.sub(fill, template)
    filled = [name for name in used if name in values]
    if not used:
        info = "No {placeholders} in the template, so the text is unchanged"
    else:
        info = "Filled %d placeholder(s): %s" % (len(filled), ", ".join(filled) if filled else "none")
    if missing:
        info += "; %d without a value (%s): %s" % (len(missing), "kept" if missing_mode == MISSING[1] else "left empty", ", ".join("{%s}" % x for x in missing))
    unused = [name for name in values if name not in used]
    if unused:
        info += "; WARNING: input name(s) not used in the template: " + ", ".join(unused)
    return text, info


def build_values(pairs):
    """Pure function. `pairs` is a list of (name, value). Empty names are skipped; duplicates are refused."""
    values = {}
    for name, value in pairs:
        name = (name or "").strip()
        if name == "":
            continue
        if not _NAME.fullmatch(name):
            raise ValueError("name %r is not valid: use letters, digits and underscore, not starting with a digit" % name)
        if name in values:
            raise ValueError("the name %r is used twice: give each input its own name" % name)
        values[name] = value
    return values


class SYTextTemplate:
    DESCRIPTION = ("Fills {name} placeholders in a text with up to four named values. A name with no matching input gives an error, or you can keep it "
                   "or leave it empty. The info line lists what was filled and warns about names the template never uses.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        opt = {}
        for i, default in ((1, "name"), (2, "style"), (3, ""), (4, "")):
            opt["name_%d" % i] = ("STRING", {"default": default, "tooltip": "Placeholder name for value %d, used as {name} in the template." % i})
            opt["value_%d" % i] = ("STRING", {"default": "", "tooltip": "Text that replaces the placeholder named in name_%d." % i})
        opt["missing_mode"] = (list(MISSING), {"default": MISSING[0], "tooltip": "A {name} with no value: stop with an error, keep it as written, or fill it with nothing."})
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "a photo of {name}, {style}", "tooltip": "Text with {name} placeholders to fill in."}),
            },
            "optional": opt,
        }

    def run(self, template, name_1="", value_1="", name_2="", value_2="", name_3="", value_3="", name_4="", value_4="",
            missing_mode=MISSING[0]):
        values = build_values([(name_1, value_1), (name_2, value_2), (name_3, value_3), (name_4, value_4)])
        return template_report(template, values, missing_mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTemplate", SYTextTemplate)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTemplate"] = "Text Template SY"
