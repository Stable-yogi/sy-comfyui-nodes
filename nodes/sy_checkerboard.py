"""Checkerboard SY: makes a new picture of two alternating colour squares."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

DEFAULT_A = "#" + "808080"
DEFAULT_B = "#" + "c0c0c0"


def check_sizes(width, height, cell, batch_size):
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %sx%s" % (width, height))
    if cell < 1:
        raise ValueError("cell must be at least 1, got %s" % cell)
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1, got %s" % batch_size)


def checker_is_a(x, y, cell):
    """Pure function. True when pixel (x, y) uses colour_a."""
    if cell < 1:
        raise ValueError("cell must be at least 1, got %s" % cell)
    return (x // cell + y // cell) % 2 == 0


class SYCheckerboard:
    DESCRIPTION = "Makes a new picture of two alternating colour squares, handy as a test pattern or background."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "tooltip": "Width of the new picture in pixels."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1, "tooltip": "Height of the new picture in pixels."}),
                "cell": ("INT", {"default": 64, "min": 1, "max": 2048, "step": 1, "tooltip": "Side length of one square in pixels."}),
                "colour_a": ("STRING", {"default": DEFAULT_A, "multiline": False, "tooltip": "Colour of the first square, 3 or 6 hex digits like a web colour."}),
                "colour_b": ("STRING", {"default": DEFAULT_B, "multiline": False, "tooltip": "Colour of the other squares, 3 or 6 hex digits like a web colour."}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1, "tooltip": "How many identical pictures to make."}),
            }
        }

    def run(self, width, height, cell, colour_a, colour_b, batch_size):
        import torch

        check_sizes(width, height, cell, batch_size)
        a = parse_hex(colour_a, "colour_a")
        b = parse_hex(colour_b, "colour_b")
        ys = (torch.arange(height) // cell)[:, None]
        xs = (torch.arange(width) // cell)[None, :]
        is_a = ((ys + xs) % 2 == 0).unsqueeze(-1)
        ca = torch.tensor(a, dtype=torch.float32)
        cb = torch.tensor(b, dtype=torch.float32)
        img = torch.where(is_a, ca, cb)
        return (img.unsqueeze(0).repeat(batch_size, 1, 1, 1).contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Checkerboard", SYCheckerboard)
