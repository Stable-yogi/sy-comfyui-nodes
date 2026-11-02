"""Shared helpers for the batch AE picture nodes. Plain helpers are pure; torch is imported inside functions."""
import math


def check_shape(shape, need_colour=True):
    """Pure function. Accepts a 3-dim [H,W,C] or 4-dim [B,H,W,C] shape. Returns the 4-dim shape."""
    shape = tuple(int(s) for s in shape)
    if len(shape) not in (3, 4):
        raise ValueError("image must be a picture or a batch of pictures ([B,H,W,C]); got %d dimensions. "
                         "Connect an IMAGE output" % len(shape))
    if len(shape) == 3:
        shape = (1,) + shape
    if min(shape) < 1:
        raise ValueError("image has no pixels (shape %s). Connect a picture that is not empty" % (list(shape),))
    if need_colour and shape[3] < 3:
        raise ValueError("this node needs a colour picture with 3 or 4 channels; got %d. "
                         "Convert the picture to RGB first" % shape[3])
    return shape


def prep_image(image, need_colour=True):
    """Torch. Returns (float tensor [B,H,W,C], was_3dim). Raises ValueError on bad input."""
    import torch

    if not isinstance(image, torch.Tensor):
        raise ValueError("image must be an IMAGE tensor; connect an IMAGE output")
    check_shape(tuple(image.shape), need_colour)
    was3 = image.dim() == 3
    x = image.unsqueeze(0) if was3 else image
    return x.float(), was3


def finish_image(out, source, was3):
    """Torch. Clamp to 0..1, restore dtype and dimensions."""
    out = out.clamp(0.0, 1.0).to(source.dtype)
    return out[0] if was3 else out


def check_range(name, value, lo, hi):
    """Pure function. Raises ValueError with a plain message if value is outside lo..hi."""
    if value != value or value < lo or value > hi:
        raise ValueError("%s must be between %s and %s, got %s" % (name, lo, hi, value))
    return value


def smoothstep(edge0, edge1, x):
    """Pure function. 0 below edge0, 1 above edge1, smooth in between."""
    t = (float(x) - edge0) / (edge1 - edge0)
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def gaussian_weights(sigma):
    """Pure function. Normalised 1-D blur weights; radius is 3 sigma (at least 1)."""
    if sigma <= 0:
        raise ValueError("blur size must be above 0, got %s" % sigma)
    r = max(1, int(math.ceil(3.0 * sigma)))
    w = [math.exp(-(i * i) / (2.0 * sigma * sigma)) for i in range(-r, r + 1)]
    total = sum(w)
    return [v / total for v in w]


def blur_nchw(x, sigma):
    """Torch. Separable gaussian blur of [B,C,H,W] with edge-copy padding."""
    import torch
    import torch.nn.functional as F

    if sigma > 6.0:
        # A wide blur on a big picture is slow and needs a huge buffer: blur a smaller copy, then scale back up.
        h, w = x.shape[2], x.shape[3]
        f = int(math.ceil(sigma / 4.0))
        sh, sw = max(1, h // f), max(1, w // f)
        if sh < h or sw < w:
            small = F.interpolate(x, size=(sh, sw), mode="area")
            small = blur_nchw(small, max(0.5, sigma * sw / float(w)))
            return F.interpolate(small, size=(h, w), mode="bilinear", align_corners=False)
    wts = gaussian_weights(sigma)
    k = torch.tensor(wts, dtype=x.dtype, device=x.device)
    r = (len(wts) - 1) // 2
    c = x.shape[1]
    kh = k.view(1, 1, 1, -1).repeat(c, 1, 1, 1)
    kv = k.view(1, 1, -1, 1).repeat(c, 1, 1, 1)
    x = F.conv2d(F.pad(x, (r, r, 0, 0), mode="replicate"), kh, groups=c)
    return F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), kv, groups=c)


def luma_of(rgb):
    """Torch. Brightness of [...,3] colours, shape [...,1]."""
    return (rgb[..., 0:1] * 0.2126 + rgb[..., 1:2] * 0.7152 + rgb[..., 2:3] * 0.0722)


def rgb_to_hsv(rgb):
    """Torch. [...,3] in 0..1 -> (h in degrees 0..360, s, v), each [...,1]."""
    import torch

    r, g, b = rgb[..., 0:1], rgb[..., 1:2], rgb[..., 2:3]
    mx = rgb.amax(dim=-1, keepdim=True)
    mn = rgb.amin(dim=-1, keepdim=True)
    d = mx - mn
    safe = torch.where(d > 0, d, torch.ones_like(d))
    h = torch.where(mx == r, torch.remainder((g - b) / safe, 6.0),
                    torch.where(mx == g, (b - r) / safe + 2.0, (r - g) / safe + 4.0))
    h = torch.where(d > 0, h * 60.0, torch.zeros_like(h))
    s = torch.where(mx > 0, d / torch.where(mx > 0, mx, torch.ones_like(mx)), torch.zeros_like(mx))
    return h, s, mx


def hsv_to_rgb(h, s, v):
    """Torch. Inverse of rgb_to_hsv. Returns [...,3]."""
    import torch

    chans = []
    for n in (5.0, 3.0, 1.0):
        k = torch.remainder(n + h / 60.0, 6.0)
        f = torch.minimum(torch.minimum(k, 4.0 - k), torch.ones_like(k)).clamp(0.0, 1.0)
        chans.append(v - v * s * f)
    return torch.cat(chans, dim=-1)
