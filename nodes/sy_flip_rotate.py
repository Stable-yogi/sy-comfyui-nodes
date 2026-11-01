"""Flip Rotate SY: mirrors a picture left-right or up-down and turns it by 90, 180 or 270 degrees."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image
    import _sy_d2_common as d2

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


def result_size(width, height, turn):
    """Pure function. Picture size after the turn: a quarter turn swaps width and height."""
    return (height, width) if turn_steps(turn) % 2 else (width, height)


def flip_info(width, height, flip_h, flip_v, turn, mask_given=False):
    """Pure function. One plain line: what was done and the new size."""
    steps = []
    if flip_h:
        steps.append("mirrored left to right")
    if flip_v:
        steps.append("mirrored top to bottom")
    if turn_steps(turn):
        steps.append("turned %s degrees clockwise" % turn.replace(" clockwise", ""))
    if not steps:
        return "Nothing selected: the picture was passed through unchanged (%s)." % d2.size_text(width, height)
    nw, nh = result_size(width, height, turn)
    text = "%s; %s -> %s" % (", then ".join(steps).capitalize(), d2.size_text(width, height), d2.size_text(nw, nh))
    return text + ("; the mask was changed the same way." if mask_given else ".")


class SYFlipRotate:
    DESCRIPTION = ("Mirrors a picture and turns it in steps of 90 degrees. The mirror is done first, then the turn. "
                   "Connect a mask to change it the same way, so picture and mask stay matched.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to flip or turn."}),
                "flip_horizontal": ("BOOLEAN", {"default": False, "tooltip": "Mirror left to right."}),
                "flip_vertical": ("BOOLEAN", {"default": False, "tooltip": "Mirror top to bottom."}),
                "rotate": (list(TURNS), {"default": "none", "tooltip": "Turn the picture clockwise by this much after any flip."}),
            },
            "optional": {
                "mask": ("MASK", {"tooltip": "Optional. Flipped and turned exactly like the picture. Must have the same size as the picture."}),
            },
        }

    @staticmethod
    def _apply(t, flip_horizontal, flip_vertical, steps):
        import torch

        if flip_horizontal:
            t = torch.flip(t, dims=[2])
        if flip_vertical:
            t = torch.flip(t, dims=[1])
        if steps:
            t = torch.rot90(t, k=-steps, dims=(1, 2))  # negative k is clockwise
        return t.contiguous()

    def run(self, image, flip_horizontal, flip_vertical, rotate, mask=None):
        import torch

        need_image(image)
        steps = turn_steps(rotate)
        h, w = image.shape[1], image.shape[2]
        out = self._apply(image, flip_horizontal, flip_vertical, steps)
        if mask is None:
            out_mask = torch.zeros((out.shape[0], out.shape[1], out.shape[2]), dtype=torch.float32)
        else:
            mb, mh, mw = d2.shape_of_mask(tuple(mask.shape))
            if (mh, mw) != (h, w):
                raise ValueError("the mask is %s but the picture is %s: resize one of them first so they match"
                                 % (d2.size_text(mw, mh), d2.size_text(w, h)))
            m3 = mask.float() if mask.dim() == 3 else mask.float().unsqueeze(0)
            out_mask = self._apply(m3, flip_horizontal, flip_vertical, steps)
        return (out, out_mask, flip_info(w, h, flip_horizontal, flip_vertical, rotate, mask is not None))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FlipRotate", SYFlipRotate)
NODE_DISPLAY_NAME_MAPPINGS["SYFlipRotate"] = "Flip Rotate SY"
