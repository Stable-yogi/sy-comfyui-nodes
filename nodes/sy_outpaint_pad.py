"""Outpaint Pad SY: pad a picture, fill the new area, and give the soft mask for outpainting in one node."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, smoothstep
    from ._sy_d3_info import need_nonempty, size_text
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, smoothstep
    from _sy_d3_info import need_nonempty, size_text
    import _sy_mask_math as mm

ASPECTS = ("off", "1:1", "4:3", "3:2", "16:9", "9:16", "21:9")
FILLS = ("edge stretch", "mirror", "blur of picture", "grey", "black")
MAX_SIDE = 16384
MAX_MEGAPIXELS = 100.0
MAX_PAD = 8192


def _aspect_pair(to_aspect):
    if to_aspect not in ASPECTS:
        raise ValueError("to_aspect must be one of: %s, got %r" % (", ".join(ASPECTS), to_aspect))
    if to_aspect == "off":
        return None
    a, b = to_aspect.split(":")
    return int(a), int(b)


def plan_padding(w, h, left, top, right, bottom, to_aspect="off", multiple=8):
    """Pure function. Returns (left, top, right, bottom, new_w, new_h).
    to_aspect other than off replaces the four numbers: equal padding on the needed sides, picture centred.
    Then the size is rounded UP to a multiple by adding to right and bottom."""
    if min(w, h) < 1:
        raise ValueError("the picture must be at least 1x1 pixels")
    if not 1 <= multiple <= 512:
        raise ValueError("multiple must be between 1 and 512, got %s" % multiple)
    pair = _aspect_pair(to_aspect)
    if pair is None:
        for name, v in (("left", left), ("top", top), ("right", right), ("bottom", bottom)):
            if not 0 <= v <= MAX_PAD:
                raise ValueError("%s must be between 0 and %d pixels, got %s" % (name, MAX_PAD, v))
    else:
        a, b = pair
        left = top = right = bottom = 0
        if w * b < h * a:      # too narrow: add width
            extra = -(-h * a // b) - w
            left = extra // 2
            right = extra - left
        elif w * b > h * a:    # too wide: add height
            extra = -(-w * b // a) - h
            top = extra // 2
            bottom = extra - top
    nw0, nh0 = w + left + right, h + top + bottom
    right += (-nw0) % multiple
    bottom += (-nh0) % multiple
    nw, nh = w + left + right, h + top + bottom
    if nw > MAX_SIDE or nh > MAX_SIDE or nw * nh > MAX_MEGAPIXELS * 1e6:
        raise ValueError("the new picture would be %s (%.1f megapixels). The limit is %d pixels per side and %d megapixels: "
                         "use smaller margins" % (size_text(nw, nh), nw * nh / 1e6, MAX_SIDE, int(MAX_MEGAPIXELS)))
    return left, top, right, bottom, nw, nh


def mirror_index(n_out, offset, size):
    """Pure function. For each new position 0..n_out-1 the source pixel to copy when the picture starts at `offset`
    and is `size` wide: the picture is mirrored again and again outward, so any margin size works."""
    out = []
    period = 2 * size
    for p in range(n_out):
        i = (p - offset) % period
        out.append(i if i < size else period - 1 - i)
    return out


def edge_index(n_out, offset, size):
    """Pure function. Like mirror_index but the border pixel is repeated (edge stretch)."""
    return [min(max(p - offset, 0), size - 1) for p in range(n_out)]


def feather_profile(size, grow, feather, pad_before, pad_after):
    """Pure function. Mask value for each of the `size` original pixels along one direction.
    Only a side that got padding makes a seam. The first `grow` pixels next to the seam are fully 1 (hard),
    then the value falls softly to 0 over `feather` more pixels."""
    out = []
    for i in range(size):
        v = 0.0
        for padded, dist in ((pad_before, i), (pad_after, size - 1 - i)):
            if not padded:
                continue
            d = dist - grow
            if d < 0:
                r = 1.0
            elif feather <= 0:
                r = 0.0
            else:
                r = smoothstep(1.0 - (d + 1.0) / (feather + 1.0))
            v = max(v, r)
        out.append(v)
    return out


def crop_box_text(left, top, w, h):
    return "%d,%d,%d,%d" % (left, top, w, h)


def pad_info(w, h, plan, to_aspect, fill, feather, grow, multiple):
    """Pure function. One plain line."""
    left, top, right, bottom, nw, nh = plan
    if not (left or top or right or bottom):
        return "Outpaint Pad: nothing to add, the picture stays %s" % size_text(w, h)
    text = "Outpaint Pad: %s -> %s, added left %d, top %d, right %d, bottom %d; fill: %s; seam feather %d px, mask grow %d px" % (
        size_text(w, h), size_text(nw, nh), left, top, right, bottom, fill, feather, grow)
    if to_aspect != "off":
        text += "; centred to %s" % to_aspect
    if multiple > 1:
        text += "; size is a multiple of %d" % multiple
    if feather + grow > min(w, h) // 2:
        text += ". The soft seam is more than half the picture: most of the picture will be painted again"
    return text


def build_canvas(image, left, top, nw, nh, fill):
    """Torch. image [B,H,W,C] -> padded [B,nh,nw,C]. The new area is filled; RGBA keeps alpha and the new area is opaque."""
    import torch
    import torch.nn.functional as F
    b, h, w, c = image.shape
    dev = image.device
    if fill in ("grey", "black"):
        canvas = torch.full((b, nh, nw, c), 0.5 if fill == "grey" else 0.0, dtype=image.dtype, device=dev)
    elif fill in ("edge stretch", "mirror"):
        fn = edge_index if fill == "edge stretch" else mirror_index
        yi = torch.tensor(fn(nh, top, h), dtype=torch.long, device=dev)
        xi = torch.tensor(fn(nw, left, w), dtype=torch.long, device=dev)
        canvas = image.index_select(1, yi).index_select(2, xi)
    elif fill == "blur of picture":
        x = image.permute(0, 3, 1, 2)
        sh, sw = max(4, nh // 16), max(4, nw // 16)
        small = F.interpolate(x, size=(sh, sw), mode="area")
        small = mm.t_blur(small.reshape(b * c, sh, sw), 3).reshape(b, c, sh, sw)
        canvas = F.interpolate(small, size=(nh, nw), mode="bilinear", align_corners=False).permute(0, 2, 3, 1).contiguous()
    else:
        raise ValueError("fill must be one of: %s, got %r" % (", ".join(FILLS), fill))
    canvas[:, top:top + h, left:left + w, :] = image
    if c == 4:
        canvas[..., 3] = 1.0
        canvas[:, top:top + h, left:left + w, 3] = image[..., 3]
    return canvas


def build_mask(b, w, h, plan, grow, feather, dtype, device):
    """Torch. Mask [B,nh,nw]: 1 on the new area, 0 on the picture, a soft seam reaching into the picture."""
    import torch
    left, top, right, bottom, nw, nh = plan
    mask = torch.ones((nh, nw), dtype=dtype, device=device)
    ry = torch.tensor(feather_profile(h, grow, feather, top > 0, bottom > 0), dtype=dtype, device=device)
    rx = torch.tensor(feather_profile(w, grow, feather, left > 0, right > 0), dtype=dtype, device=device)
    mask[top:top + h, left:left + w] = torch.maximum(ry.view(h, 1), rx.view(1, w))
    return mask.unsqueeze(0).expand(b, nh, nw).contiguous()


class SYOutpaintPad:
    DESCRIPTION = ("One box for outpainting. Adds margins to a picture (or pads it to a shape like 16:9), fills the new area so the "
                   "model has something to continue from (edge stretch, mirror, blur, grey, black), and makes the matching mask with a "
                   "soft seam that reaches into the picture. Gives the box of the original so you can paste it back. Replaces chaining "
                   "pad, fill, mask grow and feather nodes. Pad Image SY only pads with one colour.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING")
    RETURN_NAMES = ("image", "mask", "info", "crop_box")

    @classmethod
    def INPUT_TYPES(cls):
        m = {"default": 0, "min": 0, "max": MAX_PAD}
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to extend."}),
                "left": ("INT", dict(m, tooltip="Pixels to add on the left. Example: 256")),
                "top": ("INT", dict(m, tooltip="Pixels to add on the top. Example: 0")),
                "right": ("INT", dict(m, tooltip="Pixels to add on the right. Example: 256")),
                "bottom": ("INT", dict(m, tooltip="Pixels to add at the bottom. Example: 0")),
            },
            "optional": {
                "to_aspect": (list(ASPECTS), {"default": "off", "tooltip": "Pad to this shape, picture centred. Replaces the four numbers. Example: 16:9"}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 512, "tooltip": "Round the new size up to a multiple of this (added right and bottom). Example: 8"}),
                "fill": (list(FILLS), {"default": "edge stretch", "tooltip": "What the new area holds before painting. Example: blur of picture"}),
                "seam_feather": ("INT", {"default": 0, "min": 0, "max": 256, "tooltip": "Soft mask edge, this many pixels INTO the picture. Example: 32"}),
                "mask_grow": ("INT", {"default": 0, "min": 0, "max": 256, "tooltip": "Hard mask pixels into the picture before the soft part. Example: 8"}),
            },
        }

    def run(self, image, left, top, right, bottom, to_aspect="off", multiple=8, fill="edge stretch", seam_feather=0, mask_grow=0):
        need_image(image)
        need_nonempty(image.shape)
        if fill not in FILLS:
            raise ValueError("fill must be one of: %s, got %r" % (", ".join(FILLS), fill))
        if not 0 <= seam_feather <= 256 or not 0 <= mask_grow <= 256:
            raise ValueError("seam_feather and mask_grow must be between 0 and 256 pixels")
        b, h, w, c = image.shape
        plan = plan_padding(w, h, left, top, right, bottom, to_aspect, multiple)
        pl, pt, pr, pb, nw, nh = plan
        info = pad_info(w, h, plan, to_aspect, fill, seam_feather, mask_grow, multiple)
        box = crop_box_text(pl, pt, w, h)
        if not (pl or pt or pr or pb):
            import torch
            return (image, torch.zeros((b, h, w), dtype=image.dtype, device=image.device), info, box)
        canvas = build_canvas(image, pl, pt, nw, nh, fill)
        mask = build_mask(b, w, h, plan, mask_grow, seam_feather, image.dtype, image.device)
        return (canvas, mask, info, box)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "OutpaintPad", SYOutpaintPad)
NODE_DISPLAY_NAME_MAPPINGS["SYOutpaintPad"] = "Outpaint Pad SY"
