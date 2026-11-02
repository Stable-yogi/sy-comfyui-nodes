"""Key Value Lookup SY: a tiny dictionary typed as 'key = value' lines."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_table(text, separator="="):
    """Pure function. Returns a list of (key, value) pairs. Blank lines and lines starting with # are skipped."""
    if separator is None or separator == "":
        raise ValueError("separator must not be empty: type the mark that sits between key and value, for example =")
    pairs = []
    for number, raw in enumerate(str(text).splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if separator not in line:
            raise ValueError("line %d has no %r in it: write it as key %s value, or start the line with # to skip it"
                             % (number, separator, separator))
        key, value = line.split(separator, 1)
        key = key.strip()
        if not key:
            raise ValueError("line %d has no key before %r: put a word in front of it" % (number, separator))
        pairs.append((key, value.strip()))
    return pairs


def lookup(pairs, key, ignore_case=True, default=""):
    """Pure function. First match wins. Returns (value, found)."""
    wanted = str(key).strip()
    if ignore_case:
        wanted = wanted.lower()
    for k, v in pairs:
        if (k.lower() if ignore_case else k) == wanted:
            return (v, True)
    return (default, False)


class SYKeyValueLookup:
    DESCRIPTION = ("A tiny dictionary. Type lines like 'knight = a tall man in steel armour', "
                   "then give a key and get its text back. The first matching line wins.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("value", "found")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "table": ("STRING", {"multiline": True, "default": "", "tooltip": "One 'key = value' per line. Lines starting with # are ignored."}),
                "key": ("STRING", {"default": "", "tooltip": "The key to look up."}),
                "default": ("STRING", {"default": "", "tooltip": "Text to give back when the key is not in the table."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On: Knight and knight count as the same key."}),
                "separator": ("STRING", {"default": "=", "tooltip": "The mark between key and value on each line."}),
            },
        }

    def run(self, table, key, default="", ignore_case=True, separator="="):
        return lookup(parse_table(table, separator), key, ignore_case, default)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "KeyValueLookup", SYKeyValueLookup)
NODE_DISPLAY_NAME_MAPPINGS["SYKeyValueLookup"] = "Key Value Lookup SY"
