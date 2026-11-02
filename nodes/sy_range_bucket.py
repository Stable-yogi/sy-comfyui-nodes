"""Range Bucket SY: turns a number into a label by which range it falls in."""
import bisect
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

INCLUSIVE = ["lower edge in next range", "upper edge in lower range"]


def parse_edges(text):
    """Pure function. '48, 120' -> [48.0, 120.0]. Empty text gives no edges (one range for everything)."""
    parts = [p.strip() for p in str(text).replace("\n", ",").split(",") if p.strip()]
    edges = []
    for p in parts:
        try:
            v = float(p)
        except ValueError:
            raise ValueError("edges must be numbers separated by commas, such as 48, 120 (cannot read %r)" % p)
        if not math.isfinite(v):
            raise ValueError("edges must be ordinary numbers (cannot use %r)" % p)
        edges.append(v)
    for a, b in zip(edges, edges[1:]):
        if b <= a:
            raise ValueError("edges must go up, each bigger than the one before (%g is not bigger than %g)" % (b, a))
    return edges


def parse_labels(text, edge_count):
    labels = [ln.strip() for ln in str(text).splitlines()]
    while len(labels) > edge_count + 1 and labels[-1] == "":
        labels.pop()   # forgive blank lines at the end
    if len(labels) != edge_count + 1:
        raise ValueError("%d edges make %d ranges, so labels needs %d lines (one per range), but it has %d"
                         % (edge_count, edge_count + 1, edge_count + 1, len(labels)))
    return labels


def bucket_index(value, edges, inclusive="lower edge in next range"):
    """Pure function. Returns which range the value is in, counted from 0."""
    if inclusive not in INCLUSIVE:
        raise ValueError("inclusive must be one of: %s (got %r)" % (", ".join(INCLUSIVE), inclusive))
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("value must be an ordinary number, got %r" % (value,))
    for a, b in zip(edges, edges[1:]):
        if b <= a:
            raise ValueError("edges must go up, each bigger than the one before")
    if inclusive == INCLUSIVE[0]:
        return bisect.bisect_right(edges, value)
    return bisect.bisect_left(edges, value)


class SYRangeBucket:
    DESCRIPTION = ("Turns a number into a label by which range it falls in, for example a frame count into "
                   "short, medium or long. Give the edges and one label per range.")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("label", "index")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "The number to sort into a range."}),
                "edges": ("STRING", {"default": "48, 120", "tooltip": "Where the ranges split: numbers going up, separated by commas."}),
                "labels": ("STRING", {"multiline": True, "default": "short\nmedium\nlong", "tooltip": "One label per line. Needs one more line than there are edges."}),
                "inclusive": (INCLUSIVE, {"default": INCLUSIVE[0], "tooltip": "Which range a number exactly on an edge belongs to."}),
            },
        }

    def run(self, value, edges, labels, inclusive=INCLUSIVE[0]):
        e = parse_edges(edges)
        names = parse_labels(labels, len(e))
        i = bucket_index(value, e, inclusive)
        return (names[i], i)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RangeBucket", SYRangeBucket)
NODE_DISPLAY_NAME_MAPPINGS["SYRangeBucket"] = "Range Bucket SY"
