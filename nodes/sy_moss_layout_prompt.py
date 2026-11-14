"""MOSS Layout Prompt SY: turns layout boxes (from Layout Box, Box Draw or Merge) into a MOSS-Image layout prompt.
Each box label says what goes in the box:
  "text: OPEN LATE | blue shop sign"  -> words written in the picture (words | how they look)
  "person: a woman in a grey coat"    -> a character
  "a red bicycle" or "object: ..."    -> an object
MOSS reads boxes as pixel numbers from the picture centre, y first (bbox_format yxyx). X-first boxes are ignored by
the model, so this node always writes y first."""
import json
import math

try:
    from ._sy_common import category, register
    from ._sy_layout import MAX_SIDE, parse_boxes
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_layout import MAX_SIDE, parse_boxes

KINDS = {"text": "text", "person": "character", "character": "character", "object": "object"}


def read_label(label):
    """Pure function. Box label -> (kind, caption, words). kind is text, character or object."""
    label = str(label or "").strip()
    head, sep, rest = label.partition(":")
    kind = KINDS.get(head.strip().lower()) if sep else None
    if kind is None:
        kind, rest = "object", label
    rest = rest.strip()
    if kind == "text":
        words, _, look = rest.partition("|")
        words, look = words.strip(), look.strip()
        if not words:
            raise ValueError("a text box needs the words after 'text:', for example 'text: OPEN LATE | blue shop sign'")
        return kind, look, words
    return kind, rest, ""


def centred_box(box, width, height):
    """Pure function. Pixel box {x, y, w, h} -> [y0, x0, y1, x1] from the picture centre, clipped to the picture."""
    x0, y0 = max(0.0, float(box["x"])), max(0.0, float(box["y"]))
    x1 = min(float(width), float(box["x"]) + float(box["w"]))
    y1 = min(float(height), float(box["y"]) + float(box["h"]))
    if x1 <= x0 or y1 <= y0:
        return None
    hw, hh = width // 2, height // 2
    return [math.floor(y0) - hh, math.floor(x0) - hw, math.ceil(y1) - hh, math.ceil(x1) - hw]


def build_layout(box_text, width, height, caption):
    """Pure function. (prompt text, list of notes). No boxes -> the caption alone."""
    caption = str(caption or "").strip()
    if box_text is None or not str(box_text).strip():
        return caption, ["no boxes connected: the prompt is the scene text alone"]
    boxes = parse_boxes(box_text)
    items, notes = [], []
    for i, box in enumerate(boxes, 1):
        for key in ("x", "y", "w", "h"):
            if not isinstance(box.get(key), (int, float)) or isinstance(box.get(key), bool):
                raise ValueError("box %d has no number for %s" % (i, key))
        bbox = centred_box(box, width, height)
        if bbox is None:
            notes.append("box %d is outside the %dx%d picture and was left out" % (i, width, height))
            continue
        kind, look, words = read_label(box.get("label", ""))
        item = {"label": kind, "caption": look}
        if kind == "text":
            item["text"] = words
        item["bbox"] = bbox
        items.append(item)
        if not look and kind != "text":
            notes.append("box %d has no label: MOSS gets an empty object box" % i)
    if not items:
        notes.append("no box is inside the picture: the prompt is the scene text alone")
        return caption, notes
    layout = {"summary": {"caption": caption}, "items": items, "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}
    return json.dumps(layout, ensure_ascii=False, separators=(",", ":")), notes


class SYMossLayoutPrompt:
    DESCRIPTION = ("Turn layout boxes into a MOSS-Image layout prompt. Label a box 'text: WORDS | look', 'person: who', "
                   "or just name the object. Connect the prompt to the MOSS text encode node.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "caption": ("STRING", {"default": "", "multiline": True, "tooltip": "The scene in plain sentences: place, light, mood."}),
                "width": ("INT", {"default": 1024, "min": 64, "max": MAX_SIDE, "tooltip": "Picture width. Must match the empty latent."}),
                "height": ("INT", {"default": 1024, "min": 64, "max": MAX_SIDE, "tooltip": "Picture height. Must match the empty latent."}),
            },
            "optional": {
                "layout_boxes": ("STRING", {"default": "", "multiline": True, "tooltip": "Box list as JSON text from Layout Box, Box Draw or Merge. Empty = scene text only."}),
            },
        }

    def run(self, caption, width, height, layout_boxes=""):
        prompt, notes = build_layout(layout_boxes, width, height, caption)
        count = prompt.count('"bbox"')
        info = "MOSS LAYOUT PROMPT\n%d box(es) for a %dx%d picture." % (count, width, height)
        if notes:
            info += "\n" + "\n".join(notes)
        return (prompt, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MossLayoutPrompt", SYMossLayoutPrompt)
