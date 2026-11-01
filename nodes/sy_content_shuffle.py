"""Content Shuffle SY: keeps the colours and textures of a picture but scrambles where they sit."""
import math
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 32 - 1


def check_params(h, w, seed, strength, scale):
    """Plain checks with plain messages."""
    if int(h) < 1 or int(w) < 1:
        raise ValueError("picture size must be at least 1 x 1, got %s x %s" % (h, w))
    if not 0.0 <= float(strength) <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % (strength,))
    if int(scale) < 2 or int(scale) > 64:
        raise ValueError("scale must be a whole number from 2 to 64, got %s" % (scale,))
    if int(seed) < 0:
        raise ValueError("seed must be 0 or higher, got %s" % (seed,))


def grid_cells(h, w, scale):
    """Number of wobble cells along height and width. The shorter side gets `scale` cells."""
    short = min(int(h), int(w))
    return (max(1, int(round(scale * int(h) / short))), max(1, int(round(scale * int(w) / short))))


def axis_samples(n, cells):
    """For each of n pixels: (left grid point, smoothed fraction towards the next point)."""
    out = []
    for i in range(n):
        pos = (i / (n - 1.0) if n > 1 else 0.0) * cells
        i0 = min(int(math.floor(pos)), cells - 1)
        t = pos - i0
        out.append((i0, t * t * (3.0 - 2.0 * t)))
    return out


def random_grid(cells_y, cells_x, seed):
    """Two small grids (gx, gy) of values from -1 to 1, one point more than cells each way."""
    rng = random.Random(int(seed))
    gx = [[rng.uniform(-1.0, 1.0) for _ in range(cells_x + 1)] for _ in range(cells_y + 1)]
    gy = [[rng.uniform(-1.0, 1.0) for _ in range(cells_x + 1)] for _ in range(cells_y + 1)]
    return gx, gy


def field_limit(h, w, strength):
    return float(strength) * 0.25 * min(int(h), int(w))


def _blow_up(g, ys, xs, limit):
    rows = []
    for (j0, ty) in ys:
        row = []
        for (i0, tx) in xs:
            top = g[j0][i0] * (1 - tx) + g[j0][i0 + 1] * tx
            bot = g[j0 + 1][i0] * (1 - tx) + g[j0 + 1][i0 + 1] * tx
            row.append((top * (1 - ty) + bot * ty) * limit)
        rows.append(row)
    return rows


def make_wobble_field(h, w, seed, strength, scale):
    """Pure function. Returns (dx, dy): two lists of h rows with w pixel offsets each."""
    check_params(h, w, seed, strength, scale)
    h, w = int(h), int(w)
    cy, cx = grid_cells(h, w, scale)
    gx, gy = random_grid(cy, cx, seed)
    ys, xs = axis_samples(h, cy), axis_samples(w, cx)
    limit = field_limit(h, w, strength)
    return _blow_up(gx, ys, xs, limit), _blow_up(gy, ys, xs, limit)


def shuffle_tensor(image, seed, strength, scale):
    """Moves every pixel along the wobble field. Same field for every picture in the batch."""
    import torch
    import torch.nn.functional as F

    if getattr(image, "ndim", 0) != 4:
        raise ValueError("expected a picture batch shaped [batch, height, width, channels]")
    b, h, w, c = image.shape
    check_params(h, w, seed, strength, scale)
    if float(strength) == 0.0:
        return image
    cy, cx = grid_cells(h, w, scale)
    gx, gy = random_grid(cy, cx, seed)
    ys, xs = axis_samples(h, cy), axis_samples(w, cx)
    limit = field_limit(h, w, strength)
    dev = image.device
    y0 = torch.tensor([p[0] for p in ys], device=dev)
    ty = torch.tensor([p[1] for p in ys], dtype=torch.float32, device=dev).view(h, 1)
    x0 = torch.tensor([p[0] for p in xs], device=dev)
    tx = torch.tensor([p[1] for p in xs], dtype=torch.float32, device=dev).view(1, w)
    fields = []
    for g in (gx, gy):
        gt = torch.tensor(g, dtype=torch.float32, device=dev)
        top = gt[y0][:, x0] * (1 - tx) + gt[y0][:, x0 + 1] * tx
        bot = gt[y0 + 1][:, x0] * (1 - tx) + gt[y0 + 1][:, x0 + 1] * tx
        fields.append((top * (1 - ty) + bot * ty) * limit)
    dxf, dyf = fields
    px = torch.arange(w, dtype=torch.float32, device=dev).view(1, w) + dxf
    py = torch.arange(h, dtype=torch.float32, device=dev).view(h, 1) + dyf
    gxn = px * 2.0 / max(w - 1, 1) - 1.0
    gyn = py * 2.0 / max(h - 1, 1) - 1.0
    grid = torch.stack([gxn, gyn], dim=-1).unsqueeze(0).expand(b, h, w, 2).to(image.dtype)
    x = image.permute(0, 3, 1, 2)
    out = F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return out.permute(0, 2, 3, 1).contiguous()


class SYContentShuffle:
    DESCRIPTION = ("Keeps the colours and textures of a picture but scrambles where they are, by pushing every pixel "
                   "along a smooth random wobble. Handy as a colour reference for control workflows. Same seed, same result.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture (or batch) to scramble."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Picks the wobble pattern. The same seed gives the same result."}),
                "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How far pixels move. 0 changes nothing, 1 moves up to a quarter of the picture size."}),
                "scale": ("INT", {"default": 8, "min": 2, "max": 64, "tooltip": "Wobble cells across the shorter side. A bigger number gives a finer wobble."}),
            },
        }

    def run(self, image, seed, strength, scale):
        return (shuffle_tensor(image, seed, strength, scale),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ContentShuffle", SYContentShuffle)
