"""Slide Transition SY: joins two clips with a push or wipe instead of a plain crossfade."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ["push left", "push right", "wipe left", "wipe right", "wipe down", "wipe up"]


def transition_progress(index, frames):
    """Pure function. Progress 0..1 (never exactly 0 or 1) of transition frame `index` out of `frames`, with a smooth ease."""
    index = int(index)
    frames = int(frames)
    if frames < 1:
        raise ValueError("frames must be at least 1, got %d" % frames)
    if index < 0 or index >= frames:
        raise ValueError("index must be from 0 to %d, got %d" % (frames - 1, index))
    t = (index + 1) / float(frames + 1)
    return t * t * (3.0 - 2.0 * t)


def wipe_alpha(size, progress, softness):
    """Pure function. How much of the new picture shows at each of `size` positions along the wipe direction
    (position 0 is where the wipe starts). 0 = old picture, 1 = new picture."""
    size = int(size)
    progress = float(progress)
    softness = float(softness)
    if size < 1:
        raise ValueError("size must be at least 1, got %d" % size)
    if progress < 0.0 or progress > 1.0:
        raise ValueError("progress must be between 0 and 1, got %s" % progress)
    if softness < 0.0 or softness > 0.5:
        raise ValueError("softness must be between 0 and 0.5, got %s" % softness)
    edge = progress * (1.0 + softness)
    out = []
    for i in range(size):
        pos = (i + 0.5) / size
        if softness == 0.0:
            a = 1.0 if pos < edge else 0.0
        else:
            a = min(1.0, max(0.0, (edge - pos) / softness))
        out.append(a)
    return out


def join_plan(len_a, len_b, frames):
    """Pure function. Returns (frames of A kept before the transition, frames of B kept after it, total length)."""
    len_a = int(len_a)
    len_b = int(len_b)
    frames = int(frames)
    if frames < 2 or frames > 120:
        raise ValueError("frames must be between 2 and 120, got %d" % frames)
    if len_a < frames:
        raise ValueError("clip A has only %d frames but the transition needs %d. Lower frames or use a longer clip A" % (len_a, frames))
    if len_b < frames:
        raise ValueError("clip B has only %d frames but the transition needs %d. Lower frames or use a longer clip B" % (len_b, frames))
    keep_a = len_a - frames
    keep_b = len_b - frames
    return keep_a, keep_b, keep_a + frames + keep_b


def _fit_channels(b, channels):
    import torch
    c = b.shape[-1]
    if c == channels:
        return b
    if c > channels:
        return b[..., :channels]
    pad = torch.ones(b.shape[:-1] + (channels - c,), dtype=b.dtype, device=b.device)
    return torch.cat([b, pad], dim=-1)


def _blend_frame(a, b, style, p, softness):
    """a, b: [1,H,W,C] tensors of the same size. Returns the transition frame for progress p."""
    import torch
    h, w = a.shape[1], a.shape[2]
    if style in ("push left", "push right"):
        off = int(round(p * w))
        off = min(max(off, 0), w)
        if off == 0:
            return a.clone()
        if off == w:
            return b.clone()
        if style == "push left":
            return torch.cat([a[:, :, off:], b[:, :, :off]], dim=2)
        return torch.cat([b[:, :, w - off:], a[:, :, :w - off]], dim=2)
    if style in ("wipe left", "wipe right"):
        al = wipe_alpha(w, p, softness)
        if style == "wipe left":
            al = al[::-1]
        m = torch.tensor(al, dtype=a.dtype, device=a.device).view(1, 1, w, 1)
    else:
        al = wipe_alpha(h, p, softness)
        if style == "wipe up":
            al = al[::-1]
        m = torch.tensor(al, dtype=a.dtype, device=a.device).view(1, h, 1, 1)
    return a * (1.0 - m) + b * m


class SYSlideTransition:
    DESCRIPTION = ("Joins two clips with a push or a wipe instead of a plain crossfade. "
                   "The result is clip A without its last frames, then the transition, then clip B without its first frames. "
                   "Clip B is resized to fit clip A. Both clips must be at least as long as the transition.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE", {"tooltip": "The first clip. Its last frames are used by the transition."}),
                "images_b": ("IMAGE", {"tooltip": "The second clip. Its first frames are used by the transition. It is resized to fit clip A."}),
                "frames": ("INT", {"default": 12, "min": 2, "max": 120, "tooltip": "How many frames the transition takes. Both clips need at least this many."}),
                "style": (STYLES, {"default": "push left", "tooltip": "Push slides both pictures. Wipe reveals the new picture over the old one."}),
                "softness": ("FLOAT", {"default": 0.05, "min": 0.0, "max": 0.5, "step": 0.01, "tooltip": "How soft the edge of a wipe is. 0 is a hard edge. Push ignores this."}),
            },
        }

    def run(self, images_a, images_b, frames, style="push left", softness=0.05):
        import torch
        import torch.nn.functional as F
        if style not in STYLES:
            raise ValueError("style must be one of: %s" % ", ".join(STYLES))
        keep_a, keep_b, _total = join_plan(images_a.shape[0], images_b.shape[0], frames)
        frames = int(frames)
        a_all = images_a
        b_all = _fit_channels(images_b, a_all.shape[-1]).to(a_all.dtype)
        h, w = a_all.shape[1], a_all.shape[2]
        if b_all.shape[1] != h or b_all.shape[2] != w:
            b_all = F.interpolate(b_all.permute(0, 3, 1, 2), size=(h, w), mode="bilinear", align_corners=False)
            b_all = b_all.permute(0, 2, 3, 1).clamp(0.0, 1.0)
        mid = []
        for i in range(frames):
            p = transition_progress(i, frames)
            mid.append(_blend_frame(a_all[keep_a + i:keep_a + i + 1], b_all[i:i + 1], style, p, softness))
        parts = [a_all[:keep_a], torch.cat(mid, dim=0), b_all[frames:]]
        return (torch.cat(parts, dim=0).contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SlideTransition", SYSlideTransition)
NODE_DISPLAY_NAME_MAPPINGS["SYSlideTransition"] = "Slide Transition SY"
