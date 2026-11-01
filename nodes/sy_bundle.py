"""Bundle SY / Unbundle SY: carry model, clip, vae, prompts, seed and sampler settings on one wire."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")

OBJECT_KEYS = ("model", "clip", "vae", "positive", "negative", "latent", "image", "mask")
NUMBER_KEYS = ("seed", "steps", "cfg", "denoise", "width", "height")
INT_KEYS = ("seed", "steps", "width", "height")
STRING_KEYS = ("sampler_name", "scheduler", "text", "text2")
STANDARD_KEYS = OBJECT_KEYS + NUMBER_KEYS + STRING_KEYS      # the keys with their own slot
UNBUNDLE_ORDER = ("bundle",) + OBJECT_KEYS + NUMBER_KEYS + STRING_KEYS + ("extra", "keys", "missing")
EXTRA_KEY = "extra"


def need_bundle(b, what="bundle"):
    """Pure function. A bundle is a plain dict; anything else gets a plain refusal."""
    if not isinstance(b, dict):
        raise ValueError("The %s input must come from a Bundle SY node, but it is a %s. Connect the bundle output of Bundle SY."
                         % (what, type(b).__name__))
    return b


def make_bundle(base=None, **items):
    """Pure function. Copy of base with the given items added or replaced. An item that is None is left out. The incoming dict is never changed."""
    out = {}
    if base is not None:
        out.update(need_bundle(base, "base bundle"))
    for k, v in items.items():
        if v is not None:
            out[k] = v
    return out


def bundle_get(b, key, default=None):
    return need_bundle(b).get(key, default)


def keys_text(b):
    """Pure function. The keys inside the bundle as one comma list, in the order they were added."""
    return ", ".join(str(k) for k in need_bundle(b))


def missing_keys(b, wanted):
    """Pure function. Which of the wanted keys the bundle does not hold."""
    need_bundle(b)
    return [k for k in wanted if k not in b]


def custom_keys(b):
    """Pure function. Keys that have no slot of their own (named by extra_name)."""
    return [k for k in need_bundle(b) if k not in STANDARD_KEYS]


def clean_extra_name(name):
    """Pure function. The key for the free item: the given name, or 'extra' when empty. A name used by a standard slot is refused."""
    s = str(name or "").strip()
    if not s:
        return EXTRA_KEY
    if s in STANDARD_KEYS:
        raise ValueError("extra_name %r is already used by a normal slot of Bundle SY. Use the matching input, or pick another name." % s)
    return s


def extra_value(b):
    """Pure function. The free item: key 'extra' first, else the first custom key."""
    need_bundle(b)
    if EXTRA_KEY in b:
        return b[EXTRA_KEY]
    for k in b:
        if k not in STANDARD_KEYS:
            return b[k]
    return None


def unbundle(b):
    """Pure function. The 22 outputs of Unbundle SY in their fixed order (UNBUNDLE_ORDER)."""
    need_bundle(b)
    out = [b]
    missing = []
    for k in OBJECT_KEYS:
        if k in b:
            out.append(b[k])
        else:
            out.append(None)
            missing.append(k)
    for k in NUMBER_KEYS:
        if k in b:
            v = b[k]
            out.append(int(v) if k in INT_KEYS else float(v))
        else:
            out.append(0 if k in INT_KEYS else 0.0)
            missing.append(k)
    for k in STRING_KEYS:
        if k in b:
            out.append(str(b[k]))
        else:
            out.append("")
            missing.append(k)
    if EXTRA_KEY in b or custom_keys(b):
        out.append(extra_value(b))
    else:
        out.append(None)
        missing.append(EXTRA_KEY)
    out.append(keys_text(b))
    out.append(", ".join(missing))
    return tuple(out)


class SYBundle:
    DESCRIPTION = ("Packs model, clip, vae, prompts, latent, picture, mask, seed and sampler settings into one wire (a bundle). "
                   "Plug in only what you have; an unplugged input is simply left out. Give it an earlier bundle and the new "
                   "inputs are added to it or replace the same item. Open the bundle again with Unbundle SY.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("SY_BUNDLE", "STRING")
    RETURN_NAMES = ("bundle", "keys")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "bundle": ("SY_BUNDLE", {"tooltip": "An earlier bundle to add to. Inputs below replace items with the same name."}),
                "model": ("MODEL", {"tooltip": "The model (checkpoint) to carry."}),
                "clip": ("CLIP", {"tooltip": "The text encoder (clip) to carry."}),
                "vae": ("VAE", {"tooltip": "The vae to carry."}),
                "positive": ("CONDITIONING", {"tooltip": "The positive prompt (conditioning)."}),
                "negative": ("CONDITIONING", {"tooltip": "The negative prompt (conditioning)."}),
                "latent": ("LATENT", {"tooltip": "A latent to carry."}),
                "image": ("IMAGE", {"tooltip": "A picture to carry."}),
                "mask": ("MASK", {"tooltip": "A mask to carry."}),
                "seed": ("INT", {"forceInput": True, "tooltip": "The seed number. Connect a wire to include it."}),
                "steps": ("INT", {"forceInput": True, "tooltip": "The number of steps. Connect a wire to include it."}),
                "cfg": ("FLOAT", {"forceInput": True, "tooltip": "The cfg (prompt strength). Connect a wire to include it."}),
                "denoise": ("FLOAT", {"forceInput": True, "tooltip": "The denoise amount. Connect a wire to include it."}),
                "width": ("INT", {"forceInput": True, "tooltip": "The picture width. Connect a wire to include it."}),
                "height": ("INT", {"forceInput": True, "tooltip": "The picture height. Connect a wire to include it."}),
                "sampler_name": ("STRING", {"forceInput": True, "tooltip": "The sampler name as text. Connect a wire to include it."}),
                "scheduler": ("STRING", {"forceInput": True, "tooltip": "The scheduler name as text. Connect a wire to include it."}),
                "text": ("STRING", {"forceInput": True, "tooltip": "A free text, for example the prompt. Connect a wire to include it."}),
                "text2": ("STRING", {"forceInput": True, "tooltip": "A second free text. Connect a wire to include it."}),
                "extra_name": ("STRING", {"default": "", "tooltip": "A name for the extra item below. Empty means the name 'extra'."}),
                "extra": (ANY, {"tooltip": "One free item of any kind, stored under extra_name."}),
            },
        }

    def run(self, bundle=None, model=None, clip=None, vae=None, positive=None, negative=None, latent=None, image=None,
            mask=None, seed=None, steps=None, cfg=None, denoise=None, width=None, height=None, sampler_name=None,
            scheduler=None, text=None, text2=None, extra_name="", extra=None):
        items = dict(model=model, clip=clip, vae=vae, positive=positive, negative=negative, latent=latent, image=image,
                     mask=mask, seed=seed, steps=steps, cfg=cfg, denoise=denoise, width=width, height=height,
                     sampler_name=sampler_name, scheduler=scheduler, text=text, text2=text2)
        if extra is not None:
            items[clean_extra_name(extra_name)] = extra
        out = make_bundle(bundle, **items)
        return (out, keys_text(out))


class SYUnbundle:
    DESCRIPTION = ("Opens a bundle made by Bundle SY and gives every item its own output. An item that is not in the bundle "
                   "does not crash anything: pictures, models and similar come out empty (None), numbers come out as 0, and "
                   "texts come out empty. The last output, missing, lists the names that were not in the bundle, so you can "
                   "see what to plug into Bundle SY.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("SY_BUNDLE", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT", "IMAGE", "MASK",
                    "INT", "INT", "FLOAT", "FLOAT", "INT", "INT", "STRING", "STRING", "STRING", "STRING", ANY, "STRING", "STRING")
    RETURN_NAMES = UNBUNDLE_ORDER

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"bundle": ("SY_BUNDLE", {"tooltip": "The bundle to open. It comes from Bundle SY."})}}

    def run(self, bundle):
        return unbundle(bundle)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Bundle", SYBundle)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Unbundle", SYUnbundle)
