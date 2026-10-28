"""Inpaint Crop SY and Inpaint Stitch SY: draw a small painted part at full size, then put it back.

Find the painted area, take a box around it with some room, scale that box so the model draws it at full
resolution, then scale the result back down and blend it into the untouched picture with the soft mask.
"""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STITCH_TYPE = "SY_STITCH"
MULTIPLE = 16  # VAE /8 and 2x2 patches: crop sizes must divide by 16
MIN_SIDE = 64


def box_from_flags(rows_any, cols_any):
    """Pure function. rows_any[y] / cols_any[x] say if any mask pixel is set in that row / column.
    Returns (x0, y0, x1, y1) around the set pixels, or None when nothing is set."""
    ys = [i for i, v in enumerate(rows_any) if v]
    xs = [i for i, v in enumerate(cols_any) if v]
    if not ys or not xs:
        return None
    return xs[0], ys[0], xs[-1] + 1, ys[-1] + 1


def context_box(box, width, height, context, min_side):
    """Pure function. Grow the box around its centre by `context` (1.0 = tight), at least min_side,
    kept inside the picture. Returns (x0, y0, x1, y1)."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1, got %sx%s" % (width, height))
    if context < 1.0:
        raise ValueError("context must be 1.0 or more, got %s" % context)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bw = min(width, max((x1 - x0) * context, min_side))
    bh = min(height, max((y1 - y0) * context, min_side))
    nx0 = int(round(min(max(cx - bw / 2.0, 0), width - bw)))
    ny0 = int(round(min(max(cy - bh / 2.0, 0), height - bh)))
    return nx0, ny0, nx0 + int(round(bw)), ny0 + int(round(bh))


def target_size(w, h, long_side):
    """Pure function. Scale (w, h) so the long side is long_side; both sides round to a multiple of 16 (at least 64)."""
    if w < 1 or h < 1:
        raise ValueError("box size must be at least 1x1, got %sx%s" % (w, h))
    if long_side < 1:
        raise ValueError("size must be at least 1, got %s" % long_side)
    scale = long_side / float(max(w, h))
    tw = max(MIN_SIDE, int(round(w * scale / MULTIPLE)) * MULTIPLE)
    th = max(MIN_SIDE, int(round(h * scale / MULTIPLE)) * MULTIPLE)
    return tw, th


def blend(original, new, alpha):
    """Pure function. The soft-mask blend (works on numbers or tensors). alpha 0 keeps the original, 1 takes the new one."""
    return original * (1.0 - alpha) + new * alpha


def _resize_image(img, w, h):
    """IMAGE [B,H,W,C] -> [B,h,w,C]. Bicubic up, area down (no ringing when shrinking)."""
    import torch.nn.functional as F
    x = img.movedim(-1, 1)
    if w >= x.shape[3]:
        x = F.interpolate(x, size=(h, w), mode="bicubic", align_corners=False).clamp(0, 1)
    else:
        x = F.interpolate(x, size=(h, w), mode="area")
    return x.movedim(1, -1)


def _resize_mask(mask, w, h):
    import torch.nn.functional as F
    return F.interpolate(mask.unsqueeze(1), size=(h, w), mode="bilinear", align_corners=False).squeeze(1).clamp(0, 1)


def _match_batch(t, b):
    return t if t.shape[0] == b else t[:1].expand(b, *t.shape[1:])


def _mask_bbox(mask, threshold=0.01):
    """Box around every mask pixel above threshold, over the whole batch. None if empty."""
    m = (mask > threshold).any(dim=0)
    return box_from_flags(m.any(dim=1).tolist(), m.any(dim=0).tolist())


class SYInpaintCrop:
    DESCRIPTION = ("Cuts a box around the painted part and scales it up, so the model draws a small hand or face at "
                   "full size. Send 'stitch' to Inpaint Stitch to put the result back.")
    CATEGORY = category("Editors")
    FUNCTION = "crop"
    RETURN_TYPES = (STITCH_TYPE, "IMAGE", "MASK")
    RETURN_NAMES = ("stitch", "cropped_image", "cropped_mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Your whole picture."}),
                "mask": ("MASK", {"tooltip": "The painted part (already grown and softened is best)."}),
                "context": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 4.0, "step": 0.05,
                                      "tooltip": "Room around the painted part, as a factor of its size. More room matches the scene better."}),
                "size": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 16,
                                 "tooltip": "Long side of the crop the model draws, in pixels. 1024 suits Krea 2."}),
                "min_box": ("INT", {"default": 256, "min": 64, "max": 2048, "step": 16,
                                    "tooltip": "Smallest crop box on the original picture, so a tiny mark still gets some scene around it."}),
            }
        }

    def crop(self, image, mask, context, size, min_box):
        b, height, width, _ = image.shape
        if mask.dim() == 2:
            mask = mask.unsqueeze(0)
        if mask.shape[1:] != (height, width):
            mask = _resize_mask(mask, width, height)
        mask = _match_batch(mask, b)

        box = _mask_bbox(mask)
        if box is None:  # nothing painted: use the whole picture so the graph still runs
            box = (0, 0, width, height)
        x0, y0, x1, y1 = context_box(box, width, height, context, min_box)
        tw, th = target_size(x1 - x0, y1 - y0, size)

        crop_img = _resize_image(image[:, y0:y1, x0:x1, :], tw, th)
        crop_mask = _resize_mask(mask[:, y0:y1, x0:x1], tw, th)
        stitch = {"original": image, "mask": mask, "box": (x0, y0, x1, y1), "crop_size": (tw, th)}
        return (stitch, crop_img, crop_mask)


class SYInpaintStitch:
    DESCRIPTION = ("Scales the new crop back down and blends it into your picture through the soft mask. "
                   "Every pixel outside the mask stays your own.")
    CATEGORY = category("Editors")
    FUNCTION = "stitch"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "stitch": (STITCH_TYPE, {"tooltip": "The 'stitch' output of Inpaint Crop."}),
                "inpainted": ("IMAGE", {"tooltip": "The decoded crop from the sampler."}),
            }
        }

    def stitch(self, stitch, inpainted):
        if not isinstance(stitch, dict) or "box" not in stitch or "original" not in stitch or "mask" not in stitch:
            raise ValueError("stitch must come from the Inpaint Crop node; connect its 'stitch' output here")
        original = stitch["original"]
        x0, y0, x1, y1 = stitch["box"]
        b = max(original.shape[0], inpainted.shape[0])
        out = _match_batch(original, b).clone()
        mask = _match_batch(stitch["mask"], b)

        part = _resize_image(inpainted.to(out.device, out.dtype), x1 - x0, y1 - y0)
        part = _match_batch(part, b)
        alpha = mask[:, y0:y1, x0:x1].unsqueeze(-1).to(out.device, out.dtype)
        region = out[:, y0:y1, x0:x1, :]
        out[:, y0:y1, x0:x1, :] = blend(region, part, alpha)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "InpaintCrop", SYInpaintCrop)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "InpaintStitch", SYInpaintStitch)
