"""Halftone Dots SY: newspaper-print look made of round dots whose size follows the darkness."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

COLOUR_MODES = ("black on white", "keep colour")
DOT_FACTOR = 0.7  # a fully black cell gets a dot of about 0.7 * cell_size radius


def check_settings(cell_size, angle, softness, colour_mode):
    if not 3 <= int(cell_size) <= 64:
        raise ValueError("cell_size must be between 3 and 64, got %r" % (cell_size,))
    if not 0.0 <= float(angle) <= 90.0:
        raise ValueError("angle must be between 0 and 90 degrees, got %r" % (angle,))
    if not 0.0 <= float(softness) <= 1.0:
        raise ValueError("softness must be between 0 and 1, got %r" % (softness,))
    if colour_mode not in COLOUR_MODES:
        raise ValueError("colour_mode must be one of: %s, got %r" % (", ".join(COLOUR_MODES), colour_mode))


def dot_radius(darkness, cell_size):
    """Pure function. darkness 0 (white) .. 1 (black) -> dot radius in pixels. Dot area follows darkness."""
    if not 0.0 <= darkness <= 1.0:
        raise ValueError("darkness must be between 0 and 1, got %r" % (darkness,))
    if cell_size <= 0:
        raise ValueError("cell_size must be above 0, got %r" % (cell_size,))
    return DOT_FACTOR * cell_size * math.sqrt(darkness)


def cell_of(x, y, angle, cell_size):
    """Pure function. Pixel (x, y) -> (cell column, cell row, offset from the cell centre along u, along v)."""
    a = math.radians(angle)
    u = x * math.cos(a) + y * math.sin(a)
    v = -x * math.sin(a) + y * math.cos(a)
    i, j = math.floor(u / cell_size), math.floor(v / cell_size)
    return i, j, u - (i + 0.5) * cell_size, v - (j + 0.5) * cell_size


def halftone_tensor(image, cell_size, angle, colour_mode, softness):
    """Torch. image [B,H,W,C] float 0..1 -> new tensor of the same shape."""
    import torch

    check_settings(cell_size, angle, softness, colour_mode)
    cell = float(cell_size)
    a = math.radians(float(angle))
    height, width = image.shape[1], image.shape[2]
    ys, xs = torch.meshgrid(torch.arange(height, dtype=torch.float32, device=image.device),
                            torch.arange(width, dtype=torch.float32, device=image.device), indexing="ij")
    u = xs * math.cos(a) + ys * math.sin(a)
    v = -xs * math.sin(a) + ys * math.cos(a)
    ci, cj = torch.floor(u / cell), torch.floor(v / cell)
    dist = torch.sqrt((u - (ci + 0.5) * cell) ** 2 + (v - (cj + 0.5) * cell) ** 2)
    ci, cj = ci - ci.min(), cj - cj.min()
    cell_id = (ci * (cj.max() + 1.0) + cj).long().flatten()
    n_cells = int(cell_id.max()) + 1
    counts = torch.bincount(cell_id, minlength=n_cells).clamp(min=1).float()
    edge = max(1.0, float(softness) * cell * 0.5)
    outs = []
    for b in range(image.shape[0]):
        img = image[b].float()
        channels = img.shape[2]
        rgb = img[..., :3] if channels >= 3 else img[..., :1].repeat(1, 1, 3)
        lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).flatten()
        mean_lum = torch.zeros(n_cells, device=img.device).index_add_(0, cell_id, lum) / counts
        radius = DOT_FACTOR * cell * torch.sqrt((1.0 - mean_lum).clamp(0.0, 1.0))
        cover = ((radius[cell_id].reshape(height, width) - dist) / edge + 0.5).clamp(0.0, 1.0)[..., None]
        if colour_mode == "keep colour":
            sums = torch.zeros(n_cells, 3, device=img.device).index_add_(0, cell_id, rgb.reshape(-1, 3))
            ink = (sums / counts[:, None])[cell_id].reshape(height, width, 3)
        else:
            ink = torch.zeros_like(rgb)
        result = (1.0 - cover) + cover * ink
        if channels == 4:
            result = torch.cat([result, img[..., 3:4]], dim=2)
        elif channels < 3:
            result = result[..., :channels]
        outs.append(result.clamp(0.0, 1.0))
    return torch.stack(outs, dim=0)


class SYHalftoneDots:
    DESCRIPTION = ("Gives the picture a newspaper-print look. It is cut into a tilted grid of cells and every cell "
                   "becomes a round dot: the darker the cell, the bigger the dot.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture (or batch of pictures) to turn into dots."}),
            "cell_size": ("INT", {"default": 5, "min": 3, "max": 64, "tooltip": "Width of one dot cell in pixels. Bigger cells give coarser dots."}),
            "angle": ("FLOAT", {"default": 45.0, "min": 0.0, "max": 90.0, "step": 1.0, "tooltip": "Tilt of the dot grid in degrees. 45 is the classic print angle."}),
            "colour_mode": (list(COLOUR_MODES), {"default": "black on white", "tooltip": "Black dots on white paper, or dots that keep the colour of their cell."}),
            "softness": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How soft the dot edges are. 0 is crisp, 1 is very blurry."}),
        }}

    def run(self, image, cell_size, angle, colour_mode, softness):
        return (halftone_tensor(image, cell_size, angle, colour_mode, softness),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HalftoneDots", SYHalftoneDots)
NODE_DISPLAY_NAME_MAPPINGS["SYHalftoneDots"] = "Halftone Dots SY"
