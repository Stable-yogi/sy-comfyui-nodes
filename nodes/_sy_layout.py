"""Helper for the SY layout nodes: box lists as JSON text, checking and clipping. Pure Python, no node inside."""
import json
import math

MAX_LABEL = 80      # longest label text allowed
MAX_BOXES = 64      # most boxes in one list
MAX_SIDE = 16384    # biggest canvas side / box value the nodes accept

# colour name -> (red, green, blue), used when the preview draws a box
COLOUR_RGB = {
    "red": (230, 50, 50),
    "orange": (240, 140, 30),
    "yellow": (240, 220, 50),
    "green": (60, 190, 90),
    "cyan": (50, 200, 210),
    "blue": (60, 110, 230),
    "purple": (150, 90, 220),
    "pink": (235, 100, 170),
    "white": (245, 245, 245),
    "black": (15, 15, 15),
}
COLOUR_NAMES = tuple(COLOUR_RGB)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _fmt(v):
    return "%g" % v


def make_box(x, y, w, h, label, colour):
    """Build one box dict. Raises ValueError when something cannot work."""
    for name, v in (("x", x), ("y", y), ("w", w), ("h", h)):
        if not _is_number(v):
            raise ValueError("%s must be a number, got %r" % (name, v))
    if w <= 0 or h <= 0:
        raise ValueError("w and h must be bigger than 0 (got w=%s, h=%s)" % (_fmt(w), _fmt(h)))
    if x < 0 or y < 0:
        raise ValueError("x and y must be 0 or more (got x=%s, y=%s)" % (_fmt(x), _fmt(y)))
    label = "" if label is None else str(label).strip()
    if len(label) > MAX_LABEL:
        raise ValueError("label is %d characters long; shorten it to %d or fewer" % (len(label), MAX_LABEL))
    if colour not in COLOUR_RGB:
        raise ValueError("unknown colour %r; use one of: %s" % (colour, ", ".join(COLOUR_NAMES)))
    return {"x": x, "y": y, "w": w, "h": h, "label": label, "colour": colour}


def boxes_to_json(boxes):
    return json.dumps(list(boxes))


def parse_boxes(text):
    """Parse JSON text into a list of dicts. Accepts a list or one single object. Structure only, values are not judged."""
    if text is None or not str(text).strip():
        raise ValueError("the box text is empty; connect a Layout Box node or paste a JSON list")
    try:
        data = json.loads(text)
    except ValueError as e:
        raise ValueError("the box text is not valid JSON (%s)" % e)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("the box text must be a JSON list of boxes, for example [{\"x\": 0, \"y\": 0, \"w\": 100, \"h\": 100}]")
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError("box %d is not an object; each box must look like {\"x\": 0, \"y\": 0, \"w\": 100, \"h\": 100}" % (i + 1))
    return data


def overlap_area(a, b):
    ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return ox * oy if ox > 0 and oy > 0 else 0


def box_rect(box, canvas_w, canvas_h):
    """Pixel rectangle (left, top, right, bottom) clipped to the canvas, right/bottom exclusive. None if nothing is left."""
    left = max(0, int(round(box["x"])))
    top = max(0, int(round(box["y"])))
    right = min(canvas_w, int(round(box["x"] + box["w"])))
    bottom = min(canvas_h, int(round(box["y"] + box["h"])))
    if right <= left or bottom <= top:
        return None
    return (left, top, right, bottom)


def _name(i, box):
    label = box.get("label") if isinstance(box, dict) else None
    if isinstance(label, str) and label.strip():
        return 'box %d ("%s")' % (i + 1, label.strip()[:30])
    return "box %d" % (i + 1)


def check_layout(text, canvas_w, canvas_h, warn_overlap=True):
    """Check box JSON text against a canvas. Returns (valid, report). Warnings never make a layout invalid."""
    if not _is_number(canvas_w) or not _is_number(canvas_h) or canvas_w < 1 or canvas_h < 1:
        raise ValueError("canvas width and height must be 1 or more (got %r x %r)" % (canvas_w, canvas_h))
    errors, warnings = [], []
    if text is None or not str(text).strip():
        return False, "INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list."
    try:
        data = json.loads(text)
    except ValueError as e:
        return False, "INVALID: the text is not valid JSON (%s). Check commas, quotes and brackets." % e
    if not isinstance(data, list):
        return False, "INVALID: the top level must be a list of boxes, written between [ and ]."
    if len(data) == 0:
        return False, "INVALID: the list has no boxes. Add at least one."
    if len(data) > MAX_BOXES:
        errors.append("the list has %d boxes; the most allowed is %d" % (len(data), MAX_BOXES))
    good = []  # (index, box) of boxes whose numbers are usable for the overlap test
    for i, box in enumerate(data[:MAX_BOXES]):
        if not isinstance(box, dict):
            errors.append("box %d is not an object like {\"x\": 0, \"y\": 0, \"w\": 100, \"h\": 100}" % (i + 1))
            continue
        name = _name(i, box)
        numbers_ok = True
        for key in ("x", "y", "w", "h"):
            if key not in box:
                errors.append("%s is missing \"%s\"" % (name, key))
                numbers_ok = False
            elif not _is_number(box[key]):
                errors.append("%s: \"%s\" must be a number, got %r" % (name, key, box[key]))
                numbers_ok = False
        label = box.get("label", "")
        if not isinstance(label, str):
            errors.append("%s: label must be text" % name)
        elif len(label) > MAX_LABEL:
            errors.append("%s: label is %d characters; shorten it to %d or fewer" % (name, len(label), MAX_LABEL))
        colour = box.get("colour", box.get("color"))
        if colour is not None and (not isinstance(colour, str) or colour not in COLOUR_RGB):
            warnings.append("%s: unknown colour %r; the preview will use %s" % (name, colour, COLOUR_NAMES[0]))
        if not numbers_ok:
            continue
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        if w <= 0 or h <= 0:
            errors.append("%s has no size (w=%s, h=%s); both must be bigger than 0" % (name, _fmt(w), _fmt(h)))
            continue
        if x < 0 or y < 0:
            errors.append("%s starts outside the canvas (x=%s, y=%s); x and y must be 0 or more" % (name, _fmt(x), _fmt(y)))
        if x + w > canvas_w:
            errors.append("%s runs past the right edge: x + w = %s but the canvas is %s wide" % (name, _fmt(x + w), _fmt(canvas_w)))
        if y + h > canvas_h:
            errors.append("%s runs past the bottom edge: y + h = %s but the canvas is %s high" % (name, _fmt(y + h), _fmt(canvas_h)))
        good.append((i, box))
    if warn_overlap:
        for a in range(len(good)):
            for b in range(a + 1, len(good)):
                if overlap_area(good[a][1], good[b][1]) > 0:
                    warnings.append("%s and %s overlap" % (_name(*good[a]), _name(*good[b])))
    lines = []
    if errors:
        lines.append("INVALID: %d problem%s found." % (len(errors), "" if len(errors) == 1 else "s"))
        lines += ["- " + e for e in errors]
    else:
        head = "VALID: %d box%s fit%s inside %sx%s." % (len(data), "" if len(data) == 1 else "es",
                                                       "s" if len(data) == 1 else "", _fmt(canvas_w), _fmt(canvas_h))
        lines.append(head)
    lines += ["WARNING: " + w for w in warnings]
    return (not errors), "\n".join(lines)
