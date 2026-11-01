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
MISMATCH_MODES = ["error", "fill blanks or trim"]


def check_count(count, nx, ny):
    """Pure function. The batch must hold exactly nx*ny pictures, row by row."""
    if int(count) != nx * ny:
        raise ValueError("the batch has %d pictures but the grid is %d x %d = %d: make the lists match the picture count"
                         % (count, nx, ny, nx * ny))


def reconcile_count(count, nx, ny, mode="error"):
    """Pure function. Returns (pictures_to_use, blanks_to_add, note). With mode 'error' a wrong count is refused (old behaviour).
    With 'fill blanks or trim' a short batch gets empty cells at the end and a long batch loses its extra pictures."""
    count, want = int(count), int(nx) * int(ny)
    if mode not in MISMATCH_MODES:
        raise ValueError("mismatch must be one of: %s" % ", ".join(MISMATCH_MODES))
    if count == want:
        return count, 0, ""
    if mode == "error":
        check_count(count, nx, ny)
    if count < want:
        return count, want - count, "the batch was %d short of the grid, so %d empty cell%s were added at the end" % (want - count, want - count, "" if want - count == 1 else "s")
    return want, 0, "the batch had %d too many pictures, so the last %d were left out" % (count - want, count - want)


def grid_info_text(count, nx, ny, cell_w, cell_h, out_w, out_h, note=""):
    """Pure function. A plain line about the finished grid."""
    line = "Grid %d x %d (%d picture%s, cells %dx%d) -> one picture %dx%d." % (nx, ny, count, "" if count == 1 else "s", cell_w, cell_h, out_w, out_h)
    if note:
        line += " Note: " + note + "."
    if out_w * out_h > 64000000:
        line += " Warning: this is a very big picture (%.0f megapixels); lower the cell size or the count." % (out_w * out_h / 1e6)
    return line


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


def render_grid(images, xs, ys, gap, padding, background, label_size, mismatch="error", note_out=None):
    """images: [N,H,W,C] tensor. Returns one [1,H,W,3] tensor. mismatch: see reconcile_count; note_out is a list that gets the note."""
    import numpy as np
    import torch
    from PIL import Image, ImageDraw

    n, cell_h, cell_w, _ = check_shape(images.shape)
    nx, ny = axis_sizes(xs, ys)
    use, blanks, note = reconcile_count(n, nx, ny, mismatch)
    if note_out is not None:
        note_out.append(note)
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
        if i >= use:
            break  # empty cells keep the background colour
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
    DESCRIPTION = ("Builds one grid picture from a batch, with the X values across the top and the Y values down the side. "
                   "By default the batch must match the grid exactly; an option fills missing cells with blanks or trims extra pictures. "
                   "The info output states the grid size and the size of the finished picture.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("grid", "info")

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
            },
            "optional": {
                "mismatch": (MISMATCH_MODES, {"default": "error", "tooltip": "If the picture count is not X times Y: error stops, the other choice fills blanks or trims."}),
            },
        }

    def run(self, images, x_labels, y_labels, gap, padding, background, label_size, mismatch="error"):
        xs, ys = parse_axis(x_labels), parse_axis(y_labels)
        notes = []
        grid = render_grid(images, xs, ys, gap, padding, background, label_size, mismatch, notes)
        nx, ny = axis_sizes(xs, ys)
        _, cell_h, cell_w, _c = check_shape(images.shape)
        info = grid_info_text(int(images.shape[0]), nx, ny, cell_w, cell_h, int(grid.shape[2]), int(grid.shape[1]), notes[0] if notes else "")
        return (grid, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYGridAssemble", SYXYGridAssemble)
NODE_DISPLAY_NAME_MAPPINGS["SYXYGridAssemble"] = "XY Grid Assemble SY"
