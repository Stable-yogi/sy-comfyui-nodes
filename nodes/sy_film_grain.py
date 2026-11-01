"""Film Grain SY: adds seeded film grain to a picture, grey or coloured, fine or coarse."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d2_common as d2

RESPONSES = ("even", "midtones")


def grain_grid_size(height, width, size):
    """Pure function. Grain is made on a small grid and enlarged: returns (grid_h, grid_w) for a grain `size` in pixels."""
    if size < 1:
        raise ValueError("grain size must be at least 1, got %s" % size)
    if min(height, width) < 1:
        raise ValueError("picture size must be at least 1x1")
    return (max(1, -(-int(height) // int(size))), max(1, -(-int(width) // int(size))))


def seeded_noise(seed, count):
    """Pure function. `count` bell-curve numbers (mean 0, spread 1) that depend only on the seed."""
    import random

    rng = random.Random(int(seed))
    return [rng.gauss(0.0, 1.0) for _ in range(count)]


def add_grain_value(value, noise, strength):
    """Pure function. Value 0..1 plus noise times strength, kept inside 0..1."""
    v = value + noise * strength
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def check_response(response):
    if response not in RESPONSES:
        raise ValueError("response must be one of: %s, got %r" % (", ".join(RESPONSES), response))


def grain_weight(value, response):
    """Pure function. How much grain a pixel of brightness `value` (0..1) gets: 1 for even, 4v(1-v) for midtones
    (like real film: little grain in pure black and pure white, most in the middle greys)."""
    check_response(response)
    v = 0.0 if value < 0.0 else 1.0 if value > 1.0 else value
    return 1.0 if response == "even" else 4.0 * v * (1.0 - v)


def grain_info(strength, size, seed, color_grain, response, animated, frames, width, height, note=""):
    """Pure function. One plain line about the grain that was added."""
    if strength <= 0.0:
        return "Strength 0: no grain added, the picture is unchanged."
    parts = ["Added %s grain, strength %g, size %d px, seed %d, %s response" % ("colour" if color_grain else "grey", strength, size, seed, response)]
    if frames > 1:
        parts.append("%s on all %d frames" % ("different grain" if animated else "the same grain", frames))
    parts.append("picture %s" % d2.size_text(width, height))
    parts.append(note)
    return d2.join_info(parts) + "."


class SYFilmGrain:
    DESCRIPTION = ("Adds film grain. The same seed always gives the same grain. Choose grey or colour grain and how coarse it is. "
                   "Midtones response keeps pure black and white clean, like real film. Add a mask to grain only one area.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to add grain to."}),
                "strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How visible the grain is. 0 changes nothing."}),
                "size": ("INT", {"default": 1, "min": 1, "max": 32, "tooltip": "Grain size in pixels. 1 is fine grain, bigger is coarse."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 32 - 1, "tooltip": "Number that fixes the grain pattern. Change it for a new pattern."}),
                "color_grain": ("BOOLEAN", {"default": False, "tooltip": "On gives coloured grain, off gives grey grain."}),
            },
            "optional": {
                "response": (list(RESPONSES), {"default": "even", "tooltip": "even: same grain everywhere. midtones: less in pure black and white, like real film."}),
                "animated": ("BOOLEAN", {"default": True, "tooltip": "On: every frame of a batch gets its own grain. Off: all frames get the same grain."}),
                "mask": ("MASK", {"tooltip": "Optional. Add grain only where this mask is white. A different size is stretched to fit."}),
            },
        }

    def run(self, image, strength, size, seed, color_grain, response="even", animated=True, mask=None):
        import torch
        import torch.nn.functional as F

        need_image(image)
        check_response(response)
        if strength < 0:
            raise ValueError("strength cannot be negative")
        b, h, w, c = image.shape
        if strength == 0:
            return (image, grain_info(0, size, seed, color_grain, response, animated, b, w, h))
        gh, gw = grain_grid_size(h, w, size)
        gen = torch.Generator(device="cpu")
        gen.manual_seed(int(seed))
        rgb = min(c, 3)
        planes = rgb if color_grain else 1
        noise = torch.randn((b if animated else 1, planes, gh, gw), generator=gen, dtype=torch.float32)
        if size > 1:
            noise = F.interpolate(noise, size=(gh * size, gw * size), mode="nearest")
        noise = noise[:, :, :h, :w].permute(0, 2, 3, 1).to(image.device, image.dtype)
        amount = noise * strength
        if response == "midtones":
            v = image[..., :rgb].clamp(0.0, 1.0)
            amount = amount * (4.0 * v * (1.0 - v))
        out = image.clone()
        out[..., :rgb] = (image[..., :rgb] + amount).clamp(0.0, 1.0)
        out, note = d2.t_apply_with_mask(image, out, mask)
        return (out, grain_info(strength, size, seed, color_grain, response, animated, b, w, h, note))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FilmGrain", SYFilmGrain)
NODE_DISPLAY_NAME_MAPPINGS["SYFilmGrain"] = "Film Grain SY"
