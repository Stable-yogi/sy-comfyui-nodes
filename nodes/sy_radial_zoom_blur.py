"""Radial Zoom Blur SY: speed-tunnel blur that smears pixels along lines through a chosen centre."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_settings(amount, samples, centre_x, centre_y):
    if not 0.0 <= float(amount) <= 0.5:
        raise ValueError("amount must be between 0 and 0.5, got %r" % (amount,))
    if not 4 <= int(samples) <= 32:
        raise ValueError("samples must be between 4 and 32, got %r" % (samples,))
    if not 0.0 <= float(centre_x) <= 1.0 or not 0.0 <= float(centre_y) <= 1.0:
        raise ValueError("centre_x and centre_y must be between 0 and 1, got %r and %r" % (centre_x, centre_y))


def zoom_scales(amount, samples):
    """Pure function. Evenly spaced scale factors from 1.0 down to 1 - amount (samples values)."""
    if not 0.0 <= amount < 1.0:
        raise ValueError("amount must be at least 0 and below 1, got %r" % (amount,))
    if samples < 2:
        raise ValueError("samples must be at least 2, got %r" % (samples,))
    return [1.0 - amount * i / (samples - 1) for i in range(int(samples))]


def zoom_blur_tensor(image, amount, samples, centre_x, centre_y):
    """Torch. image [B,H,W,C] float 0..1 -> new tensor of the same shape."""
    import torch
    import torch.nn.functional as F

    check_settings(amount, samples, centre_x, centre_y)
    if float(amount) == 0.0:
        return image.clone()
    height, width = image.shape[1], image.shape[2]
    x = image.float().permute(0, 3, 1, 2)
    ys = (torch.arange(height, dtype=torch.float32, device=x.device) + 0.5) / height * 2.0 - 1.0
    xs = (torch.arange(width, dtype=torch.float32, device=x.device) + 0.5) / width * 2.0 - 1.0
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    cx, cy = float(centre_x) * 2.0 - 1.0, float(centre_y) * 2.0 - 1.0
    total = torch.zeros_like(x)
    scales = zoom_scales(float(amount), int(samples))
    for s in scales:
        grid = torch.stack([cx + (gx - cx) * s, cy + (gy - cy) * s], dim=-1)[None].expand(x.shape[0], -1, -1, -1)
        total = total + F.grid_sample(x, grid, mode="bilinear", padding_mode="border", align_corners=False)
    return (total / len(scales)).clamp(0.0, 1.0).permute(0, 2, 3, 1).contiguous()


class SYRadialZoomBlur:
    DESCRIPTION = ("Speed-tunnel blur. Pixels are smeared along lines going toward a chosen centre, "
                   "stronger toward the edges and untouched at the centre itself.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The picture (or batch of pictures) to blur."}),
            "amount": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 0.5, "step": 0.005, "tooltip": "How far the smear reaches, as a share of the distance to the centre. 0 is no blur."}),
            "samples": ("INT", {"default": 12, "min": 4, "max": 32, "tooltip": "Number of copies averaged. More is smoother but slower."}),
            "centre_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Horizontal position of the blur centre. 0 is left, 1 is right."}),
            "centre_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Vertical position of the blur centre. 0 is top, 1 is bottom."}),
        }}

    def run(self, image, amount, samples, centre_x, centre_y):
        return (zoom_blur_tensor(image, amount, samples, centre_x, centre_y),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RadialZoomBlur", SYRadialZoomBlur)
NODE_DISPLAY_NAME_MAPPINGS["SYRadialZoomBlur"] = "Radial Zoom Blur SY"
