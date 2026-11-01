"""Bookmark SY: marks a spot on the canvas. Press its number key and the view jumps there.
The jump happens in the browser (js/sy_bookmark.js). This file holds the node shell and the plain rules, so they can be tested."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

KEYS = tuple("123456789")
MIN_ZOOM, MAX_ZOOM = 0.2, 3.0


def find_bookmark(bookmarks, key):
    """Pure function. bookmarks is a list of dicts with 'id' and 'key'. Returns the bookmark that owns the key, or None.
    When two bookmarks share a key, the one with the lower id wins (ids are compared as numbers when they are numbers)."""
    key = str(key)
    hits = [b for b in bookmarks if str(b.get("key")) == key]
    if not hits:
        return None

    def order(b):
        try:
            return (0, float(b.get("id")), "")
        except (TypeError, ValueError):
            return (1, 0.0, str(b.get("id")))

    return sorted(hits, key=order)[0]


def shared_keys(bookmarks):
    """Pure function. The keys that more than one bookmark uses, in key order. The panel warns about them."""
    seen = {}
    for b in bookmarks:
        seen[str(b.get("key"))] = seen.get(str(b.get("key")), 0) + 1
    return [k for k in KEYS if seen.get(k, 0) > 1]


def centre_offset(node_pos, node_size, zoom, view_w, view_h):
    """Pure function. The canvas offset [x, y] that puts the middle of the node in the middle of the view at this zoom.
    The canvas draws a point p at (p + offset) * zoom, so offset = view / (2 * zoom) - middle."""
    zoom = clamp_zoom(zoom)
    cx = node_pos[0] + node_size[0] / 2.0
    cy = node_pos[1] + node_size[1] / 2.0
    return [view_w / (2.0 * zoom) - cx, view_h / (2.0 * zoom) - cy]


def clamp_zoom(zoom):
    try:
        zoom = float(zoom)
    except (TypeError, ValueError):
        zoom = 1.0
    if zoom != zoom:  # not a number
        zoom = 1.0
    return max(MIN_ZOOM, min(MAX_ZOOM, zoom))


class SYBookmark:
    DESCRIPTION = ("Marks a spot in a big workflow. Press its number key (1 to 9) while you are not typing, and the view jumps to this node at the zoom you set. "
                   "It runs nothing and has no wires.")
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": (list(KEYS), {"default": "1", "tooltip": "The number key that jumps here. Two bookmarks should not share a key."}),
                "zoom": ("FLOAT", {"default": 1.0, "min": MIN_ZOOM, "max": MAX_ZOOM, "step": 0.1, "tooltip": "How close the view is after the jump. 1 is normal size."}),
            }
        }

    def run(self, key="1", zoom=1.0):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Bookmark", SYBookmark)
