"""Shared mask and box maths for the SY mask nodes.

Pure functions work on plain nested lists: a mask is [H][W] of floats 0..1, an image is [H][W][C].
The t_* functions do the same job on torch tensors (torch is imported inside them, never at the top).
A box is (x, y, w, h) in pixels.
"""
import json
import math

CROP_INFO_VERSION = 1
MAX_RADIUS = 512


# ---------------------------------------------------------------- box maths (pure)

def clamp_box(x, y, w, h, img_w, img_h):
    """Cut a box to the image. Returns (x, y, w, h); w or h is 0 when nothing is left inside."""
    if img_w < 1 or img_h < 1:
        raise ValueError("the image must be at least 1 x 1 pixels")
    if w < 0 or h < 0:
        raise ValueError("box width and height cannot be negative")
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(img_w, x + w), min(img_h, y + h)
    return (x0, y0, max(0, x1 - x0), max(0, y1 - y0))


def pad_box(box, pad, img_w, img_h):
    """Grow a box by pad pixels on every side (negative shrinks), then keep it inside the image."""
    x, y, w, h = box
    nw, nh = max(0, w + 2 * pad), max(0, h + 2 * pad)
    return clamp_box(x - pad, y - pad, nw, nh, img_w, img_h)


def fit_multiple(box, multiple, img_w, img_h):
    """Grow a box so width and height are multiples of `multiple`, staying inside the image.
    If the image is too small for that, the box stretches to the image edge instead."""
    if multiple < 1:
        raise ValueError("multiple_of must be 1 or more")
    x, y, w, h = box
    if w < 1 or h < 1:
        raise ValueError("cannot fit an empty box")

    def one(pos, size, total):
        new = -(-size // multiple) * multiple
        if new > total:
            cand = (total // multiple) * multiple
            new = cand if cand >= size else total
        pos = pos - (new - size) // 2
        pos = max(0, min(pos, total - new))
        return pos, new

    nx, nw = one(x, w, img_w)
    ny, nh = one(y, h, img_h)
    return (nx, ny, nw, nh)


def box_mask_list(x, y, w, h, img_w, img_h):
    """A mask [H][W] that is 1.0 inside the box (clipped to the canvas) and 0.0 elsewhere."""
    bx, by, bw, bh = clamp_box(x, y, w, h, img_w, img_h)
    return [[1.0 if (by <= j < by + bh and bx <= i < bx + bw) else 0.0 for i in range(img_w)]
            for j in range(img_h)]


def mask_bbox(rows, threshold=0.5):
    """Bounding box (x, y, w, h) of every pixel with value >= threshold, or None when the mask is empty."""
    xs0 = ys0 = None
    x1 = y1 = -1
    for j, row in enumerate(rows):
        for i, v in enumerate(row):
            if v >= threshold:
                if xs0 is None or i < xs0:
                    xs0 = i
                if ys0 is None or j < ys0:
                    ys0 = j
                x1, y1 = max(x1, i), max(y1, j)
    if xs0 is None:
        return None
    return (xs0, ys0, x1 - xs0 + 1, y1 - ys0 + 1)


def make_crop_info(box, img_w, img_h):
    """Write the paste-back note as a JSON string."""
    x, y, w, h = box
    if w < 1 or h < 1 or x < 0 or y < 0 or x + w > img_w or y + h > img_h:
        raise ValueError("crop box does not fit inside the image")
    return json.dumps({"version": CROP_INFO_VERSION, "x": x, "y": y, "w": w, "h": h,
                       "image_w": img_w, "image_h": img_h}, sort_keys=True)


def parse_crop_info(text):
    """Read and check a paste-back note. Raises ValueError with a plain message when it is wrong."""
    try:
        d = json.loads(text)
    except (TypeError, ValueError):
        raise ValueError("crop_info is not valid: connect the crop_info output of Crop By Mask SY")
    if not isinstance(d, dict) or d.get("version") != CROP_INFO_VERSION:
        raise ValueError("crop_info has the wrong version: connect the crop_info output of Crop By Mask SY")
    vals = []
    for k in ("x", "y", "w", "h", "image_w", "image_h"):
        v = d.get(k)
        if not isinstance(v, int) or isinstance(v, bool):
            raise ValueError("crop_info is missing a whole number for '%s'" % k)
        vals.append(v)
    x, y, w, h, iw, ih = vals
    if w < 1 or h < 1 or x < 0 or y < 0 or x + w > iw or y + h > ih:
        raise ValueError("crop_info describes a box outside its image")
    return {"x": x, "y": y, "w": w, "h": h, "image_w": iw, "image_h": ih}


def open_sides(info):
    """Which sides of the crop box are NOT on the image border (those sides get a soft fade)."""
    return {"left": info["x"] > 0, "top": info["y"] > 0,
            "right": info["x"] + info["w"] < info["image_w"],
            "bottom": info["y"] + info["h"] < info["image_h"]}


# ---------------------------------------------------------------- pixel maths (pure lists)

def disc_half_widths(radius):
    """For each row offset dy in -r..r, the widest sideways reach dx of a round brush of that radius."""
    return {dy: int(math.isqrt(radius * radius - dy * dy)) for dy in range(-radius, radius + 1)}


def dilate_list(rows, radius, shape="round"):
    """Grow bright areas by `radius` pixels (round or square brush). Outside the image counts as 0."""
    if radius <= 0:
        return [list(r) for r in rows]
    h, w = len(rows), len(rows[0])
    hw = disc_half_widths(radius) if shape == "round" else {dy: radius for dy in range(-radius, radius + 1)}
    out = []
    for j in range(h):
        row = []
        for i in range(w):
            best = 0.0
            for dy, dx in hw.items():
                jj = j + dy
                if 0 <= jj < h:
                    src = rows[jj]
                    for ii in range(max(0, i - dx), min(w, i + dx + 1)):
                        if src[ii] > best:
                            best = src[ii]
            row.append(best)
        out.append(row)
    return out


def grow_shrink_list(rows, pixels, shape="round"):
    """Positive pixels grows the white area, negative shrinks it. Shrinking does not eat in from the image border."""
    if abs(pixels) > MAX_RADIUS:
        raise ValueError("pixels must be between -%d and %d" % (MAX_RADIUS, MAX_RADIUS))
    if shape not in ("round", "square"):
        raise ValueError("shape must be round or square")
    if pixels >= 0:
        return dilate_list(rows, pixels, shape)
    inv = [[1.0 - v for v in r] for r in rows]
    grown = dilate_list(inv, -pixels, shape)
    return [[1.0 - v for v in r] for r in grown]


def gaussian_kernel(radius):
    """Normalised 1D blur weights for taps -radius..radius. radius 0 gives [1.0]."""
    if radius <= 0:
        return [1.0]
    sigma = max(0.5, radius / 2.0)
    k = [math.exp(-(t * t) / (2.0 * sigma * sigma)) for t in range(-radius, radius + 1)]
    s = sum(k)
    return [v / s for v in k]


def blur_list(rows, radius):
    """Soft blur of a mask. Edge pixels repeat outward, so the image border stays solid."""
    if radius <= 0:
        return [list(r) for r in rows]
    k = gaussian_kernel(radius)
    h, w = len(rows), len(rows[0])
    tmp = [[sum(k[t + radius] * row[min(w - 1, max(0, i + t))] for t in range(-radius, radius + 1))
            for i in range(w)] for row in rows]
    return [[sum(k[t + radius] * tmp[min(h - 1, max(0, j + t))][i] for t in range(-radius, radius + 1))
             for i in range(w)] for j in range(h)]


def combine_value(a, b, op):
    if op == "union":
        return max(a, b)
    if op == "intersect":
        return min(a, b)
    if op == "subtract":
        return min(a, 1.0 - b)
    if op == "xor":
        return abs(a - b)
    raise ValueError("unknown combine operation: %r (use union, intersect, subtract or xor)" % (op,))


def resize_nearest_mask(rows, height, width):
    sh, sw = len(rows), len(rows[0])
    return [[rows[min(sh - 1, y * sh // height)][min(sw - 1, x * sw // width)] for x in range(width)]
            for y in range(height)]


def combine_list(a, b, op):
    """Mix two masks. If b has another size it is stretched (nearest) to the size of a."""
    if len(b) != len(a) or len(b[0]) != len(a[0]):
        b = resize_nearest_mask(b, len(a), len(a[0]))
    return [[combine_value(u, v, op) for u, v in zip(ra, rb)] for ra, rb in zip(a, b)]


def threshold_invert_list(rows, invert, use_threshold, threshold):
    """Optionally make the mask hard (1 where value >= threshold), then optionally flip it."""
    out = []
    for r in rows:
        row = []
        for v in r:
            if use_threshold:
                v = 1.0 if v >= threshold else 0.0
            if invert:
                v = 1.0 - v
            row.append(v)
        out.append(row)
    return out


def colour_mask_list(img, rgb, tolerance):
    """1.0 where every colour channel is within `tolerance` (0..255) of the wanted colour."""
    if len(rgb) != 3 or any(c < 0 or c > 255 for c in rgb):
        raise ValueError("colour values must be between 0 and 255")
    return [[1.0 if all(abs(p[c] * 255.0 - rgb[c]) <= tolerance + 1e-4 for c in range(3)) else 0.0 for p in row]
            for row in img]


def edge_fade_list(w, h, feather, sides):
    """A [h][w] mask of 1.0 that fades towards the sides marked True in `sides` (over `feather` pixels)."""
    out = []
    for j in range(h):
        row = []
        for i in range(w):
            v = 1.0
            if feather > 0:
                if sides["left"]:
                    v = min(v, (i + 1) / (feather + 1.0))
                if sides["right"]:
                    v = min(v, (w - i) / (feather + 1.0))
                if sides["top"]:
                    v = min(v, (j + 1) / (feather + 1.0))
                if sides["bottom"]:
                    v = min(v, (h - j) / (feather + 1.0))
            row.append(v)
        out.append(row)
    return out


def paste_list(base, crop, mask, x, y):
    """Blend `crop` into `base` at (x, y) using `mask` [h][w] (None means fully). Returns a new image."""
    h, w = len(crop), len(crop[0])
    if y < 0 or x < 0 or y + h > len(base) or x + w > len(base[0]):
        raise ValueError("the crop does not fit inside the image at that position")
    cb, cc = len(base[0][0]), len(crop[0][0])
    if cc < cb:
        raise ValueError("the processed crop has fewer colour channels than the image")
    out = [[list(p) for p in row] for row in base]
    for j in range(h):
        for i in range(w):
            m = 1.0 if mask is None else mask[j][i]
            p = out[y + j][x + i]
            for c in range(cb):
                p[c] = p[c] * (1.0 - m) + crop[j][i][c] * m
    return out


def overlay_list(img, mask, rgb, opacity):
    """Tint the masked area with a colour. opacity 0..1 scales the tint."""
    col = [c / 255.0 for c in rgb]
    out = []
    for ri, rm in zip(img, mask):
        row = []
        for p, m in zip(ri, rm):
            a = m * opacity
            q = list(p)
            for c in range(3):
                q[c] = p[c] * (1.0 - a) + col[c] * a
            row.append(q)
        out.append(row)
    return out


FILL_MODES = ("alpha", "black", "gray")
FILL_GRAY = 0.5


def apply_mask_list(img, mask, fill, keep):
    """Hide everything outside the kept area. keep = 'masked' keeps the white part, 'outside' keeps the black part."""
    if fill not in FILL_MODES:
        raise ValueError("fill must be alpha, black or gray")
    if keep not in ("masked", "outside"):
        raise ValueError("keep must be masked or outside")
    out = []
    for ri, rm in zip(img, mask):
        row = []
        for p, m in zip(ri, rm):
            a = m if keep == "masked" else 1.0 - m
            if fill == "alpha":
                row.append(list(p[:3]) + [a * (p[3] if len(p) > 3 else 1.0)])
            else:
                f = 0.0 if fill == "black" else FILL_GRAY
                row.append([v * a + f * (1.0 - a) for v in p[:3]] + list(p[3:]))
        out.append(row)
    return out


# ---------------------------------------------------------------- torch twins

def t_mask3(mask):
    """Make a mask tensor [B,H,W] float from [H,W] or [B,H,W]."""
    if mask.dim() == 2:
        mask = mask.unsqueeze(0)
    if mask.dim() != 3:
        raise ValueError("mask must have 2 or 3 dimensions (height x width, or batch x height x width)")
    return mask.float()


def t_match_batch(t, n):
    """Repeat/trim the first dimension of t to n items."""
    if t.shape[0] == n:
        return t
    return t[[i % t.shape[0] for i in range(n)]]


def t_resize_mask(mask, height, width):
    import torch.nn.functional as F
    if mask.shape[1] == height and mask.shape[2] == width:
        return mask
    return F.interpolate(mask.unsqueeze(1), size=(height, width), mode="nearest").squeeze(1)


def t_dilate(mask, radius, shape="round"):
    """mask [B,H,W]. Grow bright areas. Outside the image counts as 0."""
    import torch
    import torch.nn.functional as F
    if radius <= 0:
        return mask
    m = mask.unsqueeze(1)
    h = m.shape[2]
    if shape == "square":
        return F.max_pool2d(m, kernel_size=2 * radius + 1, stride=1, padding=radius).squeeze(1)
    widths = disc_half_widths(radius)
    cache = {}
    for dx in set(widths.values()):
        cache[dx] = F.max_pool2d(m, kernel_size=(1, 2 * dx + 1), stride=1, padding=(0, dx))
    stack = {dx: F.pad(v, (0, 0, radius, radius)) for dx, v in cache.items()}
    out = torch.zeros_like(m)
    for dy, dx in widths.items():
        out = torch.maximum(out, stack[dx][:, :, radius + dy: radius + dy + h, :])
    return out.squeeze(1)


def t_grow_shrink(mask, pixels, shape="round"):
    if abs(pixels) > MAX_RADIUS:
        raise ValueError("pixels must be between -%d and %d" % (MAX_RADIUS, MAX_RADIUS))
    if shape not in ("round", "square"):
        raise ValueError("shape must be round or square")
    if pixels >= 0:
        return t_dilate(mask, pixels, shape)
    return 1.0 - t_dilate(1.0 - mask, -pixels, shape)


def t_blur(mask, radius):
    """mask [B,H,W]. Gaussian blur, edge pixels repeat outward."""
    import torch
    import torch.nn.functional as F
    if radius <= 0:
        return mask
    k = torch.tensor(gaussian_kernel(radius), dtype=mask.dtype, device=mask.device)
    m = mask.unsqueeze(1)
    m = F.pad(m, (radius, radius, 0, 0), mode="replicate")
    m = F.conv2d(m, k.view(1, 1, 1, -1))
    m = F.pad(m, (0, 0, radius, radius), mode="replicate")
    m = F.conv2d(m, k.view(1, 1, -1, 1))
    return m.squeeze(1)


def t_combine(a, b, op):
    import torch
    b = t_match_batch(t_resize_mask(b, a.shape[1], a.shape[2]), a.shape[0])
    if op == "union":
        return torch.maximum(a, b)
    if op == "intersect":
        return torch.minimum(a, b)
    if op == "subtract":
        return torch.minimum(a, 1.0 - b)
    if op == "xor":
        return torch.abs(a - b)
    raise ValueError("unknown combine operation: %r (use union, intersect, subtract or xor)" % (op,))


def t_bbox(mask, threshold):
    """Box (x, y, w, h) around every masked pixel of the whole batch, or None when empty."""
    on = (mask >= threshold).any(dim=0)
    rows = on.any(dim=1).nonzero()
    if rows.numel() == 0:
        return None
    cols = on.any(dim=0).nonzero()
    y0, y1 = int(rows[0]), int(rows[-1])
    x0, x1 = int(cols[0]), int(cols[-1])
    return (x0, y0, x1 - x0 + 1, y1 - y0 + 1)


def t_edge_fade(h, w, feather, sides, device=None):
    """Torch version of edge_fade_list. Returns [1,h,w]."""
    import torch
    v = torch.ones(h, w, device=device)
    if feather > 0:
        xs = torch.arange(w, device=device, dtype=torch.float32)[None, :]
        ys = torch.arange(h, device=device, dtype=torch.float32)[:, None]
        f = feather + 1.0
        if sides["left"]:
            v = torch.minimum(v, ((xs + 1) / f).expand(h, w))
        if sides["right"]:
            v = torch.minimum(v, ((w - xs) / f).expand(h, w))
        if sides["top"]:
            v = torch.minimum(v, ((ys + 1) / f).expand(h, w))
        if sides["bottom"]:
            v = torch.minimum(v, ((h - ys) / f).expand(h, w))
    return v.unsqueeze(0)
