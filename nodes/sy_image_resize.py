"""Image Resize SY: makes a picture a chosen size by stretching, fitting inside, filling and cropping, or padding."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour, resize_tensor
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour, resize_tensor
    import _sy_d2_common as d2

MODES = ("stretch", "fit inside", "fill and crop", "pad")
SCALE_LIMITS = ("any", "never enlarge", "never shrink")
PAD_MASK = ("not masked (0)", "masked (1)")
MAX_SIDE = 16384
INTERPOLATIONS = ("bilinear", "bicubic", "area", "nearest-exact")


def round_multiple(value, multiple, down=False):
    """Rounds to the nearest multiple (or down), never below one multiple."""
    multiple = int(multiple)
    if multiple < 1:
        raise ValueError("multiple_of must be at least 1, got %d" % multiple)
    if down:
        v = (int(value) // multiple) * multiple
    else:
        v = int(round(value / float(multiple))) * multiple
    return max(multiple, v)


def plan_resize(src_w, src_h, target_w, target_h, mode, multiple=1):
    """Pure function. Returns a dict: scaled_w/h, out_w/h, crop_x/y (cut from scaled), pad_x/y (offset in canvas)."""
    if mode not in MODES:
        raise ValueError("unknown resize mode %r, pick one of: %s" % (mode, ", ".join(MODES)))
    if min(src_w, src_h, target_w, target_h) < 1:
        raise ValueError("width and height must be at least 1")
    plan = {"crop_x": 0, "crop_y": 0, "pad_x": 0, "pad_y": 0}
    if mode == "stretch":
        tw, th = round_multiple(target_w, multiple), round_multiple(target_h, multiple)
        plan.update(scaled_w=tw, scaled_h=th, out_w=tw, out_h=th)
    elif mode == "fit inside":
        s = min(target_w / float(src_w), target_h / float(src_h))
        w, h = round_multiple(src_w * s, multiple, down=True), round_multiple(src_h * s, multiple, down=True)
        plan.update(scaled_w=w, scaled_h=h, out_w=w, out_h=h)
    elif mode == "fill and crop":
        tw, th = round_multiple(target_w, multiple), round_multiple(target_h, multiple)
        s = max(tw / float(src_w), th / float(src_h))
        w, h = max(tw, int(round(src_w * s))), max(th, int(round(src_h * s)))
        plan.update(scaled_w=w, scaled_h=h, out_w=tw, out_h=th, crop_x=(w - tw) // 2, crop_y=(h - th) // 2)
    else:  # pad
        tw, th = round_multiple(target_w, multiple), round_multiple(target_h, multiple)
        s = min(tw / float(src_w), th / float(src_h))
        w, h = min(tw, max(1, int(round(src_w * s)))), min(th, max(1, int(round(src_h * s))))
        plan.update(scaled_w=w, scaled_h=h, out_w=tw, out_h=th, pad_x=(tw - w) // 2, pad_y=(th - h) // 2)
    return plan


def check_scale_limit(limit):
    if limit not in SCALE_LIMITS:
        raise ValueError("scale_limit must be one of: %s, got %r" % (", ".join(SCALE_LIMITS), limit))


def check_scaled(plan):
    """Pure function. Plain error when the working size would be absurdly large (for example fill and crop of a very thin picture)."""
    if max(plan["scaled_w"], plan["scaled_h"], plan["out_w"], plan["out_h"]) > MAX_SIDE:
        raise ValueError("this resize would need a %s picture, more than the %d pixel limit per side; "
                         "pick a smaller size or another mode" % (d2.size_text(plan["scaled_w"], plan["scaled_h"]), MAX_SIDE))


def skip_reason(src_w, src_h, plan, limit):
    """Pure function. '' when the resize should go ahead, otherwise the plain reason to leave the picture as it is.
    Uses the scaled size: never enlarge skips when either side would grow; never shrink skips when either side would get smaller."""
    check_scale_limit(limit)
    if limit == "never enlarge" and (plan["scaled_w"] > src_w or plan["scaled_h"] > src_h):
        return "the picture is smaller than the wanted size and scale_limit is never enlarge"
    if limit == "never shrink" and (plan["scaled_w"] < src_w or plan["scaled_h"] < src_h):
        return "the picture is larger than the wanted size and scale_limit is never shrink"
    return ""


def cap_megapixels(src_w, src_h, target_w, target_h, mode, multiple, max_mp):
    """Pure function. Lowers the wanted size step by step until the OUTPUT is at most max_mp megapixels (0 = off).
    Returns (target_w, target_h, was_capped)."""
    if max_mp < 0:
        raise ValueError("max_megapixels cannot be negative, got %s" % max_mp)
    if max_mp == 0:
        return int(target_w), int(target_h), False
    limit = max_mp * 1000000.0
    tw, th = int(target_w), int(target_h)
    capped = False
    for _ in range(200):
        p = plan_resize(src_w, src_h, tw, th, mode, multiple)
        if p["out_w"] * p["out_h"] <= limit:
            return tw, th, capped
        capped = True
        s = (limit / float(p["out_w"] * p["out_h"])) ** 0.5 * 0.99
        tw, th = max(1, int(tw * s)), max(1, int(th * s))
        if tw == 1 and th == 1:
            break
    return tw, th, capped


def resize_info(src_w, src_h, out_w, out_h, mode, skipped="", capped=False, mask_note=""):
    """Pure function. One plain line: what happened, the scale and the shape change."""
    if skipped:
        text = "Left at %s: %s" % (d2.size_text(src_w, src_h), skipped)
    else:
        text = "%s: %s -> %s" % (mode.capitalize(), d2.size_text(src_w, src_h), d2.size_text(out_w, out_h))
        if mode in ("fit inside", "fill and crop", "pad"):
            text += " (scale %.2fx, shape kept)" % (min(out_w / float(src_w), out_h / float(src_h)) if mode != "fill and crop" else max(out_w / float(src_w), out_h / float(src_h)))
        else:
            sx, sy = out_w / float(src_w), out_h / float(src_h)
            text += " (x %.2f, y %.2f)" % (sx, sy)
            if abs(sx - sy) / max(sx, sy) > 0.02:
                text += " - the shape changed, the picture looks squashed or stretched"
        if mode == "fill and crop":
            text += "; the edges that did not fit were cut off"
        if mode == "pad":
            text += "; the gaps were filled with the pad colour"
    if capped:
        text += "; the wanted size was lowered to stay under max_megapixels"
    if mask_note:
        text += "; " + mask_note
    return text + "."


class SYImageResize:
    DESCRIPTION = ("Changes the size of a picture. Stretch, fit inside the box, fill the box and crop the extra, or pad the gaps with a colour. "
                   "Can refuse to enlarge or shrink, cap the megapixels, and resize a mask with the picture. The info line tells the scale.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "MASK", "STRING")
    RETURN_NAMES = ("image", "width", "height", "mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to resize."}),
                "width": ("INT", {"default": 1024, "min": 1, "max": 16384, "tooltip": "Wanted width in pixels."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 16384, "tooltip": "Wanted height in pixels."}),
                "mode": (list(MODES), {"default": "fit inside", "tooltip": "How the picture meets the wanted size. Fit inside keeps the shape and may end smaller."}),
                "multiple_of": ("INT", {"default": 8, "min": 1, "max": 512, "tooltip": "Makes the result width and height a multiple of this number. 1 means off."}),
                "interpolation": (list(INTERPOLATIONS), {"default": "bilinear", "tooltip": "Smoothing method. Area is good for shrinking, nearest-exact keeps hard pixels."}),
                "pad_color": (list(COLOUR_NAMES), {"default": "black", "tooltip": "Colour of the bars when the mode is pad."}),
            },
            "optional": {
                "custom_color": ("STRING", {"default": "", "tooltip": CUSTOM_TIP}),
                "scale_limit": (list(SCALE_LIMITS), {"default": "any", "tooltip": "never enlarge / never shrink: leave the picture as it is when the resize would go that way."}),
                "max_megapixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 268.0, "step": 0.1, "tooltip": "Lower the wanted size until the result is at most this many megapixels. 0 is off."}),
                "mask": ("MASK", {"tooltip": "Optional mask that is resized together with the picture, so the two stay matched."}),
                "pad_area_in_mask": (list(PAD_MASK), {"default": "not masked (0)", "tooltip": "In pad mode: should the new bars count as masked (1) or not (0) in the mask output."}),
            },
        }

    def run(self, image, width, height, mode, multiple_of, interpolation, pad_color, custom_color="",
            scale_limit="any", max_megapixels=0.0, mask=None, pad_area_in_mask="not masked (0)"):
        import torch

        need_image(image)
        check_scale_limit(scale_limit)
        if pad_area_in_mask not in PAD_MASK:
            raise ValueError("pad_area_in_mask must be one of: %s, got %r" % (", ".join(PAD_MASK), pad_area_in_mask))
        _, sh, sw, c = image.shape
        width, height, capped = cap_megapixels(sw, sh, width, height, mode, multiple_of, max_megapixels)
        p = plan_resize(sw, sh, width, height, mode, multiple_of)
        check_scaled(p)
        mask4 = d2.t_mask_for_image(mask, image.shape[0], sh, sw) if mask is not None else None
        why = skip_reason(sw, sh, p, scale_limit)
        if why:
            out_mask = mask4[..., 0].contiguous() if mask4 is not None else torch.zeros((image.shape[0], sh, sw), dtype=torch.float32)
            return (image, int(sw), int(sh), out_mask, resize_info(sw, sh, sw, sh, mode, why))
        out = resize_tensor(image, p["scaled_h"], p["scaled_w"], interpolation)
        out_mask = resize_tensor(mask4, p["scaled_h"], p["scaled_w"], "bilinear") if mask4 is not None else None
        if mode == "fill and crop":
            out = out[:, p["crop_y"]:p["crop_y"] + p["out_h"], p["crop_x"]:p["crop_x"] + p["out_w"], :]
        elif mode == "pad":
            rgb = parse_colour(pad_color, custom_color)
            fill = [rgb[i] if i < 3 else 1.0 for i in range(c)]
            canvas = torch.tensor(fill, dtype=out.dtype, device=out.device).view(1, 1, 1, c)
            canvas = canvas.expand(out.shape[0], p["out_h"], p["out_w"], c).clone()
            canvas[:, p["pad_y"]:p["pad_y"] + p["scaled_h"], p["pad_x"]:p["pad_x"] + p["scaled_w"], :] = out
            out = canvas
            if out_mask is not None:
                big = torch.full((out.shape[0], p["out_h"], p["out_w"], 1), 1.0 if pad_area_in_mask == PAD_MASK[1] else 0.0, dtype=out_mask.dtype)
                big[:, p["pad_y"]:p["pad_y"] + p["scaled_h"], p["pad_x"]:p["pad_x"] + p["scaled_w"], :] = out_mask
                out_mask = big
        if out_mask is not None and mode == "fill and crop":
            out_mask = out_mask[:, p["crop_y"]:p["crop_y"] + p["out_h"], p["crop_x"]:p["crop_x"] + p["out_w"], :]
        if out_mask is None:
            out_mask = torch.zeros((out.shape[0], out.shape[1], out.shape[2]), dtype=torch.float32)
        else:
            out_mask = out_mask[..., 0].contiguous()
        info = resize_info(sw, sh, int(out.shape[2]), int(out.shape[1]), mode, "", capped,
                           "the mask was resized with the picture" if mask is not None else "")
        return (out.contiguous(), int(out.shape[2]), int(out.shape[1]), out_mask, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageResize", SYImageResize)
NODE_DISPLAY_NAME_MAPPINGS["SYImageResize"] = "Image Resize SY"
