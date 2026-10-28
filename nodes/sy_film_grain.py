"""Film Grain SY: adds seeded film grain to a picture, grey or coloured, fine or coarse."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


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


class SYFilmGrain:
    DESCRIPTION = "Adds film grain. The same seed always gives the same grain. Choose grey or colour grain and how coarse it is."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to add grain to."}),
                "strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How visible the grain is. 0 changes nothing."}),
                "size": ("INT", {"default": 1, "min": 1, "max": 32, "tooltip": "Grain size in pixels. 1 is fine grain, bigger is coarse."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 32 - 1, "tooltip": "Number that fixes the grain pattern. Change it for a new pattern."}),
                "color_grain": ("BOOLEAN", {"default": False, "tooltip": "On gives coloured grain, off gives grey grain."}),
            }
        }

    def run(self, image, strength, size, seed, color_grain):
        import torch
        import torch.nn.functional as F

        need_image(image)
        if strength < 0:
            raise ValueError("strength cannot be negative")
        b, h, w, c = image.shape
        gh, gw = grain_grid_size(h, w, size)
        gen = torch.Generator(device="cpu")
        gen.manual_seed(int(seed))
        rgb = min(c, 3)
        planes = rgb if color_grain else 1
        noise = torch.randn((b, planes, gh, gw), generator=gen, dtype=torch.float32)
        if size > 1:
            noise = F.interpolate(noise, size=(gh * size, gw * size), mode="nearest")
        noise = noise[:, :, :h, :w].permute(0, 2, 3, 1).to(image.device, image.dtype)
        out = image.clone()
        out[..., :rgb] = (image[..., :rgb] + noise * strength).clamp(0.0, 1.0)
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FilmGrain", SYFilmGrain)
NODE_DISPLAY_NAME_MAPPINGS["SYFilmGrain"] = "Film Grain SY"
