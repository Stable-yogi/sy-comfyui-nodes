"""Dither SY: retro few-colour look with a dotted pattern instead of smooth bands."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

METHODS = ["ordered 4x4", "ordered 8x8", "floyd-steinberg"]
MAX_DIFFUSION_WIDTH = 4096


def bayer_matrix(n):
    """Pure function. The n x n Bayer matrix (n = 4 or 8) as a list of rows, values 0..n*n-1."""
    if n not in (4, 8):
        raise ValueError("matrix size must be 4 or 8, got %s" % (n,))
    m = [[0, 2], [3, 1]]
    size = 2
    while size < n:
        nxt = [[0] * (size * 2) for _ in range(size * 2)]
        for y in range(size):
            for x in range(size):
                v = 4 * m[y][x]
                nxt[y][x] = v
                nxt[y][x + size] = v + 2
                nxt[y + size][x] = v + 3
                nxt[y + size][x + size] = v + 1
        m, size = nxt, size * 2
    return m


def quantise(value, levels):
    """Pure function. Snap value (0..1) to the nearest of `levels` evenly spaced steps."""
    check_levels(levels)
    v = min(1.0, max(0.0, float(value)))
    steps = levels - 1
    return int(v * steps + 0.5) / float(steps)


def check_levels(levels):
    if levels != levels or int(levels) != levels or levels < 2 or levels > 16:
        raise ValueError("levels must be a whole number from 2 to 16, got %s" % (levels,))
    return int(levels)


def check_method(method, width):
    """Pure function. Refuse an unknown method, or error diffusion on a very wide picture."""
    if method not in METHODS:
        raise ValueError("method must be one of %s, got %r" % (", ".join(METHODS), method))
    if method == "floyd-steinberg" and width > MAX_DIFFUSION_WIDTH:
        raise ValueError("too wide for error diffusion: pick an ordered method or shrink the picture "
                         "(%d pixels wide, the limit is %d)" % (width, MAX_DIFFUSION_WIDTH))
    return method


def _ordered(x, levels, n):
    import torch

    mat = torch.tensor(bayer_matrix(n), dtype=torch.float32, device=x.device)
    thr = (mat + 0.5) / float(n * n) - 0.5
    h, w = x.shape[1], x.shape[2]
    reps_y, reps_x = -(-h // n), -(-w // n)
    thr = thr.repeat(reps_y, reps_x)[:h, :w].view(1, h, w, 1)
    steps = float(levels - 1)
    return (torch.floor(x * steps + 0.5 + thr)).clamp(0, steps) / steps


def _diffuse(x, levels):
    """Floyd-Steinberg, processed along diagonal fronts (pixel (y, x) belongs to front x + 2y), which keeps
    exactly the normal left-to-right, top-to-bottom order of dependencies but handles each front in one go."""
    import torch

    b, h, w, c = x.shape
    steps = float(levels - 1)
    src = x.permute(0, 3, 1, 2).reshape(b * c, h, w)
    err = torch.zeros(b * c, h + 1, w + 2, dtype=src.dtype, device=src.device)  # padded: column x is stored at x + 1
    out = torch.empty_like(src)
    for t in range(w + 2 * (h - 1)):
        y0 = max(0, -((w - 1 - t) // 2))
        y1 = min(h - 1, t // 2)
        if y1 < y0:
            continue
        ys = torch.arange(y0, y1 + 1, device=src.device)
        xs = t - 2 * ys
        v = src[:, ys, xs] + err[:, ys, xs + 1]
        q = (torch.floor(v * steps + 0.5)).clamp(0, steps) / steps
        out[:, ys, xs] = q
        e = v - q
        err[:, ys, xs + 2] += e * (7.0 / 16.0)
        err[:, ys + 1, xs] += e * (3.0 / 16.0)
        err[:, ys + 1, xs + 1] += e * (5.0 / 16.0)
        err[:, ys + 1, xs + 2] += e * (1.0 / 16.0)
    return out.view(b, c, h, w).permute(0, 2, 3, 1)


def dither_tensor(image, method, levels, mono, strength):
    check_levels(levels)
    ae.check_range("strength", strength, 0.0, 1.0)
    if method not in METHODS:
        raise ValueError("method must be one of %s, got %r" % (", ".join(METHODS), method))
    import torch

    x, was3 = ae.prep_image(image, need_colour=False)
    check_method(method, x.shape[2])
    if strength == 0:
        return image.clone()
    c = x.shape[3]
    nc = min(c, 3)
    work = x[..., :nc].clamp(0.0, 1.0)
    if mono:
        work = ae.luma_of(work).expand(-1, -1, -1, 3) if nc >= 3 else work
    if method == "floyd-steinberg":
        done = _diffuse(work.contiguous(), levels)
    else:
        done = _ordered(work, levels, 4 if method == "ordered 4x4" else 8)
    out = x.clone()
    out[..., :nc] = x[..., :nc] + (done - x[..., :nc]) * strength
    return ae.finish_image(out, image, was3)


class SYDither:
    DESCRIPTION = ("Gives the picture a retro few-colour look made of dots instead of smooth bands. "
                   "Fewer levels means a rougher look. Ordered methods make a regular pattern, floyd-steinberg a grainy one.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to dither."}),
            "method": (METHODS, {"default": "ordered 8x8", "tooltip": "Ordered makes a regular dot pattern. Floyd-steinberg makes a grainy, natural one."}),
            "levels": ("INT", {"default": 4, "min": 2, "max": 16, "tooltip": "Steps per colour channel. 2 gives pure black and white dots."}),
            "mono": ("BOOLEAN", {"default": False, "tooltip": "On: the result is grey instead of colour."}),
            "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much of the dither is used. 0 keeps the original."}),
        }}

    def run(self, image, method, levels, mono, strength):
        return (dither_tensor(image, method, int(levels), bool(mono), float(strength)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Dither", SYDither)
NODE_DISPLAY_NAME_MAPPINGS["SYDither"] = "Dither SY"
