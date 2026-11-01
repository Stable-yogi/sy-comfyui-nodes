"""Before After SY: one comparison picture from a before and an after picture (split, side by side, difference, checkerboard, blend).

The node makes a normal picture, so it works everywhere and can be saved. In the browser it also shows a draggable
before / after slider on the node (the first picture of each batch, both at the same size).
"""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import resize_tensor
    from .sy_image_compare import save_previews
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import resize_tensor
    from sy_image_compare import save_previews

MODES = ["split vertical", "split horizontal", "side by side", "top and bottom", "difference", "checkerboard", "blend"]
LINE_MODES = ("split vertical", "split horizontal", "side by side", "top and bottom")
LABEL_MODES = LINE_MODES
LINE_COLOURS = {"white": (1.0, 1.0, 1.0), "black": (0.0, 0.0, 0.0), "red": (1.0, 0.0, 0.0),
                "green": (0.0, 1.0, 0.0), "blue": (0.0, 0.0, 1.0), "yellow": (1.0, 1.0, 0.0)}
MATCH_SIZES = ["resize after to before", "resize both to the smaller", "refuse on mismatch"]
BATCH_MODES = ["first picture only", "all pictures"]

# Tiny 5 x 7 bitmap letters, only the ones the labels need. '#' is a lit pixel.
FONT = {
    "b": ("#....", "#....", "#.##.", "##..#", "#...#", "##..#", "#.##."),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    "t": (".#...", ".#...", "###..", ".#...", ".#...", ".#..#", "..##."),
}
GLYPH_W, GLYPH_H = 5, 7


# ---------------------------------------------------------------- pure maths

def check_settings(mode, position, line_width, line_colour, match_size, gain, batch_mode):
    """Pure function. Plain refusals for values the node does not accept."""
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
    if not (0.0 <= float(position) <= 1.0):
        raise ValueError("position must be from 0 to 1, got %s" % position)
    if not (0 <= int(line_width) <= 20):
        raise ValueError("line_width must be from 0 to 20, got %s" % line_width)
    if line_colour not in LINE_COLOURS:
        raise ValueError("line_colour must be one of: %s, got %r" % (", ".join(LINE_COLOURS), line_colour))
    if match_size not in MATCH_SIZES:
        raise ValueError("match_size must be one of: %s, got %r" % (", ".join(MATCH_SIZES), match_size))
    if not (1.0 <= float(gain) <= 20.0):
        raise ValueError("difference_gain must be from 1 to 20, got %s" % gain)
    if batch_mode not in BATCH_MODES:
        raise ValueError("batch_mode must be one of: %s, got %r" % (", ".join(BATCH_MODES), batch_mode))


def split_cut(position, length):
    """Pure function. Where the split falls on a side of `length` pixels: 0 (all after) to length (all before)."""
    return max(0, min(int(length), int(round(float(position) * int(length)))))


def line_bounds(cut, line_width, length):
    """Pure function. First and last+1 pixel of a line centred on `cut`, kept inside 0..length."""
    start = int(cut) - int(line_width) // 2
    end = start + int(line_width)
    return max(0, start), max(0, min(int(length), end))


def checker_block(height, width):
    """Pure function. Square size of the checkerboard: an eighth of the short side, at least 1 pixel."""
    return max(1, min(int(height), int(width)) // 8)


def pick_before(mode, x, y, width, height, position):
    """Pure function. True when pixel (x, y) shows the BEFORE picture (split and checkerboard modes)."""
    if mode == "split vertical":
        return x < split_cut(position, width)
    if mode == "split horizontal":
        return y < split_cut(position, height)
    if mode == "checkerboard":
        b = checker_block(height, width)
        return ((x // b) + (y // b)) % 2 == 0
    raise ValueError("mode %r has no before/after pixel choice" % (mode,))


def target_size(match_size, size_before, size_after):
    """Pure function. Sizes are (width, height). Returns (width, height) both pictures must have.

    'resize both to the smaller' takes the size of the picture with fewer pixels.
    """
    if match_size not in MATCH_SIZES:
        raise ValueError("match_size must be one of: %s, got %r" % (", ".join(MATCH_SIZES), match_size))
    if tuple(size_before) == tuple(size_after):
        return tuple(size_before)
    if match_size == "refuse on mismatch":
        raise ValueError("the pictures differ in size (before %dx%d, after %dx%d). Resize one, or change match_size." % (
            size_before[0], size_before[1], size_after[0], size_after[1]))
    if match_size == "resize after to before":
        return tuple(size_before)
    if size_after[0] * size_after[1] < size_before[0] * size_before[1]:
        return tuple(size_after)
    return tuple(size_before)


def pic_index(i, total):
    """Pure function. Which picture of a batch of `total` goes with picture i of another batch (goes round)."""
    if int(total) < 1:
        raise ValueError("a picture input is empty")
    return int(i) % int(total)


def render_text(text, scale=1, pad=1):
    """Pure function. A box of rows of True/False: lit text pixels, with `pad` glyph-pixels of border (False)."""
    scale, pad = max(1, int(scale)), max(0, int(pad))
    text = str(text)
    for ch in text:
        if ch not in FONT:
            raise ValueError("the label font has no letter %r" % ch)
    cols = max(1, len(text) * (GLYPH_W + 1) - 1)
    grid = [[False] * (cols + 2 * pad) for _ in range(GLYPH_H + 2 * pad)]
    for n, ch in enumerate(text):
        for gy, row in enumerate(FONT[ch]):
            for gx, c in enumerate(row):
                if c == "#":
                    grid[pad + gy][pad + n * (GLYPH_W + 1) + gx] = True
    out = []
    for row in grid:
        wide = [v for v in row for _ in range(scale)]
        out.extend([list(wide) for _ in range(scale)])
    return out


def label_scale(height, width):
    """Pure function. Pixel size of one letter dot: grows with the picture so labels stay readable."""
    return max(1, min(int(height), int(width)) // 160)


def label_plan(mode, height, width, position, line_width):
    """Pure function. Where labels may go: [(text, x0, y0, x1, y1, align)] regions in the OUTPUT picture (width/height = one input)."""
    lw = int(line_width)
    if mode == "split vertical":
        cut = split_cut(position, width)
        return [("before", 0, 0, cut, height, "left"), ("after", cut, 0, width, height, "right")]
    if mode == "split horizontal":
        cut = split_cut(position, height)
        return [("before", 0, 0, width, cut, "left"), ("after", 0, cut, width, height, "left")]
    if mode == "side by side":
        return [("before", 0, 0, width, height, "left"), ("after", width + lw, 0, 2 * width + lw, height, "left")]
    if mode == "top and bottom":
        return [("before", 0, 0, width, height, "left"), ("after", 0, height + lw, width, 2 * height + lw, "left")]
    return []


def place_label(region, box_w, box_h, margin, align):
    """Pure function. (x, y) for a label box inside region (x0, y0, x1, y1), or None when it does not fit."""
    x0, y0, x1, y1 = region
    if x1 - x0 < box_w + 2 * margin or y1 - y0 < box_h + 2 * margin:
        return None
    x = x0 + margin if align == "left" else x1 - margin - box_w
    return x, y0 + margin


def info_text(mode, size_before, size_after, final_size, resized, count_before, count_after, used, mean_percent,
              labels_state, position):
    """Pure function. One plain report."""
    parts = ["Before %dx%d, after %dx%d" % (size_before + size_after)]
    if resized:
        parts.append("the pictures were resized to %dx%d" % final_size)
    parts.append("mode: " + mode + (" at %d%%" % round(float(position) * 100) if mode in ("split vertical", "split horizontal", "blend") else ""))
    parts.append("%d comparison picture%s" % (used, "" if used == 1 else "s"))
    if count_before != count_after:
        parts.append("before has %d and after has %d pictures: the shorter list was repeated" % (count_before, count_after))
    parts.append("mean difference %.2f%% of full brightness" % mean_percent)
    if labels_state:
        parts.append(labels_state)
    return "; ".join(parts) + "."


# ---------------------------------------------------------------- torch part

def _rgb(img, who):
    """Torch. Keeps three colour channels (drops alpha, repeats a grey picture)."""
    if img.dim() != 4:
        raise ValueError("%s is not a picture batch (expected 4 dimensions, got %d)" % (who, img.dim()))
    if img.shape[0] < 1:
        raise ValueError("%s is empty" % who)
    c = img.shape[3]
    if c == 1:
        return img.repeat(1, 1, 1, 3).float()
    if c < 3:
        raise ValueError("%s has %d colour channels; it needs 1, 3 or 4" % (who, c))
    return img[..., :3].float()


def _colour(line_colour, like):
    import torch
    return torch.tensor(LINE_COLOURS[line_colour], dtype=like.dtype, device=like.device).view(1, 1, 1, 3)


def compose(before, after, mode, position, line_width, line_colour, gain):
    """Torch. before/after are matched [N,H,W,3]. Returns the comparison picture."""
    import torch
    n, h, w, _c = before.shape
    col = _colour(line_colour, before)
    lw = int(line_width)
    if mode == "split vertical":
        cut = split_cut(position, w)
        pick = (torch.arange(w, device=before.device) < cut).view(1, 1, w, 1)
        out = torch.where(pick, before, after)
        a, b = line_bounds(cut, lw, w)
        if b > a:
            out = out.clone()
            out[:, :, a:b, :] = col
        return out
    if mode == "split horizontal":
        cut = split_cut(position, h)
        pick = (torch.arange(h, device=before.device) < cut).view(1, h, 1, 1)
        out = torch.where(pick, before, after)
        a, b = line_bounds(cut, lw, h)
        if b > a:
            out = out.clone()
            out[:, a:b, :, :] = col
        return out
    if mode == "side by side":
        parts = [before]
        if lw > 0:
            parts.append(col.expand(n, h, lw, 3))
        parts.append(after)
        return torch.cat(parts, dim=2)
    if mode == "top and bottom":
        parts = [before]
        if lw > 0:
            parts.append(col.expand(n, lw, w, 3))
        parts.append(after)
        return torch.cat(parts, dim=1)
    if mode == "difference":
        return ((before - after).abs() * float(gain)).clamp(0.0, 1.0)
    if mode == "checkerboard":
        b = checker_block(h, w)
        ys = (torch.arange(h, device=before.device) // b).view(h, 1)
        xs = (torch.arange(w, device=before.device) // b).view(1, w)
        pick = (((ys + xs) % 2) == 0).view(1, h, w, 1)
        return torch.where(pick, before, after)
    if mode == "blend":
        p = float(position)
        return before * (1.0 - p) + after * p
    raise ValueError("unknown mode %r" % (mode,))


def stamp(out, text, x, y, scale):
    """Torch. Dims the box behind a label and draws it in white. Parts outside the picture are cut off."""
    import torch
    bitmap = render_text(text, scale)
    bh, bw = len(bitmap), len(bitmap[0])
    H, W = out.shape[1], out.shape[2]
    y1, x1 = min(H, y + bh), min(W, x + bw)
    if y1 <= y or x1 <= x:
        return out
    lit = torch.tensor(bitmap, dtype=torch.bool, device=out.device)[:y1 - y, :x1 - x].view(1, y1 - y, x1 - x, 1)
    region = out[:, y:y1, x:x1, :] * 0.3
    out[:, y:y1, x:x1, :] = torch.where(lit, torch.ones_like(region), region)
    return out


def add_labels(out, mode, h, w, position, line_width):
    """Torch. Draws 'before' and 'after'. Returns (picture, how_many_drawn)."""
    scale = label_scale(h, w)
    margin = 2 * scale + int(line_width)
    drawn = 0
    out = out.clone()
    for text, x0, y0, x1, y1, align in label_plan(mode, h, w, position, line_width):
        box_h, box_w = len(render_text(text, scale)), len(render_text(text, scale)[0])
        spot = place_label((x0, y0, x1, y1), box_w, box_h, margin, align)
        if spot is None:
            continue
        stamp(out, text, spot[0], spot[1], scale)
        drawn += 1
    return out, drawn


def before_after(before, after, mode, position, line_width, line_colour, labels, match_size, gain, batch_mode):
    """Torch. The whole job. Returns (comparison, info text)."""
    import torch
    check_settings(mode, position, line_width, line_colour, match_size, gain, batch_mode)
    b, a = _rgb(before, "before"), _rgb(after, "after")
    count_b, count_a = int(b.shape[0]), int(a.shape[0])
    if batch_mode == "first picture only":
        b, a = b[:1], a[:1]
    n = int(b.shape[0])
    if int(a.shape[0]) != n:
        a = a[[pic_index(i, a.shape[0]) for i in range(n)]]
    size_b, size_a = (int(b.shape[2]), int(b.shape[1])), (int(a.shape[2]), int(a.shape[1]))
    final = target_size(match_size, size_b, size_a)
    resized = size_b != size_a
    if resized:
        b = resize_tensor(b, final[1], final[0])
        a = resize_tensor(a, final[1], final[0])
    mean_percent = float((b - a).abs().mean()) * 100.0
    out = compose(b, a, mode, position, line_width, line_colour, gain)
    state = ""
    if labels:
        if mode in LABEL_MODES:
            out, drawn = add_labels(out, mode, final[1], final[0], position, line_width)
            state = "labels drawn" if drawn == 2 else ("labels: %d of 2 fit" % drawn)
        else:
            state = "labels are only drawn for the split, side by side and top and bottom modes"
    return out.clamp(0.0, 1.0).contiguous(), info_text(mode, size_b, size_a, final, resized, count_b, count_a, n, mean_percent, state, position)


def slider_pair(before, after, match_size):
    """Torch. The first before and after picture at one common size, for the browser slider. Returns None when they cannot be matched."""
    b, a = _rgb(before, "before")[:1], _rgb(after, "after")[:1]
    size_b, size_a = (int(b.shape[2]), int(b.shape[1])), (int(a.shape[2]), int(a.shape[1]))
    final = target_size(match_size, size_b, size_a)
    if size_b != size_a:
        b = resize_tensor(b, final[1], final[0])
        a = resize_tensor(a, final[1], final[0])
    return b, a


class SYBeforeAfter:
    OUTPUT_NODE = True
    DESCRIPTION = ("Makes one comparison picture from a before and an after picture: split (line you place), side by side, "
                   "top and bottom, difference, checkerboard or blend. Small before/after labels. The info line gives the mean difference. "
                   "On the node you also get a draggable before / after slider in the browser.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("comparison", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "before": ("IMAGE", {"tooltip": "The picture before the change."}),
                "after": ("IMAGE", {"tooltip": "The picture after the change."}),
            },
            "optional": {
                "mode": (MODES, {"default": "split vertical", "tooltip": "How the two pictures are put together."}),
                "position": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the split is (0 to 1). In blend: how much of after is mixed in."}),
                "line_width": ("INT", {"default": 2, "min": 0, "max": 20, "tooltip": "Width of the dividing line in pixels. 0 means no line."}),
                "line_colour": (list(LINE_COLOURS), {"default": "white", "tooltip": "Colour of the dividing line."}),
                "labels": ("BOOLEAN", {"default": True, "tooltip": "Draw small before / after text. Only in the split, side by side and top and bottom modes."}),
                "match_size": (MATCH_SIZES, {"default": "resize after to before", "tooltip": "What to do when the two pictures differ in size."}),
                "difference_gain": ("FLOAT", {"default": 4.0, "min": 1.0, "max": 20.0, "step": 0.5, "tooltip": "Makes small differences brighter in difference mode."}),
                "batch_mode": (BATCH_MODES, {"default": "all pictures", "tooltip": "Use only the first picture of each batch, or compare every picture."}),
            },
        }

    def run(self, before, after, mode="split vertical", position=0.5, line_width=2, line_colour="white", labels=True,
            match_size="resize after to before", difference_gain=4.0, batch_mode="all pictures"):
        out, info = before_after(before, after, mode, position, line_width, line_colour, labels, match_size, difference_gain, batch_mode)
        try:  # the slider is a bonus: a preview problem never stops the node
            b1, a1 = slider_pair(before, after, match_size)
            return {"ui": {"sy_compare": save_previews(b1, a1)}, "result": (out, info)}
        except Exception:
            return (out, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BeforeAfter", SYBeforeAfter)
NODE_DISPLAY_NAME_MAPPINGS["SYBeforeAfter"] = "Before After SY"
