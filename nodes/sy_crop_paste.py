"""Crop By Mask SY and Paste Back SY: cut a picture around a mask, work on the crop, paste it back softly."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

EMPTY_CHOICES = ("whole_image", "error")


def plan_crop(box, padding, multiple_of, on_empty, img_w, img_h):
    """Pure function. box is the mask box (x, y, w, h) or None. Returns the crop box to cut."""
    if padding < 0:
        raise ValueError("padding cannot be negative")
    if multiple_of < 1:
        raise ValueError("multiple_of must be 1 or more")
    if on_empty not in EMPTY_CHOICES:
        raise ValueError("on_empty must be whole_image or error")
    if box is None:
        if on_empty == "error":
            raise ValueError("the mask is empty: paint something white, or set on_empty to whole_image")
        box = (0, 0, img_w, img_h)
    box = mm.pad_box(box, padding, img_w, img_h)
    return mm.fit_multiple(box, multiple_of, img_w, img_h)


def crop_by_mask(img, mask, padding, multiple_of, threshold=0.5, on_empty="whole_image"):
    """Pure function on nested lists: image [H][W][C], mask [H][W]. Returns (crop, crop_mask, crop_info_text)."""
    h, w = len(img), len(img[0])
    if len(mask) != h or len(mask[0]) != w:
        raise ValueError("the mask and the image must be the same size")
    x, y, bw, bh = plan_crop(mm.mask_bbox(mask, threshold), padding, multiple_of, on_empty, w, h)
    crop = [[list(p) for p in row[x:x + bw]] for row in img[y:y + bh]]
    cmask = [list(row[x:x + bw]) for row in mask[y:y + bh]]
    return crop, cmask, mm.make_crop_info((x, y, bw, bh), w, h)


def paste_back(base, crop, mask, crop_info, feather):
    """Pure function on nested lists. mask is [h][w] or None. Returns the new image."""
    if feather < 0 or feather > mm.MAX_RADIUS:
        raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)
    info = mm.parse_crop_info(crop_info)
    if len(base) != info["image_h"] or len(base[0]) != info["image_w"]:
        raise ValueError("the image is not the same size as the one that was cropped (%d x %d)"
                         % (info["image_w"], info["image_h"]))
    if len(crop) != info["h"] or len(crop[0]) != info["w"]:
        crop = [[crop[min(len(crop) - 1, j * len(crop) // info["h"])][min(len(crop[0]) - 1, i * len(crop[0]) // info["w"])]
                 for i in range(info["w"])] for j in range(info["h"])]
    if mask is None:
        soft = mm.edge_fade_list(info["w"], info["h"], feather, mm.open_sides(info))
    else:
        if len(mask) != info["h"] or len(mask[0]) != info["w"]:
            mask = mm.resize_nearest_mask(mask, info["h"], info["w"])
        soft = mm.blur_list(mask, feather)
    return mm.paste_list(base, crop, soft, info["x"], info["y"])


class SYCropByMask:
    DESCRIPTION = "Cuts the picture and mask around the white part of the mask. Gives a crop info note for Paste Back SY."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("crop", "crop_mask", "crop_info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to cut."}),
                "mask": ("MASK", {"tooltip": "Marks the area to keep. Must be the same size as the picture."}),
                "padding": ("INT", {"default": 32, "min": 0, "max": 4096, "step": 1, "tooltip": "Extra pixels kept around the white part for context."}),
                "multiple_of": ("INT", {"default": 8, "min": 1, "max": 512, "step": 1, "tooltip": "Crop width and height become a multiple of this. Models like 8 or 64."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.01, "max": 1.0, "step": 0.01, "tooltip": "Mask values at or above this count as white."}),
                "on_empty": (list(EMPTY_CHOICES), {"default": "whole_image", "tooltip": "When nothing is white: crop the whole image, or stop with an error."}),
            }
        }

    def run(self, image, mask, padding, multiple_of, threshold, on_empty):
        m = mm.t_mask3(mask)
        n, h, w = image.shape[0], image.shape[1], image.shape[2]
        if m.shape[1] != h or m.shape[2] != w:
            raise ValueError("the mask (%d x %d) and the image (%d x %d) must be the same size" % (m.shape[2], m.shape[1], w, h))
        m = mm.t_match_batch(m, n)
        x, y, bw, bh = plan_crop(mm.t_bbox(m, threshold), int(padding), int(multiple_of), on_empty, w, h)
        info = mm.make_crop_info((x, y, bw, bh), w, h)
        return (image[:, y:y + bh, x:x + bw, :], m[:, y:y + bh, x:x + bw], info)


class SYPasteBack:
    DESCRIPTION = "Pastes a processed crop back into the original picture with a soft edge, using the crop info from Crop By Mask SY."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The original picture, the same one that was cropped."}),
                "crop": ("IMAGE", {"tooltip": "The processed crop. It is resized to the crop box if its size differs."}),
                "crop_info": ("STRING", {"forceInput": True, "tooltip": "The crop_info output of Crop By Mask SY."}),
                "feather": ("INT", {"default": 16, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Width in pixels of the soft seam. 0 gives a hard edge."}),
            },
            "optional": {
                "crop_mask": ("MASK", {"tooltip": "Only paste where this mask is white. Leave empty to paste the whole crop."}),
            },
        }

    def run(self, image, crop, crop_info, feather, crop_mask=None):
        import torch
        import torch.nn.functional as F
        if feather < 0 or feather > mm.MAX_RADIUS:
            raise ValueError("feather must be between 0 and %d" % mm.MAX_RADIUS)
        info = mm.parse_crop_info(crop_info)
        if image.shape[1] != info["image_h"] or image.shape[2] != info["image_w"]:
            raise ValueError("the image is not the same size as the one that was cropped (%d x %d)"
                             % (info["image_w"], info["image_h"]))
        c = image.shape[3]
        if crop.shape[3] < c:
            raise ValueError("the processed crop has fewer colour channels than the image")
        crop = crop[..., :c]
        x, y, w, h = info["x"], info["y"], info["w"], info["h"]
        if crop.shape[1] != h or crop.shape[2] != w:
            crop = F.interpolate(crop.permute(0, 3, 1, 2), size=(h, w), mode="bilinear", align_corners=False).permute(0, 2, 3, 1)
        n = max(image.shape[0], crop.shape[0])
        if crop_mask is None:
            soft = mm.t_edge_fade(h, w, int(feather), mm.open_sides(info), crop.device).expand(n, h, w)
        else:
            cm = mm.t_match_batch(mm.t_resize_mask(mm.t_mask3(crop_mask), h, w), n)
            soft = mm.t_blur(cm.to(crop.device), int(feather))
        base = mm.t_match_batch(image, n)
        crop = mm.t_match_batch(crop, n).to(base.dtype)
        out = base.clone()
        s = soft.unsqueeze(-1).to(base.dtype)
        out[:, y:y + h, x:x + w, :] = base[:, y:y + h, x:x + w, :] * (1.0 - s) + crop * s
        return (out,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CropByMask", SYCropByMask)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PasteBack", SYPasteBack)
