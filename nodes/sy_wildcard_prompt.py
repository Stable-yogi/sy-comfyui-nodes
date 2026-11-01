"""Wildcard Prompt SY: one prompt with random variety ({a|b|c}, nested, N$$, __lists__). Same seed, same prompt."""
import itertools
import os
import random
import re

try:
    from ._sy_common import category, register, safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join

MODES = ("random from seed", "step through (index)")
MAX_DEPTH = 5
MAX_CHARS = 10000
COUNT_CAP = 1000000
MAX_SEED = 2 ** 64 - 1
ESCAPABLE = "{}|_\\"
_WILD = re.compile(r"__([A-Za-z0-9][A-Za-z0-9_\-./]*?)__")
_HEAD = re.compile(r"\s*(\d+)\s*\$\$")
_WEIGHT = re.compile(r"(-?(?:\d+(?:\.\d+)?|\.\d+))\s*::")
MAX_WEIGHT = 1000.0


# ---------------------------------------------------------------- wildcard lists
def parse_wildcards(text):
    """Pure function. 'name: line1 | line2' per line -> {name: [lines]}. Blank lines and # lines are skipped."""
    out = {}
    for no, raw in enumerate((text or "").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError("wildcards box, line %d: write it as  name: first | second | third  (no colon found)" % no)
        name, rest = line.split(":", 1)
        name = name.strip().lower()
        items = [p.strip() for p in rest.split("|") if p.strip()]
        if not name:
            raise ValueError("wildcards box, line %d: the list has no name before the colon" % no)
        if not items:
            raise ValueError("wildcards box, line %d: the list '%s' is empty, add at least one option after the colon" % (no, name))
        out[name] = items
    return out


def parse_wildcard_file_text(name, text):
    """Pure function. Lines of a wildcard text file (blank and # lines skipped). An empty list is refused."""
    items = [ln.strip() for ln in (text or "").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not items:
        raise ValueError("the wildcard list '%s' is empty: put at least one line in wildcards/%s.txt" % (name, name))
    return items


def load_wildcard_file(base_dir, name):
    """Reads <base_dir>/wildcards/<name>.txt through the path guard. Plain refusal when it is missing or empty."""
    try:
        path = safe_join(base_dir, "wildcards", name + ".txt")
    except ValueError:
        raise ValueError("the wildcard name '%s' is not allowed: use plain letters, numbers and dashes" % name)
    if not os.path.isfile(path):
        raise ValueError("the wildcard list '%s' was not found: save wildcards/%s.txt in the ComfyUI input folder "
                         "or write  %s: a | b | c  in the wildcards box" % (name, name, name))
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_wildcard_file_text(name, f.read())


# ---------------------------------------------------------------- parser
def _where(text, pos):
    line = text.count("\n", 0, pos) + 1
    return "character %d (line %d)" % (pos + 1, line)


class _Parser:
    def __init__(self, text):
        self.t = text
        self.i = 0

    def seq(self, depth):
        """Parse until | or } (inside a group) or the end. Returns the list of nodes."""
        t = self.t
        nodes = []
        buf = []

        def flush():
            if buf:
                nodes.append(("lit", "".join(buf)))
                del buf[:]
        while self.i < len(t):
            ch = t[self.i]
            if ch == "\\" and self.i + 1 < len(t) and t[self.i + 1] in ESCAPABLE:
                buf.append(t[self.i + 1])
                self.i += 2
            elif ch == "{":
                flush()
                nodes.append(self.group(depth + 1))
            elif ch == "}":
                if depth == 0:
                    raise ValueError("a closing brace at %s has no opening brace. Remove it, or write \\} for a plain brace" % _where(t, self.i))
                break
            elif ch == "|" and depth > 0:
                break
            elif ch == "_":
                m = _WILD.match(t, self.i)
                if m:
                    flush()
                    nodes.append(("wild", m.group(1).strip().lower(), m.group(0)))
                    self.i = m.end()
                else:
                    buf.append(ch)
                    self.i += 1
            else:
                buf.append(ch)
                self.i += 1
        flush()
        return nodes

    def group(self, depth):
        t = self.t
        start = self.i
        if depth > MAX_DEPTH:
            raise ValueError("the braces at %s are nested more than %d levels deep. Flatten the prompt" % (_where(t, start), MAX_DEPTH))
        self.i += 1
        k = 1
        m = _HEAD.match(t, self.i)
        if m:
            k = int(m.group(1))
            self.i = m.end()
        options = []
        weights = []
        while True:
            opt, wt = _take_weight(_strip(self.seq(depth)))
            options.append(opt)
            weights.append(wt)
            if self.i >= len(t):
                raise ValueError("the opening brace at %s is never closed. Add a closing brace, or write \\{ for a plain brace" % _where(t, start))
            if t[self.i] == "}":
                self.i += 1
                break
            self.i += 1  # the |
        if all(not o for o in options):
            raise ValueError("the choice list at %s is empty. Put at least one option inside, like {red|blue}" % _where(t, start))
        if k < 1:
            raise ValueError("the choice list at %s asks to pick %d options. Use 1 or more" % (_where(t, start), k))
        if k > len(options):
            raise ValueError("the choice list at %s asks to pick %d different options but has only %d" % (_where(t, start), k, len(options)))
        src = t[start:self.i]
        shown = src if len(src) <= 60 else src[:57] + "..."
        for no, wt in enumerate(weights, 1):
            if wt is not None and not 0 < wt <= MAX_WEIGHT:
                raise ValueError("the choice list %s at %s has a weight of %s on option %d. A weight must be above 0 and at most %d. "
                                 "Write it like {3::red|1::blue}" % (shown, _where(t, start), _num(wt), no, int(MAX_WEIGHT)))
        if all(wt is None for wt in weights):
            weights = None
        else:
            weights = [1.0 if wt is None else wt for wt in weights]
        return ("group", k, options, src, weights)


def _take_weight(nodes):
    """Pure function. An option that starts with  number::  carries a weight. Returns (nodes without it, weight or None).
    Only the very start of the option counts: a::b inside the text stays plain text."""
    if nodes and nodes[0][0] == "lit":
        m = _WEIGHT.match(nodes[0][1])
        if m:
            rest = nodes[0][1][m.end():].lstrip()
            nodes = list(nodes)
            nodes[0:1] = [("lit", rest)] if rest else []
            return nodes, float(m.group(1))
    return nodes, None


def _strip(nodes):
    """Trim the spaces at both ends of one option."""
    nodes = list(nodes)
    if nodes and nodes[0][0] == "lit":
        s = nodes[0][1].lstrip()
        nodes[0:1] = [("lit", s)] if s else []
    if nodes and nodes[-1][0] == "lit":
        s = nodes[-1][1].rstrip()
        nodes[-1:] = [("lit", s)] if s else []
    return nodes


def _parse(text):
    p = _Parser(text or "")
    nodes = p.seq(0)
    return nodes


def _walk(nodes):
    for n in nodes:
        yield n
        if n[0] == "group":
            for o in n[2]:
                for x in _walk(o):
                    yield x


def _num(x):
    return str(int(x)) if x == int(x) else repr(x)


def has_weights(text):
    """Pure function. True when any {...} group of the text has a  number::  weight."""
    return any(n[0] == "group" and n[4] is not None for n in _walk(_parse(text)))


def weighted_sample(rng, weights, k):
    """Pure function. k different indexes picked by weight, without putting back. Same rng state, same answer."""
    left = list(range(len(weights)))
    out = []
    for _ in range(k):
        total = sum(weights[i] for i in left)
        r = rng.random() * total
        pick = left[-1]
        acc = 0.0
        for i in left:
            acc += weights[i]
            if r < acc:
                pick = i
                break
        out.append(pick)
        left.remove(pick)
    return out


def describe(text):
    """Pure function. (number of choice groups, sorted wildcard names used)."""
    nodes = _parse(text)
    groups = sum(1 for n in _walk(nodes) if n[0] == "group")
    names = sorted({n[1] for n in _walk(nodes) if n[0] == "wild"})
    return groups, names


def wildcard_names(text):
    return describe(text)[1]


# ---------------------------------------------------------------- counting
def _lookup(wl, name):
    key = name.lower()
    if key not in wl:
        known = ", ".join(sorted(wl)) or "none"
        raise ValueError("unknown wildcard list '%s'. Known lists: %s" % (name, known))
    if not wl[key]:
        raise ValueError("the wildcard list '%s' is empty" % name)
    return wl[key]


def _esp(counts, k):
    """Sum over all k-subsets of the product of their counts."""
    dp = [1] + [0] * k
    for c in counts:
        for j in range(k, 0, -1):
            dp[j] += dp[j - 1] * c
    return dp[k]


class _Ctx:
    def __init__(self, wl, rng=None, index=None):
        self.wl = {k.lower(): v for k, v in (wl or {}).items()}
        self.rng = rng
        self.step = index is not None
        self.index = index
        self.picks = []
        self.memo = {}

    def count_seq(self, seq):
        c = 1
        for n in seq:
            c *= self.count(n)
        return c

    def count(self, n):
        key = id(n)
        if key in self.memo:
            return self.memo[key]
        if n[0] == "lit":
            c = 1
        elif n[0] == "wild":
            c = len(_lookup(self.wl, n[1]))
        else:
            counts = [self.count_seq(o) for o in n[2]]
            c = sum(counts) if n[1] == 1 else _esp(counts, n[1])
        self.memo[key] = c
        return c

    # evaluation
    def ev_seq(self, seq, idx):
        out = []
        for n in seq:
            if idx is None:
                sub = None
            else:
                c = self.count(n)
                sub = idx % c
                idx //= c
            out.append(self.ev(n, sub))
        return "".join(out)

    def ev(self, n, sub):
        if n[0] == "lit":
            return n[1]
        if n[0] == "wild":
            items = _lookup(self.wl, n[1])
            line = items[sub if sub is not None else self.rng.randrange(len(items))]
            self.picks.append("%s -> %s" % (n[2], line))
            return line
        _, k, options, src, weights = n
        slot = len(self.picks)
        self.picks.append("")
        if sub is None:
            if weights is None:
                chosen = sorted(self.rng.sample(range(len(options)), k))
            else:
                chosen = sorted(weighted_sample(self.rng, weights, k))
            subs = [None] * k
        else:
            chosen, subs = self._unrank(options, k, sub)
        parts = [self.ev_seq(options[i], s) for i, s in zip(chosen, subs)]
        text = ", ".join(parts)
        shown = src if len(src) <= 60 else src[:57] + "..."
        self.picks[slot] = "%s -> %s" % (shown, text)
        return text

    def _unrank(self, options, k, sub):
        counts = [self.count_seq(o) for o in options]
        if k == 1:
            for i, c in enumerate(counts):
                if sub < c:
                    return [i], [sub]
                sub -= c
        for combo in itertools.combinations(range(len(options)), k):
            c = 1
            for i in combo:
                c *= counts[i]
            if sub < c:
                subs = []
                for i in combo:
                    subs.append(sub % counts[i])
                    sub //= counts[i]
                return list(combo), subs
            sub -= c
        raise ValueError("internal: step index out of range")


def possible_count(text, wildcards=None):
    """Pure function. How many different results the template can give (every pick counted)."""
    ctx = _Ctx(wildcards)
    return ctx.count_seq(_parse(text))


def count_text(n):
    return ">%d" % COUNT_CAP if n > COUNT_CAP else str(n)


def expand(text, seed, wildcards=None, index=None):
    """Pure function. Returns (prompt, picks). picks = one line per choice, like '{red|blue} -> blue'.
    index None: random from the seed. index given: step through, one number walks all combinations
    (the first choice moves fastest, like the digits of a counter)."""
    nodes = _parse(text)
    rng = random.Random(int(seed))
    ctx = _Ctx(wildcards, rng, None if index is None else max(0, int(index)))
    if ctx.step:
        ctx.count_seq(nodes)  # fail early on unknown lists
    out = ctx.ev_seq(nodes, ctx.index if ctx.step else None)
    if len(out) > MAX_CHARS:
        raise ValueError("the result is %d characters long, more than the limit of %d. Use shorter lists or fewer choices" % (len(out), MAX_CHARS))
    return out, ctx.picks


def info_text(text, groups, names, seed, mode, index, total, picks, weighted=False):
    """Pure function. One plain line of counts."""
    bits = ["%d choice group%s" % (groups, "" if groups == 1 else "s"),
            "%d wildcard list%s used%s" % (len(names), "" if len(names) == 1 else "s", (" (" + ", ".join(names) + ")") if names else "")]
    if mode == MODES[1]:
        bits.append("step %d" % index)
    else:
        bits.append("seed %d" % seed)
    bits.append("%s possible result%s" % (count_text(total), "" if total == 1 else "s"))
    if weighted:
        bits.append("weights used" if mode != MODES[1] else "weights ignored while stepping")
    return "Wildcard Prompt: " + ", ".join(bits)


def run_template(text, seed, mode, index, inline_text, load_file, enabled=True):
    """Pure-ish helper the node uses. load_file(name) -> list, only called for lists not written in the box."""
    if not enabled:
        return text, "", "Wildcard Prompt: off, the text was passed through unchanged"
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
    wl = parse_wildcards(inline_text)
    groups, names = describe(text)
    for name in names:
        if name not in wl:
            wl[name] = load_file(name)
    step = mode == MODES[1]
    idx = int(index or 0) if step else None
    prompt, picks = expand(text, seed, wl, idx)
    total = possible_count(text, wl)
    return prompt, "\n".join(picks), info_text(text, groups, names, int(seed), mode, idx or 0, total, picks, has_weights(text))


class SYWildcardPrompt:
    DESCRIPTION = ("One prompt with random variety. Write {red|blue|green} to pick one, {2$$a|b|c} to pick two different, "
                   "__name__ to take a line from a wildcard list. Same seed gives the same prompt. Step through walks every "
                   "combination with one number. Shows what was picked. Give an option a weight with  number::  at its start, like "
                   "{3::red|1::blue|green} (red is 3 times as likely as green; no number means 1; only in {...} groups, not in "
                   "wildcard list lines; step through ignores weights). Lists come from the wildcards box or from "
                   "wildcards/<name>.txt in the input folder. Replaces a prompt-random node plus a list loader plus a text note.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "picks", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "a {red|blue|green} coat at {sunrise|sunset}",
                                    "tooltip": "Template. {a|b} picks one, {2$$a|b|c} two, __name__ a list line, {3::a|1::b} weighted. Example: a {3::red|1::blue} coat"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "control_after_generate": True,
                                 "tooltip": "Same seed gives the same prompt. Example: 12345"}),
                "mode": (list(MODES), {"default": MODES[0], "tooltip": "random from seed, or step through the combinations with index."}),
            },
            "optional": {
                "wildcards": ("STRING", {"multiline": True, "default": "",
                                         "tooltip": "Lists, one per line: name: first | second | third. Example: hair: red | blonde"}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 53 - 1,
                                  "tooltip": "Step-through number: 0, 1, 2 ... walks every combination, then repeats."}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off passes the text through unchanged, braces and all."}),
            },
        }

    def run(self, text, seed, mode, wildcards="", index=0, enabled=True):
        def load(name):
            import folder_paths
            return load_wildcard_file(folder_paths.get_input_directory(), name)
        return run_template(text, seed, mode, index, wildcards, load, enabled)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "WildcardPrompt", SYWildcardPrompt)
NODE_DISPLAY_NAME_MAPPINGS["SYWildcardPrompt"] = "Wildcard Prompt SY"
