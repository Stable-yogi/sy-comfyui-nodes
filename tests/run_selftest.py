"""SY selftest. Checks every node against docs/SY-NODE-STANDARD.md, then runs tests/test_*.py.
Run: py -3.12 tests/run_selftest.py   (stdlib only, no window, no network)"""
import ast
import glob
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "nodes")
sys.path.insert(0, NODES)

FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__"}
FORBIDDEN_MODULES = {"subprocess", "socket", "requests", "urllib", "http", "ftplib", "ctypes", "pickle", "marshal"}
ALLOW = {}  # {"sy_xxx.py": {"subprocess"}} -- an audited exception, listed here and in the standard
AI_WORDS = re.compile(r"claude|anthropic|codex|openai|generated with|made with ai|co-authored-by", re.I)
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")

fails = []
checks = 0


def check(ok, msg):
    global checks
    checks += 1
    if not ok:
        fails.append(msg)


def scan_source(path):
    name = os.path.basename(path)
    allowed = ALLOW.get(name, set())
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FORBIDDEN_CALLS:
            check(False, "%s:%d forbidden call %s()" % (name, n.lineno, n.func.id))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in ("system", "popen", "startfile") and isinstance(n.func.value, ast.Name) and n.func.value.id == "os":
                check(False, "%s:%d forbidden os.%s" % (name, n.lineno, n.func.attr))
        mods = []
        if isinstance(n, ast.Import):
            mods = [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods = [n.module.split(".")[0]]
        for m in mods:
            if m in FORBIDDEN_MODULES and m not in allowed:
                check(False, "%s:%d forbidden import %s" % (name, n.lineno, m))
            if m in ("comfy", "folder_paths", "server", "nodes", "execution") and n.col_offset == 0:
                check(False, "%s:%d top-level import of %s (import inside a function)" % (name, n.lineno, m))
    check(not AI_WORDS.search(src), "%s mentions an AI credit word" % name)
    check(not HEX.search(src), "%s hard-codes a hex colour (use js/sy_theme.json)" % name)


def load(path):
    spec = importlib.util.spec_from_file_location("sy_mod_" + os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_theme():
    t = json.load(open(os.path.join(ROOT, "js", "sy_theme.json"), encoding="utf-8"))
    check("tokens" in t and "groups" in t, "theme file lacks tokens/groups")
    for g, v in t["groups"].items():
        check(HEX.fullmatch(v["color"]) and HEX.fullmatch(v["bgcolor"]), "theme group %s has a bad colour" % g)
    sys.path.insert(0, NODES)
    import _sy_common as c
    check(set(c.GROUPS) == set(t["groups"]), "GROUPS in _sy_common.py and groups in sy_theme.json differ")


def check_tooltips(base, cid, cls):
    """Every required/optional input needs a plain-English tooltip of 1..120 characters."""
    check(isinstance(getattr(cls, "DESCRIPTION", None), str) and cls.DESCRIPTION.strip() != "",
          "%s: %s has no DESCRIPTION text" % (base, cid))
    try:
        spec = cls.INPUT_TYPES()
    except Exception as e:
        check(False, "%s: %s INPUT_TYPES() failed: %s" % (base, cid, e))
        return
    for section in ("required", "optional"):
        for iname, d in (spec.get(section) or {}).items():
            opts = d[1] if isinstance(d, (tuple, list)) and len(d) > 1 and isinstance(d[1], dict) else {}
            tip = opts.get("tooltip")
            ok = isinstance(tip, str) and tip.strip() != "" and len(tip) <= 120
            check(ok, "%s: %s input '%s' (%s) needs a non-empty tooltip of at most 120 characters"
                  % (base, cid, iname, section))


def check_node_files():
    files = sorted(glob.glob(os.path.join(NODES, "sy_*.py")))
    check(len(files) > 0, "no node files found")
    names = set()
    for f in files:
        scan_source(f)
        mod = load(f)
        base = os.path.basename(f)
        cm = getattr(mod, "NODE_CLASS_MAPPINGS", None)
        dm = getattr(mod, "NODE_DISPLAY_NAME_MAPPINGS", None)
        check(cm and dm, "%s lacks the two mapping dicts" % base)
        if not cm:
            continue
        for cid, cls in cm.items():
            check(cid.startswith("SY") and cid[2:3].isupper(), "%s: class id %s must be SY<Name>" % (base, cid))
            check(cid not in names, "%s: duplicate class id %s" % (base, cid))
            names.add(cid)
            check(dm.get(cid, "").endswith(" SY"), "%s: display name of %s must end with ' SY'" % (base, cid))
            check(str(getattr(cls, "CATEGORY", "")).startswith("SY/"), "%s: CATEGORY of %s must start with 'SY/'" % (base, cid))
            check(bool(getattr(cls, "DESCRIPTION", "")), "%s: %s needs a DESCRIPTION" % (base, cid))
            check_tooltips(base, cid, cls)
            check(hasattr(cls, "INPUT_TYPES") and hasattr(cls, "RETURN_TYPES") and hasattr(cls, "FUNCTION"),
                  "%s: %s lacks INPUT_TYPES/RETURN_TYPES/FUNCTION" % (base, cid))
            check(hasattr(cls, getattr(cls, "FUNCTION", "?")), "%s: %s FUNCTION names a missing method" % (base, cid))
            stem = base[3:-3]
            test = os.path.join(ROOT, "tests", "test_sy_%s.py" % stem)
            check(os.path.exists(test), "%s: missing tests/test_sy_%s.py" % (base, stem))
    for f in glob.glob(os.path.join(NODES, "_sy_*.py")):
        scan_source(f)


def run_tests():
    for f in sorted(glob.glob(os.path.join(ROOT, "tests", "test_sy_*.py"))):
        try:
            mod = load(f)
            n = mod.run()
            global checks
            checks += int(n or 1)
        except BaseException as e:  # a failing test must be visible, not hidden
            fails.append("%s: %s: %s" % (os.path.basename(f), type(e).__name__, e))


def check_repo_text():
    for p in ("README.md", "NOTICE.md", "LICENSE", "pyproject.toml"):
        t = open(os.path.join(ROOT, p), encoding="utf-8").read()
        check(not AI_WORDS.search(t), "%s mentions an AI credit word" % p)
    check("Copyright (c) 2026 Stable Yogi" in open(os.path.join(ROOT, "LICENSE"), encoding="utf-8").read(), "LICENSE author line wrong")


if __name__ == "__main__":
    check_theme()
    check_node_files()
    run_tests()
    check_repo_text()
    for m in fails:
        print("FAIL", m)
    print("selftest: %s  (%d checks, %d failed)" % ("PASS" if not fails else "FAIL", checks, len(fails)))
    sys.exit(1 if fails else 0)
