"""Dehaze SY: remove haze or fog by stretching contrast and colour where the picture looks hazy."""
try:
    from ._sy_common import category, register
    from . import _sy_ae_common as ae
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_ae_common as ae

WORK_SIZE = 768  # the haze map is smooth, so it is worked out on a copy with this long side


def estimate_airlight(values):
    """Pure function. Haze brightness: the mean of the brightest 0.1 percent of the given dark-channel values (at least one value)."""
    vals = sorted(float(v) for v in values)
    if not vals:
        raise ValueError("no pixel values to measure the haze brightness from")
    k = max(1, int(len(vals) * 0.001))
    return sum(vals[-k:]) / k


def transmission_floor(t, floor=0.1):
    """Pure function. Never let the see-through amount fall below floor, so dark spots are not blown up."""
    ae.check_range("floor", floor, 0.0, 1.0)
    return max(float(t), float(floor))


def dehaze_tensor(image, amount, patch, sky_protect, saturation_back):
    import torch
    import torch.nn.functional as F

    ae.check_range("amount", amount, 0.0, 1.0)
    ae.check_range("patch", patch, 3, 61)
    ae.check_range("sky_protect", sky_protect, 0.0, 1.0)
    ae.check_range("saturation_back", saturation_back, 0.0, 1.0)
    if int(patch) % 2 == 0:
        raise ValueError("patch must be an odd number (3, 5, 7 ... 61), got %d. Change it by one" % int(patch))
    x, was3 = ae.prep_image(image)
    if amount == 0:
        return image.clone()
    rgb = x[..., :3]
    nchw = rgb.permute(0, 3, 1, 2).clamp(0.0, 1.0)
    h, w = nchw.shape[2], nchw.shape[3]
    s = min(1.0, WORK_SIZE / float(max(h, w)))
    small = F.interpolate(nchw, scale_factor=s, mode="area") if s < 1.0 else nchw
    sh, sw = small.shape[2], small.shape[3]
    ps = max(3, int(round(int(patch) * s)))
    if ps % 2 == 0:
        ps += 1
    ps = min(ps, max(3, (min(sh, sw) // 2) * 2 - 1))
    dark = small.amin(dim=1, keepdim=True)
    dark = -F.max_pool2d(-dark, ps, stride=1, padding=ps // 2)
    b = dark.shape[0]
    flat = dark.reshape(b, -1)
    k = max(1, int(flat.shape[1] * 0.001))
    top = flat.topk(k, dim=1)
    a_scalar = top.values.mean(dim=1).clamp_min(0.05).view(b, 1, 1, 1)
    idx = top.indices
    sflat = small.reshape(b, 3, -1)
    a_rgb = torch.stack([sflat[i][:, idx[i]].mean(dim=1) for i in range(b)], dim=0).view(b, 3, 1, 1).clamp_min(0.05)
    t = 1.0 - float(amount) * dark / a_scalar
    sky = ((dark / a_scalar - 0.88) / 0.12).clamp(0.0, 1.0)
    sky = sky * sky * (3.0 - 2.0 * sky)
    t = t + (1.0 - t) * sky * float(sky_protect)
    t = ae.blur_nchw(t, max(0.5, ps / 2.0)).clamp(0.0, 1.0).clamp_min(0.1)
    if (sh, sw) != (h, w):
        t = F.interpolate(t, size=(h, w), mode="bilinear", align_corners=False).clamp_min(0.1)
    res = (nchw - a_rgb) / t + a_rgb
    res = res.permute(0, 2, 3, 1)
    grey = ae.luma_of(res)
    res = grey + (res - grey) * (1.0 + 0.5 * float(saturation_back))
    out = x.clone()
    out[..., :3] = res
    return ae.finish_image(out, image, was3)


class SYDehaze:
    DESCRIPTION = ("Removes haze or fog by stretching contrast and colour in the hazy areas. "
                   "Sky protection keeps a very bright sky from turning dark or blue. Amount 0 does nothing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE", {"tooltip": "The hazy picture or pictures."}),
            "amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How much haze to remove. 0 does nothing."}),
            "patch": ("INT", {"default": 15, "min": 3, "max": 61, "step": 2, "tooltip": "Size of the area used to find haze, an odd number. Bigger is smoother."}),
            "sky_protect": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Keeps very bright sky from going dark or blue."}),
            "saturation_back": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Adds colour back after the haze is gone."}),
        }}

    def run(self, image, amount, patch, sky_protect, saturation_back):
        return (dehaze_tensor(image, float(amount), int(patch), float(sky_protect), float(saturation_back)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Dehaze", SYDehaze)
NODE_DISPLAY_NAME_MAPPINGS["SYDehaze"] = "Dehaze SY"
