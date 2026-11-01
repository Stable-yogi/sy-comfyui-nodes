"""Rounded Corners SY: rounds the corners of a picture and paints what is cut off."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from ._sy_hexcolour import parse_hex
    from ._sy_d3_info import need_nonempty, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    from _sy_hexcolour import parse_hex
    from _sy_d3_info import need_nonempty, size_text

DEFAULT_BACKGROUND = "#" + "000000"


def corner_coverage(x, y, w, h, radius):
    """Pure function. How much of pixel (x, y) lies inside the rounded rectangle, 0..1, with a 1-pixel soft edge.
    The pixel centre (x + 0.5, y + 0.5) is used. radius is in pixels and is capped at half the shorter side."""
    if w < 1 or h < 1:
        raise ValueError("picture size must be at least 1x1")
    if radius < 0:
        raise ValueError("radius must not be negative, got %s" % radius)
    r = min(float(radius), min(w, h) / 2.0)
    if r <= 0.0:
        return 1.0
    px, py = x + 0.5, y + 0.5
    qx = abs(px - w / 2.0) - (w / 2.0 - r)
    qy = abs(py - h / 2.0) - (h / 2.0 - r)
    outside = (max(qx, 0.0) ** 2 + max(qy, 0.0) ** 2) ** 0.5
    d = outside + min(max(qx, qy), 0.0) - r  # signed distance to the edge, negative inside
    v = 0.5 - d
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def check_percent(radius_percent):
    if not 0.0 <= radius_percent <= 50.0:
        raise ValueError("radius_percent must be between 0 and 50, got %s" % radius_percent)


def radius_pixels(radius_percent, w, h):
    check_percent(radius_percent)
    return radius_percent / 100.0 * min(w, h)


def corner_info(radius_percent, width, height, transparent=False):
    """Pure function. Plain sentence: the real radius in pixels and what fills the corners."""
    r = radius_pixels(radius_percent, width, height)
    if r <= 0.0:
        return "Radius is 0: the picture was passed through unchanged (the mask is all white)."
    text = "Corner radius %.1f%% of the shorter side = %.0f px on a %s picture" % (radius_percent, r, size_text(width, height))
    if transparent:
        return text + "; the corners are see-through (alpha channel added), the background colour is not used."
    return text + "; the cut-off corners are painted with the background colour."


class SYRoundedCorners:
    DESCRIPTION = "Rounds the corners of a picture. The cut-off corners are painted with a background colour and also given as a mask. Switch on transparent_corners to get an alpha channel instead of a painted corner."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to round the corners of."}),
                "radius_percent": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 50.0, "step": 0.5, "tooltip": "Corner size as a percent of the shorter side. 50 makes a circle or pill."}),
                "background": ("STRING", {"default": DEFAULT_BACKGROUND, "multiline": False, "tooltip": "Colour painted in the cut-off corners, as 3 or 6 hex digits."}),
            },
            "optional": {
                "transparent_corners": ("BOOLEAN", {"default": False, "tooltip": "On: keep the corners see-through (adds an alpha channel) instead of painting the background colour."}),
            },
        }

    def run(self, image, radius_percent, background, transparent_corners=False):
        import torch

        need_image(image)
        need_nonempty(image.shape)
        check_percent(radius_percent)
        bg = parse_hex(background, "background")
        b, h, w, c = image.shape
        r = radius_pixels(radius_percent, w, h)
        info = corner_info(radius_percent, int(w), int(h), bool(transparent_corners))
        if r <= 0.0:
            return (image, torch.ones((b, h, w), dtype=image.dtype, device=image.device), info)
        r = min(r, min(w, h) / 2.0)
        py = (torch.arange(h, dtype=torch.float32, device=image.device) + 0.5)[:, None]
        px = (torch.arange(w, dtype=torch.float32, device=image.device) + 0.5)[None, :]
        qx = (px - w / 2.0).abs() - (w / 2.0 - r)
        qy = (py - h / 2.0).abs() - (h / 2.0 - r)
        outside = torch.sqrt(qx.clamp(min=0.0) ** 2 + qy.clamp(min=0.0) ** 2)
        d = outside + torch.maximum(qx, qy).clamp(max=0.0) - r
        cov = (0.5 - d).clamp(0.0, 1.0)  # (H, W)
        bgt = torch.tensor(bg, dtype=torch.float32, device=image.device)
        rgb = image[..., :3].to(torch.float32)
        cov4 = cov[None, :, :, None]
        mask = cov.to(image.dtype)[None].repeat(b, 1, 1).contiguous()
        if transparent_corners:
            if c > 3:
                alpha = image[..., 3:4].to(torch.float32) * cov4
            else:
                alpha = cov4.expand(b, h, w, 1)
            return (torch.cat([image[..., :3], alpha.to(image.dtype)], dim=-1).contiguous(), mask, info)
        out = image.clone()
        out[..., :3] = (rgb * cov4 + bgt * (1.0 - cov4)).to(image.dtype)
        return (out, mask, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RoundedCorners", SYRoundedCorners)
NODE_DISPLAY_NAME_MAPPINGS["SYRoundedCorners"] = "Rounded Corners SY"
