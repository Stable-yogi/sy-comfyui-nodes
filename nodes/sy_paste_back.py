"""Paste Back SY: cut the original area out of a padded picture, or paste an edited area back, using the crop_box of Outpaint Pad SY."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, smoothstep
    from ._sy_d3_info import need_nonempty, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, smoothstep
    from _sy_d3_info import need_nonempty, size_text

MODES = ("cut out the original area", "paste into another picture")
MAX_FEATHER = 256


def parse_box(text):
    """Pure function. 'x,y,w,h' (spaces allowed) -> (x, y, w, h) whole numbers. x,y >= 0, w,h >= 1. Plain refusal otherwise."""
    raw = (text or "").strip()
    if not raw:
        raise ValueError("crop_box is empty: connect the crop_box output of Outpaint Pad SY, or write four numbers like  100,0,512,512")
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        raise ValueError("crop_box needs four numbers separated by commas (x,y,width,height), got %r" % raw)
    vals = []
    for name, p in zip(("x", "y", "width", "height"), parts):
        try:
            v = int(p)
        except ValueError:
            raise ValueError("crop_box: %s must be a whole number, got %r. Write it like  100,0,512,512" % (name, p))
        vals.append(v)
    x, y, w, h = vals
    if x < 0 or y < 0:
        raise ValueError("crop_box: x and y cannot be negative, got %d,%d" % (x, y))
    if w < 1 or h < 1:
        raise ValueError("crop_box: width and height must be at least 1, got %dx%d" % (w, h))
    return x, y, w, h


def check_box(box, pic_w, pic_h, what="picture"):
    """Pure function. Plain refusal when the box does not lie fully inside a picture of pic_w x pic_h."""
    x, y, w, h = box
    if x + w > pic_w or y + h > pic_h:
        raise ValueError("the box %s at %d,%d does not fit inside the %s, which is %s. Check that crop_box belongs to this picture"
                         % (size_text(w, h), x, y, what, size_text(pic_w, pic_h)))
    return box


def feather_profile(size, feather):
    """Pure function. Weight for each of the `size` pixels along one direction: 1 in the middle, falling softly
    towards both ends over `feather` pixels inward. feather 0 gives all 1 (hard)."""
    if size < 1:
        return []
    if feather <= 0:
        return [1.0] * size
    out = []
    for i in range(size):
        d = min(i, size - 1 - i)
        out.append(1.0 if d >= feather else smoothstep((d + 1.0) / (feather + 1.0)))
    return out


def cut_info(box, src_w, src_h, count):
    x, y, w, h = box
    return "Paste Back: cut %s out of the %s picture at %d,%d (%d picture%s)" % (
        size_text(w, h), size_text(src_w, src_h), x, y, count, "" if count == 1 else "s")


def paste_info(box, tgt_w, tgt_h, count, feather, has_mask):
    x, y, w, h = box
    soft = []
    if feather:
        soft.append("edge feather %d px" % feather)
    if has_mask:
        soft.append("soft mask")
    return "Paste Back: pasted %s at %d,%d into the %s picture (%d picture%s); %s" % (
        size_text(w, h), x, y, size_text(tgt_w, tgt_h), count, "" if count == 1 else "s",
        ", ".join(soft) if soft else "hard edge")


def batch_plan(ib, tb):
    """Pure function. How many output pictures when pasting ib edited pictures into tb targets."""
    if ib == tb or tb == 1:
        return ib
    raise ValueError("the edited batch has %d pictures but the target batch has %d. Use the same number, or one single target picture" % (ib, tb))


class SYPasteBackBox:
    DESCRIPTION = ("Puts an outpainted or inpainted picture back, or cuts the original area out again, using the crop_box from "
                   "Outpaint Pad SY. Cut out: returns the part of the picture inside the box. Paste: the box is given in the "
                   "coordinates of the edited picture, and that part is placed into the target picture at the SAME x,y. "
                   "Optional soft mask (1 = take from the edited picture) and edge feather make a soft join. Pictures keep their alpha.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The edited or padded picture the box is measured in."}),
                "crop_box": ("STRING", {"forceInput": True, "tooltip": "x,y,width,height from Outpaint Pad SY. Example: 100,0,512,512"}),
                "mode": (list(MODES), {"default": MODES[0], "tooltip": "Cut the box out of the image, or paste it into the target."}),
            },
            "optional": {
                "target": ("IMAGE", {"tooltip": "Picture to paste into (needed for paste). The box lands at the same x,y."}),
                "mask": ("MASK", {"tooltip": "Soft paste mask, 1 = take from image. Same size as image or the box. No mask = hard paste."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": MAX_FEATHER, "tooltip": "Soft edge of the pasted box, pixels inward. Example: 16"}),
            },
        }

    def run(self, image, crop_box, mode, target=None, mask=None, feather=0):
        need_image(image)
        need_nonempty(image.shape)
        if mode not in MODES:
            raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
        if not 0 <= int(feather) <= MAX_FEATHER:
            raise ValueError("feather must be between 0 and %d pixels, got %s" % (MAX_FEATHER, feather))
        box = parse_box(crop_box)
        b, ih, iw, ic = image.shape
        check_box(box, iw, ih, "image")
        x, y, w, h = box
        if mode == MODES[0]:
            return (image[:, y:y + h, x:x + w, :].contiguous(), cut_info(box, iw, ih, b))
        if target is None:
            raise ValueError("paste needs a target picture: connect the picture to paste into, or switch the mode to cut out")
        import torch
        need_image(target)
        need_nonempty(target.shape, "target")
        tb, th, tw, tc = target.shape
        check_box(box, tw, th, "target picture")
        n = batch_plan(b, tb)
        region = image[:, y:y + h, x:x + w, :].to(device=target.device, dtype=target.dtype)
        if ic != tc:
            if tc == 4:      # image has no alpha: fully opaque
                region = torch.cat([region[..., :3], torch.ones_like(region[..., :1])], dim=-1)
            else:            # target has no alpha: alpha of image is dropped
                region = region[..., :tc]
        out = target.expand(n, th, tw, tc).clone()
        weight = None
        if mask is not None:
            if getattr(mask, "ndim", 0) == 2:
                mask = mask.unsqueeze(0)
            if getattr(mask, "ndim", 0) != 3:
                raise ValueError("the mask must be a mask batch shaped [batch, height, width]")
            mb, mh, mw = mask.shape
            if (mh, mw) == (ih, iw):
                mpart = mask[:, y:y + h, x:x + w]
            elif (mh, mw) == (h, w):
                mpart = mask
            else:
                raise ValueError("the mask is %s but it must match the image (%s) or the box (%s)"
                                 % (size_text(mw, mh), size_text(iw, ih), size_text(w, h)))
            if mb not in (1, n):
                raise ValueError("the mask batch has %d masks but there are %d pictures. Use one mask or the same number" % (mb, n))
            weight = mpart.to(device=target.device, dtype=target.dtype).clamp(0.0, 1.0).unsqueeze(-1)
        if feather:
            ry = torch.tensor(feather_profile(h, feather), dtype=target.dtype, device=target.device).view(1, h, 1, 1)
            rx = torch.tensor(feather_profile(w, feather), dtype=target.dtype, device=target.device).view(1, 1, w, 1)
            soft = torch.minimum(ry, rx)
            weight = soft if weight is None else weight * soft
        if weight is None:
            out[:, y:y + h, x:x + w, :] = region
        else:
            base = out[:, y:y + h, x:x + w, :]
            out[:, y:y + h, x:x + w, :] = base * (1.0 - weight) + region * weight
        return (out, paste_info(box, tw, th, n, int(feather), mask is not None))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PasteBackBox", SYPasteBackBox)
NODE_DISPLAY_NAME_MAPPINGS["SYPasteBackBox"] = "Paste Back Box SY"
