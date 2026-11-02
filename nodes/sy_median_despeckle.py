"""Median Despeckle SY: removes small specks and hot pixels while keeping edges."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_args(size, passes):
    if size < 3 or size > 15 or size % 2 == 0:
        raise ValueError("size must be an odd number from 3 to 15, got %s" % size)
    if passes < 1 or passes > 4:
        raise ValueError("passes must be from 1 to 4, got %s" % passes)


def median_of_window(values):
    """Pure function. The middle value of a list (odd length). An even length takes the lower of the two middle values."""
    vals = sorted(values)
    if not vals:
        raise ValueError("the window is empty: give at least one value")
    return vals[(len(vals) - 1) // 2]


def median_filter_2d(rows, size):
    """Pure function. Median filter on a small grid of numbers (list of lists); edges repeat the border."""
    check_args(size, 1)
    h, w = len(rows), len(rows[0])
    r = size // 2
    out = []
    for y in range(h):
        line = []
        for x in range(w):
            win = [rows[min(h - 1, max(0, y + dy))][min(w - 1, max(0, x + dx))]
                   for dy in range(-r, r + 1) for dx in range(-r, r + 1)]
            line.append(median_of_window(win))
        out.append(line)
    return out


class SYMedianDespeckle:
    DESCRIPTION = "Removes small specks and hot pixels by replacing each pixel with the middle value of its neighbours. Edges stay sharp."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch to clean."}),
                "size": ("INT", {"default": 3, "min": 3, "max": 15, "step": 2, "tooltip": "Width of the neighbour square in pixels. Odd numbers only; bigger removes bigger specks."}),
                "passes": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1, "tooltip": "How many times to repeat the cleaning."}),
            }
        }

    def run(self, image, size, passes):
        import torch
        import torch.nn.functional as F

        check_args(size, passes)
        r = size // 2
        b, h, w, c = image.shape
        x = image.permute(0, 3, 1, 2).reshape(b * c, 1, h, w)
        strip = max(1, 2000000 // max(1, w * size * size * b * c))   # rows per strip, keeps memory small
        for _ in range(passes):
            padded = F.pad(x, (r, r, r, r), mode="replicate")
            win = padded.unfold(2, size, 1).unfold(3, size, 1)       # [N,1,H,W,size,size] view
            parts = []
            for y0 in range(0, h, strip):
                piece = win[:, :, y0:y0 + strip].reshape(b * c, 1, min(strip, h - y0), w, size * size)
                parts.append(piece.median(dim=-1).values)
            x = torch.cat(parts, dim=2)
        out = x.reshape(b, c, h, w).permute(0, 2, 3, 1).contiguous()
        return (out.to(image.dtype),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MedianDespeckle", SYMedianDespeckle)
NODE_DISPLAY_NAME_MAPPINGS["SYMedianDespeckle"] = "Median Despeckle SY"
