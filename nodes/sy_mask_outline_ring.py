"""Mask Outline Ring SY: makes a band around the edge of a mask (an outline)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

POSITIONS = ["outside", "inside", "centred"]


def check_args(width, position, soft, threshold):
    if not 1 <= width <= 200:
        raise ValueError("width must be between 1 and 200 pixels, got %s" % width)
    if position not in POSITIONS:
        raise ValueError("position must be one of %s, got %r" % (", ".join(POSITIONS), position))
    if not 0.0 <= soft <= 1.0:
        raise ValueError("soft must be between 0 and 1, got %s" % soft)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1, got %s" % threshold)


def ring_widths(width, position):
    """Pure function. Returns (outer_grow, inner_shrink): how many pixels the mask grows outward and shrinks inward.
    The two always add up to width. The odd pixel of a centred ring goes outside."""
    if width < 1:
        raise ValueError("width must be at least 1 pixel, got %s" % width)
    if position == "outside":
        return (width, 0)
    if position == "inside":
        return (0, width)
    if position == "centred":
        return (width - width // 2, width // 2)
    raise ValueError("position must be one of %s, got %r" % (", ".join(POSITIONS), position))


def round_split(radius):
    """Pure function. A round grow of `radius` pixels is built from one square step of s pixels and d diamond steps
    (s + d = radius, about 0.41 / 0.59 of it). Returns (s, d)."""
    if radius < 0:
        raise ValueError("radius must be 0 or more, got %s" % radius)
    s = int(round(radius * 0.4142))
    return (s, radius - s)


def blur_plan(width, soft):
    """Pure function. Returns (sigma, shrink): the blur size in pixels and the whole-number shrink factor used
    to blur a small copy when the band is wide (width above 6). (0, 1) means no blur."""
    if soft <= 0.0:
        return (0.0, 1)
    sigma = soft * width / 2.0
    shrink = 1
    if width > 6:
        shrink = max(1, int(sigma // 3))
    return (sigma, shrink)


class SYMaskOutlineRing:
    DESCRIPTION = ("Makes an outline: a band of the chosen width around the edge of a mask, outside it, inside it, or centred on the edge. "
                   "The band is round. Soft feathers its edges. Edges of the picture itself never get a band.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to draw an outline around."}),
                "width": ("INT", {"default": 6, "min": 1, "max": 200, "step": 1, "tooltip": "Thickness of the outline in pixels."}),
                "position": (POSITIONS, {"default": "centred", "tooltip": "Where the band sits: outside the mask, inside it, or half and half on the edge."}),
                "soft": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much the band edges are feathered. 0 gives hard edges."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Mask values above this count as white, the rest as black."}),
            }
        }

    @staticmethod
    def _grow(x, radius):
        """Round grow of a bool [H,W] tensor by `radius` pixels: diamond steps by shifting, then one square step."""
        import torch
        import torch.nn.functional as F

        s, d = round_split(radius)
        for _ in range(d):
            y = x.clone()
            y[1:] |= x[:-1]
            y[:-1] |= x[1:]
            y[:, 1:] |= x[:, :-1]
            y[:, :-1] |= x[:, 1:]
            x = y
        if s:
            f = x.to(torch.float32)[None, None]
            f = F.max_pool2d(F.max_pool2d(f, (1, 2 * s + 1), 1, (0, s)), (2 * s + 1, 1), 1, (s, 0))
            x = f[0, 0] > 0.5
        return x

    @staticmethod
    def _blur(x, sigma, shrink):
        import torch
        import torch.nn.functional as F

        h, w = x.shape[-2:]
        if shrink > 1:
            x = F.avg_pool2d(x, shrink, shrink, ceil_mode=True)
            sigma = sigma / shrink
        r = max(1, int(sigma * 3))
        t = torch.arange(-r, r + 1, dtype=torch.float32, device=x.device)
        k = torch.exp(-(t * t) / (2 * sigma * sigma))
        k = (k / k.sum())
        kern = k.view(1, 1, -1)
        a = x[0, 0].unsqueeze(1)                                   # rows as a batch: [H,1,W]
        a = F.conv1d(F.pad(a, (r, r), mode="replicate"), kern)
        a = a.squeeze(1).t().unsqueeze(1)                          # columns as a batch: [W,1,H]
        a = F.conv1d(F.pad(a, (r, r), mode="replicate"), kern)
        x = a.squeeze(1).t()[None, None]
        if shrink > 1:
            x = F.interpolate(x, size=(h, w), mode="bilinear", align_corners=False)
        return x

    def run(self, mask, width, position, soft, threshold):
        import torch

        check_args(width, position, soft, threshold)
        grow, shrink_px = ring_widths(width, position)
        sigma, small = blur_plan(width, soft)
        m = mask if mask.dim() == 3 else mask.unsqueeze(0)
        out = torch.empty(m.shape, dtype=torch.float32, device=m.device)
        for i in range(m.shape[0]):
            b = m[i] > threshold
            outer = self._grow(b, grow) if grow else b
            inner = ~self._grow(~b, shrink_px) if shrink_px else b
            ring = (outer & ~inner).to(torch.float32)[None, None]
            if sigma > 0:
                ring = self._blur(ring, sigma, small)
            out[i] = ring[0, 0].clamp(0.0, 1.0)
        return (out if mask.dim() == 3 else out[0],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskOutlineRing", SYMaskOutlineRing)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskOutlineRing"] = "Mask Outline Ring SY"
