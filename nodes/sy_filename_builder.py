"""Filename Builder SY: turns a name pattern with tokens into a file name text."""
try:
    from ._sy_safe_paths import check_filename, clean_extension, expand_pattern
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import check_filename, clean_extension, expand_pattern
    from _sy_common import category, register


def build_filename(pattern, seed=0, counter=1, extension="", now=None):
    """Pure function. Fills {date} {time} {seed} {counter} and adds the extension. Checks the result is a plain name."""
    if not str(pattern).strip():
        raise ValueError("pattern is empty: type a name such as shot_{counter}")
    if int(counter) < 0:
        raise ValueError("counter must be 0 or more")
    name = expand_pattern(pattern, seed, now, counter=counter)
    return check_filename(name + clean_extension(extension))


class SYFilenameBuilder:
    DESCRIPTION = "Builds a file name from a pattern. Tokens: {date} {time} {seed} {counter}. Only makes text, saves nothing."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pattern": ("STRING", {"default": "shot_{date}_{counter}", "tooltip": "Name with tokens: {date} {time} {seed} {counter}. No slashes."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
                "counter": ("INT", {"default": 1, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Number used for the {counter} token, shown with 5 digits."}),
                "extension": ("STRING", {"default": "", "tooltip": "Optional ending such as png or .txt. Leave empty for none."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, pattern, seed, counter, extension):
        return float("nan") if "{time}" in str(pattern) else None

    def run(self, pattern, seed, counter, extension):
        return (build_filename(pattern, seed, counter, extension),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FilenameBuilder", SYFilenameBuilder)
NODE_DISPLAY_NAME_MAPPINGS["SYFilenameBuilder"] = "Filename Builder SY"
