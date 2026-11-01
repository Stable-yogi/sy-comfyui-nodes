"""Mask From Words SY: select things in a picture by typing what they are ("the red dress"), using a SAM3 model file."""
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

FOLDER = "sam3"
NO_MODEL = "(no model installed: use Model Downloader SY)"
WHICH = ("all matches together", "biggest one", "one at a time (batch of masks)")
MAX_WORDS = 200
MAX_PIXELS = 64
MAX_PER_PHRASE = 30      # most separate things looked for per phrase
TOO_OLD = ("This ComfyUI is too old for Mask From Words SY (it needs the built-in SAM3 nodes). "
           "Update ComfyUI and try again.")


def clean_words(text):
    """Pure function. Trim, collapse runs of spaces and line breaks, keep at most 200 characters."""
    if text is None:
        return ""
    s = " ".join(str(text).split())
    return s[:MAX_WORDS].strip()


def sam_prompt(words, per_phrase=MAX_PER_PHRASE):
    """Pure function. Turns cleaned words into the text the SAM3 text encoder reads: one or more phrases split at
    commas, each asking for up to `per_phrase` separate matches. Colons and brackets in the words are dropped."""
    if per_phrase < 1:
        raise ValueError("per_phrase must be at least 1")
    text = clean_words(words)
    for ch in ":()":
        text = text.replace(ch, " ")
    parts = [" ".join(p.split()) for p in text.split(",")]
    parts = [p for p in parts if p]
    if not parts:
        raise ValueError("Type what to select in 'words', for example: person, or the red dress")
    return ", ".join("%s:%d" % (p, per_phrase) for p in parts)


def check_which(which):
    if which not in WHICH:
        raise ValueError("which must be one of: %s, got %r" % (", ".join(WHICH), which))
    return which


def pick_mask_index(areas, which):
    """Pure function. Which found things (by position in `areas`, their pixel counts) go into the result.
    all together -> every index; biggest -> the one largest index; one at a time -> every index."""
    check_which(which)
    idx = list(range(len(areas)))
    if not idx:
        return []
    if which == WHICH[1]:
        best = 0
        for i in idx:
            if areas[i] > areas[best]:
                best = i
        return [best]
    return idx


def combine_style(which):
    """Pure function. 'union' (one mask per picture from all picks), 'single' (the one biggest), 'each' (one mask per find)."""
    check_which(which)
    return ("union", "single", "each")[WHICH.index(which)]


def threshold_ok(t):
    if isinstance(t, bool) or not isinstance(t, (int, float)) or t < 0.0 or t > 1.0:
        raise ValueError("threshold must be between 0 and 1, got %r" % (t,))
    return float(t)


def pixels_ok(value, what, low):
    """Pure function. A whole number of pixels between `low` and 64."""
    try:
        if isinstance(value, bool) or int(value) != value:
            raise ValueError
        v = int(value)
    except (TypeError, ValueError):
        raise ValueError("%s must be a whole number of pixels between %d and %d, got %r" % (what, low, MAX_PIXELS, value))
    if v < low or v > MAX_PIXELS:
        raise ValueError("%s must be between %d and %d pixels, got %d" % (what, low, MAX_PIXELS, v))
    return v


def no_match_text(words):
    return "Nothing matched '%s'. Try other words or lower the threshold." % words


def info_text(words, found, which, masks_out, pictures):
    """Pure function. One plain sentence about the result."""
    if found == 0:
        return no_match_text(words)
    style = combine_style(which)
    thing = "thing" if found == 1 else "things"
    pic = "picture" if pictures == 1 else "pictures"
    if style == "union":
        how = "all joined into one mask per picture"
    elif style == "single":
        how = "the biggest one kept per picture"
    else:
        how = "one mask each"
    return "Found %d %s for '%s' in %d %s: %s (%d mask%s out)." % (
        found, thing, words, pictures, pic, how, masks_out, "" if masks_out == 1 else "s")


def model_choices(names):
    names = sorted(n for n in names if isinstance(n, str) and n.strip())
    return names if names else [NO_MODEL]


def check_plain_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("pick a model file from the list")
    norm = name.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":") or ".." in norm.split("/"):
        raise ValueError("the model must be a plain file name from the list, not a path: %r" % name)
    return name


def _sam3_folder_names():
    """Names of model files: the sam3 folder (registered here when ComfyUI does not know it yet), plus any
    checkpoint whose name says sam3. Empty without ComfyUI."""
    try:
        import folder_paths
    except Exception:
        return []
    names = []
    try:
        if FOLDER not in folder_paths.folder_names_and_paths:
            folder_paths.add_model_folder_path(FOLDER, os.path.join(folder_paths.models_dir, FOLDER))
        ok = folder_paths.supported_pt_extensions
        names += [n for n in folder_paths.get_filename_list(FOLDER) if os.path.splitext(n)[1].lower() in ok]
    except Exception:
        pass
    try:
        names += [n for n in folder_paths.get_filename_list("checkpoints") if "sam3" in n.lower() and n not in names]
    except Exception:
        pass
    return names


def list_models():
    return model_choices(_sam3_folder_names())


def resolve_model_path(name):
    if name == NO_MODEL:
        raise ValueError("No SAM3 model is installed. Put the model file into the ComfyUI folder models/sam3 "
                         "(or use Model Downloader SY), refresh the page and pick it.")
    check_plain_name(name)
    try:
        import folder_paths
    except Exception:
        raise ValueError("ComfyUI folders are not available, so %r cannot be found" % name)
    for kind in (FOLDER, "checkpoints"):
        try:
            path = folder_paths.get_full_path(kind, name)
        except Exception:
            path = None
        if path and os.path.isfile(path):
            return path
    raise ValueError("The model file %r was not found in models/sam3. Refresh the page and pick another file." % name)


# ---------------------------------------------------------------- model (loaded once, kept in memory)
_CACHE = {"path": None, "stamp": None, "bundle": None}


def _get_bundle(path):
    """(model, clip) for a SAM3 file, loaded once and kept."""
    stamp = os.path.getmtime(path)
    if _CACHE["bundle"] is not None and _CACHE["path"] == path and _CACHE["stamp"] == stamp:
        return _CACHE["bundle"]
    try:
        import comfy.sd
        import folder_paths
        from comfy_extras.nodes_sam3 import SAM3_Detect  # noqa: F401  (check that the core node exists)
    except Exception:
        raise ValueError(TOO_OLD)
    try:
        out = comfy.sd.load_checkpoint_guess_config(path, output_vae=False, output_clip=True,
                                                    embedding_directory=folder_paths.get_folder_paths("embeddings"))
    except Exception as e:
        raise ValueError("This file could not be loaded as a SAM3 model: %s (%s). Pick a different file." % (os.path.basename(path), e))
    model, clip = out[0], out[1]
    if model is None or clip is None or not hasattr(model.model, "diffusion_model") \
            or not hasattr(model.model.diffusion_model, "forward_segment"):
        raise ValueError("This file is not a SAM3 model: %s. Pick a different file." % os.path.basename(path))
    _CACHE.update(path=path, stamp=stamp, bundle=(model, clip))
    return _CACHE["bundle"]


def _release(bundle):
    try:
        import comfy.model_management as mm
        mm.unload_model_and_clones(bundle[0])
        mm.unload_model_and_clones(bundle[1].patcher)
    except Exception:
        pass


def _encode_words(bundle, prompt):
    clip = bundle[1]
    return clip.encode_from_tokens_scheduled(clip.tokenize(prompt))


def _detect(bundle, cond, frame, threshold):
    """Run the core SAM3 detector on ONE picture [1,H,W,C]. Returns a list of masks, each [H,W] floats 0/1."""
    from comfy_extras.nodes_sam3 import SAM3_Detect
    out = SAM3_Detect.execute(bundle[0], frame[..., :3], conditioning=cond, threshold=threshold,
                              refine_iterations=2, individual_masks=True)
    masks = out.args[0] if hasattr(out, "args") else out[0]
    return [masks[i] for i in range(masks.shape[0])]


# ---------------------------------------------------------------- picture maths (torch is imported inside)
def _grow_shrink(mask, px):
    if px == 0:
        return mask
    import torch.nn.functional as F
    r = abs(px)
    x = mask.unsqueeze(1)
    if px < 0:
        x = -x
    x = F.max_pool2d(x, (1, 2 * r + 1), stride=1, padding=(0, r))
    x = F.max_pool2d(x, (2 * r + 1, 1), stride=1, padding=(r, 0))
    if px < 0:
        x = -x
    return x.squeeze(1)


def _feather(mask, px):
    if px <= 0:
        return mask
    import torch.nn.functional as F
    x = mask.unsqueeze(1)
    for _ in range(2):
        x = F.avg_pool2d(x, (1, 2 * px + 1), stride=1, padding=(0, px), count_include_pad=False)
        x = F.avg_pool2d(x, (2 * px + 1, 1), stride=1, padding=(px, 0), count_include_pad=False)
    return x.squeeze(1)


def assemble(image, per_picture, which, grow, feather):
    """image [B,H,W,C>=3]; per_picture = list of B lists of [H,W] masks. Returns (mask, cutout, found, masks_out)."""
    import torch
    check_which(which)
    style = combine_style(which)
    b, h, w, _ = image.shape
    if len(per_picture) != b:
        raise ValueError("internal: found-lists do not match the picture count")
    out_masks, sources, found = [], [], 0
    for i, items in enumerate(per_picture):
        items = [t.to(device=image.device, dtype=image.dtype) for t in items]
        areas = [float(t.sum()) for t in items]
        real = [k for k, a in enumerate(areas) if a > 0.0]
        items = [items[k] for k in real]
        areas = [areas[k] for k in real]
        found += len(items)
        picks = pick_mask_index(areas, which)
        if style == "each":
            for k in picks:
                out_masks.append(items[k])
                sources.append(i)
        else:
            if picks:
                m = torch.stack([items[k] for k in picks]).amax(dim=0)
            else:
                m = torch.zeros(h, w, dtype=image.dtype, device=image.device)
            out_masks.append(m)
            sources.append(i)
    if not out_masks:           # one-at-a-time and nothing found anywhere: an empty mask per picture
        out_masks = [torch.zeros(h, w, dtype=image.dtype, device=image.device) for _ in range(b)]
        sources = list(range(b))
    mask = torch.stack(out_masks).clamp(0.0, 1.0)
    mask = _feather(_grow_shrink(mask, grow), feather).clamp(0.0, 1.0)
    rgb = image[..., :3][torch.tensor(sources, dtype=torch.long, device=image.device)]
    cutout = torch.cat([rgb, mask.unsqueeze(-1)], dim=-1)
    return mask, cutout, found, len(out_masks) if found else 0


class SYMaskFromWords:
    DESCRIPTION = ("Selects things in a picture from words you type, for example 'person' or 'the red dress'. "
                   "Gives a mask (1 = selected), a cut-out picture with a see-through background, how many separate things were found "
                   "and a short note. Nothing found gives an empty mask, not an error. Needs a SAM3 model file.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "IMAGE", "INT", "STRING")
    RETURN_NAMES = ("mask", "cutout", "found", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture (or batch) to select things in."}),
                "words": ("STRING", {"default": "person", "multiline": False,
                                     "tooltip": "What to select, in plain words. Example: the red dress. Commas look for several things."}),
                "model": (list_models(), {"tooltip": "SAM3 model file from models/sam3."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01,
                                        "tooltip": "How sure it must be. Lower finds more. Finds things that are not there? Raise it to 0.8."}),
                "which": (list(WHICH), {"default": WHICH[0], "tooltip": "Join everything found, keep the biggest, or give one mask per find."}),
                "grow": ("INT", {"default": 0, "min": -MAX_PIXELS, "max": MAX_PIXELS,
                                 "tooltip": "Pixels to widen the selection. Negative numbers shrink it."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": MAX_PIXELS, "tooltip": "Soft edge in pixels. 0 = off."}),
            }
        }

    def run(self, image, words, model, threshold=0.5, which=WHICH[0], grow=0, feather=0):
        text = clean_words(words)
        if not text:
            raise ValueError("'words' is empty. Type what to select, for example: person, or the red dress")
        threshold = threshold_ok(threshold)
        check_which(which)
        grow = pixels_ok(grow, "grow", -MAX_PIXELS)
        feather = pixels_ok(feather, "feather", 0)
        if getattr(image, "ndim", 0) != 4 or image.shape[-1] < 3:
            raise ValueError("expected a picture batch shaped [batch, height, width, 3 or 4 channels]")
        prompt = sam_prompt(text)
        path = resolve_model_path(model)
        bundle = _get_bundle(path)
        try:
            cond = _encode_words(bundle, prompt)
            per_picture = [_detect(bundle, cond, image[i:i + 1], threshold) for i in range(image.shape[0])]
        finally:
            _release(bundle)
        mask, cutout, found, masks_out = assemble(image, per_picture, which, grow, feather)
        if found == 0:
            return (mask, cutout, 0, no_match_text(text))
        return (mask, cutout, found, info_text(text, found, which, masks_out, image.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskFromWords", SYMaskFromWords)
NODE_DISPLAY_NAME_MAPPINGS["SYMaskFromWords"] = "Mask From Words SY"
