"""Sampler SY: one box that does the whole sampling job (noise, sigmas, guider, sampler) with a Fast switch."""
try:
    from ._sy_common import category, register
    from ._sy_sampler_names import sampler_names, scheduler_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_sampler_names import sampler_names, scheduler_names

MAX_SEED = 2 ** 64 - 1


def pick_steps(fast_mode, steps, fast_steps):
    """Pure function. Fast mode uses fast_steps, otherwise steps. Both must be at least 1."""
    chosen = fast_steps if fast_mode else steps
    chosen = int(chosen)
    if chosen < 1:
        raise ValueError("%s must be at least 1, got %s" % ("fast_steps" if fast_mode else "steps", chosen))
    return chosen


def needs_cfg_guider(has_negative, cfg):
    """Pure function. A negative prompt with cfg other than 1 needs the CFG guider. Otherwise the plain guider is enough."""
    return bool(has_negative) and abs(float(cfg) - 1.0) > 1e-6


def check_seed(seed):
    """Pure function. The seed must be a whole number from 0 to 2**64-1."""
    value = int(seed)
    if value < 0 or value > MAX_SEED:
        raise ValueError("seed must be between 0 and %d, got %d" % (MAX_SEED, value))
    return value


def settings_text(seed, steps, fast_mode, cfg, sampler, scheduler, denoise, guider):
    """Pure function. One readable block of the settings that were used. Handy to save next to a picture."""
    return "\n".join([
        "mode: %s" % ("fast" if fast_mode else "quality"),
        "steps: %d" % steps,
        "cfg: %g (%s guider)" % (float(cfg), guider),
        "sampler: %s" % sampler,
        "scheduler: %s" % scheduler,
        "denoise: %g" % float(denoise),
        "seed: %d" % seed,
    ])


def _core(name, **kwargs):
    """Run a ComfyUI core node by its name. Works for the old and the new node style, so a ComfyUI update does not break this."""
    import nodes as comfy_nodes
    cls = comfy_nodes.NODE_CLASS_MAPPINGS.get(name)
    if cls is None:
        raise ValueError("this ComfyUI has no core node %r, so Sampler SY cannot run" % name)
    out = getattr(cls(), cls.FUNCTION)(**kwargs)
    if isinstance(out, dict) and "result" in out:
        out = out["result"]
    return tuple(out)


class SYSampler:
    DESCRIPTION = ("The whole sampling job in one box: noise, steps, guider and sampler. "
                   "A Fast switch swaps to a short step count. It also gives you the settings it used as text.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "LATENT", "STRING", "INT")
    RETURN_NAMES = ("latent", "denoised", "settings", "seed")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model to sample with."}),
                "positive": ("CONDITIONING", {"tooltip": "What you want in the result (your encoded prompt)."}),
                "latent": ("LATENT", {"tooltip": "The starting latent: an empty one, or one from a picture or clip."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "control_after_generate": True, "tooltip": "Same seed and settings give the same result."}),
                "fast_mode": ("BOOLEAN", {"default": False, "tooltip": "On: use fast_steps. Off: use steps."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 1000, "tooltip": "Steps used when fast mode is off."}),
                "fast_steps": ("INT", {"default": 4, "min": 1, "max": 1000, "tooltip": "Steps used when fast mode is on."}),
                "cfg": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "How strongly to follow the prompt. 1 skips the negative prompt."}),
                "sampler": (sampler_names(), {"default": "euler", "tooltip": "The sampling method. euler is a safe choice."}),
                "scheduler": (scheduler_names(), {"default": "simple", "tooltip": "How the steps are spread over the noise."}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "1 makes a new result. Lower keeps part of the start latent."}),
            },
            "optional": {
                "negative": ("CONDITIONING", {"tooltip": "What you do not want. Used only when cfg is not 1."}),
            },
        }

    def run(self, model, positive, latent, seed, fast_mode, steps, fast_steps, cfg, sampler, scheduler, denoise, negative=None):
        seed = check_seed(seed)
        n_steps = pick_steps(fast_mode, steps, fast_steps)
        use_cfg = needs_cfg_guider(negative is not None, cfg)
        (noise,) = _core("RandomNoise", noise_seed=seed)
        (sampler_obj,) = _core("KSamplerSelect", sampler_name=sampler)
        (sigmas,) = _core("BasicScheduler", model=model, scheduler=scheduler, steps=n_steps, denoise=float(denoise))
        if use_cfg:
            (guider,) = _core("CFGGuider", model=model, positive=positive, negative=negative, cfg=float(cfg))
        else:
            (guider,) = _core("BasicGuider", model=model, conditioning=positive)
        out, denoised = _core("SamplerCustomAdvanced", noise=noise, guider=guider, sampler=sampler_obj, sigmas=sigmas, latent_image=latent)
        text = settings_text(seed, n_steps, fast_mode, cfg, sampler, scheduler, denoise, "CFG" if use_cfg else "basic")
        return (out, denoised, text, seed)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Sampler", SYSampler)
