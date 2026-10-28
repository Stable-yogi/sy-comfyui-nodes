"""Image Compare SY: puts two pictures together as side by side, difference, blend, checker or wipe."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("side_by_side", "difference", "blend", "checker", "wipe")


def resize_nearest(img, height, width):
    """Pure function. img is nested lists [H][W][C]. Returns a nearest-neighbour copy of the new size."""
    sh, sw = len(img), len(img[0])
    return [[list(img[min(sh - 1, y * sh // height)][min(sw - 1, x * sw // width)]) for x in range(width)]
            for y in range(height)]


def compare_images(a, b, mode, amount=0.5):
    """Pure function on nested lists [H][W][C] of floats. b is resized to a when sizes differ."""
    if mode not in MODES:
        raise ValueError("unknown compare mode: %r" % (mode,))
    amount = max(0.0, min(1.0, float(amount)))
    height, width = len(a), len(a[0])
    if len(b) != height or len(b[0]) != width:
        b = resize_nearest(b, height, width)
    if mode == "side_by_side":
        return [[list(p) for p in a[y]] + [list(p) for p in b[y]] for y in range(height)]
    block = max(1, min(height, width) // 8)
    cut = int(round(amount * width))
    out = []
    for y in range(height):
        row = []
        for x in range(width):
            pa, pb = a[y][x], b[y][x]
            if mode == "difference":
                row.append([abs(u - v) for u, v in zip(pa, pb)])
            elif mode == "blend":
                row.append([u * (1.0 - amount) + v * amount for u, v in zip(pa, pb)])
            elif mode == "checker":
                row.append(list(pa if ((x // block) + (y // block)) % 2 == 0 else pb))
            else:  # wipe
                row.append(list(pa if x < cut else pb))
        out.append(row)
    return out


def compare_tensors(a, b, mode, amount):
    """Same maths as compare_images but on torch tensors [B,H,W,C]; torch is imported here, not at the top."""
    import torch

    if mode not in MODES:
        raise ValueError("unknown compare mode: %r" % (mode,))
    amount = max(0.0, min(1.0, float(amount)))
    if b.shape[0] != a.shape[0]:
        b = b[[i % b.shape[0] for i in range(a.shape[0])]]
    if b.shape[1:3] != a.shape[1:3]:
        h, w = a.shape[1], a.shape[2]
        yi = torch.clamp(torch.arange(h) * b.shape[1] // h, max=b.shape[1] - 1)
        xi = torch.clamp(torch.arange(w) * b.shape[2] // w, max=b.shape[2] - 1)
        b = b[:, yi][:, :, xi]
    if b.shape[3] != a.shape[3]:
        c = min(a.shape[3], b.shape[3])
        a, b = a[..., :c], b[..., :c]
    h, w = a.shape[1], a.shape[2]
    if mode == "side_by_side":
        return torch.cat([a, b], dim=2)
    if mode == "difference":
        return torch.abs(a - b)
    if mode == "blend":
        return a * (1.0 - amount) + b * amount
    if mode == "checker":
        block = max(1, min(h, w) // 8)
        ys = (torch.arange(h) // block)[:, None]
        xs = (torch.arange(w) // block)[None, :]
        pick_a = (((ys + xs) % 2) == 0)[None, :, :, None]
    else:  # wipe
        cut = int(round(amount * w))
        pick_a = (torch.arange(w) < cut)[None, None, :, None]
    return torch.where(pick_a, a, b)


class SYImageCompare:
    DESCRIPTION = "Compares two pictures: side by side, difference, blend, checker or wipe. B is resized to match A."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE", {"tooltip": "The first picture. Its size sets the result size."}),
                "image_b": ("IMAGE", {"tooltip": "The second picture. It is resized to fit the first if needed."}),
                "mode": (list(MODES), {"default": "side_by_side", "tooltip": "How to put the two pictures together."}),
                "amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Blend mix, or wipe position. 0 shows A, 1 shows B."}),
            }
        }

    def run(self, image_a, image_b, mode, amount):
        return (compare_tensors(image_a, image_b, mode, amount),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageCompare", SYImageCompare)
NODE_DISPLAY_NAME_MAPPINGS["SYImageCompare"] = "Image Compare SY"
