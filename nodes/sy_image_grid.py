"""Image Grid SY and Labelled AB Grid SY: contact sheets and comparison strips with optional captions."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape, fit_tensor
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape, fit_tensor

MAX_SIDE = 16384
COLOR_NAMES = {
    "black": (0, 0, 0), "white": (255, 255, 255), "gray": (128, 128, 128), "dark_gray": (40, 40, 40),
    "red": (200, 40, 40), "green": (40, 160, 70), "blue": (50, 90, 200), "gold": (212, 165, 55),
}
DIRECTIONS = ("row", "column")


def parse_color(text):
    """Pure function. A colour name from COLOR_NAMES or six hex digits (with or without a leading hash). Returns (r,g,b)."""
    s = str(text).strip().lower()
    if s in COLOR_NAMES:
        return COLOR_NAMES[s]
    h = s[1:] if s.startswith("#") else s
    if len(h) == 6 and all(ch in "0123456789abcdef" for ch in h):
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    raise ValueError("background %r is not a colour: use a name (%s) or six hex digits like 202020"
                     % (text, ", ".join(sorted(COLOR_NAMES))))


def text_color_for(bg):
    """Pure function. Black text on a light background, white text on a dark one."""
    lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    return (0, 0, 0) if lum > 128 else (255, 255, 255)


def split_labels(text, count):
    """Pure function. One label per line, padded with empty strings to `count`. Extra lines are ignored."""
    lines = [ln.strip() for ln in str(text or "").splitlines()]
    return lines[:count] + [""] * max(0, count - len(lines))


def grid_layout(count, columns, cell_w, cell_h, gap, label_h):
    """Pure function. Cell positions for a contact sheet.
    Returns {rows, columns, width, height, cells: [(x, y, label_y), ...]}. The outer margin equals the gap."""
    count, columns, cell_w, cell_h, gap, label_h = (int(v) for v in (count, columns, cell_w, cell_h, gap, label_h))
    if count < 1:
        raise ValueError("need at least 1 picture for a grid, got %d" % count)
    if columns < 1:
        raise ValueError("columns must be at least 1, got %d" % columns)
    if cell_w < 1 or cell_h < 1:
        raise ValueError("picture size must be at least 1x1")
    if gap < 0 or label_h < 0:
        raise ValueError("gap and label height cannot be negative")
    cols = min(columns, count)
    rows = -(-count // cols)
    width = gap * (cols + 1) + cell_w * cols
    height = gap * (rows + 1) + (cell_h + label_h) * rows
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("the sheet would be %dx%d pixels, more than %d: use fewer pictures, fewer columns or a smaller gap"
                         % (width, height, MAX_SIDE))
    cells = []
    for i in range(count):
        r, c = divmod(i, cols)
        x = gap + c * (cell_w + gap)
        y = gap + r * (cell_h + label_h + gap)
        cells.append((x, y, y + cell_h))
    return {"rows": rows, "columns": cols, "width": width, "height": height, "cells": cells}


def label_height(labels, label_size):
    """Pure function. Height of the caption strip: zero when there are no captions."""
    return int(label_size) + 8 if any(labels) else 0


def ab_columns(count, direction):
    """Pure function. A strip is one row (pictures side by side) or one column (stacked)."""
    if direction not in DIRECTIONS:
        raise ValueError("direction must be one of %s, got %r" % (", ".join(DIRECTIONS), direction))
    return int(count) if direction == "row" else 1


def _load_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=int(size))
    except TypeError:  # old Pillow: fixed small font
        return ImageFont.load_default()


def fit_text(draw, font, text, max_width):
    """Shorten text with three dots until it fits max_width pixels."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while len(text) > 1 and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def render_sheet(frames, columns, gap, background, labels, label_size):
    """frames: list of [H,W,C] tensors (the first one sets the cell size). Returns one [1,H,W,3] tensor."""
    import numpy as np
    import torch
    from PIL import Image, ImageDraw

    bg = parse_color(background)
    cell_h, cell_w = check_shape((1,) + tuple(frames[0].shape))[1:3]
    lh = label_height(labels, label_size)
    lay = grid_layout(len(frames), columns, cell_w, cell_h, gap, lh)
    canvas = torch.empty(lay["height"], lay["width"], 3, dtype=torch.float32)
    canvas[:] = torch.tensor([v / 255.0 for v in bg], dtype=torch.float32)
    for f, (x, y, _) in zip(frames, lay["cells"]):
        cell = fit_tensor(f[None].float().cpu(), cell_h, cell_w, 3)[0]
        canvas[y:y + cell_h, x:x + cell_w] = cell
    if lh:
        arr = (canvas.clamp(0, 1) * 255.0 + 0.5).to(torch.uint8).numpy()
        img = Image.fromarray(arr, "RGB")
        draw = ImageDraw.Draw(img)
        font = _load_font(label_size)
        ink = text_color_for(bg)
        for (x, _, ly), text in zip(lay["cells"], labels):
            if not text:
                continue
            text = fit_text(draw, font, text, cell_w - 4)
            tw = draw.textlength(text, font=font)
            draw.text((x + (cell_w - tw) / 2.0, ly + 3), text, fill=ink, font=font)
        canvas = torch.from_numpy(np.array(img)).float() / 255.0
    return canvas[None]


class SYImageGrid:
    DESCRIPTION = "Lays a batch of pictures out as one contact sheet. Optional captions, one per line, go under each picture."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("sheet",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The batch of pictures to put on the sheet. All are sized like the first one."}),
                "columns": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "How many pictures per row. Fewer pictures than columns gives a single row."}),
                "gap": ("INT", {"default": 8, "min": 0, "max": 256, "tooltip": "Space in pixels between pictures and around the edge."}),
                "background": ("STRING", {"default": "black", "tooltip": "Sheet colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits."}),
            },
            "optional": {
                "labels": ("STRING", {"default": "", "multiline": True, "tooltip": "One caption per line, in picture order. Leave empty for no captions."}),
                "label_size": ("INT", {"default": 20, "min": 8, "max": 96, "tooltip": "Caption text height in pixels."}),
            },
        }

    def run(self, images, columns, gap, background, labels="", label_size=20):
        n = check_shape(images.shape)[0]
        caps = split_labels(labels, n)
        frames = [images[i] for i in range(n)]
        return (render_sheet(frames, columns, gap, background, caps, label_size),)


class SYLabelledABGrid:
    DESCRIPTION = "Puts two to four pictures in a strip with a caption under each. Good for comparing checkpoints on the same prompt."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("strip",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": ("IMAGE", {"tooltip": "First picture. Its size sets the size of every cell."}),
                "image_b": ("IMAGE", {"tooltip": "Second picture. It is resized to match the first."}),
                "label_a": ("STRING", {"default": "A", "tooltip": "Caption under the first picture. Leave empty for none."}),
                "label_b": ("STRING", {"default": "B", "tooltip": "Caption under the second picture. Leave empty for none."}),
                "direction": (list(DIRECTIONS), {"default": "row", "tooltip": "row puts pictures side by side, column stacks them."}),
                "gap": ("INT", {"default": 8, "min": 0, "max": 256, "tooltip": "Space in pixels between pictures and around the edge."}),
                "background": ("STRING", {"default": "black", "tooltip": "Strip colour: a name like black or white, or six hex digits."}),
                "label_size": ("INT", {"default": 24, "min": 8, "max": 96, "tooltip": "Caption text height in pixels."}),
            },
            "optional": {
                "image_c": ("IMAGE", {"tooltip": "Optional third picture."}),
                "image_d": ("IMAGE", {"tooltip": "Optional fourth picture."}),
                "label_c": ("STRING", {"default": "C", "tooltip": "Caption under the third picture."}),
                "label_d": ("STRING", {"default": "D", "tooltip": "Caption under the fourth picture."}),
            },
        }

    def run(self, image_a, image_b, label_a, label_b, direction, gap, background, label_size,
            image_c=None, image_d=None, label_c="C", label_d="D"):
        import torch

        items = [(image_a, label_a), (image_b, label_b)]
        if image_c is not None:
            items.append((image_c, label_c))
        if image_d is not None:
            items.append((image_d, label_d))
        for im, _ in items:
            check_shape(im.shape)
        cols = ab_columns(len(items), direction)
        caps = [str(lb or "").strip() for _, lb in items]
        batch = max(im.shape[0] for im, _ in items)
        out = []
        for b in range(batch):
            frames = [im[b % im.shape[0]] for im, _ in items]
            out.append(render_sheet(frames, cols, gap, background, caps, label_size))
        return (torch.cat(out, dim=0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageGrid", SYImageGrid)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LabelledABGrid", SYLabelledABGrid)
NODE_DISPLAY_NAME_MAPPINGS["SYImageGrid"] = "Image Grid SY"
NODE_DISPLAY_NAME_MAPPINGS["SYLabelledABGrid"] = "Labelled AB Grid SY"
