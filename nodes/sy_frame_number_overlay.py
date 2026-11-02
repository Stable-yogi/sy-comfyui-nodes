"""Frame Number Overlay SY: burns the frame number and time into a corner of every frame."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex

SHOWS = ["frame", "time", "frame and time"]
CORNERS = ["top left", "top right", "bottom left", "bottom right"]
DEFAULT_TEXT = "#" + "ffffff"
DEFAULT_BOX = "#" + "000000"


def label_text(index, fps, start_number, show):
    """Pure function. Text for one frame, for example 'f 0012 | 0.50 s'. Time counts from the first frame."""
    if show not in SHOWS:
        raise ValueError("show must be one of %s, got %r" % (", ".join(SHOWS), show))
    if float(fps) <= 0:
        raise ValueError("fps must be above 0, got %r" % fps)
    frame = "f %04d" % (int(start_number) + int(index))
    secs = "%.2f s" % (int(index) / float(fps))
    if show == "frame":
        return frame
    if show == "time":
        return secs
    return frame + " | " + secs


def corner_origin(corner, w, h, tw, th, margin=4):
    """Pure function. Top-left (x, y) of a box of size tw x th placed in a corner of a w x h picture."""
    if corner not in CORNERS:
        raise ValueError("corner must be one of %s, got %r" % (", ".join(CORNERS), corner))
    x = margin if "left" in corner else w - tw - margin
    y = margin if "top" in corner else h - th - margin
    return max(0, x), max(0, y)


class SYFrameNumberOverlay:
    DESCRIPTION = ("Burns the frame number, and optionally the time, into a corner of every frame. "
                   "Useful for checking cuts and timing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The clip as a batch of frames."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 240.0, "step": 0.5, "tooltip": "Frames per second, used to work out the time."}),
                "start_number": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "The number shown on the first frame."}),
                "show": (SHOWS, {"default": "frame and time", "tooltip": "What to print: the frame number, the time, or both."}),
                "corner": (CORNERS, {"default": "top left", "tooltip": "Which corner of the picture holds the label."}),
                "size": ("INT", {"default": 28, "min": 8, "max": 200, "tooltip": "Text height in pixels."}),
                "text_colour": ("STRING", {"default": DEFAULT_TEXT, "multiline": False, "tooltip": "Text colour, as 3 or 6 hex digits like a web colour."}),
                "box_colour": ("STRING", {"default": DEFAULT_BOX, "multiline": False, "tooltip": "Colour of the box behind the text, as hex digits."}),
            }
        }

    def run(self, images, fps, start_number, show, corner, size, text_colour, box_colour):
        import numpy as np
        import torch
        from PIL import Image, ImageDraw, ImageFont
        tc = tuple(int(round(v * 255)) for v in parse_hex(text_colour, "text_colour"))
        bc = tuple(int(round(v * 255)) for v in parse_hex(box_colour, "box_colour"))
        n, h, w, c = (int(s) for s in images.shape)
        if c not in (3, 4):
            raise ValueError("pictures need 3 or 4 colour channels, got %d" % c)
        try:
            font = ImageFont.load_default(int(size))
        except TypeError:
            font = ImageFont.load_default()
        arr = (images.detach().cpu().clamp(0, 1) * 255.0).round().to(torch.uint8).numpy()
        pad = max(2, int(size) // 6)
        mode = "RGBA" if c == 4 else "RGB"
        extra = (255,) if c == 4 else ()
        out = np.empty_like(arr)
        for i in range(n):
            text = label_text(i, fps, start_number, show)
            im = Image.fromarray(arr[i], mode)
            d = ImageDraw.Draw(im)
            l, t, r, b = d.textbbox((0, 0), text, font=font)
            tw, th = r - l + 2 * pad, b - t + 2 * pad
            x, y = corner_origin(corner, w, h, tw, th)
            d.rectangle([x, y, x + tw, y + th], fill=bc + extra)
            d.text((x + pad - l, y + pad - t), text, font=font, fill=tc + extra)
            out[i] = np.asarray(im)
        res = torch.from_numpy(out.astype(np.float32) / 255.0).to(images.dtype)
        return (res,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameNumberOverlay", SYFrameNumberOverlay)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameNumberOverlay"] = "Frame Number Overlay SY"
