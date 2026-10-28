"""Shared pure helpers for the XY plot nodes (values list, pick, grid, label strip). No torch import here."""

MAX_VALUES = 64
MAX_SIDE = 16384
MODES = ("numbers", "text list", "seeds")
COLOR_NAMES = {
    "black": (0, 0, 0), "white": (255, 255, 255), "gray": (128, 128, 128), "dark_gray": (40, 40, 40),
    "red": (200, 40, 40), "green": (40, 160, 70), "blue": (50, 90, 200), "gold": (212, 165, 55),
}


def format_number(v):
    """Whole numbers print without a decimal point; others print short (up to 6 decimals, no trailing zeros)."""
    v = float(v)
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def number_range(start, stop, steps):
    """Evenly spaced numbers from start to stop, both included. steps=1 gives just start."""
    steps = int(steps)
    if steps < 1 or steps > MAX_VALUES:
        raise ValueError("steps must be between 1 and %d, got %d" % (MAX_VALUES, steps))
    start, stop = float(start), float(stop)
    if steps == 1:
        return [format_number(start)]
    return [format_number(start + (stop - start) * i / (steps - 1)) for i in range(steps)]


def text_items(text):
    """Split on commas or new lines, trim each part, drop empty parts."""
    parts = []
    for line in str(text or "").replace("\r", "\n").split("\n"):
        parts.extend(p.strip() for p in line.split(","))
    parts = [p for p in parts if p]
    if not parts:
        raise ValueError("the text list is empty: type values separated by commas, for example euler, dpmpp_2m, ddim")
    if len(parts) > MAX_VALUES:
        raise ValueError("too many values (%d): the most allowed is %d" % (len(parts), MAX_VALUES))
    return parts


def seed_list(first, count, step):
    count = int(count)
    if count < 1 or count > MAX_VALUES:
        raise ValueError("seed count must be between 1 and %d, got %d" % (MAX_VALUES, count))
    first, step = int(first), int(step)
    if first < 0:
        raise ValueError("first seed cannot be negative, got %d" % first)
    vals = [first + step * i for i in range(count)]
    if min(vals) < 0:
        raise ValueError("seed step is negative and goes below zero: raise the first seed or use a smaller step")
    return [str(v) for v in vals]


def build_values(mode, start=0.0, stop=1.0, steps=5, text="", seed_first=0, seed_count=4, seed_step=1):
    """Return the list of axis values (strings) for one mode."""
    if mode == "numbers":
        return number_range(start, stop, steps)
    if mode == "text list":
        return text_items(text)
    if mode == "seeds":
        return seed_list(seed_first, seed_count, seed_step)
    raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))


def parse_axis(text):
    """One value per line, trimmed. Empty lines are dropped. An empty axis gives an empty list (meaning: no such axis)."""
    return [ln.strip() for ln in str(text or "").replace("\r", "\n").split("\n") if ln.strip()]


def axis_sizes(x_values, y_values):
    """Returns (nx, ny). An empty axis counts as 1 (a single column or row with no label)."""
    return max(1, len(x_values)), max(1, len(y_values))


def pick_cell(nx, ny, index, wrap=False):
    """Row-major: index 0..nx*ny-1 gives (x_index, y_index). Out of range raises unless wrap is on."""
    nx, ny, index = int(nx), int(ny), int(index)
    total = nx * ny
    if nx < 1 or ny < 1:
        raise ValueError("both axes need at least 1 value")
    if index < 0:
        raise ValueError("index cannot be negative, got %d" % index)
    if index >= total:
        if not wrap:
            raise ValueError("index %d is outside the grid: it has %d x %d = %d cells, so use 0 to %d (or turn wrap on)"
                             % (index, nx, ny, total, total - 1))
        index %= total
    return index % nx, index // nx


def parse_color(text):
    """A colour name from COLOR_NAMES, or six hex digits with an optional leading hash sign. Returns (r, g, b)."""
    s = str(text).strip().lower()
    if s in COLOR_NAMES:
        return COLOR_NAMES[s]
    h = s[1:] if s.startswith("#") else s
    if len(h) == 6 and all(ch in "0123456789abcdef" for ch in h):
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    raise ValueError("background %r is not a colour: use a name (%s) or six hex digits" % (text, ", ".join(sorted(COLOR_NAMES))))


def text_color_for(bg):
    lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    return (0, 0, 0) if lum > 128 else (255, 255, 255)


def grid_layout(nx, ny, cell_w, cell_h, gap, padding, head_w, head_h):
    """Pixel plan. head_h = height of the header row (0 for none), head_w = width of the label column (0 for none).
    Returns {width, height, cells: [(x, y)] row-major, col_x: [centre x], row_y: [centre y], head_y, head_x}."""
    nx, ny, cell_w, cell_h, gap, padding, head_w, head_h = (int(v) for v in (nx, ny, cell_w, cell_h, gap, padding, head_w, head_h))
    if nx < 1 or ny < 1:
        raise ValueError("both axes need at least 1 value")
    if cell_w < 1 or cell_h < 1:
        raise ValueError("picture size must be at least 1x1")
    if min(gap, padding, head_w, head_h) < 0:
        raise ValueError("gap, padding and label sizes cannot be negative")
    left = padding + (head_w + gap if head_w else 0)
    top = padding + (head_h + gap if head_h else 0)
    width = left + nx * cell_w + (nx - 1) * gap + padding
    height = top + ny * cell_h + (ny - 1) * gap + padding
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("the grid would be %dx%d pixels, more than %d: use fewer values, smaller pictures or a smaller gap"
                         % (width, height, MAX_SIDE))
    cells = [(left + c * (cell_w + gap), top + r * (cell_h + gap)) for r in range(ny) for c in range(nx)]
    return {
        "width": width, "height": height, "cells": cells,
        "col_x": [left + c * (cell_w + gap) + cell_w / 2.0 for c in range(nx)],
        "row_y": [top + r * (cell_h + gap) + cell_h / 2.0 for r in range(ny)],
        "head_y": padding, "head_x": padding,
    }


def markdown_table(x_values, y_values, x_name="X", y_name="Y"):
    """A Markdown table: one row per y value, one column per x value, each cell showing its picture number (grid order, starting at 0)."""
    nx, ny = axis_sizes(x_values, y_values)
    xs = list(x_values) or [""]
    ys = list(y_values) or [""]
    esc = lambda s: str(s).replace("|", "\\|")
    head = "| %s \\ %s | " % (esc(y_name), esc(x_name)) + " | ".join(esc(x) for x in xs) + " |"
    sep = "|" + "---|" * (nx + 1)
    rows = []
    n = 0
    for y in ys:
        cells = []
        for _ in xs:
            cells.append(str(n))
            n += 1
        rows.append("| " + esc(y) + " | " + " | ".join(cells) + " |")
    return "\n".join([head, sep] + rows)
