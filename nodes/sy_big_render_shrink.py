"""Big Render Shrink SY: shrinks a big render (8 or 16 MP) to a smaller size cleanly, so fine detail stays and harsh edges calm down."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import blur_tensor, need_image, resize_tensor
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import blur_tensor, need_image, resize_tensor

MP = 1048576  # same megapixel as H3 Image Size SY, so 4 MP is 2048 x 2048
TARGETS = {"2 MP": 2.0, "1 MP": 1.0, "4 MP": 4.0, "long side": 0.0}
LOOKS = ("clean", "crisp", "soft")
LOOK_TIPS = "clean: smooth and true to the render. crisp: clean plus a light sharpen. soft: the gentlest, good for skin."


def round_down(value, multiple):
    multiple = int(multiple)
    if multiple < 1:
        raise ValueError("multiple_of must be at least 1, got %d" % multiple)
    return max(multiple, (int(value) // multiple) * multiple)


def shrink_size(src_w, src_h, target, long_side=2048, multiple=16):
    """Pure function. The smaller size with the same shape. Returns (width, height, shrinks).
    shrinks is False when the picture is already at or under the target; then the size is the source size."""
    if target not in TARGETS:
        raise ValueError("unknown target %r, pick one of: %s" % (target, ", ".join(TARGETS)))
    src_w, src_h = int(src_w), int(src_h)
    if min(src_w, src_h) < 1:
        raise ValueError("width and height must be at least 1")
    if target == "long side":
        if int(long_side) < 64:
            raise ValueError("long_side must be at least 64 pixels, got %d" % int(long_side))
        s = int(long_side) / float(max(src_w, src_h))
    else:
        s = (TARGETS[target] * MP / float(src_w * src_h)) ** 0.5
    if s >= 1.0:
        return src_w, src_h, False
    return round_down(src_w * s, multiple), round_down(src_h * s, multiple), True


def shrink_plan(look, sharpen):
    """Pure function. (interpolation, sharpen amount, blur radius) for a look."""
    if look not in LOOKS:
        raise ValueError("unknown look %r, pick one of: %s" % (look, ", ".join(LOOKS)))
    if not 0.0 <= float(sharpen) <= 1.0:
        raise ValueError("sharpen must be between 0 and 1, got %s" % sharpen)
    if look == "soft":
        return "area", 0.0, 0.0
    if look == "crisp":
        return "bicubic", float(sharpen), 1.0
    return "bicubic", 0.0, 0.0


def shrink_info(src_w, src_h, w, h, shrinks, look, amount):
    """Pure function. One plain line about what happened."""
    if not shrinks:
        return "Left at %dx%d: the picture is already at or under the wanted size." % (src_w, src_h)
    text = "Shrunk %dx%d (%.1f MP) -> %dx%d (%.1f MP), %.2fx smaller per side, look %s" % (
        src_w, src_h, src_w * src_h / float(MP), w, h, w * h / float(MP), src_w / float(w), look)
    if amount > 0:
        text += ", sharpen %.2f" % amount
    if src_w * src_h < 6 * MP:
        text += ". Tip: render at 8 or 16 MP first for the cleanest small picture"
    return text + "."


def sharpen_tensor(img, amount, radius):
    """Unsharp mask: picture + amount x (picture - blurred picture), kept between 0 and 1."""
    if amount <= 0:
        return img
    rgb = img[..., :3]
    sharp = (rgb + amount * (rgb - blur_tensor(rgb, radius))).clamp(0.0, 1.0)
    if img.shape[3] > 3:
        import torch
        return torch.cat([sharp, img[..., 3:]], dim=3).contiguous()
    return sharp.contiguous()


class SYBigRenderShrink:
    DESCRIPTION = ("Shrinks a big render to a smaller size with a high quality filter. Render at 8 or 16 MP, then shrink to 2 MP or 1 MP: "
                   "fine detail stays and the harsh, crusty edges of a direct small render calm down. The shape is kept and the picture is never enlarged.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The big render (one picture or a batch)."}),
                "target": (list(TARGETS), {"default": "2 MP", "tooltip": "The size of the small picture. long side: set the longest side in pixels below."}),
                "look": (list(LOOKS), {"default": "clean", "tooltip": LOOK_TIPS}),
            },
            "optional": {
                "long_side": ("INT", {"default": 2048, "min": 64, "max": 16384, "step": 16, "tooltip": "Longest side in pixels when target is long side."}),
                "sharpen": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "How much the crisp look sharpens. 0.2 to 0.4 looks natural."}),
                "multiple_of": ("INT", {"default": 16, "min": 1, "max": 256, "tooltip": "Width and height become a multiple of this number. 1 means off."}),
            },
        }

    def run(self, image, target, look, long_side=2048, sharpen=0.3, multiple_of=16):
        need_image(image)
        _, sh, sw, _ = image.shape
        w, h, shrinks = shrink_size(sw, sh, target, long_side, multiple_of)
        interp, amount, radius = shrink_plan(look, sharpen)
        if not shrinks:
            return (image, int(sw), int(sh), shrink_info(sw, sh, sw, sh, False, look, 0.0))
        out = resize_tensor(image, h, w, interp)
        out = sharpen_tensor(out, amount, radius)
        return (out, int(w), int(h), shrink_info(sw, sh, w, h, True, look, amount))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BigRenderShrink", SYBigRenderShrink)
NODE_DISPLAY_NAME_MAPPINGS["SYBigRenderShrink"] = "Big Render Shrink SY"
