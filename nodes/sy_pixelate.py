"""Pixelate SY: turns a picture into big square blocks."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_d3_info import need_nonempty, plural, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_d3_info import need_nonempty, plural, size_text

MODES = ("average", "nearest")


def block_ranges(side, block):
    """Pure function. Splits a side of `side` pixels into (start, end) blocks from 0. The last block may be smaller."""
    if side < 1:
        raise ValueError("the picture side must be at least 1 pixel")
    if block < 1:
        raise ValueError("block_size must be at least 1, got %s" % block)
    return [(s, min(s + block, side)) for s in range(0, side, block)]


def resolve_block(block_size, blocks_across, width):
    """Pure function. Block size in pixels. blocks_across 0 uses block_size; above 0 it wins and picks the size
    that gives about that many blocks along the width."""
    if blocks_across < 0:
        raise ValueError("blocks_across cannot be negative, got %s" % blocks_across)
    if blocks_across > 0:
        if width < 1:
            raise ValueError("the picture side must be at least 1 pixel")
        return max(1, -(-int(width) // int(blocks_across)))
    if block_size < 1:
        raise ValueError("block_size must be at least 1, got %s" % block_size)
    return int(block_size)


def pool_window(block, height, width):
    """Pure function. (kernel_h, kernel_w) for averaging: never bigger than the picture, so a block larger than the picture
    side still works (the whole side becomes one block)."""
    if block < 1 or height < 1 or width < 1:
        raise ValueError("block and picture sizes must be at least 1")
    return (min(block, height), min(block, width))


def pixelate_info(block, width, height, mode):
    """Pure function. Plain sentence about the blocks."""
    cols = -(-width // block)
    rows = -(-height // block)
    if block == 1:
        return "Block size is 1: the picture was passed through unchanged."
    text = "Blocks of %dx%d px on a %s picture: %d x %d = %s (%s)." % (
        block, block, size_text(width, height), cols, rows, plural(cols * rows, "block"), "mean colour" if mode == "average" else "top-left pixel")
    if block >= min(width, height):
        text += " The block is as big as a picture side, so that whole side is one colour: lower block_size."
    return text


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
    DESCRIPTION = "Makes a picture blocky, like big pixels. Each block becomes one colour. Set blocks_across to say how many blocks you want across the picture instead of a pixel size. The info output counts the blocks."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to make blocky."}),
                "block_size": ("INT", {"default": 8, "min": 1, "max": 512, "tooltip": "Width and height of each block in pixels. 1 changes nothing."}),
                "mode": (list(MODES), {"default": "average", "tooltip": "Average uses the mean colour of the block. Nearest uses its top-left pixel."}),
            },
            "optional": {
                "blocks_across": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 1, "tooltip": "Wanted number of blocks across the width, for example 64. 0 uses block_size instead."}),
            },
        }

    def run(self, image, block_size, mode, blocks_across=0):
        import torch
        import torch.nn.functional as F

        need_image(image)
        need_nonempty(image.shape)
        if block_size < 1:
            raise ValueError("block_size must be at least 1, got %s" % block_size)
        if mode not in MODES:
            raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
        _, h, w, c = image.shape
        b = resolve_block(block_size, blocks_across, w)
        info = pixelate_info(b, int(w), int(h), mode)
        if b == 1:
            return (image, info)
        rgb = min(c, 3)
        x = image[..., :rgb].permute(0, 3, 1, 2)
        if mode == "average":
            small = F.avg_pool2d(x.to(torch.float32), kernel_size=pool_window(b, h, w), stride=b, ceil_mode=True).to(image.dtype)
        else:
            small = x[:, :, ::b, ::b]
        big = small.repeat_interleave(b, dim=2).repeat_interleave(b, dim=3)[:, :, :h, :w]
        out = image.clone()
        out[..., :rgb] = big.permute(0, 2, 3, 1)
        return (out, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Pixelate", SYPixelate)
