"""Overlap Blend SY: joins two clips with a smooth cross-fade over the frames they share."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CURVES = ("linear", "smooth", "ease in", "ease out")


def blend_weights(overlap, curve="smooth"):
    """Pure function. Weights of clip B for each shared frame, strictly between 0 and 1."""
    overlap = int(overlap)
    if overlap < 1:
        raise ValueError("overlap_frames must be at least 1, got %d" % overlap)
    if curve not in CURVES:
        raise ValueError("curve must be one of: %s" % ", ".join(CURVES))
    out = []
    for i in range(overlap):
        t = (i + 1) / (overlap + 1)
        if curve == "linear":
            w = t
        elif curve == "smooth":
            w = t * t * (3 - 2 * t)
        elif curve == "ease in":
            w = t * t
        else:
            w = 1 - (1 - t) * (1 - t)
        out.append(w)
    return out


def check_join(shape_a, shape_b, overlap):
    """Pure function. Shapes are (frames, height, width, channels). Returns the joined frame count."""
    overlap = int(overlap)
    if tuple(shape_a[1:]) != tuple(shape_b[1:]):
        raise ValueError("the two clips have different sizes: clip_a is %dx%d with %d channels, clip_b is %dx%d with %d channels. "
                         "Resize one of them so both match" % (shape_a[2], shape_a[1], shape_a[3], shape_b[2], shape_b[1], shape_b[3]))
    if overlap > shape_a[0] or overlap > shape_b[0]:
        raise ValueError("overlap_frames is %d but clip_a has %d frames and clip_b has %d. "
                         "Lower overlap_frames to %d or less" % (overlap, shape_a[0], shape_b[0], min(shape_a[0], shape_b[0])))
    return shape_a[0] + shape_b[0] - overlap


class SYOverlapBlend:
    DESCRIPTION = ("Joins two clips with a smooth cross-fade over the frames they share, so the seam does not jump. "
                   "The last frames of clip A fade into the first frames of clip B.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("joined", "frames_out")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_a": ("IMAGE", {"tooltip": "The first clip. Its last frames fade out."}),
                "clip_b": ("IMAGE", {"tooltip": "The second clip. Its first frames fade in. Must be the same size as clip_a."}),
                "overlap_frames": ("INT", {"default": 5, "min": 1, "max": 1000, "tooltip": "How many frames the two clips share and cross-fade over."}),
                "curve": (list(CURVES), {"default": "smooth", "tooltip": "How fast clip B takes over during the shared frames."}),
            },
        }

    def run(self, clip_a, clip_b, overlap_frames, curve):
        import torch
        check_join(tuple(clip_a.shape), tuple(clip_b.shape), overlap_frames)
        n = int(overlap_frames)
        na = int(clip_a.shape[0])
        b = clip_b.to(device=clip_a.device, dtype=clip_a.dtype)
        w = torch.tensor(blend_weights(n, curve), dtype=clip_a.dtype, device=clip_a.device).view(n, 1, 1, 1)
        mixed = (1 - w) * clip_a[na - n:] + w * b[:n]
        joined = torch.cat([clip_a[:na - n], mixed, b[n:]], dim=0)
        return (joined, int(joined.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "OverlapBlend", SYOverlapBlend)
NODE_DISPLAY_NAME_MAPPINGS["SYOverlapBlend"] = "Overlap Blend SY"
