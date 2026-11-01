"""Extra helpers for the SY layout nodes (value pass, batch E). Pure Python, no node inside."""
import json

try:
    from ._sy_layout import MAX_BOXES, MAX_LABEL, _fmt, _is_number
except ImportError:  # run as a plain file by the selftest
    from _sy_layout import MAX_BOXES, MAX_LABEL, _fmt, _is_number


def snap_value(value, multiple, minimum=0):
    """Round value to the nearest multiple (halves go up). multiple 1 or less changes nothing."""
    if multiple <= 1:
        return value
    snapped = int(value // multiple + (1 if value % multiple * 2 >= multiple else 0)) * multiple
    return max(snapped, minimum)


def snap_box_numbers(x, y, w, h, multiple):
    """Snap x, y, w, h to a multiple. A width or height never becomes 0."""
    return (snap_value(x, multiple), snap_value(y, multiple),
            snap_value(w, multiple, multiple if multiple > 1 else 0),
            snap_value(h, multiple, multiple if multiple > 1 else 0))


def check_fits(label, x, y, w, h, canvas_w, canvas_h):
    """Raise a plain ValueError when a box does not fit a canvas. A canvas side of 0 means: do not check that side."""
    name = 'Box "%s"' % label if label else "The box"
    if canvas_w and x + w > canvas_w:
        raise ValueError("%s runs past the right edge: x + w = %s but the canvas is %s wide. Lower x or w." % (name, _fmt(x + w), _fmt(canvas_w)))
    if canvas_h and y + h > canvas_h:
        raise ValueError("%s runs past the bottom edge: y + h = %s but the canvas is %s high. Lower y or h." % (name, _fmt(y + h), _fmt(canvas_h)))


def box_info(box, note=""):
    """One plain line describing a box."""
    name = 'Box "%s"' % box["label"] if box.get("label") else "Box"
    text = "%s: %sx%s at (%s, %s), right edge %s, bottom edge %s, %s." % (
        name, _fmt(box["w"]), _fmt(box["h"]), _fmt(box["x"]), _fmt(box["y"]),
        _fmt(box["x"] + box["w"]), _fmt(box["y"] + box["h"]), box.get("colour", "red"))
    return text + (" " + note if note else "")


def box_key(box):
    """What makes two boxes the same box for dropping duplicates."""
    return (box.get("x"), box.get("y"), box.get("w"), box.get("h"), box.get("label", ""), box.get("colour", box.get("color")))


def drop_duplicate_boxes(boxes):
    """Returns (boxes_without_exact_copies, how_many_were_dropped). Order is kept, the first copy stays."""
    seen = set()
    kept = []
    for b in boxes:
        try:
            key = box_key(b)
            hash(key)
        except TypeError:
            kept.append(b)
            continue
        if key in seen:
            continue
        seen.add(key)
        kept.append(b)
    return kept, len(boxes) - len(kept)


def clip_boxes_text(text, canvas_w, canvas_h):
    """Return (json_text, dropped, changed). Boxes are cut to fit the canvas. Boxes that are broken or end up with no area are dropped.
    When the text cannot be read at all it comes back unchanged with (text, 0, 0)."""
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return text, 0, 0
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return text, 0, 0
    out = []
    dropped = changed = 0
    for box in data[:MAX_BOXES]:
        if not isinstance(box, dict) or not all(k in box and _is_number(box[k]) for k in ("x", "y", "w", "h")):
            dropped += 1
            continue
        left = max(0, box["x"])
        top = max(0, box["y"])
        right = min(canvas_w, box["x"] + box["w"])
        bottom = min(canvas_h, box["y"] + box["h"])
        if right <= left or bottom <= top:
            dropped += 1
            continue
        new = dict(box)
        new.update({"x": left, "y": top, "w": right - left, "h": bottom - top})
        if new != box:
            changed += 1
        label = new.get("label")
        if isinstance(label, str) and len(label) > MAX_LABEL:
            new["label"] = label[:MAX_LABEL]
            changed += 1
        out.append(new)
    dropped += max(0, len(data) - MAX_BOXES)
    return json.dumps(out), dropped, changed


def multiple_warnings(text, multiple):
    """Plain WARNING lines for boxes whose x, y, w or h are not a multiple of `multiple`. Empty list when multiple is 1 or less
    or when the text cannot be read (the normal check reports that)."""
    if multiple <= 1:
        return []
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    lines = []
    for i, box in enumerate(data[:MAX_BOXES]):
        if not isinstance(box, dict):
            continue
        bad = [k for k in ("x", "y", "w", "h") if _is_number(box.get(k)) and box[k] % multiple != 0]
        if bad:
            label = box.get("label")
            name = 'box %d ("%s")' % (i + 1, label.strip()[:30]) if isinstance(label, str) and label.strip() else "box %d" % (i + 1)
            lines.append("WARNING: %s: %s not a multiple of %d" % (name, ", ".join(bad) + (" is" if len(bad) == 1 else " are"), multiple))
    return lines
