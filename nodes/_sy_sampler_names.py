"""Sampler and scheduler name lists. Pure Python; comfy is imported lazily inside the functions."""

FALLBACK_SAMPLERS = [
    "euler", "euler_ancestral", "heun", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_sde",
    "uni_pc", "res_multistep", "ddim",
]
FALLBACK_SCHEDULERS = [
    "simple", "sgm_uniform", "karras", "exponential", "ddim_uniform", "beta",
    "normal", "linear_quadratic", "kl_optimal",
]


def sampler_names():
    """Valid sampler names from ComfyUI, or a safe fallback list when comfy cannot be imported."""
    try:
        import comfy.samplers
        names = list(comfy.samplers.KSampler.SAMPLERS)
        if names:
            return names
    except Exception:
        pass
    return list(FALLBACK_SAMPLERS)


def scheduler_names():
    """Valid scheduler names from ComfyUI, or a safe fallback list when comfy cannot be imported."""
    try:
        import comfy.samplers
        names = list(comfy.samplers.KSampler.SCHEDULERS)
        if names:
            return names
    except Exception:
        pass
    return list(FALLBACK_SCHEDULERS)


def pick_valid(name, valid, fallbacks):
    """Return `name` when it is in `valid`; else the first of `fallbacks` that is valid; else the first valid name."""
    if name in valid:
        return name
    for f in fallbacks:
        if f in valid:
            return f
    if not valid:
        raise ValueError("no sampler or scheduler names are available")
    return valid[0]
