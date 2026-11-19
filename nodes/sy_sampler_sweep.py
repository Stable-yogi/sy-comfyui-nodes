"""Sampler Sweep SY: one prompt, several sampler + scheduler pairs, the same seed. Gives all results as one latent batch,
a caption per result (pair and time) for Image Grid SY, and a time table, so you can see which pair looks best and which is fastest."""
import time

try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names

MAX_PAIRS = 24
MAX_SEED = 2 ** 64 - 1
DEFAULT_PAIRS = "er_sde + simple\neuler + simple\neuler_ancestral + simple\ner_sde + beta\ner_sde + karras"


def parse_pairs(text, samplers, schedulers):
    """Pure function. One pair per line, 'sampler + scheduler' (also 'sampler, scheduler' or 'sampler scheduler').
    Empty lines and lines starting with # are skipped. Unknown names raise a ValueError that names the line."""
    pairs = []
    for n, raw in enumerate(str(text or "").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p for p in line.replace("+", " ").replace(",", " ").split() if p]
        if len(parts) != 2:
            raise ValueError("line %d %r: write one pair as 'sampler + scheduler', for example 'er_sde + simple'" % (n, line))
        s, c = parts
        if s not in samplers:
            raise ValueError("line %d: %r is not a sampler in this ComfyUI" % (n, s))
        if c not in schedulers:
            raise ValueError("line %d: %r is not a scheduler in this ComfyUI (try simple, normal or beta)" % (n, c))
        pairs.append((s, c))
    if not pairs:
        raise ValueError("type at least one pair, for example 'er_sde + simple'")
    if len(pairs) > MAX_PAIRS:
        raise ValueError("at most %d pairs at once (you typed %d); each one is a full picture" % (MAX_PAIRS, len(pairs)))
    return pairs


def pair_caption(sampler, scheduler, seconds):
    """Pure function. Caption under one picture."""
    return "%s + %s  %.1f s" % (sampler, scheduler, seconds)


def time_table(pairs, seconds, steps):
    """Pure function. Plain text table, fastest first, with the time per step."""
    rows = sorted(zip(pairs, seconds), key=lambda r: r[1])
    lines = ["%d pairs, %d steps each, fastest first:" % (len(pairs), steps)]
    for (s, c), t in rows:
        lines.append("%-28s %6.1f s  (%.2f s per step)" % (s + " + " + c, t, t / max(1, steps)))
    rest = sorted(seconds[1:])
    if rest and seconds[0] > 1.5 * rest[len(rest) // 2]:
        lines.append("The first pair (%s + %s) also loaded the model, so its time is too long. Put it twice to see its real time." % pairs[0])
    return "\n".join(lines)


def _core(name, **kwargs):
    """Run a ComfyUI core node by its name (old and new node style)."""
    import nodes as comfy_nodes
    cls = comfy_nodes.NODE_CLASS_MAPPINGS.get(name)
    if cls is None:
        raise ValueError("this ComfyUI has no core node %r, so Sampler Sweep SY cannot run" % name)
    out = getattr(cls(), cls.FUNCTION)(**kwargs)
    if isinstance(out, dict) and "result" in out:
        out = out["result"]
    return tuple(out)


class SYSamplerSweep:
    DESCRIPTION = ("Try several sampler + scheduler pairs on one prompt with the same seed. Gives all results as one batch "
                   "(decode it and feed Image Grid SY), a caption per picture with its time, and a time table, fastest first. "
                   "The first pair also loads the model, so its time can be longer: put a pair twice to see the real time.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "STRING", "STRING")
    RETURN_NAMES = ("latents", "labels", "time_table")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model to sample with."}),
                "positive": ("CONDITIONING", {"tooltip": "Your encoded prompt."}),
                "latent": ("LATENT", {"tooltip": "An empty latent with batch size 1."}),
                "pairs": ("STRING", {"default": DEFAULT_PAIRS, "multiline": True,
                                     "tooltip": "One pair per line: sampler + scheduler. At most 24. Lines starting with # are skipped."}),
                "seed": ("INT", {"default": 42, "min": 0, "max": MAX_SEED, "tooltip": "The same seed is used for every pair, so the compare is fair."}),
                "steps": ("INT", {"default": 25, "min": 1, "max": 1000, "tooltip": "Steps for every pair."}),
                "cfg": ("FLOAT", {"default": 2.5, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "How strongly to follow the prompt. 1 skips the negative prompt."}),
            },
            "optional": {
                "negative": ("CONDITIONING", {"tooltip": "What you do not want. Used only when cfg is not 1."}),
            },
        }

    def run(self, model, positive, latent, pairs, seed, steps, cfg, negative=None):
        import torch
        todo = parse_pairs(pairs, sampler_names(), scheduler_names())
        if int(latent["samples"].shape[0]) != 1:
            raise ValueError("Sampler Sweep SY needs a latent with batch size 1 (got %d)" % int(latent["samples"].shape[0]))
        use_cfg = negative is not None and abs(float(cfg) - 1.0) > 1e-6
        if use_cfg:
            (guider,) = _core("CFGGuider", model=model, positive=positive, negative=negative, cfg=float(cfg))
        else:
            (guider,) = _core("BasicGuider", model=model, conditioning=positive)
        outs, secs = [], []
        for s, c in todo:
            (noise,) = _core("RandomNoise", noise_seed=int(seed))
            (sampler_obj,) = _core("KSamplerSelect", sampler_name=s)
            (sigmas,) = _core("BasicScheduler", model=model, scheduler=c, steps=int(steps), denoise=1.0)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            out, _ = _core("SamplerCustomAdvanced", noise=noise, guider=guider, sampler=sampler_obj, sigmas=sigmas, latent_image=latent)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            secs.append(time.perf_counter() - t0)
            outs.append(out["samples"])
        result = dict(latent)
        result["samples"] = torch.cat(outs, dim=0)
        result.pop("batch_index", None)
        result.pop("noise_mask", None)
        labels = "\n".join(pair_caption(s, c, t) for (s, c), t in zip(todo, secs))
        return (result, labels, time_table(todo, secs, int(steps)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SamplerSweep", SYSamplerSweep)
NODE_DISPLAY_NAME_MAPPINGS["SYSamplerSweep"] = "Sampler Sweep SY"
