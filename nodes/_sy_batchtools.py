"""Shared helpers for the SY batch nodes. Pure Python checks plus tensor helpers (torch imported lazily)."""


def check_shape(shape):
    """Pure function. Accepts a tensor shape [count, height, width, channels] and returns it as ints."""
    try:
        dims = tuple(int(v) for v in shape)
    except TypeError:
        raise ValueError("images must be a picture batch, got %r" % (shape,))
    if len(dims) != 4:
        raise ValueError("images must be a batch shaped [count, height, width, channels], got %d dimensions" % len(dims))
    if min(dims) < 1:
        raise ValueError("the picture batch is empty or has a zero size: %s" % (dims,))
    return dims


def concat_plan(shapes, resize_to_first):
    """Pure function. Checks a list of batch shapes can join. Returns the target size and total count."""
    if not shapes:
        raise ValueError("nothing to join: connect at least one image input")
    shapes = [check_shape(s) for s in shapes]
    _, height, width, channels = shapes[0]
    for k, s in enumerate(shapes[1:], 2):
        if (s[1], s[2]) != (height, width) and not resize_to_first:
            raise ValueError("input %d is %dx%d but the first is %dx%d: turn on resize_to_first or resize it before"
                             % (k, s[2], s[1], width, height))
    return {"height": height, "width": width, "channels": channels, "total": sum(s[0] for s in shapes)}


def fit_tensor(t, height, width, channels):
    """Resize (smooth) and fix the channel count of a [B,H,W,C] tensor. torch is imported here."""
    import torch
    import torch.nn.functional as F

    if t.shape[1] != height or t.shape[2] != width:
        x = t.permute(0, 3, 1, 2)
        x = F.interpolate(x, size=(height, width), mode="bilinear", align_corners=False)
        t = x.permute(0, 2, 3, 1).clamp(0.0, 1.0)
    have = t.shape[3]
    if have == 1 and channels > 1:
        t = t.expand(-1, -1, -1, min(channels, 3))
        have = t.shape[3]
    if have > channels:
        t = t[..., :channels]
    elif have < channels:
        pad = torch.ones(t.shape[0], t.shape[1], t.shape[2], channels - have, dtype=t.dtype, device=t.device)
        t = torch.cat([t, pad], dim=3)
    return t.contiguous()


def concat_tensors(tensors, resize_to_first):
    """Join [B,H,W,C] tensors into one batch, sized like the first one."""
    import torch

    plan = concat_plan([tuple(t.shape) for t in tensors], resize_to_first)
    parts = [fit_tensor(t, plan["height"], plan["width"], plan["channels"]) for t in tensors]
    return torch.cat(parts, dim=0)
