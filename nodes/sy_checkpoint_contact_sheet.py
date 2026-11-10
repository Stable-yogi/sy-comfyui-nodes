"""Checkpoint Contact Sheet SY: renders the same prompts with several checkpoints, one after the other, and lays the
pictures out as one labelled sheet (a row per checkpoint, a column per prompt). Each checkpoint is unloaded before the next."""
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_MODELS = 12
MAX_PROMPTS = 6


def clean_lines(text):
    """Pure function. Non-empty lines without spaces at the ends; lines starting with # are skipped."""
    return [ln.strip() for ln in str(text or "").splitlines() if ln.strip() and not ln.strip().startswith("#")]


def match_checkpoints(wanted, available):
    """Pure function. Each wanted line picks one file: an exact name, else the one name that ends with it,
    else the one name that holds it (case does not matter). Returns (picked, problems)."""
    picked, problems = [], []
    low = [(a, a.lower().replace("\\", "/")) for a in available]
    for w in wanted:
        lw = w.lower().replace("\\", "/")
        exact = [a for a, la in low if la == lw]
        hits = exact or [a for a, la in low if la.endswith(lw)] or [a for a, la in low if lw in la]
        same_file = len({os.path.basename(h.replace("\\", "/")).lower() for h in hits}) == 1
        if len(hits) > 1 and same_file:
            problems.append("note: %d copies of %s found in different folders; used %s" % (len(hits), model_label(hits[0]), hits[0]))
        if len(hits) == 1 or (hits and same_file):
            if hits[0] not in picked:
                picked.append(hits[0])
        elif not hits:
            problems.append("skipped: no checkpoint matches %r" % w)
        else:
            problems.append("skipped: %r matches %d checkpoints (%s); write more of the name" % (w, len(hits), ", ".join(hits[:3])))
    return picked, problems


def model_label(name):
    """Pure function. The file name without folders and without the extension."""
    base = os.path.basename(str(name).replace("\\", "/"))
    return base.rsplit(".", 1)[0] if "." in base else base


def check_plan(models, prompts, width, height):
    if not models:
        raise ValueError("no checkpoint to render: write one checkpoint name (or part of it) per line")
    if not prompts:
        raise ValueError("no prompt: write one prompt per line")
    if len(models) > MAX_MODELS:
        raise ValueError("%d checkpoints is too many for one sheet; the limit is %d" % (len(models), MAX_MODELS))
    if len(prompts) > MAX_PROMPTS:
        raise ValueError("%d prompts is too many for one sheet; the limit is %d" % (len(prompts), MAX_PROMPTS))
    if width % 8 or height % 8:
        raise ValueError("width and height must be multiples of 8, got %dx%d" % (width, height))


def sheet_text(models, prompts, seconds, problems):
    lines = ["CHECKPOINT CONTACT SHEET", "%d checkpoint%s x %d prompt%s, same seed for all." % (
        len(models), "" if len(models) == 1 else "s", len(prompts), "" if len(prompts) == 1 else "s")]
    for name, sec in zip(models, seconds):
        lines.append("%s: %.1f s" % (model_label(name), sec))
    for i, p in enumerate(prompts):
        lines.append("prompt %d: %s" % (i + 1, p))
    lines += [p[0].upper() + p[1:] for p in problems]
    return "\n".join(lines)


class SYCheckpointContactSheet:
    DESCRIPTION = ("Renders the same prompts with several all-in-one checkpoints, one after the other, and gives one "
                   "labelled sheet: a row per checkpoint, a column per prompt, same seed for all. Each checkpoint is "
                   "unloaded before the next, so the memory need is that of one checkpoint. Good for picking a model.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING")
    RETURN_NAMES = ("sheet", "images", "info")

    @classmethod
    def INPUT_TYPES(cls):
        try:
            import comfy.samplers as cs
            samplers, schedulers = list(cs.KSampler.SAMPLERS), list(cs.KSampler.SCHEDULERS)
        except Exception:
            samplers, schedulers = ["euler"], ["normal"]
        return {"required": {
            "checkpoints": ("STRING", {"multiline": True, "default": "",
                                       "tooltip": "One checkpoint per line: the file name or a unique part of it. Up to 12."}),
            "prompts": ("STRING", {"multiline": True, "default": "a portrait photo of a woman in a garden, soft light",
                                   "tooltip": "One prompt per line. Up to 6. Each becomes a column."}),
            "negative": ("STRING", {"multiline": True, "default": "", "tooltip": "Used for every picture. Empty is fine."}),
            "width": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 8, "tooltip": "Picture width in pixels."}),
            "height": ("INT", {"default": 1024, "min": 256, "max": 2048, "step": 8, "tooltip": "Picture height in pixels."}),
            "steps": ("INT", {"default": 25, "min": 1, "max": 150, "tooltip": "Same for every checkpoint."}),
            "cfg": ("FLOAT", {"default": 6.0, "min": 0.0, "max": 30.0, "step": 0.1, "tooltip": "Same for every checkpoint."}),
            "sampler_name": (samplers, {"default": "euler" if "euler" in samplers else samplers[0], "tooltip": "Sampler for every picture."}),
            "scheduler": (schedulers, {"default": "normal" if "normal" in schedulers else schedulers[0], "tooltip": "Scheduler for every picture."}),
            "seed": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff, "tooltip": "Same seed for all, so only the checkpoint changes."}),
            "label_size": ("INT", {"default": 28, "min": 10, "max": 96, "tooltip": "Size of the label text on the sheet."}),
        }}

    def run(self, checkpoints, prompts, negative, width, height, steps, cfg, sampler_name, scheduler, seed, label_size):
        try:
            import folder_paths
            import nodes as comfy_nodes
            import comfy.model_management as mm
            import torch
        except ImportError:
            raise ValueError("Checkpoint Contact Sheet SY loads checkpoints, so it only runs inside ComfyUI.")
        try:
            from .sy_xy_grid_assemble import render_grid
        except ImportError:
            from sy_xy_grid_assemble import render_grid
        models, problems = match_checkpoints(clean_lines(checkpoints), folder_paths.get_filename_list("checkpoints"))
        plist = clean_lines(prompts)
        check_plan(models, plist, int(width), int(height))
        with torch.inference_mode():  # no gradient links, so a picture never keeps its model on the card
            pictures, seconds = self._render(comfy_nodes, mm, torch, models, plist, negative, width, height, steps, cfg,
                                             sampler_name, scheduler, seed)
        images = torch.cat(pictures, dim=0)
        xs = ["prompt %d" % (i + 1) for i in range(len(plist))]
        ys = [model_label(n) for n in models]
        sheet = render_grid(images, xs, ys, 8, 16, "dark_gray", int(label_size))
        text = sheet_text(models, plist, seconds, problems)
        return {"ui": {"text": [text]}, "result": (sheet, images, text)}

    @staticmethod
    def _render(comfy_nodes, mm, torch, models, plist, negative, width, height, steps, cfg, sampler_name, scheduler, seed):
        import gc
        import time
        pictures, seconds = [], []
        for name in models:
            t0 = time.time()
            model, clip, vae = comfy_nodes.CheckpointLoaderSimple().load_checkpoint(name)[:3]
            if clip is None or vae is None:
                raise ValueError("%s has no text encoder or VAE inside; this node needs all-in-one checkpoints" % name)
            neg = comfy_nodes.CLIPTextEncode().encode(clip, negative or "")[0]
            for p in plist:
                pos = comfy_nodes.CLIPTextEncode().encode(clip, p)[0]
                latent = {"samples": torch.zeros([1, 4, int(height) // 8, int(width) // 8])}
                out = comfy_nodes.common_ksampler(model, int(seed), int(steps), float(cfg), sampler_name, scheduler,
                                                  pos, neg, latent, denoise=1.0)[0]
                pictures.append(comfy_nodes.VAEDecode().decode(vae, out)[0][:1].cpu())
            seconds.append(time.time() - t0)
            del model, clip, vae, neg, pos, out
            mm.unload_all_models()
            gc.collect()
            mm.soft_empty_cache()
        return pictures, seconds


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CheckpointContactSheet", SYCheckpointContactSheet)
