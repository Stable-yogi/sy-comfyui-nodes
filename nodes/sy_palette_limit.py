"""Palette Limit SY: reduces a picture to a few colours for a poster or pixel-art look."""
import random

try:
    from ._sy_common import category, register
    from ._sy_hexcolour import to_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import to_hex

DITHERS = ("none", "ordered 4x4")
MAX_SAMPLE = 4096
BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def _dist(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def kmeans_palette(pixels, k, seed, iterations=8):
    """Pure function. pixels: list of (r, g, b) floats 0..1. Returns k colours, darkest first, same answer for the same seed.
    At most 4096 pixels are used (picked by the seed). If the picture has fewer than k different colours, some repeat."""
    if not (2 <= k <= 64):
        raise ValueError("colours must be between 2 and 64, got %s" % (k,))
    pts = [tuple(float(v) for v in p[:3]) for p in pixels]
    if not pts:
        raise ValueError("the picture has no pixels to build a palette from")
    rng = random.Random(int(seed))
    if len(pts) > MAX_SAMPLE:
        pts = rng.sample(pts, MAX_SAMPLE)
    # spread-out starting colours (each new one is picked far from those already chosen)
    centres = [pts[rng.randrange(len(pts))]]
    while len(centres) < k:
        d = [min(_dist(p, c) for c in centres) for p in pts]
        total = sum(d)
        if total <= 0:
            centres.append(centres[0])
            continue
        pick = rng.random() * total
        acc = 0.0
        chosen = pts[-1]
        for p, dv in zip(pts, d):
            acc += dv
            if acc >= pick and dv > 0:
                chosen = p
                break
        centres.append(chosen)
    for _ in range(max(1, int(iterations))):
        sums = [[0.0, 0.0, 0.0, 0] for _ in range(k)]
        for p in pts:
            best = min(range(k), key=lambda i: _dist(p, centres[i]))
            s = sums[best]
            s[0] += p[0]
            s[1] += p[1]
            s[2] += p[2]
            s[3] += 1
        new = []
        for i in range(k):
            s = sums[i]
            new.append((s[0] / s[3], s[1] / s[3], s[2] / s[3]) if s[3] else centres[i])
        if new == centres:
            break
        centres = new
    return sorted(centres, key=luma)


def palette_text(palette):
    """Pure function. Colours as web colours separated by commas."""
    return ",".join(to_hex(c) for c in palette)


def dither_offset(x, y, spread):
    """Pure function. Ordered 4x4 offset (about -spread/2 .. +spread/2) for pixel x, y."""
    return ((BAYER4[y % 4][x % 4] + 0.5) / 16.0 - 0.5) * spread


def dither_spread(k):
    """Pure function. How strongly the dither nudges a colour before it is matched: smaller for bigger palettes."""
    return 1.0 / max(2.0, k ** (1.0 / 3.0))


def limit_tensor(image, colours, dither, seed):
    """Torch [B,H,W,C]. Returns (image with only `colours` colours, palette text). Alpha and extra channels stay."""
    import torch

    if dither not in DITHERS:
        raise ValueError("dither must be one of: %s, got %r" % (", ".join(DITHERS), dither))
    if image.shape[3] < 3:
        raise ValueError("this node needs a colour picture with at least 3 channels")
    b, h, w, c = image.shape
    rgb = image[..., :3].float().clamp(0.0, 1.0)
    flat = rgb.reshape(-1, 3)
    gen = torch.Generator().manual_seed(int(seed))
    idx = torch.randperm(flat.shape[0], generator=gen)[:MAX_SAMPLE]
    sample = [tuple(v) for v in flat[idx].cpu().tolist()]
    palette = kmeans_palette(sample, int(colours), seed)
    pal = torch.tensor(palette, dtype=torch.float32, device=image.device)
    work = rgb
    if dither == "ordered 4x4":
        ys = torch.arange(h, device=image.device).view(h, 1) % 4
        xs = torch.arange(w, device=image.device).view(1, w) % 4
        bayer = torch.tensor(BAYER4, dtype=torch.float32, device=image.device)
        off = ((bayer[ys, xs] + 0.5) / 16.0 - 0.5) * dither_spread(int(colours))
        work = rgb + off.view(1, h, w, 1)
    flat = work.reshape(-1, 3)
    out = torch.empty_like(flat)
    step = 1 << 20
    for i in range(0, flat.shape[0], step):
        d = torch.cdist(flat[i:i + step], pal)
        out[i:i + step] = pal[d.argmin(dim=1)]
    result = image.clone()
    result[..., :3] = out.reshape(b, h, w, 3).to(image.dtype)
    return result, palette_text(palette)


class SYPaletteLimit:
    DESCRIPTION = ("Reduces a picture to a small number of colours for a poster or pixel-art look. "
                   "The colour list is also given as text, darkest first.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "palette")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to reduce. All of them share one colour list."}),
            "colours": ("INT", {"default": 8, "min": 2, "max": 64, "tooltip": "How many colours the result may use."}),
            "dither": (list(DITHERS), {"default": "none", "tooltip": "Ordered 4x4 adds a fine checker pattern that hides banding."}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Same seed and same picture give the same colours every time."}),
        }}

    def run(self, image, colours, dither, seed):
        return limit_tensor(image, colours, dither, seed)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PaletteLimit", SYPaletteLimit)
NODE_DISPLAY_NAME_MAPPINGS["SYPaletteLimit"] = "Palette Limit SY"
