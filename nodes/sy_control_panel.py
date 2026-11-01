"""Control Panel SY: one node that holds many dials (number, whole number, switch, text, dropdown, seed). Each row has its own name and range."""
import json
import math
import secrets

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_ROWS = 32
MAX_SEED = 2 ** 53 - 1  # the biggest whole number a browser keeps exactly
KINDS = ("float", "int", "switch", "text", "dropdown", "seed")
SEED_MODES = ("fixed", "random", "increment")
OUT_TYPES = {"float": "FLOAT", "int": "INT", "seed": "INT", "switch": "BOOLEAN", "text": "STRING", "dropdown": "STRING"}
_last_seed = {}  # (node id, row number) -> (value seen, seed used) for the increment mode


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")


def _fail(row, what):
    raise ValueError("Row %d: %s Fix it in the Control Panel, or delete the row." % (row, what))


def _number(value, what, row, allow_none=False):
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _fail(row, "%s must be a number, got %r." % (what, value))
    if math.isnan(value) or math.isinf(value):
        _fail(row, "%s is not a usable number." % what)
    return float(value) if isinstance(value, float) else value


def parse_rows(text):
    """Pure function. The rows text (a JSON list) -> clean rows
    {"name", "kind", "value", "min", "max", "step", "options", "mode"}. Plain refusal for anything unreadable."""
    if text is None or not str(text).strip():
        return []
    try:
        data = json.loads(text)
    except ValueError:
        raise ValueError("The Control Panel rows are not readable. Use the panel on the node, or reset the rows to [].")
    if not isinstance(data, list):
        raise ValueError("The Control Panel rows must be a list. Use the panel on the node.")
    if len(data) > MAX_ROWS:
        raise ValueError("There are %d rows but the most allowed is %d. Delete some rows." % (len(data), MAX_ROWS))
    rows = []
    for i, r in enumerate(data, 1):
        if not isinstance(r, dict):
            raise ValueError("Row %d is not a Control Panel row. Delete it in the panel." % i)
        kind = r.get("kind", "float")
        if kind not in KINDS:
            _fail(i, "the kind %r is not one of: %s." % (kind, ", ".join(KINDS)))
        name = r.get("name", "")
        if name is None:
            name = ""
        if not isinstance(name, str):
            _fail(i, "the name must be text, got %r." % (name,))
        mn = _number(r.get("min"), "the lowest value", i, True)
        mx = _number(r.get("max"), "the highest value", i, True)
        if mn is not None and mx is not None and mn > mx:
            _fail(i, "the lowest value %g is above the highest value %g." % (mn, mx))
        step = _number(r.get("step"), "the step", i, True)
        if step is not None and step <= 0:
            _fail(i, "the step must be above 0.")
        options = r.get("options", [])
        if options is None:
            options = []
        if not isinstance(options, list) or not all(isinstance(o, str) for o in options):
            _fail(i, "the dropdown list must be a list of text entries.")
        mode = r.get("mode", "fixed")
        if mode not in SEED_MODES:
            _fail(i, "the seed mode %r is not one of: %s." % (mode, ", ".join(SEED_MODES)))
        value = r.get("value")
        if kind in ("float", "int", "seed"):
            value = _number(0 if value is None else value, "the value", i)
        elif kind == "switch":
            if value is None:
                value = False
            if not isinstance(value, bool):
                _fail(i, "the switch must be true or false, got %r." % (value,))
        else:
            value = "" if value is None else value
            if not isinstance(value, str):
                _fail(i, "the value must be text, got %r." % (value,))
        rows.append({"name": name.strip(), "kind": kind, "value": value, "min": mn, "max": mx, "step": step,
                     "options": [o for o in options], "mode": mode})
    return rows


def rows_to_json(rows):
    """Pure function. Rows -> the JSON text stored in the node."""
    return json.dumps(rows)


def row_label(row, number):
    """Pure function. The name shown for a row; rows without a name are called Row N."""
    return row["name"] or "Row %d" % number


def seed_for_run(row, key):
    """Pure function (the increment memory is the only state). The seed this run uses."""
    value = max(0, min(int(row["value"]), MAX_SEED))
    mode = row["mode"]
    if mode == "fixed":
        return value
    if mode == "random":
        return secrets.randbelow(MAX_SEED + 1)
    seen, used = _last_seed.get(key, (None, None))
    nxt = value if seen != value or used is None else (used + 1) % (MAX_SEED + 1)
    _last_seed[key] = (value, nxt)
    return nxt


def row_output(row, number, key=None):
    """Pure function. The value row number `number` (1 based) sends out."""
    kind, value = row["kind"], row["value"]
    if kind == "float":
        return float(value)
    if kind == "int":
        return int(round(value))
    if kind == "seed":
        return seed_for_run(row, (key, number))
    if kind == "switch":
        return bool(value)
    if kind == "dropdown":
        if row["options"] and value not in row["options"]:
            raise ValueError("Row %d (%s): '%s' is not in the dropdown list. Pick it again in the Control Panel." % (number, row_label(row, number), value))
        return value
    return value


def build_outputs(rows, key=None):
    """Pure function. Rows -> (tuple of MAX_ROWS values, seeds) where seeds = {row index: seed used} for the seed rows."""
    out, seeds = [], {}
    for i, r in enumerate(rows, 1):
        v = row_output(r, i, key)
        out.append(v)
        if r["kind"] == "seed":
            seeds[i - 1] = v
    out.extend([None] * (MAX_ROWS - len(out)))
    return tuple(out), seeds


def changes_every_run(rows):
    """Pure function. True when a seed row is random or counting up, so the node must run again each time."""
    return any(r["kind"] == "seed" and r["mode"] != "fixed" for r in rows)


class SYControlPanel:
    DESCRIPTION = ("One panel for the settings you change most. Every row is a dial with its own name and its own range: "
                   "a number, a whole number, a switch, a text, a dropdown with your own list, or a seed. The range is yours, "
                   "so you can go as high or low as you like, and typing a number is never cut off. Each row is one output; "
                   "connect it to any input. 'Take widgets from nodes' moves the widgets of other nodes into the panel and "
                   "connects them for you.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = tuple(ANY for _ in range(MAX_ROWS))
    RETURN_NAMES = tuple("out%d" % i for i in range(1, MAX_ROWS + 1))
    SY_NO_PREVIEW = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "rows": ("STRING", {"default": "[]", "multiline": False,
                                    "tooltip": "The rows of the panel. The panel on the node fills this in; you do not type it."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, rows, unique_id=None):
        try:
            if changes_every_run(parse_rows(rows)):
                return float("nan")
        except ValueError:
            return float("nan")
        return rows

    def run(self, rows, unique_id=None):
        parsed = parse_rows(rows)
        values, seeds = build_outputs(parsed, unique_id)
        ui = {"sy_seeds": [json.dumps(seeds)]} if seeds else {}
        return {"ui": ui, "result": values}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ControlPanel", SYControlPanel)
NODE_DISPLAY_NAME_MAPPINGS["SYControlPanel"] = "Control Panel SY"
