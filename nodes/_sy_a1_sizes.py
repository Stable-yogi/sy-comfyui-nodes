"""Shared pure helpers for the batch A1 size and frame nodes: snap to a multiple, aspect fit, 4n+1 frame counts."""
import math

SNAP_CHOICES = ["off", "8", "16", "32", "64"]
SNAP_DIRECTIONS = ["nearest", "down", "up"]
FRAME_RULES = ["off", "4n+1 trim", "4n+1 extend"]

ASPECTS = {
    "preset": None,
    "1:1": (1, 1),
    "5:4": (5, 4),
    "4:3": (4, 3),
    "3:2": (3, 2),
    "16:9": (16, 9),
    "21:9": (21, 9),
    "4:5": (4, 5),
    "3:4": (3, 4),
    "2:3": (2, 3),
    "9:16": (9, 16),
}


def snap_value(value, multiple, direction="nearest", minimum=None, maximum=None):
    """Pure function. Rounds `value` to a multiple of `multiple` (nearest, down or up) and keeps it inside minimum..maximum."""
    multiple = int(multiple)
    if multiple < 1:
        raise ValueError("the multiple must be at least 1, got %d" % multiple)
    if direction not in SNAP_DIRECTIONS:
        raise ValueError("snap direction must be one of: %s" % ", ".join(SNAP_DIRECTIONS))
    v = float(value)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError("size must be a normal number, got %s" % value)
    if direction == "down":
        k = math.floor(v / multiple)
    elif direction == "up":
        k = math.ceil(v / multiple)
    else:
        k = math.floor(v / multiple + 0.5)
    out = int(k * multiple)
    if minimum is not None:
        low = -(-int(minimum) // multiple) * multiple  # smallest multiple that is at least `minimum`
        out = max(out, low)
    if maximum is not None:
        high = (int(maximum) // multiple) * multiple  # biggest multiple that is at most `maximum`
        out = min(out, high)
    return out


def snap_choice(text):
    """Pure function. 'off' -> 0, '16' -> 16. Anything else is refused in plain words."""
    if text not in SNAP_CHOICES:
        raise ValueError("snap_to must be one of: %s, got %r" % (", ".join(SNAP_CHOICES), text))
    return 0 if text == "off" else int(text)


def scale_to_megapixels(width, height, megapixels):
    """Pure function. Same shape, new pixel count. Returns floats (width, height)."""
    width, height, mp = float(width), float(height), float(megapixels)
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be above 0 to scale them, got %gx%g" % (width, height))
    if not (0 < mp <= 1000):
        raise ValueError("target megapixels must be above 0 and at most 1000, got %s" % megapixels)
    k = math.sqrt(mp * 1_000_000 / (width * height))
    return (width * k, height * k)


def fit_aspect(pixels, ratio_w, ratio_h):
    """Pure function. A float (width, height) with the given shape that holds about `pixels` pixels."""
    if ratio_w <= 0 or ratio_h <= 0 or pixels <= 0:
        raise ValueError("aspect and pixel count must be above 0")
    w = math.sqrt(pixels * ratio_w / ratio_h)
    return (w, w * ratio_h / ratio_w)


def snap_frame_count(count, rule):
    """Pure function. Video models like Wan and LTX want 4n+1 frames (1, 5, 9 ... 81). Returns the fitted count."""
    if rule not in FRAME_RULES:
        raise ValueError("frame rule must be one of: %s" % ", ".join(FRAME_RULES))
    count = int(count)
    if count < 1:
        raise ValueError("frame count must be at least 1, got %d" % count)
    if rule == "off" or count % 4 == 1:
        return count
    if rule == "4n+1 trim":
        return max(1, ((count - 1) // 4) * 4 + 1)
    return ((count - 1) // 4 + 1) * 4 + 1


def is_4n1(count):
    return int(count) >= 1 and int(count) % 4 == 1


def ratio_text(width, height):
    """Pure function. 1920x1080 -> '16:9'. A side of 0 gives 'none'."""
    width, height = int(width), int(height)
    if width <= 0 or height <= 0:
        return "none"
    g = math.gcd(width, height)
    return "%d:%d" % (width // g, height // g)
