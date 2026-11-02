"""Chromatic Aberration SY: lens colour fringes. Red drifts outward, blue inward, more toward the edges."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def channel_scales(strength, max_radius):
    """Pure function. (red_scale, blue_scale): how much each colour is magnified around the centre.
    A point at max_radius moves by `strength` pixels: red outward (scale above 1), blue inward (below 1)."""
    if strength < 0:
        raise ValueError("strength cannot be negative, got %s" % strength)
    if max_radius <= 0:
        raise ValueError("max_radius must be above 0, got %s" % max_radius)
    k = float(strength) / float(max_radius)
    return 1.0 + k, max(0.01, 1.0 - k)


def far_corner_radius(width, height, cx, cy):
    """Pure function. Distance in pixels from the centre point to the farthest corner."""
    px, py = cx * width, cy * height
    return max(1e-6, max(((x - px) ** 2 + (y - py) ** 2) ** 0.5 for x in (0, width) for y in (0, height)))


def aberrate(image, strength, centre_x, centre_y):
    """Torch [B,H,W,C]. Resamples the red and blue channels around the centre; green and extra channels stay."""
    import torch
    import torch.nn.functional as F

    if not (0.0 <= centre_x <= 1.0 and 0.0 <= centre_y <= 1.0):
        raise ValueError("centre_x and centre_y must be between 0 and 1")
    if strength <= 0 or image.shape[3] < 3:
        return image
    b, h, w, c = image.shape
    r_scale, b_scale = channel_scales(strength, far_corner_radius(w, h, centre_x, centre_y))
    ys = torch.arange(h, dtype=torch.float32, device=image.device) + 0.5
    xs = torch.arange(w, dtype=torch.float32, device=image.device) + 0.5
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    cx, cy = centre_x * w, centre_y * h

    def grid(scale):
        sx = cx + (gx - cx) / scale
        sy = cy + (gy - cy) / scale
        g = torch.stack([sx / w * 2.0 - 1.0, sy / h * 2.0 - 1.0], dim=-1)
        return g.unsqueeze(0).expand(b, h, w, 2)

    chan = image.permute(0, 3, 1, 2).float()
    red = F.grid_sample(chan[:, 0:1], grid(r_scale), mode="bilinear", padding_mode="border", align_corners=False)
    blue = F.grid_sample(chan[:, 2:3], grid(b_scale), mode="bilinear", padding_mode="border", align_corners=False)
    out = chan.clone()
    out[:, 0:1], out[:, 2:3] = red, blue
    return out.permute(0, 2, 3, 1).to(image.dtype).contiguous()


class SYChromaticAberration:
    DESCRIPTION = ("Adds the colour fringes of a cheap lens: red slides outward and blue inward, "
                   "more and more toward the edges. Strength 0 leaves the picture as it is.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture or pictures to give colour fringes."}),
            "strength": ("FLOAT", {"default": 4.0, "min": 0.0, "max": 20.0, "step": 0.1, "tooltip": "How many pixels red and blue drift apart at the far corner. 0 does nothing."}),
            "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the fringes start, left to right. 0.5 is the middle."}),
            "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Where the fringes start, top to bottom. 0.5 is the middle."}),
        }}

    def run(self, image, strength, centre_x, centre_y):
        return (aberrate(image, strength, centre_x, centre_y),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ChromaticAberration", SYChromaticAberration)
NODE_DISPLAY_NAME_MAPPINGS["SYChromaticAberration"] = "Chromatic Aberration SY"
