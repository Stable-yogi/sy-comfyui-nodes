"""Value Noise Image SY: makes a cloud, paper or grain texture from scratch."""
import math

try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

DEFAULT_A = "#" + "000000"
DEFAULT_B = "#" + "ffffff"
MASK32 = 0xFFFFFFFF


def check_args(width, height, scale, octaves, batch):
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %sx%s" % (width, height))
    if scale < 1:
        raise ValueError("scale must be at least 1 pixel per feature, got %s" % scale)
    if octaves < 1 or octaves > 8:
        raise ValueError("octaves must be from 1 to 8, got %s" % octaves)
    if batch < 1:
        raise ValueError("batch must be at least 1, got %s" % batch)


def seed_term(seed, octave):
    return (int(seed) * 1013904223 + octave * 2654435761) & MASK32


def lattice_value(ix, iy, sterm):
    """Pure function. Seeded random number 0..1 for one grid corner (same maths as the picture version)."""
    h = (ix * 374761393 + iy * 668265263 + sterm) & MASK32
    h = ((h ^ (h >> 13)) * 1274126177) & MASK32
    h ^= h >> 16
    return h / float(MASK32)


def smooth(t):
    return t * t * (3.0 - 2.0 * t)


def cell_size(scale, octave):
    return max(1.0, float(scale) / (2 ** octave))


def noise_grid(w, h, scale, octaves, seed):
    """Pure function. Rows of values 0..1: smooth interpolation of seeded random grids; each octave has half the size and half the weight."""
    check_args(w, h, scale, octaves, 1)
    total = sum(0.5 ** o for o in range(octaves))
    rows = [[0.0] * w for _ in range(h)]
    for o in range(octaves):
        cs = cell_size(scale, o)
        st = seed_term(seed, o)
        wt = 0.5 ** o
        for y in range(h):
            gy = (y + 0.5) / cs
            iy = math.floor(gy)
            fy = smooth(gy - iy)
            for x in range(w):
                gx = (x + 0.5) / cs
                ix = math.floor(gx)
                fx = smooth(gx - ix)
                a = lattice_value(ix, iy, st)
                b = lattice_value(ix + 1, iy, st)
                c = lattice_value(ix, iy + 1, st)
                d = lattice_value(ix + 1, iy + 1, st)
                top = a + (b - a) * fx
                bot = c + (d - c) * fx
                rows[y][x] += wt * (top + (bot - top) * fy)
    return [[min(1.0, max(0.0, v / total)) for v in line] for line in rows]


def noise_tensor(w, h, scale, octaves, seed):
    """Same picture as noise_grid, built with torch. Returns [h, w] floats 0..1."""
    import torch

    total = sum(0.5 ** o for o in range(octaves))
    acc = torch.zeros(h, w, dtype=torch.float64)
    ys = torch.arange(h, dtype=torch.float64) + 0.5
    xs = torch.arange(w, dtype=torch.float64) + 0.5

    def corner(ix, iy, st):
        v = (ix * 374761393 + iy * 668265263 + st) & MASK32
        v = ((v ^ (v >> 13)) * 1274126177) & MASK32
        v = v ^ (v >> 16)
        return v.to(torch.float64) / float(MASK32)

    for o in range(octaves):
        cs = cell_size(scale, o)
        st = seed_term(seed, o)
        gy = ys / cs
        gx = xs / cs
        iy = torch.floor(gy)
        ix = torch.floor(gx)
        fy = smooth(gy - iy)[:, None]
        fx = smooth(gx - ix)[None, :]
        iyl = iy.to(torch.int64)[:, None]
        ixl = ix.to(torch.int64)[None, :]
        a = corner(ixl, iyl, st)
        b = corner(ixl + 1, iyl, st)
        c = corner(ixl, iyl + 1, st)
        d = corner(ixl + 1, iyl + 1, st)
        top = a + (b - a) * fx
        bot = c + (d - c) * fx
        acc += (top + (bot - top) * fy) * (0.5 ** o)
    return (acc / total).clamp(0.0, 1.0).to(torch.float32)


class SYValueNoiseImage:
    DESCRIPTION = "Makes a cloud, paper or grain texture from scratch with smooth seeded noise. Handy as an overlay or a mask source. The same seed gives the same picture."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 1, "tooltip": "Width of the new picture in pixels."}),
                "height": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 1, "tooltip": "Height of the new picture in pixels."}),
                "scale": ("FLOAT", {"default": 48.0, "min": 2.0, "max": 256.0, "step": 1.0, "tooltip": "Size of the biggest blobs in pixels. Small gives fine grain, big gives clouds."}),
                "octaves": ("INT", {"default": 4, "min": 1, "max": 6, "step": 1, "tooltip": "Layers of detail. Each layer has half the size and half the strength."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53 - 1, "tooltip": "Same seed gives the same picture. Change it for a new pattern."}),
                "colour_a": ("STRING", {"default": DEFAULT_A, "multiline": False, "tooltip": "Colour of the darkest noise value, 3 or 6 hex digits like a web colour."}),
                "colour_b": ("STRING", {"default": DEFAULT_B, "multiline": False, "tooltip": "Colour of the brightest noise value, 3 or 6 hex digits like a web colour."}),
                "batch": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1, "tooltip": "How many pictures to make. Each one uses the next seed."}),
            }
        }

    def run(self, width, height, scale, octaves, seed, colour_a, colour_b, batch):
        import torch

        check_args(width, height, scale, octaves, batch)
        a = torch.tensor(parse_hex(colour_a, "colour_a"), dtype=torch.float32)
        b = torch.tensor(parse_hex(colour_b, "colour_b"), dtype=torch.float32)
        masks = torch.stack([noise_tensor(width, height, scale, octaves, seed + i) for i in range(batch)])
        img = a + (b - a) * masks.unsqueeze(-1)
        return (img.contiguous(), masks.contiguous())


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ValueNoiseImage", SYValueNoiseImage)
NODE_DISPLAY_NAME_MAPPINGS["SYValueNoiseImage"] = "Value Noise Image SY"
