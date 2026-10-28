"""Colour Match SY: shifts the colours of a picture towards a reference picture (mean and spread per channel)."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def mean_std(values):
    """Pure function. Returns (mean, standard deviation) of a list of numbers."""
    if not values:
        raise ValueError("cannot measure an empty picture")
    n = len(values)
    mean = sum(values) / float(n)
    var = sum((v - mean) ** 2 for v in values) / float(n)
    return mean, var ** 0.5


def match_values(values, ref_mean, ref_std, strength):
    """Pure function. Moves the list so its mean and spread approach the reference. Result stays inside 0..1."""
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be between 0 and 1, got %s" % strength)
    mean, std = mean_std(values)
    scale = (ref_std / std) if std > 1e-6 else 1.0
    out = []
    for v in values:
        matched = (v - mean) * scale + ref_mean
        r = v * (1.0 - strength) + matched * strength
        out.append(0.0 if r < 0.0 else 1.0 if r > 1.0 else r)
    return out


class SYColourMatch:
    DESCRIPTION = "Makes a picture look like the colours of a reference picture. Good for keeping a series of pictures in one look."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to change."}),
                "reference": ("IMAGE", {"tooltip": "The picture whose colours are copied. A batch is matched one to one, then repeats."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How far to move towards the reference. 0 changes nothing, 1 is a full match."}),
            }
        }

    def run(self, image, reference, strength):
        import torch

        need_image(image)
        need_image(reference)
        if not 0.0 <= strength <= 1.0:
            raise ValueError("strength must be between 0 and 1, got %s" % strength)
        rgb = min(image.shape[3], reference.shape[3], 3)
        if reference.shape[0] != image.shape[0]:
            reference = reference[[i % reference.shape[0] for i in range(image.shape[0])]]
        src = image[..., :rgb]
        ref = reference[..., :rgb]
        s_mean = src.mean(dim=(1, 2), keepdim=True)
        s_std = src.std(dim=(1, 2), keepdim=True, unbiased=False)
        r_mean = ref.mean(dim=(1, 2), keepdim=True)
        r_std = ref.std(dim=(1, 2), keepdim=True, unbiased=False)
        scale = torch.where(s_std > 1e-6, r_std / s_std.clamp_min(1e-6), torch.ones_like(s_std))
        matched = (src - s_mean) * scale + r_mean
        out = image.clone()
        out[..., :rgb] = (src * (1.0 - strength) + matched * strength).clamp(0.0, 1.0)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourMatch", SYColourMatch)
NODE_DISPLAY_NAME_MAPPINGS["SYColourMatch"] = "Colour Match SY"
