"""Ken Burns SY: turns one picture into a slow zoom-and-pan clip."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

EASES = ["linear", "ease in out"]


def _ease(t, ease):
    if ease == "linear":
        return t
    if ease == "ease in out":
        return t * t * (3.0 - 2.0 * t)
    raise ValueError("ease must be one of %s, got %r" % (", ".join(EASES), ease))


def ken_burns_boxes(w, h, frames, zoom_start, zoom_end, pan_x, pan_y, ease):
    """Pure function. One (x0, y0, x1, y1) float box per frame, always inside the w x h picture.
    The box shrinks with the zoom. The view centre moves from -pan to +pan of the free space."""
    w, h, frames = int(w), int(h), int(frames)
    if w < 1 or h < 1:
        raise ValueError("picture size must be at least 1 x 1, got %d x %d" % (w, h))
    if frames < 2:
        raise ValueError("frames must be at least 2, got %d" % frames)
    for name, v in (("zoom_start", zoom_start), ("zoom_end", zoom_end)):
        if not (1.0 <= float(v) <= 4.0):
            raise ValueError("%s must be between 1 and 4, got %r" % (name, v))
    for name, v in (("pan_x", pan_x), ("pan_y", pan_y)):
        if not (-1.0 <= float(v) <= 1.0):
            raise ValueError("%s must be between -1 and 1, got %r" % (name, v))
    _ease(0.0, ease)
    boxes = []
    for i in range(frames):
        t = _ease(i / (frames - 1), ease)
        zoom = float(zoom_start) + (float(zoom_end) - float(zoom_start)) * t
        bw, bh = w / zoom, h / zoom
        move = 2.0 * t - 1.0  # -1 at the first frame, +1 at the last
        cx = w / 2.0 + float(pan_x) * move * (w - bw) / 2.0
        cy = h / 2.0 + float(pan_y) * move * (h - bh) / 2.0
        x0 = min(max(cx - bw / 2.0, 0.0), w - bw)
        y0 = min(max(cy - bh / 2.0, 0.0), h - bh)
        boxes.append((x0, y0, x0 + bw, y0 + bh))
    return boxes


class SYKenBurns:
    DESCRIPTION = ("Turns one picture into a slow zoom-and-pan clip. The output has the same size as the picture. "
                   "Only the first picture of a batch is used.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to animate. If it is a batch, the first picture is used."}),
                "frames": ("INT", {"default": 48, "min": 2, "max": 600, "tooltip": "How many frames the clip has."}),
                "zoom_start": ("FLOAT", {"default": 1.0, "min": 1.0, "max": 4.0, "step": 0.01, "tooltip": "Zoom at the first frame. 1 shows the whole picture."}),
                "zoom_end": ("FLOAT", {"default": 1.3, "min": 1.0, "max": 4.0, "step": 0.01, "tooltip": "Zoom at the last frame. Bigger means closer."}),
                "pan_x": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.05, "tooltip": "Sideways move. The view goes from minus this to plus this of the free space."}),
                "pan_y": ("FLOAT", {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.05, "tooltip": "Up and down move. Works like pan_x. Minus starts at the top."}),
                "ease": (EASES, {"default": "ease in out", "tooltip": "Linear moves at a steady pace. Ease in out starts and ends gently."}),
            }
        }

    def run(self, image, frames, zoom_start, zoom_end, pan_x, pan_y, ease):
        import torch
        import torch.nn.functional as F
        h, w = int(image.shape[1]), int(image.shape[2])
        boxes = ken_burns_boxes(w, h, frames, zoom_start, zoom_end, pan_x, pan_y, ease)
        src = image[0:1].permute(0, 3, 1, 2).to(torch.float32)  # [1,C,H,W]
        xs = (torch.arange(w, dtype=torch.float32) + 0.5) / w
        ys = (torch.arange(h, dtype=torch.float32) + 0.5) / h
        grids = []
        for (x0, y0, x1, y1) in boxes:
            gx = (x0 + xs * (x1 - x0)) / w * 2.0 - 1.0
            gy = (y0 + ys * (y1 - y0)) / h * 2.0 - 1.0
            grids.append(torch.stack([gx.view(1, w).expand(h, w), gy.view(h, 1).expand(h, w)], dim=-1))
        grid = torch.stack(grids, 0).to(src.device)
        out = F.grid_sample(src.expand(len(boxes), -1, -1, -1), grid, mode="bilinear",
                            padding_mode="border", align_corners=False)
        return (out.permute(0, 2, 3, 1).clamp(0.0, 1.0).to(image.dtype).contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "KenBurns", SYKenBurns)
NODE_DISPLAY_NAME_MAPPINGS["SYKenBurns"] = "Ken Burns SY"
