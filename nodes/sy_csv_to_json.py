"""CSV To JSON SY: turns pasted table text (CSV, tab, semicolon or pipe separated) into JSON text."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DELIMS = {"comma": ",", "tab": "\t", "semicolon": ";", "pipe": "|"}
_AUTO_ORDER = ("comma", "tab", "semicolon", "pipe")
SHAPES = ("list of objects", "list of lists", "object of columns")


def detect_delimiter(text):
    """Pure function. The delimiter that appears most (outside quotes) in the first line. Comma if none."""
    best, best_n = ",", 0
    counts = {k: 0 for k in DELIMS}
    inq = False
    for ch in text:
        if ch == '"':
            inq = not inq
        elif not inq:
            if ch in ("\n", "\r"):
                break
            for k, d in DELIMS.items():
                if ch == d:
                    counts[k] += 1
    for k in _AUTO_ORDER:
        if counts[k] > best_n:
            best, best_n = DELIMS[k], counts[k]
    return best


def parse_table(text, delimiter="auto"):
    """Pure function. Splits table text into rows (lists of strings). Handles quoted cells, doubled quotes
    and quoted line breaks. Blank lines are skipped."""
    if not isinstance(text, str):
        raise ValueError("table must be text")
    if delimiter == "auto":
        d = detect_delimiter(text)
    elif delimiter in DELIMS:
        d = DELIMS[delimiter]
    else:
        raise ValueError("delimiter must be one of: auto, %s (got %r)" % (", ".join(DELIMS), delimiter))
    rows, row, cell = [], [], []
    inq = False
    quoted = False
    i, n = 0, len(text)

    def end_row():
        if len(row) == 1 and row[0] == "" and not quoted:
            row.clear()
            return
        rows.append(list(row))
        row.clear()

    while i < n:
        ch = text[i]
        if inq:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    cell.append('"')
                    i += 1
                else:
                    inq = False
            else:
                cell.append(ch)
        elif ch == '"' and not cell:
            inq = True
            quoted = True
        elif ch == d:
            row.append("".join(cell))
            cell = []
        elif ch in ("\n", "\r"):
            if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 1
            row.append("".join(cell))
            cell = []
            end_row()
            quoted = False
        else:
            cell.append(ch)
        i += 1
    if inq:
        raise ValueError("table has a quote that is never closed: add the missing \" or remove it")
    if cell or row:
        row.append("".join(cell))
        end_row()
    return rows


def convert_cell(s):
    """Pure function. "30" -> 30, "2.5" -> 2.5, "true"/"false" -> booleans, anything else (also "") stays text.
    Numbers with a leading zero (like 007) stay text so ids and zip codes keep their zeros."""
    t = s.strip()
    low = t.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if t == "":
        return s
    body = t[1:] if t[0] in "+-" else t
    if body.isascii() and body.isdigit():
        if len(body) > 1 and body[0] == "0":
            return s
        return int(t)
    parts = body.split(".")
    if len(parts) == 2 and parts[0].isascii() and parts[1].isascii() and parts[0].isdigit() and parts[1].isdigit():
        if len(parts[0]) > 1 and parts[0][0] == "0":
            return s
        return float(t)
    return s


def unique_names(names):
    """Pure function. Duplicate names get _2, _3 ... added. Empty names become colN."""
    out, seen = [], set()
    for i, raw in enumerate(names):
        base = raw.strip() or "col%d" % (i + 1)
        name, k = base, 2
        while name in seen:
            name = "%s_%d" % (base, k)
            k += 1
        seen.add(name)
        out.append(name)
    return out


def table_to_json(text, has_header=True, delimiter="auto", shape="list of objects", convert_numbers=True, indent=2):
    """Pure function. Returns (json_text, row_count). row_count counts data rows."""
    if shape not in SHAPES:
        raise ValueError("shape must be one of: %s (got %r)" % (", ".join(SHAPES), shape))
    indent = int(indent)
    if indent < 0 or indent > 8:
        raise ValueError("indent must be 0 to 8, got %d" % indent)
    rows = parse_table(text, delimiter) if str(text).strip() != "" else []
    if not rows:
        raise ValueError("the table is empty: paste at least one line of CSV text")
    if has_header:
        header = unique_names(rows[0])
        data = rows[1:]
        first_data_line = 2
    else:
        width = max(len(r) for r in rows)
        header = ["col%d" % (i + 1) for i in range(width)]
        data = rows
        first_data_line = 1
    width = len(header)
    fixed = []
    for i, r in enumerate(data):
        if len(r) > width:
            raise ValueError("row %d has %d cells but there are only %d columns: remove the extra cells or add a header name"
                             % (i + first_data_line, len(r), width))
        r = r + [""] * (width - len(r))
        fixed.append([convert_cell(c) for c in r] if convert_numbers else list(r))
    if shape == "list of objects":
        result = [dict(zip(header, r)) for r in fixed]
    elif shape == "list of lists":
        result = fixed
    else:
        result = {h: [r[j] for r in fixed] for j, h in enumerate(header)}
    return json.dumps(result, ensure_ascii=False, indent=indent if indent > 0 else None), len(fixed)


class SYCsvToJson:
    DESCRIPTION = ("Turns pasted table text (CSV or tab separated) into JSON. Pick the shape of the result. "
                   "Numbers and true/false can become real JSON values.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("json_text", "row_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "table": ("STRING", {"multiline": True, "default": "", "tooltip": "The table as text, one row per line. Quoted cells may hold commas."}),
                "has_header": ("BOOLEAN", {"default": True, "tooltip": "On: the first line holds column names. Off: columns are named col1, col2 and so on."}),
                "delimiter": (["auto", "comma", "tab", "semicolon", "pipe"], {"default": "auto", "tooltip": "What separates the cells. Auto uses the one seen most in the first line."}),
                "shape": (list(SHAPES), {"default": "list of objects", "tooltip": "How the JSON is laid out: one object per row, plain lists, or one list per column."}),
                "convert_numbers": ("BOOLEAN", {"default": True, "tooltip": "On: 30 becomes a number and true/false become booleans. Empty cells stay empty text."}),
                "indent": ("INT", {"default": 2, "min": 0, "max": 8, "tooltip": "Spaces of indentation in the JSON. 0 puts it all on one line."}),
                "on_error": (["raise", "empty text"], {"default": "raise", "tooltip": "Raise stops with a message. Empty text gives empty JSON text and 0 rows instead."}),
            }
        }

    def run(self, table, has_header, delimiter, shape, convert_numbers, indent, on_error):
        try:
            return table_to_json(table, has_header, delimiter, shape, convert_numbers, indent)
        except ValueError:
            if on_error == "empty text":
                return ("", 0)
            raise


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CsvToJson", SYCsvToJson)
NODE_DISPLAY_NAME_MAPPINGS["SYCsvToJson"] = "CSV To JSON SY"
