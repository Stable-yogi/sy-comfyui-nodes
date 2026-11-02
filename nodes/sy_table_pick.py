"""Table Pick SY: takes one cell from pasted table text (CSV, tab, semicolon or pipe separated)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DELIMS = {"comma": ",", "tab": "\t", "semicolon": ";", "pipe": "|"}
_AUTO_ORDER = ("comma", "tab", "semicolon", "pipe")


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
    """Pure function. Splits table text into a list of rows (lists of strings).
    Handles "quoted, cells", doubled quotes ("") and quoted line breaks. Blank lines are skipped."""
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
            row.clear()   # blank line
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


def _resolve_column(header, column, has_header):
    col = str(column).strip()
    if col == "":
        raise ValueError("column is empty: type a column name or a number starting at 1")
    if has_header and header is not None:
        want = col.casefold()
        for idx, name in enumerate(header):
            if name.strip().casefold() == want:
                return idx
    if col.isdigit():
        num = int(col)
        if num < 1:
            raise ValueError("column numbers start at 1, got %s" % col)
        return num - 1
    if has_header:
        raise ValueError("no column named %r. Columns are: %s" % (col, ", ".join(h.strip() for h in header or [])))
    raise ValueError("column %r is a name, but has_header is off. Use a number starting at 1" % col)


def pick_cell(rows, row, column, has_header=True, default=""):
    """Pure function. Returns (value, found, row_count). row 0 = first data row. row_count = data rows."""
    row = int(row)
    if row < 0:
        raise ValueError("row must be 0 or more, got %d" % row)
    if str(column).strip() == "":
        raise ValueError("column is empty: type a column name or a number starting at 1")
    if not rows:
        return (default, False, 0)
    header = rows[0] if has_header else None
    data = rows[1:] if has_header else rows
    count = len(data)
    ci = _resolve_column(header, column, has_header)
    if row >= count or ci >= len(data[row]):
        return (default, False, count)
    return (data[row][ci], True, count)


class SYTablePick:
    DESCRIPTION = ("Takes one cell from pasted table text (CSV or tab separated). Choose the row and a column "
                   "name or number. If the cell does not exist you get your default text and found is off.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "INT")
    RETURN_NAMES = ("value", "found", "row_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "table": ("STRING", {"multiline": True, "default": "", "tooltip": "The table as text, one row per line. Quoted cells may hold commas."}),
                "row": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which data row to read. 0 is the first row after the header."}),
                "column": ("STRING", {"default": "1", "tooltip": "A column name from the header, or a number starting at 1."}),
                "has_header": ("BOOLEAN", {"default": True, "tooltip": "On: the first line holds column names and is not a data row."}),
                "delimiter": (["auto", "comma", "tab", "semicolon", "pipe"], {"default": "auto", "tooltip": "What separates the cells. Auto uses the one seen most in the first line."}),
                "default": ("STRING", {"default": "", "tooltip": "Text to give back when the row or cell does not exist."}),
            }
        }

    def run(self, table, row, column, has_header, delimiter, default):
        rows = parse_table(table, delimiter)
        return pick_cell(rows, row, column, has_header, default)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TablePick", SYTablePick)
NODE_DISPLAY_NAME_MAPPINGS["SYTablePick"] = "Table Pick SY"
