"""Shared helpers for the batch D2 image nodes: size text, mask matching ("only inside this mask") and plain info lines.

Pure functions work on plain numbers and shapes. The t_* functions use torch, imported inside them.
"""


def size_text(width, height):
    return "%dx%d" % (int(width), int(height))


def shape_of_mask(shape):
    """Pure function. A mask shape (H,W) or (B,H,W) -> (batch, height, width). Plain error for anything else."""
    dims = tuple(int(v) for v in shape)
    if len(dims) == 2:
        dims = (1,) + dims
    if len(dims) != 3 or min(dims) < 1:
        raise ValueError("the mask must be a flat black and white picture (height x width, or batch x height x width), got shape %s" % (tuple(shape),))
    return dims


def mask_note(mask_shape, img_h, img_w):
    """Pure function. Empty text when the mask already has the picture size, else a short note that it was stretched."""
    _, mh, mw = shape_of_mask(mask_shape)
    if (mh, mw) == (int(img_h), int(img_w)):
        return ""
    return "mask %s was stretched to the picture size %s" % (size_text(mw, mh), size_text(img_w, img_h))


def coverage_percent(total, white):
    """Pure function. How much of the picture a mask covers, in percent."""
    return 0.0 if total <= 0 else 100.0 * float(white) / float(total)


def coverage_text(percent):
    """Pure function. Plain words for how much a mask covers."""
    if percent <= 0.0:
        return "empty (nothing selected)"
    if percent >= 99.99:
        return "full (everything selected)"
    return "%.1f%% selected" % percent


def join_info(parts):
    """Pure function. Join the non-empty pieces with a semicolon into one line."""
    return "; ".join(p for p in parts if p)


def cover_crop_plan(src_w, src_h, dst_w, dst_h):
    """Pure function. Scale a src_w x src_h picture to cover dst_w x dst_h, then cut the middle.
    Returns (scaled_w, scaled_h, crop_x, crop_y)."""
    if min(src_w, src_h, dst_w, dst_h) < 1:
        raise ValueError("picture sizes must be at least 1x1")
    s = max(dst_w / float(src_w), dst_h / float(src_h))
    sw, sh = max(dst_w, int(round(src_w * s))), max(dst_h, int(round(src_h * s)))
    return (sw, sh, (sw - dst_w) // 2, (sh - dst_h) // 2)


def t_mask_for_image(mask, batch, height, width):
    """torch. Mask (H,W) or (B,H,W) -> float tensor [batch, height, width, 1] in 0..1.
    A mask of another size is stretched smoothly; a mask batch is repeated or trimmed to the picture batch."""
    import torch.nn.functional as F

    shape_of_mask(tuple(mask.shape))
    m = mask.float()
    if m.dim() == 2:
        m = m.unsqueeze(0)
    if m.shape[0] != batch:
        m = m[[i % m.shape[0] for i in range(batch)]]
    if m.shape[1] != height or m.shape[2] != width:
        m = F.interpolate(m.unsqueeze(1), size=(height, width), mode="bilinear", align_corners=False).squeeze(1)
    return m.clamp(0.0, 1.0).unsqueeze(-1)


def t_blend_masked(original, edited, mask4):
    """torch. Show `edited` where the mask is white and `original` where it is black (soft in between)."""
    m = mask4.to(device=original.device, dtype=original.dtype)
    return (original + (edited - original) * m).contiguous()


def t_apply_with_mask(original, edited, mask):
    """torch. Returns (result, note). With no mask the edit is used everywhere. An empty mask returns the original."""
    if mask is None:
        return edited, ""
    b, h, w = original.shape[0], original.shape[1], original.shape[2]
    m4 = t_mask_for_image(mask, b, h, w)
    note = mask_note(tuple(mask.shape), h, w)
    if float(m4.max()) <= 0.0:
        return original, join_info(["the mask is empty, so nothing was changed", note])
    return t_blend_masked(original, edited, m4), join_info(["only inside the mask (%s)" % coverage_text(100.0 * float(m4.mean())), note])


def need_rgb(image, who):
    """A colour picture [B,H,W,C] with at least 3 channels, or a plain error naming the node."""
    if getattr(image, "ndim", 0) != 4:
        raise ValueError("%s needs a picture batch shaped [batch, height, width, channels]" % who)
    if image.shape[3] < 3:
        raise ValueError("%s needs a colour picture, but this one has only %d channel(s). Convert it to colour first" % (who, image.shape[3]))
    if min(image.shape) < 1:
        raise ValueError("%s got an empty picture batch" % who)
