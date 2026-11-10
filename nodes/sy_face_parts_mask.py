"""Face Parts Mask SY: tick face parts (skin, eyes, brows, lips, hair, neck ...) and get one mask of them, from a
face-parsing model file. One node does what used to take a model loader, a processor loader, a parser and a picker.
Model: a Segformer face-parsing model (config.json, preprocessor_config.json, model.safetensors) in models/face_parsing."""
import json
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FOLDER = "face_parsing"
NEEDED = ("config.json", "preprocessor_config.json", "model.safetensors")
# (input name shown on the node, label in the model file, default)
PARTS = (
    ("background", "background", False),
    ("skin", "skin", True),
    ("nose", "nose", True),
    ("glasses", "eye_g", False),
    ("left_eye", "l_eye", True),
    ("right_eye", "r_eye", True),
    ("left_brow", "l_brow", True),
    ("right_brow", "r_brow", True),
    ("left_ear", "l_ear", False),
    ("right_ear", "r_ear", False),
    ("mouth_inside", "mouth", True),
    ("upper_lip", "u_lip", True),
    ("lower_lip", "l_lip", True),
    ("hair", "hair", False),
    ("hat", "hat", False),
    ("earring", "ear_r", False),
    ("necklace", "neck_l", False),
    ("neck", "neck", False),
    ("clothes", "cloth", False),
)
PART_NAMES = tuple(p[0] for p in PARTS)
DEFAULT_MEAN = (0.485, 0.456, 0.406)
DEFAULT_STD = (0.229, 0.224, 0.225)
DEFAULT_SIZE = 512
_CACHE = {}


def picked_labels(flags):
    """Pure function. Model label names for the ticked parts. `flags` maps node input name -> bool."""
    unknown = [k for k in flags if k not in PART_NAMES]
    if unknown:
        raise ValueError("unknown face part(s): %s; allowed: %s" % (", ".join(sorted(unknown)), ", ".join(PART_NAMES)))
    return [label for name, label, _ in PARTS if flags.get(name)]


def label_ids(id2label, labels):
    """Pure function. Class numbers for the label names, read from the model's id2label table."""
    lookup = {str(v): int(k) for k, v in id2label.items()}
    missing = [l for l in labels if l not in lookup]
    if missing:
        raise ValueError("this face-parsing model has no part(s) %s; it knows: %s"
                         % (", ".join(missing), ", ".join(sorted(lookup))))
    return sorted(lookup[l] for l in labels)


def preprocess_settings(cfg):
    """Pure function. (height, width, mean, std, rescale) from a preprocessor_config.json dict."""
    size = cfg.get("size", DEFAULT_SIZE)
    if isinstance(size, dict):
        h, w = int(size.get("height", DEFAULT_SIZE)), int(size.get("width", DEFAULT_SIZE))
    else:
        h = w = int(size)
    if not (32 <= h <= 4096 and 32 <= w <= 4096):
        raise ValueError("preprocessor size %dx%d is outside 32-4096" % (w, h))
    mean = tuple(float(x) for x in cfg.get("image_mean", DEFAULT_MEAN))
    std = tuple(float(x) for x in cfg.get("image_std", DEFAULT_STD))
    if len(mean) != 3 or len(std) != 3 or min(std) <= 0:
        raise ValueError("preprocessor mean/std must be 3 numbers each, std above 0")
    return h, w, mean, std, bool(cfg.get("do_normalize", True))


def palette(n):
    """Pure function. n distinct preview colours as (r, g, b) 0-1, class 0 (background) black."""
    out = [(0.0, 0.0, 0.0)]
    for i in range(1, n):
        h = (i * 0.618033988749895) % 1.0
        k = int(h * 6)
        f = h * 6 - k
        v, s = 1.0, 0.75
        p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
        out.append(((v, q, p, p, t, v)[k % 6], (t, v, v, q, p, p)[k % 6], (p, p, t, v, v, q)[k % 6]))
    return out


def missing_files(folder):
    if not folder or not os.path.isdir(folder):
        return list(NEEDED)
    return [f for f in NEEDED if not os.path.isfile(os.path.join(folder, f))]


def model_folder():
    """The first face_parsing folder ComfyUI knows that holds all 3 files (models/face_parsing by default)."""
    import folder_paths
    tries = []
    try:
        tries += list(folder_paths.get_folder_paths(FOLDER))
    except Exception:
        pass
    tries.append(os.path.join(folder_paths.models_dir, FOLDER))
    for t in tries:
        if not missing_files(t):
            return t
    raise ValueError("Face Parts Mask SY needs a Segformer face-parsing model in models/%s (files: %s). "
                     "Missing in %s: %s" % (FOLDER, ", ".join(NEEDED), tries[-1], ", ".join(missing_files(tries[-1]))))


def _load(folder, device):
    key = (folder, str(device))
    if key not in _CACHE:
        from transformers import SegformerForSemanticSegmentation
        model = SegformerForSemanticSegmentation.from_pretrained(folder, local_files_only=True).to(device).eval()
        with open(os.path.join(folder, "preprocessor_config.json"), encoding="utf-8") as f:
            pre = preprocess_settings(json.load(f))
        _CACHE.clear()
        _CACHE[key] = (model, pre)
    return _CACHE[key]


def parse_faces(image, folder, device):
    """Class number per pixel for every picture in the batch: a [B, H, W] long tensor on the CPU."""
    import torch
    import torch.nn.functional as F
    model, (h, w, mean, std, norm) = _load(folder, device)
    m = torch.tensor(mean, device=device).view(1, 3, 1, 1)
    s = torch.tensor(std, device=device).view(1, 3, 1, 1)
    out = []
    with torch.no_grad():
        for i in range(image.shape[0]):
            x = image[i:i + 1, :, :, :3].permute(0, 3, 1, 2).to(device, torch.float32)
            H, W = x.shape[-2:]
            x = F.interpolate(x, size=(h, w), mode="bilinear", align_corners=False)
            if norm:
                x = (x - m) / s
            logits = model(pixel_values=x.to(model.dtype)).logits.float()
            logits = F.interpolate(logits, size=(H, W), mode="bilinear", align_corners=False)
            out.append(logits.argmax(dim=1).cpu())
    return torch.cat(out, 0)


class SYFacePartsMask:
    DESCRIPTION = ("Tick the face parts you want (skin, eyes, brows, lips, hair, neck and more) and get one white mask "
                   "of them, ready for skin fixes, face detail or inpainting. Also gives a coloured map of all parts "
                   "so you can see what the model found. Needs the face-parsing model files in models/face_parsing.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "IMAGE", "STRING")
    RETURN_NAMES = ("mask", "parts_map", "info")

    @classmethod
    def INPUT_TYPES(cls):
        req = {"image": ("IMAGE", {"tooltip": "The picture(s) with a face."})}
        for name, label, default in PARTS:
            req[name] = ("BOOLEAN", {"default": default, "tooltip": "On: %s goes into the mask." % name.replace("_", " ")})
        return {"required": req}

    def run(self, image, **flags):
        import torch
        import comfy.model_management as mm
        labels = picked_labels(flags)
        folder = model_folder()
        device = mm.get_torch_device()
        model, _ = _load(folder, device)
        ids = label_ids(model.config.id2label, labels)
        cls_map = parse_faces(image, folder, device)
        mask = torch.zeros(cls_map.shape, dtype=torch.float32)
        for i in ids:
            mask[cls_map == i] = 1.0
        pal = torch.tensor(palette(len(model.config.id2label)), dtype=torch.float32)
        parts_map = pal[cls_map.clamp(0, len(pal) - 1)]
        cover = float(mask.mean()) * 100.0
        info = "FACE PARTS MASK\n%d picture(s), parts: %s\nMask covers %.1f%% of the picture." % (
            image.shape[0], ", ".join(n for n, _, _ in PARTS if flags.get(n)) or "(none ticked: empty mask)", cover)
        return (mask, parts_map, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FacePartsMask", SYFacePartsMask)
