"""Flip Rotate SY: mirrors a picture left-right or up-down and turns it by 90, 180 or 270 degrees."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image

TURNS = ("none", "90 clockwise", "180", "270 clockwise")


def turn_steps(turn):
    if turn not in TURNS:
        raise ValueError("unknown rotation %r, pick one of: %s" % (turn, ", ".join(TURNS)))
    return TURNS.index(turn)  # number of clockwise quarter turns


def flip_rotate_grid(grid, flip_h, flip_v, turn):
    """Pure function on nested lists [H][W]. Flips first, then turns clockwise."""
    steps = turn_steps(turn)
    g = [list(r) for r in grid]
    if flip_h:
        g = [r[::-1] for r in g]
    if flip_v:
        g = g[::-1]
    for _ in range(steps):  # one clockwise quarter turn: rows become columns, read bottom to top
        g = [list(col) for col in zip(*g[::-1])]
    return g


class SYFlipRotate:
    DESCRIPTION = "Mirrors a picture and turns it in steps of 90 degrees. The mirror is done first, then the turn."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to flip or turn."}),
                "flip_horizontal": ("BOOLEAN", {"default": False, "tooltip": "Mirror left to right."}),
                "flip_vertical": ("BOOLEAN", {"default": False, "tooltip": "Mirror top to bottom."}),
                "rotate": (list(TURNS), {"default": "none", "tooltip": "Turn the picture clockwise by this much after any flip."}),
            }
        }

    def run(self, image, flip_horizontal, flip_vertical, rotate):
        import torch

        need_image(image)
        steps = turn_steps(rotate)
        out = image
        if flip_horizontal:
            out = torch.flip(out, dims=[2])
        if flip_vertical:
            out = torch.flip(out, dims=[1])
        if steps:
            out = torch.rot90(out, k=-steps, dims=(1, 2))  # negative k is clockwise
        return (out.contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FlipRotate", SYFlipRotate)
NODE_DISPLAY_NAME_MAPPINGS["SYFlipRotate"] = "Flip Rotate SY"
