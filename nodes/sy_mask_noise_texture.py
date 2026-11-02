"""Mask Noise Texture SY: draws a cloudy mask from seeded noise (dirt, mist, random cut-outs)."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_M = 0xFFFFFFFF
_PX = 374761393
_PY = 668265263
_PS = 3266489917
_R1 = 1274126177
_R2 = 668265263
_OCTAVE_STEP = 1013904223


def check_args(width, height, scale, octaves, contrast, seed, threshold):
    if not 8 <= width <= 8192 or not 8 <= height <= 8192:
        raise ValueError("width and height must each be between 8 and 8192, got %sx%s" % (width, height))
    if not 2.0 <= scale <= 512.0:
        raise ValueError("scale must be between 2 and 512 pixels, got %s" % scale)
    if not 1 <= octaves <= 6:
        raise ValueError("octaves must be between 1 and 6, got %s" % octaves)
    if not 0.1 <= contrast <= 8.0:
        raise ValueError("contrast must be between 0.1 and 8, got %s" % contrast)
    if not 0 <= seed <= 2 ** 53:
        raise ValueError("seed must be between 0 and 2**53, got %s" % seed)
    if not -1.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between -1 and 1 (-1 gives soft clouds), got %s" % threshold)


def seed_term(seed):
    """Pure function. Folds a big seed into one 32-bit number (integer maths only)."""
    s = (seed ^ (seed >> 32)) & _M
    return (s * _PS) & _M


def lattice_hash(ix, iy, seed):
    """Pure function, integer maths only, same answer on every machine. Returns a number from 0 to 1 for lattice point (ix, iy)."""
    h = (ix * _PX + iy * _PY + seed_term(seed) + 2654435769) & _M
    h = ((h ^ (h >> 15)) * _R1) & _M
    h = ((h ^ (h >> 13)) * _R2) & _M
    h ^= h >> 16
    return h / 4294967295.0


def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def octave_seed(seed, octave):
    return (seed + octave * _OCTAVE_STEP) & ((1 << 64) - 1)


def octave_cell(scale, octave):
    """Pure function. Cloud size in pixels for an octave: each octave is half the size of the one before (never below 1 pixel)."""
    return max(1.0, scale / (2 ** octave))


def shape_value(n, contrast):
    """Pure function. Pushes a noise value (0..1) away from or towards the middle, then clamps to 0..1."""
    return min(1.0, max(0.0, (n - 0.5) * contrast + 0.5))


def noise_at(x, y, scale, octaves, seed):
    """Pure function. The raw noise value (0..1) at pixel (x, y): bilinear smoothstep between lattice values,
    each octave at half the cloud size and half the weight."""
    total = 0.0
    weight = 1.0
    norm = 0.0
    for o in range(octaves):
        cell = octave_cell(scale, o)
        fx = (x + 0.5) / cell
        fy = (y + 0.5) / cell
        ix, iy = math.floor(fx), math.floor(fy)
        tx, ty = smoothstep(fx - ix), smoothstep(fy - iy)
        s = octave_seed(seed, o)
        a = lattice_hash(ix, iy, s)
        b = lattice_hash(ix + 1, iy, s)
        c = lattice_hash(ix, iy + 1, s)
        d = lattice_hash(ix + 1, iy + 1, s)
        total += weight * ((a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty)
        norm += weight
        weight *= 0.5
    return total / norm


def _hash_tensor(ix, iy, seed):
    """Same maths as lattice_hash on integer tensors."""
    h = (ix * _PX + iy * _PY + seed_term(seed) + 2654435769) & _M
    h = ((h ^ (h >> 15)) * _R1) & _M
    h = ((h ^ (h >> 13)) * _R2) & _M
    h = h ^ (h >> 16)
    return h.to("cpu").double() / 4294967295.0


class SYMaskNoiseTexture:
    DESCRIPTION = ("Draws a cloudy mask from seeded noise, for dirt, mist or random cut-outs. The same seed always gives the same mask. "
                   "Leave threshold at -1 for soft clouds, or set a level to cut them into hard black and white shapes.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 8, "max": 8192, "step": 1, "tooltip": "Width of the mask in pixels."}),
                "height": ("INT", {"default": 1024, "min": 8, "max": 8192, "step": 1, "tooltip": "Height of the mask in pixels."}),
                "scale": ("FLOAT", {"default": 64.0, "min": 2.0, "max": 512.0, "step": 1.0, "tooltip": "Size of the biggest clouds in pixels."}),
                "octaves": ("INT", {"default": 3, "min": 1, "max": 6, "step": 1, "tooltip": "How many layers of finer detail are added on top of the big clouds."}),
                "contrast": ("FLOAT", {"default": 1.5, "min": 0.1, "max": 8.0, "step": 0.1, "tooltip": "Higher gives darker darks and brighter brights. Lower gives a flat grey haze."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "step": 1, "tooltip": "Same seed gives the same clouds. Change it for a new pattern."}),
                "threshold": ("FLOAT", {"default": -1.0, "min": -1.0, "max": 1.0, "step": 0.01, "tooltip": "-1 keeps soft clouds. Any other level cuts them into hard black and white shapes."}),
            }
        }

    def run(self, width, height, scale, octaves, contrast, seed, threshold):
        import torch

        check_args(width, height, scale, octaves, contrast, seed, threshold)
        acc = torch.zeros(height, width, dtype=torch.float32)
        weight = 1.0
        norm = 0.0
        for o in range(octaves):
            cell = octave_cell(scale, o)
            s = octave_seed(seed, o)
            fx = (torch.arange(width, dtype=torch.float64) + 0.5) / cell
            fy = (torch.arange(height, dtype=torch.float64) + 0.5) / cell
            ix0 = torch.floor(fx).to(torch.int64)
            iy0 = torch.floor(fy).to(torch.int64)
            tx = smoothstep(fx - ix0).to(torch.float32)
            ty = smoothstep(fy - iy0).to(torch.float32)
            gx = int(ix0.max()) + 2
            gy = int(iy0.max()) + 2
            lat = _hash_tensor(torch.arange(gx, dtype=torch.int64)[None, :].expand(gy, gx),
                               torch.arange(gy, dtype=torch.int64)[:, None].expand(gy, gx), s).to(torch.float32)
            rows = lat[:, ix0] * (1.0 - tx)[None, :] + lat[:, ix0 + 1] * tx[None, :]
            layer = rows[iy0] * (1.0 - ty)[:, None] + rows[iy0 + 1] * ty[:, None]
            acc += layer * weight
            norm += weight
            weight *= 0.5
        acc /= norm
        acc = ((acc - 0.5) * contrast + 0.5).clamp_(0.0, 1.0)
        if threshold > -1.0:
            acc = (acc > threshold).to(torch.float32)
        return (acc[None],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskNoiseTexture", SYMaskNoiseTexture)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskNoiseTexture"] = "Mask Noise Texture SY"
