"""Ratio Split SY: shares a total between up to four parts by a ratio like 1:2:1."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_ratios(ratios):
    """Pure function. Returns a list of 1 to 4 non-negative floats."""
    parts = [p.strip() for p in str(ratios).split(":")]
    if len(parts) > 4:
        raise ValueError("ratios can have at most 4 parts, got %d" % len(parts))
    values = []
    for p in parts:
        try:
            v = float(p)
        except ValueError:
            raise ValueError("ratios must be numbers separated by colons like 1:2:1, got %r" % (ratios,))
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("ratios must be ordinary numbers, got %r" % (ratios,))
        if v < 0:
            raise ValueError("ratios must not be negative, got %r" % (ratios,))
        values.append(v)
    if sum(values) <= 0:
        raise ValueError("ratios must not all be zero: at least one part needs to be above 0")
    return values


def _whole_shares(total, values):
    """Share a whole number out in whole parts that add up exactly (largest remainder method)."""
    t = int(round(abs(total)))
    s = sum(values)
    raw = [t * v / s for v in values]
    base = [int(x) for x in raw]
    left = t - sum(base)
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] - base[i]), i))
    for i in order[:left]:
        base[i] += 1
    sign = -1 if total < 0 else 1
    return [float(sign * b) for b in base]


def ratio_split(total, ratios, whole_numbers=False):
    """Pure function. Returns (p1, p2, p3, p4, list_text); unused parts are 0.
    whole_numbers gives whole parts that add up exactly to the (rounded) total, like 100 split 1:1:1 = 34, 33, 33."""
    total = float(total)
    values = parse_ratios(ratios)
    s = sum(values)
    shares = _whole_shares(total, values) if whole_numbers else [total * v / s for v in values]
    text = ", ".join("%g" % x for x in shares)
    shares += [0.0] * (4 - len(shares))
    return shares[0], shares[1], shares[2], shares[3], text


def split_info(total, ratios, whole_numbers=False):
    """Pure function. One plain sentence about the split."""
    out = ratio_split(total, ratios, whole_numbers)
    parts = len(parse_ratios(ratios))
    text = "%g split %s = %s (parts add up to %g)" % (float(total), str(ratios).replace(" ", ""), out[4], sum(out[:parts]))
    if whole_numbers and float(total) != round(float(total)):
        text += ", total was rounded to a whole number first"
    return text


class SYRatioSplit:
    DESCRIPTION = "Shares a number out by a ratio. For example 100 split 1:3 gives 25 and 75. Up to four parts. Turn on whole_numbers to get whole parts that add up exactly, which is what you need to share out frames or pixels."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "FLOAT", "FLOAT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("part_1", "part_2", "part_3", "part_4", "list", "info")

    @classmethod
    def INPUT_TYPES(cls):
        big = 1.0e9
        return {
            "required": {
                "total": ("FLOAT", {"default": 100.0, "min": -big, "max": big, "step": 0.01, "tooltip": "The number to share out."}),
                "ratios": ("STRING", {"default": "1:2:1", "multiline": False, "tooltip": "Up to four numbers split by colons, like 1:2:1. No negatives."}),
            },
            "optional": {
                "whole_numbers": ("BOOLEAN", {"default": False, "tooltip": "On gives whole parts that add up exactly (100 split 1:1:1 = 34, 33, 33). Good for frames."}),
            },
        }

    def run(self, total, ratios, whole_numbers=False):
        return ratio_split(total, ratios, whole_numbers) + (split_info(total, ratios, whole_numbers),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RatioSplit", SYRatioSplit)
