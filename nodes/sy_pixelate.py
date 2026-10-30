"""Pixelate SY: turns a picture into big square blocks."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

MODES = ("average", "nearest")


def block_ranges(side, block):
    """Pure function. Splits a side of `side` pixels into (start, end) blocks from 0. The last block may be smaller."""
    if side < 1:
        raise ValueError("the picture side must be at least 1 pixel")
    if block < 1:
        raise ValueError("block_size must be at least 1, got %s" % block)
    return [(s, min(s + block, side)) for s in range(0, side, block)]


def pixelate_grid(grid, block, mode):
    """Pure function. grid is rows of pixel values (numbers). Returns a new grid with every block filled."""
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
    h, w = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for y0, y1 in block_ranges(h, block):
        for x0, x1 in block_ranges(w, block):
            if mode == "nearest":
                v = grid[y0][x0]
            else:
                total = sum(grid[y][x] for y in range(y0, y1) for x in range(x0, x1))
                v = total / float((y1 - y0) * (x1 - x0))
            for y in range(y0, y1):
                for x in range(x0, x1):
                    out[y][x] = v
    return out


class SYPixelate:
    DESCRIPTION = "Makes a picture blocky, like big pixels. Each block becomes one colour."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to make blocky."}),
                "block_size": ("INT", {"default": 8, "min": 1, "max": 512, "tooltip": "Width and height of each block in pixels. 1 changes nothing."}),
                "mode": (list(MODES), {"default": "average", "tooltip": "Average uses the mean colour of the block. Nearest uses its top-left pixel."}),
            }
        }

    def run(self, image, block_size, mode):
        import torch
        import torch.nn.functional as F

        need_image(image)
        if block_size < 1:
            raise ValueError("block_size must be at least 1, got %s" % block_size)
        if mode not in MODES:
            raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
        b = int(block_size)
        if b == 1:
            return (image,)
        _, h, w, c = image.shape
        rgb = min(c, 3)
        x = image[..., :rgb].permute(0, 3, 1, 2)
        if mode == "average":
            small = F.avg_pool2d(x.to(torch.float32), kernel_size=b, stride=b, ceil_mode=True).to(image.dtype)
        else:
            small = x[:, :, ::b, ::b]
        big = small.repeat_interleave(b, dim=2).repeat_interleave(b, dim=3)[:, :, :h, :w]
        out = image.clone()
        out[..., :rgb] = big.permute(0, 2, 3, 1)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Pixelate", SYPixelate)
