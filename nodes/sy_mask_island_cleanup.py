"""Mask Island Cleanup SY: deletes tiny white specks and fills tiny black holes in a mask."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_args(min_island, min_hole, threshold):
    if min_island < 0 or min_hole < 0:
        raise ValueError("min_island and min_hole must be 0 or more, got %s and %s" % (min_island, min_hole))
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)


def label_regions(rows):
    """Pure function. Flood fill (4 neighbours) over rows of 0/1. Returns (labels, sizes): labels has a region number per pixel, sizes[number] is its pixel count."""
    if not rows or not rows[0]:
        raise ValueError("the mask is empty: it needs at least one row and one column")
    h, w = len(rows), len(rows[0])
    labels = [[-1] * w for _ in range(h)]
    sizes = []
    for y0 in range(h):
        for x0 in range(w):
            if labels[y0][x0] != -1:
                continue
            val = rows[y0][x0]
            lab = len(sizes)
            labels[y0][x0] = lab
            stack = [(y0, x0)]
            n = 0
            while stack:
                y, x = stack.pop()
                n += 1
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < h and 0 <= nx < w and labels[ny][nx] == -1 and rows[ny][nx] == val:
                        labels[ny][nx] = lab
                        stack.append((ny, nx))
            sizes.append(n)
    return labels, sizes


def _flip_small(rows, value, limit):
    """Flip regions of `value` that are smaller than `limit` pixels."""
    if limit <= 0:
        return rows
    labels, sizes = label_regions(rows)
    return [[(1 - v) if (v == value and sizes[labels[y][x]] < limit) else v for x, v in enumerate(line)]
            for y, line in enumerate(rows)]


def clean_binary(rows, min_island, min_hole):
    """Pure function. Removes white regions smaller than min_island, then fills black regions smaller than min_hole."""
    check_args(min_island, min_hole, 0.5)
    rows = [list(r) for r in rows]
    rows = _flip_small(rows, 1, min_island)
    return _flip_small(rows, 0, min_hole)


class SYMaskIslandCleanup:
    DESCRIPTION = "Tidies a mask by deleting tiny white specks and filling tiny black holes. The mask is first turned into pure black and white by the threshold."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to tidy."}),
                "min_island": ("INT", {"default": 64, "min": 0, "max": 10000, "step": 1, "tooltip": "White specks smaller than this many pixels are deleted. 0 keeps all."}),
                "min_hole": ("INT", {"default": 64, "min": 0, "max": 10000, "step": 1, "tooltip": "Black holes smaller than this many pixels are filled. 0 keeps all."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask values above this count as white, the rest as black."}),
            }
        }

    def run(self, mask, min_island, min_hole, threshold):
        import torch

        check_args(min_island, min_hole, threshold)
        m = mask if mask.dim() == 3 else mask.unsqueeze(0)
        out = []
        for one in m:
            binary = (one > threshold).to(torch.int64).tolist()
            out.append(torch.tensor(clean_binary(binary, min_island, min_hole), dtype=torch.float32))
        res = torch.stack(out).to(mask.device)
        return (res if mask.dim() == 3 else res[0],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskIslandCleanup", SYMaskIslandCleanup)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskIslandCleanup"] = "Mask Island Cleanup SY"
