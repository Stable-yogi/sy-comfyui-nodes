"""Perspective Warp SY: pull the four corners of a picture to new places."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

EDGES = ["black", "stretch", "mirror"]
PLAIN_CORNERS = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
MAX_SIDE = 8192


def homography_from_corners(src_points, dst_points):
    """Pure function. 3x3 matrix (list of lists) that maps each src point to its dst point.
    Solves the 8x8 system with Gaussian elimination."""
    if len(src_points) != 4 or len(dst_points) != 4:
        raise ValueError("need exactly 4 source points and 4 target points")
    a = []
    for (x, y), (u, v) in zip(src_points, dst_points):
        a.append([x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y, u])
        a.append([0.0, 0.0, 0.0, x, y, 1.0, -v * x, -v * y, v])
    n = 8
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-12:
            raise ValueError("these corners cannot be mapped (two or more corners lie on one line). "
                             "Move the corners so they form a proper four-sided shape")
        a[col], a[piv] = a[piv], a[col]
        p = a[col][col]
        a[col] = [val / p for val in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col]
                a[r] = [rv - f * cv for rv, cv in zip(a[r], a[col])]
    s = [a[i][8] for i in range(n)]
    return [[s[0], s[1], s[2]], [s[3], s[4], s[5]], [s[6], s[7], 1.0]]


def apply_homography(h, x, y):
    """Pure function. Move the point (x, y) through the 3x3 matrix h."""
    w = h[2][0] * x + h[2][1] * y + h[2][2]
    if abs(w) < 1e-12:
        raise ValueError("this point cannot be mapped (it lies on the horizon of the warp)")
    return ((h[0][0] * x + h[0][1] * y + h[0][2]) / w, (h[1][0] * x + h[1][1] * y + h[1][2]) / w)


def check_corners(points):
    """Pure function. Refuse a flipped, bow-tie, or zero-area shape. Order: top-left, top-right, bottom-right, bottom-left."""
    if len(points) != 4:
        raise ValueError("need exactly 4 corners")
    for i in range(4):
        ax, ay = points[i]
        bx, by = points[(i + 1) % 4]
        cx, cy = points[(i + 2) % 4]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if cross <= 1e-9:
            raise ValueError("the corners make a flipped or flat shape. Corners must keep their order: "
                             "top-left, top-right, bottom-right, bottom-left, each turning the same way with no corner pushed inside")
    return points


def output_size(width, height, points, keep_size):
    """Pure function. (new_width, new_height, min_x, min_y, span_x, span_y) of the result canvas."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    if keep_size:
        return width, height, 0.0, 0.0, 1.0, 1.0
    mnx, mny, spx, spy = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    nw, nh = max(1, int(round(width * spx))), max(1, int(round(height * spy)))
    if nw > MAX_SIDE or nh > MAX_SIDE:
        raise ValueError("the result would be %dx%d pixels, more than %d. Move the corners closer together or turn keep_size on"
                         % (nw, nh, MAX_SIDE))
    return nw, nh, mnx, mny, spx, spy


def is_plain(points):
    return all(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for p, q in zip(points, PLAIN_CORNERS))


def warp_tensor(image, points, edge, keep_size):
    if edge not in EDGES:
        raise ValueError("edge must be one of %s, got %r" % (", ".join(EDGES), edge))
    for p in points:
        ae.check_range("corner x", p[0], -0.5, 1.5)
        ae.check_range("corner y", p[1], -0.5, 1.5)
    check_corners(points)
    import torch
    import torch.nn.functional as F

    x, was3 = ae.prep_image(image, need_colour=False)
    if keep_size and is_plain(points):
        return image.clone()
    b, h, w, c = x.shape
    nw, nh, mnx, mny, spx, spy = output_size(w, h, points, keep_size)
    inv = homography_from_corners(list(points), PLAIN_CORNERS)
    dev = x.device
    ys = (torch.arange(nh, device=dev, dtype=torch.float32).view(nh, 1).expand(nh, nw) + 0.5) / nh * spy + mny
    xs = (torch.arange(nw, device=dev, dtype=torch.float32).view(1, nw).expand(nh, nw) + 0.5) / nw * spx + mnx
    wd = inv[2][0] * xs + inv[2][1] * ys + inv[2][2]
    bad = wd.abs() < 1e-9
    wd = torch.where(bad, torch.ones_like(wd), wd)
    sx = (inv[0][0] * xs + inv[0][1] * ys + inv[0][2]) / wd
    sy = (inv[1][0] * xs + inv[1][1] * ys + inv[1][2]) / wd
    sx = torch.where(bad, torch.full_like(sx, 10.0), sx)
    sy = torch.where(bad, torch.full_like(sy, 10.0), sy)
    grid = torch.stack((sx * 2.0 - 1.0, sy * 2.0 - 1.0), dim=-1).unsqueeze(0)
    pad = {"stretch": "border", "mirror": "reflection", "black": "zeros"}[edge]
    out = F.grid_sample(x.permute(0, 3, 1, 2), grid.expand(b, nh, nw, 2), mode="bilinear", padding_mode=pad, align_corners=False)
    return ae.finish_image(out.permute(0, 2, 3, 1), image, was3)


class SYPerspectiveWarp:
    DESCRIPTION = ("Pulls the four corners of the picture to new places. Use it to straighten a slanted photo or to tilt a card. "
                   "Corners must keep their order: top-left, top-right, bottom-right, bottom-left.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        req = {"image": ("IMAGE", {"tooltip": "The picture or pictures to warp."})}
        names = (("tl", "top-left", 0.0, 0.0), ("tr", "top-right", 1.0, 0.0), ("br", "bottom-right", 1.0, 1.0), ("bl", "bottom-left", 0.0, 1.0))
        for key, label, dx, dy in names:
            req[key + "_x"] = ("FLOAT", {"default": dx, "min": -0.5, "max": 1.5, "step": 0.005,
                                         "tooltip": "%s x, 0 is the left edge, 1 the right edge." % label})
            req[key + "_y"] = ("FLOAT", {"default": dy, "min": -0.5, "max": 1.5, "step": 0.005,
                                         "tooltip": "%s y, 0 is the top edge, 1 the bottom edge." % label})
        req["edge"] = (EDGES, {"default": "black", "tooltip": "What fills the places the warped picture does not cover."})
        req["keep_size"] = ("BOOLEAN", {"default": True, "tooltip": "On: result has the original size. Off: result is cropped to the new shape."})
        return {"required": req}

    def run(self, image, tl_x, tl_y, tr_x, tr_y, br_x, br_y, bl_x, bl_y, edge, keep_size):
        pts = [(float(tl_x), float(tl_y)), (float(tr_x), float(tr_y)), (float(br_x), float(br_y)), (float(bl_x), float(bl_y))]
        return (warp_tensor(image, pts, edge, bool(keep_size)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PerspectiveWarp", SYPerspectiveWarp)
NODE_DISPLAY_NAME_MAPPINGS["SYPerspectiveWarp"] = "Perspective Warp SY"
