"""Shared finishing step for the SY picture tone and filter nodes (batch D1).

Every tone node computes a new RGB picture. `finish_rgb` then does the same careful last steps for all of them:
pass-through when switched off, blend with the original (mix), limit to a mask, keep the alpha channel,
clamp to 0..1, and cope with a mask of another size or batch. No node class lives in this file.
Pure helpers work on plain numbers; torch is imported only inside functions.
"""

MIX_TIP = "How much of the effect to use. 1 = full effect, 0.5 = half, 0 = original picture."
MASK_TIP = "Optional. White = apply the effect, black = keep the original. A different size is stretched to fit."
ENABLED_TIP = "Turn off to pass the picture through untouched (handy to compare before and after)."


def check_mix(mix):
    if not 0.0 <= mix <= 1.0:
        raise ValueError("mix must be between 0 and 1, got %s" % mix)


def blend_value(orig, new, weight):
    """Pure function. One value: original at weight 0, new at weight 1. Result is kept inside 0..1."""
    r = orig + (new - orig) * weight
    return 0.0 if r < 0.0 else 1.0 if r > 1.0 else r


def check_mask_batch(mask_batch, image_batch):
    """Pure function. A mask batch must be 1 or the same count as the picture batch."""
    if mask_batch not in (1, image_batch):
        raise ValueError("the mask holds %d masks but the picture batch holds %d; use 1 mask or the same number"
                         % (mask_batch, image_batch))


def info_line(label, enabled, mix, masked, detail=""):
    """Pure function. One plain sentence telling what the node did."""
    if not enabled:
        return "%s: switched off, picture passed through unchanged" % label
    parts = []
    if detail:
        parts.append(detail)
    parts.append("mix %d%%" % int(round(mix * 100)))
    parts.append("inside the mask only" if masked else "whole picture")
    return "%s: %s" % (label, ", ".join(parts))


def weight_map(image, mask, mix):
    """Torch. Returns a weight tensor [B,H,W,1] (float32, on the picture's device) from mask and mix."""
    import torch
    check_mix(mix)
    b, h, w = image.shape[0], image.shape[1], image.shape[2]
    if mask is None:
        return torch.full((b, h, w, 1), float(mix), dtype=torch.float32, device=image.device)
    try:
        from . import _sy_mask_math as mm
    except ImportError:
        import _sy_mask_math as mm
    m = mm.t_mask3(mask)
    check_mask_batch(m.shape[0], b)
    if m.shape[1] != h or m.shape[2] != w:
        import torch.nn.functional as F
        m = F.interpolate(m.unsqueeze(1), size=(h, w), mode="bilinear", align_corners=False).squeeze(1)
    m = mm.t_match_batch(m, b).clamp(0.0, 1.0).to(image.device)
    return (m * float(mix)).unsqueeze(-1)


def finish_rgb(image, new_rgb, mask=None, mix=1.0, enabled=True):
    """Torch. image [B,H,W,C>=3]; new_rgb [B,H,W,3] is the full-strength result.
    Returns the blended picture. Channels after the third (alpha) are kept from the original."""
    if not enabled:
        return image
    check_mix(mix)
    if mask is None and mix >= 1.0:
        w = None
    else:
        w = weight_map(image, mask, mix)
    rgb = image[..., :3].to(new_rgb.dtype)
    new_rgb = new_rgb.clamp(0.0, 1.0)  # clamp the full effect first, so a half mix is exactly halfway
    res = new_rgb if w is None else rgb + (new_rgb - rgb) * w
    out = image.clone()
    out[..., :3] = res.clamp(0.0, 1.0).to(image.dtype)
    return out
