"""Mask Keep Largest SY: keeps only the biggest separate blobs of a mask."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 1024  # masks longer than this are labelled on a shrunken copy


def check_args(threshold, keep, min_pixels, connectivity):
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    if not 1 <= keep <= 16:
        raise ValueError("keep must be between 1 and 16, got %s" % keep)
    if min_pixels < 0:
        raise ValueError("min_pixels must be 0 or more, got %s" % min_pixels)
    if connectivity not in ("4", "8"):
        raise ValueError("connectivity must be 4 or 8, got %r" % (connectivity,))


def label_components(grid, connectivity="8"):
    """Pure function. Rows of 0/1 in. Returns (labels, sizes): labels is 0 for background and 1, 2, 3... for each blob;
    sizes[k] is the pixel count of label k (sizes[0] counts the background)."""
    if not grid or not grid[0]:
        raise ValueError("the mask is empty: it needs at least one row and one column")
    if connectivity not in ("4", "8"):
        raise ValueError("connectivity must be 4 or 8, got %r" % (connectivity,))
    h, w = len(grid), len(grid[0])
    parent = [0]

    def find(a):
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    labels = [[0] * w for _ in range(h)]
    eight = connectivity == "8"
    for y in range(h):
        row = grid[y]
        cur = labels[y]
        up = labels[y - 1] if y else None
        for x in range(w):
            if not row[x]:
                continue
            near = []
            if x and cur[x - 1]:
                near.append(cur[x - 1])
            if up is not None:
                if up[x]:
                    near.append(up[x])
                if eight:
                    if x and up[x - 1]:
                        near.append(up[x - 1])
                    if x + 1 < w and up[x + 1]:
                        near.append(up[x + 1])
            if not near:
                parent.append(len(parent))
                cur[x] = len(parent) - 1
            else:
                low = min(near)
                cur[x] = low
                for v in near:
                    if v != low:
                        union(low, v)
    remap = {}
    sizes = [0]
    for y in range(h):
        cur = labels[y]
        for x in range(w):
            v = cur[x]
            if v:
                r = find(v)
                k = remap.get(r)
                if k is None:
                    k = len(sizes)
                    remap[r] = k
                    sizes.append(0)
                cur[x] = k
                sizes[k] += 1
            else:
                sizes[0] += 1
    return labels, sizes


def pick_labels(sizes, keep, min_pixels, scale=1):
    """Pure function. Chooses the label numbers to keep: the `keep` biggest blobs, each at least min_pixels
    (a blob size is multiplied by `scale` first, for shrunken copies). Biggest first, ties by lower label."""
    order = sorted(range(1, len(sizes)), key=lambda k: (-sizes[k], k))
    return [k for k in order if sizes[k] * scale >= min_pixels][:keep]


class SYMaskKeepLargest:
    DESCRIPTION = ("Keeps only the biggest separate blob or blobs of a mask and drops all the others. "
                   "Masks longer than 1024 pixels are labelled on a shrunken copy (whole-number steps) and mapped back, "
                   "so very thin bridges between blobs can be missed there, and sizes are close but not exact. "
                   "With a batch the kept output is the total over all frames.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "INT")
    RETURN_NAMES = ("mask", "kept")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to clean up."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask values above this count as white, the rest as black."}),
                "keep": ("INT", {"default": 1, "min": 1, "max": 16, "step": 1, "tooltip": "How many of the biggest blobs to keep."}),
                "min_pixels": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1, "tooltip": "Blobs smaller than this many pixels are dropped even if they are among the biggest."}),
                "connectivity": (["4", "8"], {"default": "8", "tooltip": "4: pixels join only side to side. 8: pixels also join diagonally."}),
            }
        }

    def run(self, mask, threshold, keep, min_pixels, connectivity):
        import torch
        import torch.nn.functional as F

        check_args(threshold, keep, min_pixels, connectivity)
        m = mask if mask.dim() == 3 else mask.unsqueeze(0)
        out = torch.zeros(m.shape, dtype=torch.float32, device=m.device)
        kept_total = 0
        for i in range(m.shape[0]):
            b = m[i] > threshold
            if not bool(b.any()):
                continue
            h, w = b.shape
            f = max(1, -(-max(h, w) // MAX_SIDE))
            small = b[::f, ::f] if f > 1 else b
            labels, sizes = label_components(small.to(torch.uint8).tolist(), connectivity)
            chosen = pick_labels(sizes, keep, min_pixels, f * f)
            kept_total += len(chosen)
            if not chosen:
                continue
            lut = torch.zeros(len(sizes), dtype=torch.bool)
            lut[chosen] = True
            sel = lut[torch.tensor(labels, dtype=torch.int64)].to(m.device)
            if f > 1:
                sel = sel.repeat_interleave(f, 0).repeat_interleave(f, 1)[:h, :w]
                grown = F.max_pool2d(sel.to(torch.float32)[None, None], 2 * f - 1, 1, f - 1)[0, 0] > 0.5
                sel = grown & b
            out[i] = sel.to(torch.float32)
        return (out if mask.dim() == 3 else out[0], kept_total)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskKeepLargest", SYMaskKeepLargest)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskKeepLargest"] = "Mask Keep Largest SY"
