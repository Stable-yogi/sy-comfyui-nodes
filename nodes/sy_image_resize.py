"""Image Resize SY: makes a picture a chosen size by stretching, fitting inside, filling and cropping, or padding."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour, resize_tensor
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import COLOUR_NAMES, CUSTOM_TIP, need_image, parse_colour, resize_tensor

MODES = ("stretch", "fit inside", "fill and crop", "pad")
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


class SYImageResize:
    DESCRIPTION = "Changes the size of a picture. Stretch, fit inside the box, fill the box and crop the extra, or pad the gaps with a colour."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")

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
            },
        }

    def run(self, image, width, height, mode, multiple_of, interpolation, pad_color, custom_color=""):
        import torch

        need_image(image)
        _, sh, sw, c = image.shape
        p = plan_resize(sw, sh, width, height, mode, multiple_of)
        out = resize_tensor(image, p["scaled_h"], p["scaled_w"], interpolation)
        if mode == "fill and crop":
            out = out[:, p["crop_y"]:p["crop_y"] + p["out_h"], p["crop_x"]:p["crop_x"] + p["out_w"], :]
        elif mode == "pad":
            rgb = parse_colour(pad_color, custom_color)
            fill = [rgb[i] if i < 3 else 1.0 for i in range(c)]
            canvas = torch.tensor(fill, dtype=out.dtype, device=out.device).view(1, 1, 1, c)
            canvas = canvas.expand(out.shape[0], p["out_h"], p["out_w"], c).clone()
            canvas[:, p["pad_y"]:p["pad_y"] + p["scaled_h"], p["pad_x"]:p["pad_x"] + p["scaled_w"], :] = out
            out = canvas
        return (out.contiguous(), int(out.shape[2]), int(out.shape[1]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageResize", SYImageResize)
NODE_DISPLAY_NAME_MAPPINGS["SYImageResize"] = "Image Resize SY"
