"""Video Stabilise SY: cancels camera shake by following how the whole picture moves (shift only)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ANALYSIS_SIZE = 256   # longest side of the small grey frames used to measure movement


def smooth_path(values, window):
    """Pure function. Moving average over `window` frames, centred, shrinking at both ends."""
    window = int(window)
    if window < 1:
        raise ValueError("smoothing must be at least 1 frame, got %d" % window)
    n = len(values)
    half = window // 2
    out = []
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n - 1, i + half)
        k = min(i - lo, hi - i)          # same number of frames on both sides, so the ends do not drift
        seg = values[i - k:i + k + 1]
        out.append(sum(seg) / float(len(seg)))
    return out


def wrap_peak(index, size):
    """Pure function. Turns a position in the correlation grid into a signed shift."""
    index = int(index)
    size = int(size)
    return index - size if index > size // 2 else index


def shifts_from_peaks(peaks, sizes, scale=1.0):
    """Pure function. peaks: [(row, col)] per frame pair, sizes: (rows, cols). Returns [(dx, dy)] as floats."""
    rows, cols = sizes
    sx, sy = scale if isinstance(scale, tuple) else (scale, scale)
    return [(wrap_peak(c, cols) * sx, wrap_peak(r, rows) * sy) for r, c in peaks]


def cumulative(shifts):
    """Pure function. Path of the picture: frame 0 sits at (0, 0), then every shift is added."""
    path = [(0.0, 0.0)]
    for dx, dy in shifts:
        path.append((path[-1][0] + dx, path[-1][1] + dy))
    return path


def corrections(shifts, window, max_shift):
    """Pure function. shifts: [(dx, dy)] between neighbouring frames (N-1 of them).

    Returns N integer (dx, dy) moves to apply, each limited to +-max_shift.
    """
    max_shift = int(max_shift)
    if max_shift < 1:
        raise ValueError("max_shift must be at least 1 pixel, got %d" % max_shift)
    path = cumulative(shifts)
    sx = smooth_path([p[0] for p in path], window)
    sy = smooth_path([p[1] for p in path], window)
    out = []
    for i, (px, py) in enumerate(path):
        cx = int(round(sx[i] - px))
        cy = int(round(sy[i] - py))
        out.append((max(-max_shift, min(max_shift, cx)), max(-max_shift, min(max_shift, cy))))
    return out


def format_shifts(moves):
    """Pure function. One 'dx,dy' line per frame."""
    return "\n".join("%d,%d" % (dx, dy) for dx, dy in moves)


def crop_amounts(moves):
    """Pure function. How many pixels to cut from every side so no empty border is left."""
    return (max([abs(dx) for dx, _ in moves] + [0]), max([abs(dy) for _, dy in moves] + [0]))


def _measure(images):
    """Torch. Returns [(dx, dy)] full-size pixels between neighbouring frames."""
    import torch
    import torch.nn.functional as F
    n, h, w, _ = images.shape
    scale = max(1.0, max(h, w) / float(ANALYSIS_SIZE))
    sh, sw = max(8, int(round(h / scale))), max(8, int(round(w / scale)))
    gray = images[..., :3].float().mean(dim=-1, keepdim=True).permute(0, 3, 1, 2)
    small = F.interpolate(gray, size=(sh, sw), mode="area")[:, 0]
    small = small - small.mean(dim=(1, 2), keepdim=True)
    win = torch.hann_window(sh, periodic=False).view(sh, 1) * torch.hann_window(sw, periodic=False).view(1, sw)
    small = small * win
    spec = torch.fft.fft2(small)
    peaks = []
    for i in range(1, n):
        cross = spec[i] * torch.conj(spec[i - 1])
        cross = cross / (cross.abs() + 1e-8)
        corr = torch.fft.ifft2(cross).real
        flat = int(torch.argmax(corr).item())
        peaks.append((flat // sw, flat % sw))
    return shifts_from_peaks(peaks, (sh, sw), scale=(w / float(sw), h / float(sh)))


def _shift_frame(frame, dx, dy):
    """Torch. Moves a [H,W,C] frame by whole pixels and fills the gap with black."""
    import torch
    h, w = frame.shape[0], frame.shape[1]
    out = torch.zeros_like(frame)
    if abs(dx) >= w or abs(dy) >= h:
        return out
    sx0, sx1 = max(0, -dx), min(w, w - dx)
    sy0, sy1 = max(0, -dy), min(h, h - dy)
    out[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx] = frame[sy0:sy1, sx0:sx1]
    return out


def stabilise(images, smoothing, crop_edges, max_shift):
    """Torch function. images [N,H,W,C] -> (new images, 'dx,dy' lines)."""
    import torch
    import torch.nn.functional as F
    if int(smoothing) < 1:
        raise ValueError("smoothing must be at least 1 frame, got %s" % smoothing)
    n, h, w, c = images.shape
    if n < 2:
        return images.clone(), format_shifts([(0, 0)] * n)
    raw = _measure(images)
    shifts = [(dx, dy) for dx, dy in raw]
    moves = corrections(shifts, smoothing, max_shift)
    out = torch.stack([_shift_frame(images[i], moves[i][0], moves[i][1]) for i in range(n)])
    if crop_edges:
        cx, cy = crop_amounts(moves)
        if cx or cy:
            if 2 * cx >= w - 1 or 2 * cy >= h - 1:
                raise ValueError("the shake is bigger than the picture can hide: lower max_shift or turn crop_edges off")
            cropped = out[:, cy:h - cy, cx:w - cx, :].permute(0, 3, 1, 2)
            cropped = F.interpolate(cropped, size=(h, w), mode="bilinear", align_corners=False)
            out = cropped.permute(0, 2, 3, 1).contiguous().clamp(0.0, 1.0)
    return out, format_shifts(moves)


class SYVideoStabilise:
    DESCRIPTION = ("Cancels camera shake. It follows how the whole picture moves from frame to frame and moves each frame "
                   "back along a smoothed path. Shift only, no turning or zoom. Tells you the move used for every frame.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "shifts")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "smoothing": ("INT", {"default": 15, "min": 1, "max": 60, "tooltip": "How many frames the camera path is averaged over. Higher is steadier but may drift."}),
                "crop_edges": ("BOOLEAN", {"default": True, "tooltip": "On: crop away the empty borders and scale back up. Off: leave black borders."}),
                "max_shift": ("INT", {"default": 80, "min": 1, "max": 400, "tooltip": "Biggest move allowed for any frame, in pixels. Keeps one bad measurement from throwing a frame away."}),
            }
        }

    def run(self, images, smoothing, crop_edges, max_shift):
        out, text = stabilise(images, smoothing, crop_edges, max_shift)
        return (out, text)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoStabilise", SYVideoStabilise)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoStabilise"] = "Video Stabilise SY"
