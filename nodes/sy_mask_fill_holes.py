"""Mask Fill Holes SY: fills enclosed holes inside a mask (a donut becomes a disc)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_args(threshold, max_hole_size, connectivity):
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)
    if max_hole_size < 0:
        raise ValueError("max_hole_size must be 0 or more (0 fills every hole), got %s" % max_hole_size)
    if connectivity not in ("4", "8"):
        raise ValueError("connectivity must be 4 or 8, got %r" % (connectivity,))


def _steps(connectivity):
    if connectivity == "4":
        return ((-1, 0), (1, 0), (0, -1), (0, 1))
    return ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))


def sparse_components(points, connectivity):
    """Pure function. Splits a list of (y, x) points into touching groups. Returns a list of groups (lists of points)."""
    steps = _steps(connectivity)
    left = set(points)
    groups = []
    for p in points:
        if p not in left:
            continue
        left.discard(p)
        stack = [p]
        group = []
        while stack:
            y, x = stack.pop()
            group.append((y, x))
            for dy, dx in steps:
                q = (y + dy, x + dx)
                if q in left:
                    left.discard(q)
                    stack.append(q)
        groups.append(group)
    return groups


def hole_points(grid, connectivity):
    """Pure function. Rows of 0/1 in; the (y, x) list of every hole pixel out. A hole is background that cannot reach the picture border."""
    if not grid or not grid[0]:
        raise ValueError("the mask is empty: it needs at least one row and one column")
    h, w = len(grid), len(grid[0])
    steps = _steps(connectivity)
    seen = [[False] * w for _ in range(h)]
    stack = []
    for y in range(h):
        for x in range(w):
            if (y in (0, h - 1) or x in (0, w - 1)) and not grid[y][x] and not seen[y][x]:
                seen[y][x] = True
                stack.append((y, x))
    while stack:
        y, x = stack.pop()
        for dy, dx in steps:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not grid[ny][nx] and not seen[ny][nx]:
                seen[ny][nx] = True
                stack.append((ny, nx))
    return [(y, x) for y in range(h) for x in range(w) if not grid[y][x] and not seen[y][x]]


def label_holes(grid, connectivity="4"):
    """Pure function. Returns the pixel count of every hole in rows of 0/1 (empty list = no holes)."""
    return [len(g) for g in sparse_components(hole_points(grid, connectivity), connectivity)]


def _run_ids(bg):
    """Number every unbroken horizontal run of background pixels (0 = not background). bg is a bool [H,W] tensor."""
    import torch

    flat = bg.reshape(-1)
    w = bg.shape[1]
    before = torch.cat([flat.new_zeros(1), flat[:-1]])
    col0 = (torch.arange(flat.numel(), device=bg.device) % w) == 0
    start = flat & (~before | col0)
    return torch.cumsum(start.to(torch.int64), 0) * flat.to(torch.int64)


def _sweep(ids, reached):
    """Marks every background run that already holds a reached pixel as reached (4-neighbour flood along rows)."""
    import torch

    flat_ids = ids
    hit = torch.zeros(int(flat_ids.max()) + 1, dtype=torch.bool, device=ids.device)
    hit[flat_ids[reached.reshape(-1)]] = True
    hit[0] = False
    return hit[flat_ids].view(reached.shape)


class SYMaskFillHoles:
    DESCRIPTION = ("Fills enclosed holes inside a mask, so a donut becomes a disc. A hole is a black area that cannot reach the edge of the picture. "
                   "A ring with a gap in it is not closed, so it stays open. The result is pure black and white.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask whose holes should be filled."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask values above this count as white, the rest as black."}),
                "max_hole_size": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1, "tooltip": "Fill only holes up to this many pixels. 0 fills every hole."}),
                "connectivity": (["4", "8"], {"default": "4", "tooltip": "4: outside leaks only in straight lines, diagonal gaps stay shut. 8: it also leaks through diagonal gaps."}),
            }
        }

    def run(self, mask, threshold, max_hole_size, connectivity):
        import torch
        import torch.nn.functional as F

        check_args(threshold, max_hole_size, connectivity)
        m = mask if mask.dim() == 3 else mask.unsqueeze(0)
        out = torch.empty(m.shape, dtype=torch.float32, device=m.device)
        for i in range(m.shape[0]):
            b = m[i] > threshold
            h, w = b.shape
            bg = ~b
            reached = torch.zeros_like(bg)
            reached[0, :] = bg[0, :]
            reached[h - 1, :] = bg[h - 1, :]
            reached[:, 0] = bg[:, 0]
            reached[:, w - 1] = bg[:, w - 1]
            ids_r = _run_ids(bg)
            ids_c = _run_ids(bg.t().contiguous())
            bgf = bg.to(torch.float32)[None, None]
            count = int(reached.sum())
            for _ in range(4 * (h + w)):
                reached = _sweep(ids_r, reached)
                reached = _sweep(ids_c, reached.t().contiguous()).t().contiguous()
                if connectivity == "8":
                    grown = F.max_pool2d(reached.to(torch.float32)[None, None], 3, 1, 1) * bgf
                    reached = grown[0, 0] > 0.5
                new_count = int(reached.sum())
                if new_count == count:
                    break
                count = new_count
            holes = bg & ~reached
            total = int(holes.sum())
            if total and max_hole_size > 0 and total > max_hole_size:
                pts = [tuple(p) for p in holes.nonzero().tolist()]
                keep = torch.zeros_like(holes)
                for g in sparse_components(pts, connectivity):
                    if len(g) <= max_hole_size:
                        ys = torch.tensor([p[0] for p in g], device=m.device)
                        xs = torch.tensor([p[1] for p in g], device=m.device)
                        keep[ys, xs] = True
                holes = keep
            out[i] = (b | holes).to(torch.float32)
        return (out if mask.dim() == 3 else out[0],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFillHoles", SYMaskFillHoles)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskFillHoles"] = "Mask Fill Holes SY"
