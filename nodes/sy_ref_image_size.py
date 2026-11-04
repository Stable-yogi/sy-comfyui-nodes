"""Ref Image Size SY: puts a reference picture into the shape and size of the video before it goes to a video model."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("fit inside video", "fill video (crop)", "pad to video shape", "keep shape")
PADS = ("black", "white", "grey", "edge")


def _even(value, multiple):
    return max(multiple, int(round(value / float(multiple))) * multiple)


def plan_size(src_w, src_h, video_w, video_h, mode, max_side=0, multiple=8):
    """Pure function. Returns a dict: scale_w, scale_h (size after scaling), crop (x, y, w, h) or None,
    pad (left, top, right, bottom) or None, out_w, out_h, notes (list)."""
    src_w, src_h, video_w, video_h = int(src_w), int(src_h), int(video_w), int(video_h)
    max_side, multiple = int(max_side), int(multiple)
    if mode not in MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(MODES))
    if min(src_w, src_h) < 1:
        raise ValueError("the reference picture is empty (%dx%d)" % (src_w, src_h))
    if min(video_w, video_h) < 16:
        raise ValueError("video size %dx%d is too small: use the width and height of your video" % (video_w, video_h))
    if max_side < 0:
        raise ValueError("max_side cannot be negative: 0 means no limit")
    if multiple not in (1, 2, 8, 16, 32, 64):
        raise ValueError("multiple must be 1, 2, 8, 16, 32 or 64")
    notes = []
    box_w, box_h = video_w, video_h
    if max_side and max(box_w, box_h) > max_side:
        f = max_side / float(max(box_w, box_h))
        box_w, box_h = max(16, int(round(box_w * f))), max(16, int(round(box_h * f)))
        notes.append("capped to %d pixels on the long side" % max_side)
    box_w, box_h = _even(box_w, multiple), _even(box_h, multiple)
    crop = pad = None
    if mode == "keep shape":
        f = max(box_w, box_h) / float(max(src_w, src_h))
        out_w, out_h = _even(src_w * f, multiple), _even(src_h * f, multiple)
        scale_w, scale_h = out_w, out_h
    elif mode == "fit inside video" or mode == "pad to video shape":
        f = min(box_w / float(src_w), box_h / float(src_h))
        scale_w, scale_h = max(1, int(round(src_w * f))), max(1, int(round(src_h * f)))
        if mode == "fit inside video":
            out_w, out_h = _even(scale_w, multiple), _even(scale_h, multiple)
            scale_w, scale_h = out_w, out_h
        else:
            out_w, out_h = box_w, box_h
            left, top = (out_w - scale_w) // 2, (out_h - scale_h) // 2
            pad = (left, top, out_w - scale_w - left, out_h - scale_h - top)
    else:
        f = max(box_w / float(src_w), box_h / float(src_h))
        scale_w, scale_h = max(box_w, int(round(src_w * f))), max(box_h, int(round(src_h * f)))
        out_w, out_h = box_w, box_h
        crop = ((scale_w - out_w) // 2, (scale_h - out_h) // 2, out_w, out_h)
        lost = 1.0 - (out_w * out_h) / float(scale_w * scale_h)
        if lost > 0.3:
            notes.append("%d%% of the picture is cut off: a head may be lost, try pad to video shape" % round(lost * 100))
    if f > 1.0:
        notes.append("the picture is made %.1fx bigger: a larger reference keeps more detail" % f)
    src_wide, vid_wide = src_w >= src_h, video_w >= video_h
    if src_wide != vid_wide and src_w != src_h and video_w != video_h:
        notes.append("the picture is %s but the video is %s" % ("wide" if src_wide else "tall", "wide" if vid_wide else "tall"))
    return {"scale_w": scale_w, "scale_h": scale_h, "crop": crop, "pad": pad, "out_w": out_w, "out_h": out_h, "notes": notes}


def _pad_value(pad_colour):
    return {"black": 0.0, "white": 1.0, "grey": 0.5}.get(pad_colour)


class SYRefImageSize:
    DESCRIPTION = ("Puts a reference picture into the shape and size of your video before a video model reads it. "
                   "Fit keeps the whole picture, fill crops it to the video shape, pad adds borders so nothing is cut. "
                   "max_side keeps big pictures from slowing the model down.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The reference picture (one or a batch)."}),
                "video_width": ("INT", {"default": 864, "min": 16, "max": 16384, "tooltip": "Width of the video you make. Wire it from your size node."}),
                "video_height": ("INT", {"default": 480, "min": 16, "max": 16384, "tooltip": "Height of the video you make. Wire it from your size node."}),
                "mode": (list(MODES), {"default": "pad to video shape", "tooltip": "Fit: whole picture, own shape. Fill: video shape, edges cut. Pad: video shape, borders added. Keep shape: only resize."}),
            },
            "optional": {
                "max_side": ("INT", {"default": 0, "min": 0, "max": 16384, "tooltip": "Longest side limit in pixels. 0 = the video size. Smaller is faster and uses less memory."}),
                "pad_colour": (list(PADS), {"default": "grey", "tooltip": "Border colour for pad mode. Edge repeats the outer pixels."}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 64, "tooltip": "Width and height are rounded to this step. 8 is safe for most models."}),
            },
        }

    def run(self, image, video_width, video_height, mode, max_side=0, pad_colour="grey", multiple=8):
        import torch
        import torch.nn.functional as F
        if pad_colour not in PADS:
            raise ValueError("pad_colour must be one of: %s" % ", ".join(PADS))
        h, w = image.shape[1], image.shape[2]
        plan = plan_size(w, h, video_width, video_height, mode, max_side, multiple)
        x = image.movedim(-1, 1)
        x = F.interpolate(x, size=(plan["scale_h"], plan["scale_w"]), mode="bicubic", align_corners=False, antialias=True)
        if plan["crop"]:
            cx, cy, cw, ch = plan["crop"]
            x = x[:, :, cy:cy + ch, cx:cx + cw]
        if plan["pad"]:
            left, top, right, bottom = plan["pad"]
            if pad_colour == "edge":
                x = F.pad(x, (left, right, top, bottom), mode="replicate")
            else:
                x = F.pad(x, (left, right, top, bottom), mode="constant", value=_pad_value(pad_colour))
        out = torch.clamp(x.movedim(1, -1), 0.0, 1.0).contiguous()
        info = "%dx%d -> %dx%d (%s)" % (w, h, plan["out_w"], plan["out_h"], mode)
        if plan["notes"]:
            info += "\n" + "\n".join(plan["notes"])
        return (out, plan["out_w"], plan["out_h"], info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RefImageSize", SYRefImageSize)
NODE_DISPLAY_NAME_MAPPINGS["SYRefImageSize"] = "Ref Image Size SY"
