"""Text Template SY: fills {name} placeholders in a text from up to four named values."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def fill_template(template, values):
    """Pure function. `values` is a dict name -> text. Every {name} in the template must be in it."""
    if not isinstance(template, str):
        raise ValueError("template must be a string, got %s" % type(template).__name__)
    missing = []
    for name in _PLACEHOLDER.findall(template):
        if name not in values and name not in missing:
            missing.append(name)
    if missing:
        raise ValueError("the template uses {%s} but no input has that name: set a name_N field to it"
                         % "}, {".join(missing))
    return _PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), template)


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
    DESCRIPTION = "Fills {name} placeholders in a text with up to four named values. A name with no matching input gives an error."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        opt = {}
        for i, default in ((1, "name"), (2, "style"), (3, ""), (4, "")):
            opt["name_%d" % i] = ("STRING", {"default": default, "tooltip": "Placeholder name for value %d, used as {name} in the template." % i})
            opt["value_%d" % i] = ("STRING", {"default": "", "tooltip": "Text that replaces the placeholder named in name_%d." % i})
        return {
            "required": {
                "template": ("STRING", {"multiline": True, "default": "a photo of {name}, {style}", "tooltip": "Text with {name} placeholders to fill in."}),
            },
            "optional": opt,
        }

    def run(self, template, name_1="", value_1="", name_2="", value_2="", name_3="", value_3="", name_4="", value_4=""):
        values = build_values([(name_1, value_1), (name_2, value_2), (name_3, value_3), (name_4, value_4)])
        return (fill_template(template, values),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTemplate", SYTextTemplate)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTemplate"] = "Text Template SY"
