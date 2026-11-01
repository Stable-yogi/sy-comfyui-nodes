"""Tone Curve SY: auto levels, black/white point, midtone and a drawn tone curve in one node, plus a before/after histogram picture."""
import bisect
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d1_finish as fin
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d1_finish as fin

LUMA = (0.2126, 0.7152, 0.0722)
AUTO_MODES = ("off", "per picture", "whole batch")
PRESET_NAMES = ("none", "soft contrast", "strong contrast", "lift shadows", "fade blacks", "invert")
PRESETS = {
    "soft contrast": ((0.0, 0.0), (0.25, 0.21), (0.75, 0.79), (1.0, 1.0)),
    "strong contrast": ((0.0, 0.0), (0.25, 0.14), (0.75, 0.86), (1.0, 1.0)),
    "lift shadows": ((0.0, 0.0), (0.25, 0.36), (0.6, 0.68), (1.0, 1.0)),
    "fade blacks": ((0.0, 0.10), (1.0, 1.0)),
    "invert": ((0.0, 1.0), (1.0, 0.0)),
}
MAX_POINTS = 64
MIN_GAP = 0.01          # white point must stay at least this far above the black point
FLAT_GAP = 2.0 / 255.0  # a picture whose found range is smaller than this is treated as flat


def _clamp(v):
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def parse_curve_points(text):
    """Pure function. Turns text like "0,0 0.25,0.2 0.75,0.85 1,1" into a list of (x, y) pairs.
    Pairs may be split by spaces, new lines or semicolons. x must grow from left to right.
    A missing start (0,0) or end (1,1) is added. Empty text gives an empty list (no curve)."""
    if text is None or not str(text).strip():
        return []
    tokens = str(text).replace(";", " ").split()
    if len(tokens) > MAX_POINTS:
        raise ValueError("a curve may have at most %d points, got %d" % (MAX_POINTS, len(tokens)))
    pts = []
    for tok in tokens:
        parts = tok.split(",")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError('curve point "%s" is not a pair like 0.25,0.2 (two numbers with a comma, pairs split by spaces)' % tok)
        try:
            x, y = float(parts[0]), float(parts[1])
        except ValueError:
            raise ValueError('curve point "%s" holds something that is not a number' % tok)
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError('curve point "%s" is outside 0..1 (both numbers must be between 0 and 1)' % tok)
        if pts and x <= pts[-1][0]:
            raise ValueError("curve points must go from left to right: x %s comes after x %s" % (x, pts[-1][0]))
        pts.append((x, y))
    if pts[0][0] > 0.0:
        pts.insert(0, (0.0, 0.0))
    if pts[-1][0] < 1.0:
        pts.append((1.0, 1.0))
    return pts


def curve_slopes(points):
    """Pure function. Slope at each point for a smooth curve that never overshoots (monotone cubic, Fritsch-Carlson)."""
    n = len(points)
    if n < 2:
        raise ValueError("a curve needs at least 2 points")
    h = [points[k + 1][0] - points[k][0] for k in range(n - 1)]
    d = [(points[k + 1][1] - points[k][1]) / h[k] for k in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, n - 1):
        m[k] = 0.0 if d[k - 1] * d[k] <= 0.0 else (d[k - 1] + d[k]) / 2.0
    for k in range(n - 1):
        if d[k] == 0.0:
            m[k] = m[k + 1] = 0.0
            continue
        a, b = m[k] / d[k], m[k + 1] / d[k]
        s = a * a + b * b
        if s > 9.0:
            t = 3.0 / math.sqrt(s)
            m[k], m[k + 1] = t * a * d[k], t * b * d[k]
    return m


def curve_value(points, slopes, x):
    """Pure function. Height of the smooth curve at x (0..1), kept inside 0..1."""
    x = _clamp(x)
    xs = [p[0] for p in points]
    k = min(max(bisect.bisect_right(xs, x) - 1, 0), len(points) - 2)
    x0, y0 = points[k]
    x1, y1 = points[k + 1]
    h = x1 - x0
    t = (x - x0) / h
    t2, t3 = t * t, t * t * t
    r = ((2 * t3 - 3 * t2 + 1) * y0 + (t3 - 2 * t2 + t) * h * slopes[k]
         + (-2 * t3 + 3 * t2) * y1 + (t3 - t2) * h * slopes[k + 1])
    return _clamp(r)


def curve_lut(points, size=256):
    """Pure function. Lookup table (list of `size` numbers 0..1) of a curve. Empty points give the straight line."""
    if not points:
        return [i / (size - 1) for i in range(size)]
    sl = curve_slopes(points)
    return [curve_value(points, sl, i / (size - 1)) for i in range(size)]


def auto_level_points(hist, clip_percent):
    """Pure function. From a histogram (list of counts, dark to bright) find the black and white point as fractions 0..1.
    The darkest and brightest `clip_percent` percent of the pixels are ignored. A flat or empty picture gives (0, 1)."""
    total = float(sum(hist))
    n = len(hist)
    if total <= 0 or n < 2:
        return (0.0, 1.0)
    limit = total * clip_percent / 100.0
    cum, lo = 0.0, 0
    for i in range(n):
        cum += hist[i]
        if cum > limit:
            lo = i
            break
    cum, hi = 0.0, n - 1
    for i in range(n - 1, -1, -1):
        cum += hist[i]
        if cum > limit:
            hi = i
            break
    lo_f, hi_f = lo / (n - 1.0), hi / (n - 1.0)
    if hi_f - lo_f < FLAT_GAP:
        return (0.0, 1.0)
    return (lo_f, hi_f)


def preset_points(name):
    """Pure function. Curve points of a preset name, or an empty list for 'none'."""
    if name not in PRESET_NAMES:
        raise ValueError("unknown curve preset %r (allowed: %s)" % (name, ", ".join(PRESET_NAMES)))
    return list(PRESETS.get(name, ()))


def choose_curve(curve_points, curve_preset):
    """Pure function. (points, label). Typed points win; the preset is used only when the text is empty."""
    pts = parse_curve_points(curve_points)
    if pts:
        return pts, "your own curve (%d points)" % len(pts)
    pre = preset_points(curve_preset)
    if pre:
        return pre, "preset " + curve_preset
    return [], ""


def levels_value(v, lo=0.0, hi=1.0, black=0.0, white=1.0, midtone=1.0):
    """Pure function. One value through auto levels, black/white point and midtone (above 1 brightens the middle)."""
    v = _clamp((v - lo) / (hi - lo))
    v = _clamp((v - black) / (white - black))
    return v ** (1.0 / midtone) if v > 0.0 else 0.0


def build_lut(lo=0.0, hi=1.0, black=0.0, white=1.0, midtone=1.0, points=None, size=256):
    """Pure function. The whole tone change of one channel as a lookup table of `size` numbers 0..1."""
    sl = curve_slopes(points) if points else None
    out = []
    for i in range(size):
        v = levels_value(i / (size - 1.0), lo, hi, black, white, midtone)
        out.append(curve_value(points, sl, v) if points else v)
    return out


def check_settings(auto_levels, clip_percent, black_point, white_point, midtone, curve_preset, histogram_size):
    """Pure function. Plain refusals before any work starts."""
    if auto_levels not in AUTO_MODES:
        raise ValueError("auto_levels must be one of: %s" % ", ".join(AUTO_MODES))
    if not 0.0 <= clip_percent <= 10.0:
        raise ValueError("clip_percent must be between 0 and 10, got %s" % clip_percent)
    if not 0.0 <= black_point <= 0.95:
        raise ValueError("black_point must be between 0 and 0.95, got %s" % black_point)
    if not 0.05 <= white_point <= 1.0:
        raise ValueError("white_point must be between 0.05 and 1, got %s" % white_point)
    if white_point - black_point < MIN_GAP:
        raise ValueError("white_point (%s) must be above black_point (%s)" % (white_point, black_point))
    if not 0.1 <= midtone <= 5.0:
        raise ValueError("midtone must be between 0.1 and 5, got %s" % midtone)
    if curve_preset not in PRESET_NAMES:
        raise ValueError("unknown curve preset %r (allowed: %s)" % (curve_preset, ", ".join(PRESET_NAMES)))
    if not 64 <= histogram_size <= 512:
        raise ValueError("histogram_size must be between 64 and 512, got %s" % histogram_size)


def is_neutral(auto_levels, black_point, white_point, midtone, points):
    """Pure function. True when no setting changes the picture."""
    return auto_levels == "off" and black_point == 0.0 and white_point == 1.0 and midtone == 1.0 and not points


def _span(vals):
    lo, hi = min(vals), max(vals)
    return "%.2f" % lo if "%.2f" % lo == "%.2f" % hi else "%.2f-%.2f" % (lo, hi)


def describe_levels(los, his, clip_percent, per_channel):
    """Pure function. What auto levels found. los/his: one (r, g, b) tuple per picture."""
    if per_channel:
        black = " ".join("%s %s" % (n, _span([t[k] for t in los])) for k, n in enumerate("RGB"))
        white = " ".join("%s %s" % (n, _span([t[k] for t in his])) for k, n in enumerate("RGB"))
    else:
        black, white = _span([t[0] for t in los]), _span([t[0] for t in his])
    return "black %s, white %s, clipped %s%%" % (black, white, ("%g" % clip_percent))


def tone_info(enabled, levels_text, curve_label, manual, mix, masked, changed):
    """Pure function. One plain sentence."""
    if not enabled:
        return "Tone Curve: switched off, picture passed through unchanged"
    if not changed:
        return "Tone Curve: every setting is neutral, the picture was not changed"
    parts = []
    if levels_text:
        parts.append("auto levels found " + levels_text)
    if manual:
        parts.append(manual)
    parts.append("curve: " + curve_label if curve_label else "no curve")
    return fin.info_line("Tone Curve", True, mix, masked, "; ".join(parts))


# ---- torch part -------------------------------------------------------------

def _hists(v, per_channel):
    """Torch. 256-bin counts, shape [B, K, 256]; K is 3 (red, green, blue) or 1 (brightness)."""
    import torch
    b = v.shape[0]
    if per_channel:
        q = v.permute(0, 3, 1, 2).reshape(b, 3, -1)
    else:
        w = torch.tensor(LUMA, dtype=v.dtype, device=v.device)
        q = (v * w).sum(dim=-1).reshape(b, 1, -1)
    q = (q.clamp(0.0, 1.0) * 255.0 + 0.5).long()
    k = q.shape[1]
    off = (torch.arange(b * k, device=v.device) * 256).view(b, k, 1)
    return torch.bincount((q + off).reshape(-1), minlength=b * k * 256).view(b, k, 256)


def _find_levels(v, mode, clip_percent, per_channel):
    """Torch. Returns two lists with one (r, g, b) tuple per picture: the found black and white points."""
    h = _hists(v, per_channel)
    if mode == "whole batch":
        h = h.sum(dim=0, keepdim=True)
    h = h.cpu().tolist()
    los, his = [], []
    for per_pic in h:
        pts = [auto_level_points(ch, clip_percent) for ch in per_pic]
        if len(pts) == 1:
            pts = pts * 3
        los.append(tuple(p[0] for p in pts))
        his.append(tuple(p[1] for p in pts))
    if mode == "whole batch":
        los, his = los * v.shape[0], his * v.shape[0]
    return los, his


def _apply_luts(v, luts):
    """Torch. Applies a [B,3,256] lookup table to a [B,H,W,3] picture, blending between neighbouring entries."""
    b, hh, ww = v.shape[0], v.shape[1], v.shape[2]
    x = v.clamp(0.0, 1.0).permute(0, 3, 1, 2).reshape(b, 3, -1) * 255.0
    i0 = x.floor().long().clamp(0, 254)
    f = x - i0.to(x.dtype)
    g0 = luts.gather(2, i0)
    g1 = luts.gather(2, i0 + 1)
    out = g0 + (g1 - g0) * f
    return out.reshape(b, 3, hh, ww).permute(0, 2, 3, 1).contiguous()


def _resample(h, width):
    import torch.nn.functional as F
    t = h.float().view(1, -1, 256)
    mode = "area" if width < 256 else "linear"
    kw = {} if mode == "area" else {"align_corners": False}
    return F.interpolate(t, size=width, mode=mode, **kw)[0]


def _histogram_image(before, after, size):
    """Torch. One picture [1, size/2, size, 3]: the 'before' brightness as grey bars, the 'after' red, green and blue as lines."""
    import torch
    width, height = int(size), max(32, int(size) // 2)
    dev = before.device
    hb = _hists(before, False).sum(dim=0)             # [1,256]
    ha = _hists(after, True).sum(dim=0)               # [3,256]
    rows = _resample(torch.cat([hb, ha], dim=0).float(), width)   # [4,width]
    inner = rows[:, max(1, width // 256):-max(1, width // 256)] if width > 4 else rows
    peak = float(inner.max()) if inner.numel() else 0.0
    if peak <= 0.0:
        peak = 1.0
    hts = ((rows / peak).clamp(0.0, 1.0) * (height - 1)).round().long()   # [4,width] bar heights
    r = torch.arange(height, device=dev).view(height, 1)
    canvas = torch.full((height, width, 3), 0.08, dtype=torch.float32, device=dev)
    grey = torch.tensor([0.45, 0.45, 0.45], dtype=torch.float32, device=dev)
    canvas = torch.where((r <= hts[0].view(1, width)).unsqueeze(-1), grey, canvas)
    for c in range(3):
        cur = hts[1 + c].view(1, width)
        prev = torch.cat([cur[:, :1], cur[:, :-1]], dim=1)
        on = (r >= torch.minimum(cur, prev)) & (r <= torch.maximum(cur, prev))
        col = torch.full((3,), 0.25, dtype=torch.float32, device=dev)
        col[c] = 1.0
        canvas = torch.where(on.unsqueeze(-1), torch.maximum(canvas, col), canvas)
    return canvas.flip(0).unsqueeze(0).contiguous()


class SYToneCurve:
    DESCRIPTION = ("Levels, curves, auto contrast and a histogram in one node. Auto levels stretch a flat picture (per picture or for the "
                   "whole batch, optionally per colour channel to remove a colour cast), black point, white point and midtone fine-tune it, "
                   "and a tone curve (type points or pick a preset) shapes the contrast. Every setting starts neutral. "
                   "Outputs the picture, a histogram picture (before in grey, after in colour) and an info line.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("image", "histogram", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to adjust."}),
            },
            "optional": {
                "auto_levels": (list(AUTO_MODES), {"default": "off", "tooltip": "Stretch dark and bright ends to fill the range. Per picture or one setting for the batch."}),
                "clip_percent": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 10.0, "step": 0.1, "tooltip": "Percent of the darkest and brightest pixels ignored when auto levelling."}),
                "black_point": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 0.95, "step": 0.01, "tooltip": "This brightness becomes pure black. 0 is unchanged."}),
                "white_point": ("FLOAT", {"default": 1.0, "min": 0.05, "max": 1.0, "step": 0.01, "tooltip": "This brightness becomes pure white. 1 is unchanged."}),
                "midtone": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.01, "tooltip": "Middle tones. Above 1 brightens them, below 1 darkens them. 1 is unchanged."}),
                "curve_points": ("STRING", {"default": "", "multiline": True, "tooltip": "Tone curve as x,y pairs from 0 to 1, e.g. 0,0 0.25,0.2 0.75,0.85 1,1. Empty = no curve."}),
                "curve_preset": (list(PRESET_NAMES), {"default": "none", "tooltip": "Ready-made curve. Used only when the curve points box is empty."}),
                "per_channel": ("BOOLEAN", {"default": False, "tooltip": "Auto levels on red, green and blue separately. Also removes a colour cast."}),
                "mix": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": fin.MIX_TIP}),
                "mask": ("MASK", {"tooltip": fin.MASK_TIP}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": fin.ENABLED_TIP}),
                "histogram_size": ("INT", {"default": 256, "min": 64, "max": 512, "step": 1, "tooltip": "Width of the histogram picture in pixels (height is half)."}),
            },
        }

    def run(self, image, auto_levels="off", clip_percent=0.5, black_point=0.0, white_point=1.0, midtone=1.0, curve_points="",
            curve_preset="none", per_channel=False, mix=1.0, mask=None, enabled=True, histogram_size=256):
        import torch
        need_image(image)
        if image.shape[3] < 3:
            raise ValueError("this node needs a colour picture with 3 channels, got %d" % image.shape[3])
        check_settings(auto_levels, clip_percent, black_point, white_point, midtone, curve_preset, histogram_size)
        fin.check_mix(mix)
        points, curve_label = choose_curve(curve_points, curve_preset)
        masked = mask is not None
        neutral = is_neutral(auto_levels, black_point, white_point, midtone, points)
        rgb = image[..., :3].to(torch.float32)
        if not enabled or neutral:
            return (image, _histogram_image(rgb, rgb, histogram_size),
                    tone_info(enabled, "", "", "", mix, masked, False))
        b = rgb.shape[0]
        if auto_levels != "off":
            los, his = _find_levels(rgb, auto_levels, clip_percent, per_channel)
            levels_text = describe_levels(los, his, clip_percent, per_channel)
        else:
            los, his, levels_text = [(0.0,) * 3] * b, [(1.0,) * 3] * b, ""
        cache = {}
        luts = []
        for lo3, hi3 in zip(los, his):
            key = (lo3, hi3)
            if key not in cache:
                cache[key] = [build_lut(lo3[k], hi3[k], black_point, white_point, midtone, points) for k in range(3)]
            luts.append(cache[key])
        lut_t = torch.tensor(luts, dtype=torch.float32, device=rgb.device)
        new_rgb = _apply_luts(rgb, lut_t)
        out = fin.finish_rgb(image, new_rgb, mask, mix, True)
        manual = []
        if black_point != 0.0 or white_point != 1.0:
            manual.append("black point %g, white point %g" % (black_point, white_point))
        if midtone != 1.0:
            manual.append("midtone %g" % midtone)
        info = tone_info(True, levels_text, curve_label, ", ".join(manual), mix, masked, True)
        return (out, _histogram_image(rgb, out[..., :3].to(torch.float32), histogram_size), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ToneCurve", SYToneCurve)
NODE_DISPLAY_NAME_MAPPINGS["SYToneCurve"] = "Tone Curve SY"
