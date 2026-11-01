"""Layout Boxes Preview SY: draws the layout boxes with their labels over a picture or a blank canvas."""
try:
    from ._sy_common import category, register
    from ._sy_layout import COLOUR_NAMES, COLOUR_RGB, MAX_SIDE, box_rect, parse_boxes
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import COLOUR_NAMES, COLOUR_RGB, MAX_SIDE, box_rect, parse_boxes

BLANK_RGB = (40, 40, 44)


def plan_numbered(text, canvas_w, canvas_h):
    """Pure function. Returns (plan, skipped). plan holds (rect, rgb, label, box_number) ready to draw; box_number counts from 1
    in the original list. skipped lists the box numbers that are fully outside the canvas and so not drawn."""
    plan = []
    skipped = []
    for i, box in enumerate(parse_boxes(text)):
        try:
            rect = box_rect(box, canvas_w, canvas_h)
        except (KeyError, TypeError, ValueError, OverflowError):
            raise ValueError("box %d needs numbers for x, y, w and h; run Layout JSON Check to see what is wrong" % (i + 1))
        if rect is None:
            skipped.append(i + 1)
            continue
        colour = box.get("colour", box.get("color"))
        rgb = COLOUR_RGB.get(colour, COLOUR_RGB[COLOUR_NAMES[0]]) if isinstance(colour, str) else COLOUR_RGB[COLOUR_NAMES[0]]
        label = box.get("label", "")
        plan.append((rect, rgb, label if isinstance(label, str) else "", i + 1))
    return plan, skipped


def plan_boxes(text, canvas_w, canvas_h):
    """Pure function. Returns a list of (rect, rgb, label) ready to draw. Boxes outside the canvas are clipped or skipped."""
    return [item[:3] for item in plan_numbered(text, canvas_w, canvas_h)[0]]


def preview_info(drawn, skipped, width, height):
    """Pure function. A plain line saying what was drawn and what was left out."""
    text = "Drew %d box%s on %dx%d." % (drawn, "" if drawn == 1 else "es", width, height)
    if skipped:
        text += " Not drawn because they are fully outside the picture: box %s." % ", ".join(str(n) for n in skipped)
    return text


def draw_plan(pil_image, plan, line_width, show_labels, fill_opacity=0.0, show_numbers=False):
    """Draw the plan on a PIL image (PIL is imported here, not at the top). Plan items are (rect, rgb, label) or (rect, rgb, label, number)."""
    from PIL import Image, ImageDraw, ImageFont

    if fill_opacity > 0:
        layer = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
        fill_draw = ImageDraw.Draw(layer)
        alpha = int(round(max(0.0, min(1.0, fill_opacity)) * 255))
        for item in plan:
            (left, top, right, bottom), rgb = item[0], item[1]
            fill_draw.rectangle([left, top, right - 1, bottom - 1], fill=tuple(rgb) + (alpha,))
        pil_image.paste(Image.alpha_composite(pil_image.convert("RGBA"), layer).convert("RGB"))
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.load_default()
    for item in plan:
        (left, top, right, bottom), rgb, label = item[0], item[1], item[2]
        if show_numbers and len(item) > 3:
            label = ("%d %s" % (item[3], label)).strip()
        draw.rectangle([left, top, right - 1, bottom - 1], outline=rgb, width=line_width)
        if (show_labels or show_numbers) and label:
            tb = draw.textbbox((0, 0), label, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            ty = max(0, top - th - 4)
            draw.rectangle([left, ty, left + tw + 6, ty + th + 4], fill=rgb)
            draw.text((left + 3, ty + 1 - tb[1]), label, fill=COLOUR_RGB["black"], font=font)
    return pil_image


class SYLayoutBoxesPreview:
    DESCRIPTION = "Draws layout boxes and their labels over a picture, or over a blank canvas when no picture is connected. Can number the boxes, tint them, and tells you which boxes fell outside the picture."
    CATEGORY = category("Editors")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

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
                "fill_opacity": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "Tint inside each box. 0 is outline only, 0.3 is a light tint, 1 is solid."}),
                "show_numbers": ("BOOLEAN", {"default": False, "tooltip": "Put the box number (1, 2, 3 ...) before its label, to match the numbers in check reports."}),
            },
        }

    def run(self, layout_boxes, line_width, show_labels, blank_width, blank_height, image=None, fill_opacity=0.0, show_numbers=False):
        import numpy as np
        import torch
        from PIL import Image

        if image is None:
            frames = [np.full((blank_height, blank_width, 3), BLANK_RGB, dtype=np.uint8)]
        else:
            arr = (image[..., :3].clamp(0.0, 1.0) * 255.0 + 0.5).to(torch.uint8).cpu().numpy()
            frames = [arr[i] for i in range(arr.shape[0])]
        out = []
        info = ""
        for frame in frames:
            h, w = frame.shape[0], frame.shape[1]
            plan, skipped = plan_numbered(layout_boxes, w, h)
            pil = draw_plan(Image.fromarray(frame, "RGB"), plan, line_width, show_labels, fill_opacity, show_numbers)
            out.append(torch.from_numpy(np.asarray(pil, dtype=np.uint8).copy()).float() / 255.0)
            if not info:
                info = preview_info(len(plan), skipped, w, h)
        return (torch.stack(out, dim=0), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LayoutBoxesPreview", SYLayoutBoxesPreview)
NODE_DISPLAY_NAME_MAPPINGS["SYLayoutBoxesPreview"] = "Layout Boxes Preview SY"
