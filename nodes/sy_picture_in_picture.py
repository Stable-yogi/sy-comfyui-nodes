"""Picture In Picture SY: puts a small copy of one picture or clip inside another, with a border."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "centre"]
UNEVEN = ["stop at shorter", "repeat last"]


def clip_length(len_a, len_b, when_uneven="repeat last"):
    """Pure function. How many output frames. A batch of 1 repeats against a longer clip."""
    len_a, len_b = int(len_a), int(len_b)
    if len_a < 1 or len_b < 1:
        raise ValueError("both inputs need at least one picture (base has %d, inset has %d)" % (len_a, len_b))
    if when_uneven not in UNEVEN:
        raise ValueError("when_uneven must be one of: %s (got %r)" % (", ".join(UNEVEN), when_uneven))
    if len_a == 1:
        return len_b
    if len_b == 1:
        return len_a
    return min(len_a, len_b) if when_uneven == "stop at shorter" else max(len_a, len_b)


def inset_box(base_w, base_h, inset_w, inset_h, size, position, margin):
    """Pure function. Returns (x, y, w, h) of the small picture, always fully inside the base."""
    base_w, base_h, inset_w, inset_h, margin = int(base_w), int(base_h), int(inset_w), int(inset_h), int(margin)
    if min(base_w, base_h, inset_w, inset_h) < 1:
        raise ValueError("picture sizes must be at least 1 pixel")
    if position not in POSITIONS:
        raise ValueError("position must be one of: %s (got %r)" % (", ".join(POSITIONS), position))
    size = float(size)
    if size < 0.05 or size > 0.9:
        raise ValueError("size must be between 0.05 and 0.9 (got %s)" % size)
    if margin < 0:
        raise ValueError("margin cannot be negative")
    w = max(1, int(round(base_w * size)))
    h = max(1, int(round(w * inset_h / float(inset_w))))
    gap = 0 if position == "centre" else margin
    if w + 2 * gap > base_w or h + 2 * gap > base_h:
        raise ValueError("the small picture (%dx%d) plus margin %d does not fit in %dx%d. "
                         "Lower size or margin" % (w, h, margin, base_w, base_h))
    left = gap if position in ("top-left", "bottom-left") else base_w - w - gap
    top = gap if position in ("top-left", "top-right") else base_h - h - gap
    if position == "centre":
        left, top = (base_w - w) // 2, (base_h - h) // 2
    return (left, top, w, h)


def round_rect_distance(px, py, w, h, radius):
    """Pure function. Signed distance from point (px, py) to a rounded rectangle at the origin.
    Negative = inside. Radius is limited to half the shorter side."""
    r = max(0.0, min(float(radius), min(w, h) / 2.0))
    qx = abs(px - w / 2.0) - (w / 2.0 - r)
    qy = abs(py - h / 2.0) - (h / 2.0 - r)
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    return outside + min(max(qx, qy), 0.0) - r


def check_border(border, w, h):
    """Pure function. Refuses a border that would swallow the small picture."""
    if int(border) < 0:
        raise ValueError("border cannot be negative")
    if int(border) * 2 + 2 > min(w, h):
        raise ValueError("border %d is too thick for a %dx%d small picture. Lower border or raise size" % (border, w, h))


class SYPictureInPicture:
    DESCRIPTION = ("Puts a small copy of one picture or clip inside another, with an optional border, "
                   "rounded corners and see-through. The output has the size of the base. "
                   "It refuses a placement that would hang outside the picture.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_base": ("IMAGE", {"tooltip": "The big picture or clip that stays in the background."}),
                "images_inset": ("IMAGE", {"tooltip": "The small picture or clip that is placed on top."}),
                "position": (POSITIONS, {"default": "bottom-right", "tooltip": "Which corner the small picture sits in, or the centre."}),
                "size": ("FLOAT", {"default": 0.3, "min": 0.05, "max": 0.9, "step": 0.01, "tooltip": "Width of the small picture as a fraction of the base width."}),
                "margin": ("INT", {"default": 24, "min": 0, "max": 500, "tooltip": "Gap in pixels between the small picture and the edge."}),
                "border": ("INT", {"default": 4, "min": 0, "max": 64, "tooltip": "Thickness of the frame around the small picture, in pixels."}),
                "border_grey": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Brightness of the frame. 0 is black, 1 is white."}),
                "corner_radius": ("INT", {"default": 0, "min": 0, "max": 200, "tooltip": "How round the corners are, in pixels. 0 is square."}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "1 hides the base behind the small picture, lower lets it show through."}),
                "when_uneven": (UNEVEN, {"default": "repeat last", "tooltip": "If the clips differ in length: stop at the shorter or repeat the last frame."}),
            }
        }

    def run(self, images_base, images_inset, position, size, margin, border, border_grey, corner_radius, opacity, when_uneven):
        import torch
        import torch.nn.functional as F

        count = clip_length(images_base.shape[0], images_inset.shape[0], when_uneven)
        bh, bw, chans = int(images_base.shape[1]), int(images_base.shape[2]), int(images_base.shape[3])
        ih, iw = int(images_inset.shape[1]), int(images_inset.shape[2])
        x, y, w, h = inset_box(bw, bh, iw, ih, size, position, margin)
        check_border(border, w, h)
        if not 0.0 <= float(opacity) <= 1.0:
            raise ValueError("opacity must be between 0 and 1 (got %s)" % opacity)

        # soft coverage of the outer shape and of the picture area inside the border
        ys = (torch.arange(h, dtype=torch.float32) + 0.5).unsqueeze(1)
        xs = (torch.arange(w, dtype=torch.float32) + 0.5).unsqueeze(0)

        def coverage(ox, oy, cw, ch, rad):
            r = max(0.0, min(float(rad), min(cw, ch) / 2.0))
            qx = (xs - ox - cw / 2.0).abs() - (cw / 2.0 - r)
            qy = (ys - oy - ch / 2.0).abs() - (ch / 2.0 - r)
            dist = torch.sqrt(qx.clamp(min=0) ** 2 + qy.clamp(min=0) ** 2) + torch.maximum(qx, qy).clamp(max=0) - r
            return (0.5 - dist).clamp(0.0, 1.0)

        outer = coverage(0, 0, w, h, corner_radius)
        if border > 0:
            inner = coverage(border, border, w - 2 * border, h - 2 * border, max(0, corner_radius - border))
        else:
            inner = outer
        mix = (inner / outer.clamp(min=1e-6)).clamp(0.0, 1.0).unsqueeze(-1)
        alpha = (outer * float(opacity)).unsqueeze(-1)
        grey = torch.full((chans,), float(border_grey), dtype=torch.float32)
        if chans == 4:
            grey[3] = 1.0

        out = torch.empty((count, bh, bw, chans), dtype=images_base.dtype)
        for i in range(count):
            base = images_base[min(i, images_base.shape[0] - 1)]
            small = images_inset[min(i, images_inset.shape[0] - 1)].to(torch.float32)
            if small.shape[2] != chans:
                if small.shape[2] > chans:
                    small = small[..., :chans]
                elif small.shape[2] == 1:
                    small = small.expand(-1, -1, chans)
                else:
                    small = torch.cat([small, torch.ones(ih, iw, chans - small.shape[2])], dim=2)
            moved = small.permute(2, 0, 1).unsqueeze(0)
            moved = F.interpolate(moved, size=(h, w), mode="bilinear", align_corners=False, antialias=(w < iw))
            small = moved.squeeze(0).permute(1, 2, 0)
            colour = small * mix + grey * (1.0 - mix)
            frame = base.clone()
            region = base[y:y + h, x:x + w].to(torch.float32)
            frame[y:y + h, x:x + w] = (region * (1.0 - alpha) + colour * alpha).to(frame.dtype)
            out[i] = frame
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PictureInPicture", SYPictureInPicture)
NODE_DISPLAY_NAME_MAPPINGS["SYPictureInPicture"] = "Picture In Picture SY"
