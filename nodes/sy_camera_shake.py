"""Camera Shake SY: gives every frame of a batch a smooth, repeatable hand-held shake (small shift and turn)."""
import math
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

EDGES = ("reflect", "border", "crop_zoom")
POINT_SPACING = 8.0  # frames between random control points at speed 1


def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def smooth_noise(count, speed, rng):
    """Pure function. `count` values in -1..1 from random control points joined with smoothstep."""
    points = int((count - 1) * speed / POINT_SPACING) + 3
    ctrl = [rng.uniform(-1.0, 1.0) for _ in range(points)]
    out = []
    for f in range(count):
        pos = f * speed / POINT_SPACING
        i = int(pos)
        w = smoothstep(pos - i)
        out.append(ctrl[i] * (1.0 - w) + ctrl[i + 1] * w)
    return out


def check_args(count, strength, rotation, speed):
    if int(count) < 1:
        raise ValueError("need at least 1 frame, got %d" % int(count))
    if float(strength) < 0:
        raise ValueError("strength cannot be negative, got %s" % strength)
    if float(rotation) < 0:
        raise ValueError("rotation cannot be negative, got %s" % rotation)
    if float(speed) <= 0:
        raise ValueError("speed must be above 0, got %s" % speed)


def shake_offsets(count, strength, rotation, speed, seed):
    """Pure function. List of (dx pixels, dy pixels, angle degrees), one per frame. Same seed = same shake."""
    check_args(count, strength, rotation, speed)
    rng = random.Random(int(seed))
    nx = smooth_noise(int(count), float(speed), rng)
    ny = smooth_noise(int(count), float(speed), rng)
    na = smooth_noise(int(count), float(speed), rng)
    return [(nx[i] * float(strength), ny[i] * float(strength), na[i] * float(rotation)) for i in range(int(count))]


def crop_zoom_factor(width, height, strength, rotation):
    """Pure function. Scale (1 or more) that hides every empty border for the largest shift and turn."""
    shift = 2.0 * float(strength) * max(1.0 / width, 1.0 / height)
    turn = math.radians(float(rotation)) * (max(width, height) / float(min(width, height)))
    return 1.0 + shift + turn


def check_edge(edge):
    if edge not in EDGES:
        raise ValueError("edge must be one of: %s, got %r" % (", ".join(EDGES), edge))


def shake_theta(dx, dy, angle, width, height, zoom=1.0):
    """Pure function. 2x3 matrix rows for torch affine_grid (output position -> input position, in -1..1 units)."""
    a = math.radians(angle)
    c, s = math.cos(a) / zoom, math.sin(a) / zoom
    return [[c, -s * height / float(width), dx * 2.0 / width],
            [s * width / float(height), c, dy * 2.0 / height]]


class SYCameraShake:
    DESCRIPTION = ("Adds a smooth hand-held camera shake to a batch of frames. Each frame moves and turns a little, "
                   "and the same seed always gives the same shake. crop_zoom enlarges slightly so no empty border shows.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to shake, in order."}),
                "strength": ("FLOAT", {"default": 6.0, "min": 0.0, "max": 500.0, "step": 0.1, "tooltip": "Biggest sideways or up-down shift in pixels."}),
                "rotation": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 45.0, "step": 0.05, "tooltip": "Biggest turn in degrees."}),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.05, "max": 20.0, "step": 0.05, "tooltip": "How fast the shake wobbles. Higher is more nervous."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Same seed gives the same shake."}),
                "edge": (list(EDGES), {"default": "reflect", "tooltip": "What fills the border: reflect mirrors, border stretches, crop_zoom enlarges so none shows."}),
            },
        }

    def run(self, images, strength, rotation, speed, seed, edge):
        import torch
        import torch.nn.functional as F

        check_edge(edge)
        if images.ndim != 4:
            raise ValueError("images must be shaped [batch, height, width, channels], got %s" % (tuple(images.shape),))
        count, h, w = int(images.shape[0]), int(images.shape[1]), int(images.shape[2])
        offs = shake_offsets(count, strength, rotation, speed, seed)
        zoom = crop_zoom_factor(w, h, strength, rotation) if edge == "crop_zoom" else 1.0
        theta = torch.tensor([shake_theta(dx, dy, ang, w, h, zoom) for dx, dy, ang in offs], dtype=torch.float32)
        src = images.to(torch.float32).permute(0, 3, 1, 2)
        grid = F.affine_grid(theta, list(src.shape), align_corners=False)
        mode = "reflection" if edge == "reflect" else "border"
        res = F.grid_sample(src, grid, mode="bilinear", padding_mode=mode, align_corners=False)
        out = res.permute(0, 2, 3, 1).clamp(0.0, 1.0).to(images.dtype)
        return (out, "Camera Shake: %d frames, up to %s px and %s degrees, speed %s, seed %d, edge %s" % (count, strength, rotation, speed, int(seed), edge))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CameraShake", SYCameraShake)
NODE_DISPLAY_NAME_MAPPINGS["SYCameraShake"] = "Camera Shake SY"
