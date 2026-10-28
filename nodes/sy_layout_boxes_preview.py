"""Layout Boxes Preview SY: draws the layout boxes with their labels over a picture or a blank canvas."""
try:
    from ._sy_common import category, register
    from ._sy_layout import COLOUR_NAMES, COLOUR_RGB, MAX_SIDE, box_rect, parse_boxes
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import COLOUR_NAMES, COLOUR_RGB, MAX_SIDE, box_rect, parse_boxes

BLANK_RGB = (40, 40, 44)


def plan_boxes(text, canvas_w, canvas_h):
    """Pure function. Returns a list of (rect, rgb, label) ready to draw. Boxes outside the canvas are clipped or skipped."""
    plan = []
    for i, box in enumerate(parse_boxes(text)):
        try:
            rect = box_rect(box, canvas_w, canvas_h)
        except (KeyError, TypeError, ValueError, OverflowError):
            raise ValueError("box %d needs numbers for x, y, w and h; run Layout JSON Check to see what is wrong" % (i + 1))
        if rect is None:
            continue
        colour = box.get("colour", box.get("color"))
        rgb = COLOUR_RGB.get(colour, COLOUR_RGB[COLOUR_NAMES[0]]) if isinstance(colour, str) else COLOUR_RGB[COLOUR_NAMES[0]]
        label = box.get("label", "")
        plan.append((rect, rgb, label if isinstance(label, str) else ""))
    return plan


def draw_plan(pil_image, plan, line_width, show_labels):
    """Draw the plan on a PIL image (PIL is imported here, not at the top)."""
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.load_default()
    for (left, top, right, bottom), rgb, label in plan:
        draw.rectangle([left, top, right - 1, bottom - 1], outline=rgb, width=line_width)
        if show_labels and label:
            tb = draw.textbbox((0, 0), label, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            ty = max(0, top - th - 4)
            draw.rectangle([left, ty, left + tw + 6, ty + th + 4], fill=rgb)
            draw.text((left + 3, ty + 1 - tb[1]), label, fill=COLOUR_RGB["black"], font=font)
    return pil_image


class SYLayoutBoxesPreview:
    DESCRIPTION = "Draws layout boxes and their labels over a picture, or over a blank canvas when no picture is connected."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "layout_boxes": ("STRING", {"default": "", "multiline": True, "tooltip": "The box list as JSON text. Connect a Layout Box or Merge node, or paste it."}),
                "line_width": ("INT", {"default": 3, "min": 1, "max": 32, "tooltip": "Thickness of the box outline in pixels."}),
                "show_labels": ("BOOLEAN", {"default": True, "tooltip": "Write each box label above its top left corner."}),
                "blank_width": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "tooltip": "Width of the blank canvas. Used only when no picture is connected."}),
                "blank_height": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "tooltip": "Height of the blank canvas. Used only when no picture is connected."}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Optional picture to draw on. Leave it out to use a blank canvas."}),
            },
        }

    def run(self, layout_boxes, line_width, show_labels, blank_width, blank_height, image=None):
        import numpy as np
        import torch
        from PIL import Image

        if image is None:
            frames = [np.full((blank_height, blank_width, 3), BLANK_RGB, dtype=np.uint8)]
        else:
            arr = (image[..., :3].clamp(0.0, 1.0) * 255.0 + 0.5).to(torch.uint8).cpu().numpy()
            frames = [arr[i] for i in range(arr.shape[0])]
        out = []
        for frame in frames:
            h, w = frame.shape[0], frame.shape[1]
            plan = plan_boxes(layout_boxes, w, h)
            pil = draw_plan(Image.fromarray(frame, "RGB"), plan, line_width, show_labels)
            out.append(torch.from_numpy(np.asarray(pil, dtype=np.uint8).copy()).float() / 255.0)
        return (torch.stack(out, dim=0),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBoxesPreview", SYLayoutBoxesPreview)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesPreview"] = "Layout Boxes Preview SY"
