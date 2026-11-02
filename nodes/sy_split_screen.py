"""Split Screen SY: puts two pictures or clips side by side, stacked, or cut along a diagonal."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LAYOUTS = ["side by side", "stacked", "diagonal split"]
FITS = ["crop to fill", "stretch"]
UNEVEN = ["stop at shorter", "repeat last"]


def clip_length(len_a, len_b, when_uneven="repeat last"):
    """Pure function. How many output frames. A batch of 1 repeats against a longer clip."""
    len_a, len_b = int(len_a), int(len_b)
    if len_a < 1 or len_b < 1:
        raise ValueError("both inputs need at least one picture (A has %d, B has %d)" % (len_a, len_b))
    if when_uneven not in UNEVEN:
        raise ValueError("when_uneven must be one of: %s (got %r)" % (", ".join(UNEVEN), when_uneven))
    if len_a == 1:
        return len_b
    if len_b == 1:
        return len_a
    return min(len_a, len_b) if when_uneven == "stop at shorter" else max(len_a, len_b)


def fill_crop_box(src_w, src_h, dst_w, dst_h):
    """Pure function. The centred part (x, y, w, h) of the source with the target's proportions."""
    src_w, src_h, dst_w, dst_h = int(src_w), int(src_h), int(dst_w), int(dst_h)
    if min(src_w, src_h, dst_w, dst_h) < 1:
        raise ValueError("picture sizes must be at least 1 pixel")
    if src_w * dst_h > dst_w * src_h:  # source is wider than the target: cut the sides
        w = max(1, (src_h * dst_w) // dst_h)
        return ((src_w - w) // 2, 0, w, src_h)
    h = max(1, (src_w * dst_h) // dst_w)
    return (0, (src_h - h) // 2, src_w, h)


def split_regions(layout, split, width, height, divider=0):
    """Pure function. Per row: (divider_start, b_start). The divider covers [divider_start, b_start),
    B covers b_start to the right edge, A covers everything left of divider_start."""
    width, height, divider = int(width), int(height), int(divider)
    if layout not in LAYOUTS:
        raise ValueError("layout must be one of: %s (got %r)" % (", ".join(LAYOUTS), layout))
    split = float(split)
    if split < 0.05 or split > 0.95:
        raise ValueError("split must be between 0.05 and 0.95 (got %s)" % split)
    if width < 2 or height < 2:
        raise ValueError("the picture is too small to split (%dx%d)" % (width, height))
    if divider < 0:
        raise ValueError("divider_width cannot be negative")
    limit = width if layout != "stacked" else height
    if divider >= limit:
        raise ValueError("divider_width %d is as big as the picture. Lower it" % divider)
    rows = []
    if layout == "stacked":
        start = int(round(split * height)) - divider // 2
        start = max(0, min(height - divider, start))
        for r in range(height):
            if r < start:
                rows.append((width, width))
            elif r < start + divider:
                rows.append((0, width))
            else:
                rows.append((0, 0))
        return rows
    for r in range(height):
        if layout == "side by side":
            centre = split * width
        else:  # diagonal: the cut runs from the top right towards the bottom left
            centre = split * width + (0.5 - r / (height - 1.0)) * width
        start = int(round(centre)) - divider // 2
        start = max(0, min(width - divider, start))
        rows.append((start, start + divider))
    return rows


def split_masks_plan(layout, split, width, height, divider=0):
    """Pure function. Per row: the first pixel (from the left) that shows picture B."""
    return [b for _d, b in split_regions(layout, split, width, height, divider)]


class SYSplitScreen:
    DESCRIPTION = ("Puts two pictures or clips together: side by side, stacked, or cut along a diagonal. "
                   "Both are resized to the size of A first. A single picture can be mixed with a clip.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE", {"tooltip": "Shows on the left, top, or left of the diagonal. Sets the output size."}),
                "images_b": ("IMAGE", {"tooltip": "Shows on the right, bottom, or right of the diagonal."}),
                "layout": (LAYOUTS, {"default": "side by side", "tooltip": "How the two pictures are cut: left and right, top and bottom, or slanted."}),
                "split": ("FLOAT", {"default": 0.5, "min": 0.05, "max": 0.95, "step": 0.01, "tooltip": "Where the divider sits. 0.5 is the middle."}),
                "divider_width": ("INT", {"default": 0, "min": 0, "max": 64, "tooltip": "Thickness of the divider line in pixels. 0 means no line."}),
                "divider_grey": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Brightness of the divider line. 0 is black, 1 is white."}),
                "fit": (FITS, {"default": "crop to fill", "tooltip": "Crop to fill keeps the proportions. Stretch squeezes B to the size of A."}),
                "when_uneven": (UNEVEN, {"default": "repeat last", "tooltip": "If the clips differ in length: stop at the shorter or repeat the last frame."}),
            }
        }

    def run(self, images_a, images_b, layout, split, divider_width, divider_grey, fit, when_uneven):
        import torch
        import torch.nn.functional as F

        if fit not in FITS:
            raise ValueError("fit must be one of: %s (got %r)" % (", ".join(FITS), fit))
        count = clip_length(images_a.shape[0], images_b.shape[0], when_uneven)
        height, width, chans = int(images_a.shape[1]), int(images_a.shape[2]), int(images_a.shape[3])
        regions = split_regions(layout, split, width, height, divider_width)
        cols = torch.arange(width).unsqueeze(0)
        div_start = torch.tensor([d for d, _b in regions]).unsqueeze(1)
        b_start = torch.tensor([b for _d, b in regions]).unsqueeze(1)
        is_b = (cols >= b_start).unsqueeze(-1)
        is_div = ((cols >= div_start) & (cols < b_start)).unsqueeze(-1)
        grey = torch.full((chans,), float(divider_grey), dtype=images_a.dtype)
        if chans == 4:
            grey[3] = 1.0
        out = torch.empty((count, height, width, chans), dtype=images_a.dtype)
        for i in range(count):
            a = images_a[min(i, images_a.shape[0] - 1)]
            b = images_b[min(i, images_b.shape[0] - 1)].to(images_a.dtype)
            if b.shape[2] != chans:
                if b.shape[2] > chans:
                    b = b[..., :chans]
                else:
                    pad = torch.ones(b.shape[0], b.shape[1], chans - b.shape[2], dtype=b.dtype)
                    b = torch.cat([b, pad], dim=2) if b.shape[2] > 1 else b.expand(-1, -1, chans)
            if b.shape[0] != height or b.shape[1] != width:
                if fit == "crop to fill":
                    x, y, w, h = fill_crop_box(b.shape[1], b.shape[0], width, height)
                    b = b[y:y + h, x:x + w]
                moved = b.permute(2, 0, 1).unsqueeze(0)
                moved = F.interpolate(moved, size=(height, width), mode="bilinear", align_corners=False)
                b = moved.squeeze(0).permute(1, 2, 0)
            frame = torch.where(is_b, b, a)
            if divider_width > 0:
                frame = torch.where(is_div, grey, frame)
            out[i] = frame
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SplitScreen", SYSplitScreen)
NODE_DISPLAY_NAME_MAPPINGS["SYSplitScreen"] = "Split Screen SY"
