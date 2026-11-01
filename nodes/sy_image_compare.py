"""Image Compare SY: puts two pictures together as side by side, difference, blend, checker or wipe."""
try:
    from ._sy_common import category, register
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_d2_common as d2

MODES = ("side_by_side", "difference", "blend", "checker", "wipe")
RESIZES = ("nearest", "smooth")
SAME_LIMIT = 0.5 / 255.0  # less than half a colour step counts as no difference


def check_resize(resize_b):
    if resize_b not in RESIZES:
        raise ValueError("resize_b must be one of: %s, got %r" % (", ".join(RESIZES), resize_b))


def diff_text(mean_diff, max_diff, changed_percent):
    """Pure function. Plain words for how far two pictures differ (values are 0..1 colour distances)."""
    if max_diff <= SAME_LIMIT:
        return "the pictures are identical"
    return "average difference %.2f%% of full brightness, biggest %.1f%%, %.1f%% of the pixels differ" % (
        mean_diff * 100.0, max_diff * 100.0, changed_percent)


def compare_info(mode, size_a, size_b, batch_a, batch_b, resize_b, diff):
    """Pure function. One plain line: what was compared, any resizing, and how different the pictures are."""
    parts = ["Compared A %s with B %s using %s" % (d2.size_text(*size_a), d2.size_text(*size_b), mode.replace("_", " "))]
    if size_a != size_b:
        shaped = abs(size_a[0] / float(size_a[1]) - size_b[0] / float(size_b[1])) > 0.01
        parts.append("B was resized to the size of A (%s)%s" % (resize_b, ", its shape changed" if shaped else ""))
    if batch_a != batch_b:
        parts.append("A has %d picture(s) and B has %d: B was repeated or trimmed to match A" % (batch_a, batch_b))
    parts.append(diff)
    return "; ".join(parts) + "."


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


def match_b(a, b, resize_b="nearest"):
    """Torch. Repeat/trim B to the batch of A and resize it to the size of A. Returns the new B."""
    import torch
    import torch.nn.functional as F

    check_resize(resize_b)
    if b.shape[0] != a.shape[0]:
        b = b[[i % b.shape[0] for i in range(a.shape[0])]]
    if b.shape[1:3] != a.shape[1:3]:
        h, w = a.shape[1], a.shape[2]
        if resize_b == "smooth":
            x = F.interpolate(b.permute(0, 3, 1, 2), size=(h, w), mode="bilinear", align_corners=False, antialias=True)
            b = x.permute(0, 2, 3, 1).clamp(0.0, 1.0).contiguous()
        else:
            yi = torch.clamp(torch.arange(h) * b.shape[1] // h, max=b.shape[1] - 1)
            xi = torch.clamp(torch.arange(w) * b.shape[2] // w, max=b.shape[2] - 1)
            b = b[:, yi][:, :, xi]
    return b


def diff_stats(a, b):
    """Torch. (mean, max, percent of pixels that differ) between A and an already matched B, on the shared colour channels."""
    c = min(a.shape[3], b.shape[3], 3)
    d = (a[..., :c].float() - b[..., :c].float()).abs()
    per_pixel = d.amax(dim=-1)
    return float(d.mean()), float(d.max()), 100.0 * float((per_pixel > SAME_LIMIT).float().mean())


def compare_tensors(a, b, mode, amount, resize_b="nearest"):
    """Same maths as compare_images but on torch tensors [B,H,W,C]; torch is imported here, not at the top."""
    import torch

    if mode not in MODES:
        raise ValueError("unknown compare mode: %r" % (mode,))
    amount = max(0.0, min(1.0, float(amount)))
    b = match_b(a, b, resize_b)
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


def save_previews(image_a, image_b):
    """Saves the first picture of A and B as small temp files so the browser can show a slider. Returns the file list."""
    import os
    import numpy as np
    import folder_paths
    from PIL import Image
    import uuid
    folder = folder_paths.get_temp_directory()
    tag = uuid.uuid4().hex[:10]
    files = []
    for name, batch in (("a", image_a), ("b", image_b)):
        arr = (batch[0].clamp(0, 1) * 255).byte().cpu().numpy()
        fn = "sycompare_%s_%s.png" % (tag, name)
        Image.fromarray(arr[:, :, :3] if arr.shape[2] >= 3 else np.repeat(arr[:, :, :1], 3, axis=2)).save(
            os.path.join(folder, fn), compress_level=1)
        files.append({"filename": fn, "subfolder": "", "type": "temp"})
    return files


class SYImageCompare:
    OUTPUT_NODE = True
    DESCRIPTION = ("Compares two pictures: side by side, difference, blend, checker or wipe. B is resized to match A. "
                   "The info line says if the pictures are identical, or how much they differ, and warns if B had to be reshaped.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE", {"tooltip": "The first picture. Its size sets the result size."}),
                "image_b": ("IMAGE", {"tooltip": "The second picture. It is resized to fit the first if needed."}),
                "mode": (list(MODES), {"default": "side_by_side", "tooltip": "How to put the two pictures together."}),
                "amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Blend mix, or wipe position. 0 shows A, 1 shows B."}),
            },
            "optional": {
                "resize_b": (list(RESIZES), {"default": "nearest", "tooltip": "How B is resized when its size differs: nearest keeps hard pixels, smooth looks cleaner."}),
            },
        }

    def run(self, image_a, image_b, mode, amount, resize_b="nearest"):
        out = compare_tensors(image_a, image_b, mode, amount, resize_b)
        matched = match_b(image_a, image_b, resize_b)
        mean, biggest, changed = diff_stats(image_a, matched)
        info = compare_info(mode, (image_a.shape[2], image_a.shape[1]), (image_b.shape[2], image_b.shape[1]),
                            image_a.shape[0], image_b.shape[0], resize_b, diff_text(mean, biggest, changed))
        return {"ui": {"sy_compare": save_previews(image_a, image_b)}, "result": (out, info)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageCompare", SYImageCompare)
NODE_DISPLAY_NAME_MAPPINGS["SYImageCompare"] = "Image Compare SY"
