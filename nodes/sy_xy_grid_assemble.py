"""XY Grid Assemble SY: puts a batch of pictures into one labelled XY grid."""
try:
    from ._sy_common import category, register
    from ._sy_xy import axis_sizes, grid_layout, parse_axis, parse_color, text_color_for
    from ._sy_batchtools import check_shape, fit_tensor
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_xy import axis_sizes, grid_layout, parse_axis, parse_color, text_color_for
    from _sy_batchtools import check_shape, fit_tensor

MAX_LABEL_COLUMN = 600


def check_count(count, nx, ny):
    """Pure function. The batch must hold exactly nx*ny pictures, row by row."""
    if int(count) != nx * ny:
        raise ValueError("the batch has %d pictures but the grid is %d x %d = %d: make the lists match the picture count"
                         % (count, nx, ny, nx * ny))


def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=int(size))
    except TypeError:  # old Pillow: fixed small font
        return ImageFont.load_default()


def _fit(draw, font, text, max_width):
    if draw.textlength(text, font=font) <= max_width:
        return text
    while len(text) > 1 and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text + "..."


def render_grid(images, xs, ys, gap, padding, background, label_size):
    """images: [N,H,W,C] tensor. Returns one [1,H,W,3] tensor."""
    import numpy as np
    import torch
    from PIL import Image, ImageDraw

    n, cell_h, cell_w, _ = check_shape(images.shape)
    nx, ny = axis_sizes(xs, ys)
    check_count(n, nx, ny)
    bg = parse_color(background)
    ink = text_color_for(bg)
    font = _font(label_size)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    head_h = int(label_size) + 10 if xs else 0
    head_w = 0
    if ys:
        head_w = min(MAX_LABEL_COLUMN, int(max(probe.textlength(t, font=font) for t in ys)) + 12)
    lay = grid_layout(nx, ny, cell_w, cell_h, gap, padding, head_w, head_h)
    canvas = torch.empty(lay["height"], lay["width"], 3, dtype=torch.float32)
    canvas[:] = torch.tensor([v / 255.0 for v in bg], dtype=torch.float32)
    for i, (x, y) in enumerate(lay["cells"]):
        canvas[y:y + cell_h, x:x + cell_w] = fit_tensor(images[i:i + 1].float().cpu(), cell_h, cell_w, 3)[0]
    if xs or ys:
        arr = (canvas.clamp(0, 1) * 255.0 + 0.5).to(torch.uint8).numpy()
        img = Image.fromarray(arr, "RGB")
        draw = ImageDraw.Draw(img)
        for text, cx in zip(xs, lay["col_x"]):
            t = _fit(draw, font, text, cell_w - 4)
            draw.text((cx - draw.textlength(t, font=font) / 2.0, lay["head_y"] + 4), t, fill=ink, font=font)
        for text, cy in zip(ys, lay["row_y"]):
            t = _fit(draw, font, text, head_w - 6)
            draw.text((lay["head_x"] + 3, cy - label_size / 2.0), t, fill=ink, font=font)
        canvas = torch.from_numpy(np.array(img)).float() / 255.0
    return canvas[None]


class SYXYGridAssemble:
    DESCRIPTION = "Builds one grid picture from a batch, with the X values across the top and the Y values down the side."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("grid",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures, row by row: X changes fastest. The count must be X count times Y count."}),
                "x_labels": ("STRING", {"default": "", "multiline": True, "tooltip": "Labels across the top, one per line. Empty means one column and no header."}),
                "y_labels": ("STRING", {"default": "", "multiline": True, "tooltip": "Labels down the side, one per line. Empty means one row and no side labels."}),
                "gap": ("INT", {"default": 8, "min": 0, "max": 256, "tooltip": "Space in pixels between pictures."}),
                "padding": ("INT", {"default": 12, "min": 0, "max": 256, "tooltip": "Space in pixels around the whole grid."}),
                "background": ("STRING", {"default": "dark_gray", "tooltip": "Grid colour: black, white, gray, dark_gray, red, green, blue, gold or six hex digits."}),
                "label_size": ("INT", {"default": 24, "min": 8, "max": 96, "tooltip": "Label text height in pixels."}),
            }
        }

    def run(self, images, x_labels, y_labels, gap, padding, background, label_size):
        xs, ys = parse_axis(x_labels), parse_axis(y_labels)
        return (render_grid(images, xs, ys, gap, padding, background, label_size),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYGridAssemble", SYXYGridAssemble)
NODE_DISPLAY_NAME_MAPPINGS["SYXYGridAssemble"] = "XY Grid Assemble SY"
