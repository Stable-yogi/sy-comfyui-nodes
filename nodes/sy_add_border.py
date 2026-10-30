"""Add Border SY: adds a coloured frame around a picture, outside it or painted over its edge."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_hexcolour import parse_hex

MODES = ("outside", "inside")
DEFAULT_COLOUR = "#" + "000000"


def check_size(size):
    if size < 0:
        raise ValueError("size must not be negative, got %s" % size)


def check_mode(mode):
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))


def border_ring(x, y, w, h, size):
    """Pure function. True when pixel (x, y) of a w x h picture lies in the outer ring of `size` pixels."""
    check_size(size)
    if w < 1 or h < 1:
        raise ValueError("picture size must be at least 1x1")
    return x < size or y < size or x >= w - size or y >= h - size


class SYAddBorder:
    DESCRIPTION = "Adds a coloured border around a picture. Outside makes the picture bigger; inside paints over the edge. Also gives a mask of the border."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to put a border on."}),
                "size": ("INT", {"default": 16, "min": 0, "max": 1024, "step": 1, "tooltip": "Border thickness in pixels. 0 changes nothing."}),
                "colour": ("STRING", {"default": DEFAULT_COLOUR, "multiline": False, "tooltip": "Border colour, as 3 or 6 hex digits like a web colour."}),
                "mode": (list(MODES), {"default": "outside", "tooltip": "outside grows the picture; inside keeps the size and paints the edge."}),
            }
        }

    def run(self, image, size, colour, mode):
        import torch

        need_image(image)
        check_size(size)
        check_mode(mode)
        col = parse_hex(colour, "colour")
        b, h, w, c = image.shape
        if size == 0:
            return (image, torch.zeros((b, h, w), dtype=image.dtype, device=image.device))
        colv = torch.tensor(list(col) + ([1.0] if c == 4 else []), dtype=image.dtype, device=image.device)
        if mode == "outside":
            oh, ow = h + 2 * size, w + 2 * size
            out = colv.expand(b, oh, ow, c).clone()
            out[:, size:size + h, size:size + w, :] = image
            mask = torch.ones((b, oh, ow), dtype=image.dtype, device=image.device)
            mask[:, size:size + h, size:size + w] = 0.0
            return (out, mask)
        ys = torch.arange(h, device=image.device)[:, None]
        xs = torch.arange(w, device=image.device)[None, :]
        ring = (xs < size) | (ys < size) | (xs >= w - size) | (ys >= h - size)
        ring_b = ring[None, :, :, None]
        out = torch.where(ring_b, colv.view(1, 1, 1, c), image)
        if c == 4:
            out[..., 3] = torch.where(ring[None], torch.ones_like(image[..., 3]), image[..., 3])
        mask = ring[None].expand(b, h, w).to(image.dtype).contiguous()
        return (out.contiguous(), mask)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "AddBorder", SYAddBorder)
NODE_DISPLAY_NAME_MAPPINGS["SYAddBorder"] = "Add Border SY"
