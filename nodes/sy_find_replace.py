"""Find Replace SY: replace text, plain or with a regular expression, and count the changes."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_PATTERN = 500
MAX_INPUT = 1000000


def find_replace(text, find, replace, use_regex=False, case_sensitive=True, whole_word=False, max_count=0):
    """Pure function. Returns (new_text, number_of_replacements). whole_word skips matches inside longer words. max_count 0 means all."""
    text = "" if text is None else str(text)
    find = "" if find is None else str(find)
    replace = "" if replace is None else str(replace)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if len(find) > MAX_PATTERN:
        raise ValueError("find is too long: %d characters (limit %d)" % (len(find), MAX_PATTERN))
    if find == "":
        return text, 0
    if max_count < 0:
        raise ValueError("max_count must be 0 (all) or more, got %d" % max_count)
    flags = 0 if case_sensitive else re.IGNORECASE
    if use_regex:
        source = "(?<!\\w)(?:%s)(?!\\w)" % find if whole_word else find
        try:
            pattern = re.compile(source, flags)
        except re.error as e:
            raise ValueError("bad regular expression %r: %s" % (find, e))
        try:
            return pattern.subn(replace, text, count=max_count)
        except (re.error, IndexError) as e:
            raise ValueError("bad replacement %r: %s" % (replace, e))
    source = re.escape(find)
    if whole_word:
        source = "(?<!\\w)" + source + "(?!\\w)"
    pattern = re.compile(source, flags)
    return pattern.subn(lambda m: replace, text, count=max_count)


def parse_rules(rules):
    """Pure function. One rule per line: old => new. Blank lines and lines starting with # are skipped. Returns [(old, new)]."""
    out = []
    for number, line in enumerate((rules or "").replace("\r\n", "\n").split("\n"), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=>" not in line:
            raise ValueError('rules line %d has no "=>": write it like  old words => new words' % number)
        old, new = line.split("=>", 1)
        old, new = old.strip(), new.strip()
        if not old:
            raise ValueError("rules line %d has nothing before the =>" % number)
        out.append((old, new))
    return out


def apply_rules(text, rules, case_sensitive=True, whole_word=False):
    """Pure function. Runs the rules in order on plain text. Returns (new_text, total_replacements)."""
    total = 0
    for old, new in parse_rules(rules):
        text, k = find_replace(text, old, new, False, case_sensitive, whole_word)
        total += k
    return text, total


def replace_info(text, find, count, case_sensitive=True, rules_count=0):
    """Pure function. One plain line: what happened, or why nothing matched."""
    if count:
        return "Replaced %d time%s." % (count, "" if count == 1 else "s")
    if not find and not rules_count:
        return "Nothing to do: find is empty."
    if case_sensitive and find and find.lower() in (text or "").lower():
        return "No exact match, but the text is there in other capital letters: turn case_sensitive off."
    return "No match found, the text is unchanged."


class SYFindReplace:
    DESCRIPTION = ("Finds text and replaces it: plain words, whole words only, or patterns (regex), with a limit on how many. A rules box "
                   "applies a whole list of 'old => new' changes in one go. Gives the count and an info line that also says "
                   "when a capital-letter difference was the reason nothing matched.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text you want to change."}),
                "find": ("STRING", {"default": "", "tooltip": "The words to look for in the text."}),
                "replace": ("STRING", {"default": "", "tooltip": "What to put in place of every match. Empty removes the match."}),
                "use_regex": ("BOOLEAN", {"default": False, "tooltip": "On: Find is a pattern (regex) for advanced matching. Off: plain words."}),
                "case_sensitive": ("BOOLEAN", {"default": True, "tooltip": "On: Cat and cat are different. Off: capital letters are ignored."}),
            },
            "optional": {
                "whole_word": ("BOOLEAN", {"default": False, "tooltip": "On: cat does not match inside category. Off: any match counts."}),
                "max_count": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "Replace only the first N matches. 0 means all of them."}),
                "rules": ("STRING", {"default": "", "multiline": True, "tooltip": "More changes, one per line: old => new. Run after the find above. Lines starting with # are skipped."}),
            },
        }

    def run(self, text, find, replace, use_regex=False, case_sensitive=True, whole_word=False, max_count=0, rules=""):
        out, count = find_replace(text, find, replace, use_regex, case_sensitive, whole_word, max_count)
        n_rules = len(parse_rules(rules))
        if n_rules:
            out, more = apply_rules(out, rules, case_sensitive, whole_word)
            count += more
        return out, count, replace_info(text, find, count, case_sensitive, n_rules)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FindReplace", SYFindReplace)
NODE_DISPLAY_NAME_MAPPINGS["SYFindReplace"] = "Find Replace SY"
