"""H3 Save Bundle SY and H3 Load Bundle SY: keep a latent, its prompt, seed and reference pictures together in one folder."""
import json
import os
import re
from datetime import datetime

try:
    from ._sy_safe_paths import clean_token, root_folder, safe_join, tensor_to_pil
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import clean_token, root_folder, safe_join, tensor_to_pil
    from _sy_common import category, register

BUNDLE_ROOT = "sy_bundles"
LATENT_FILE = "latent.safetensors"
PROMPT_FILE = "prompt.txt"
META_FILE = "meta.json"
NO_BUNDLES = "(none)"
MAX_SEED = 2 ** 64 - 1
MAX_PROMPT_CHARS = 5_000_000
REF_SLOTS = (1, 2, 3)


def ref_file(slot):
    return "ref_%d.png" % int(slot)


def clean_bundle_name(name):
    """Pure function. A safe folder name from the box text. Refuses empty names, '..', '/' and a backslash."""
    raw = str(name if name is not None else "")
    if "/" in raw or "\\" in raw:
        raise ValueError("bundle_name must not contain / or a backslash: type a plain name such as h3-preview-001")
    if ".." in raw:
        raise ValueError("bundle_name must not contain '..': type a plain name such as h3-preview-001")
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", clean_token(raw))
    if not cleaned.strip("_"):
        raise ValueError("bundle_name is empty: type a name with letters or numbers, such as h3-preview-001")
    return cleaned


def build_meta(seed, prompt, refs, now=None):
    """Pure function. The meta.json content. `refs` is a list of slot numbers that are filled."""
    seed = int(seed)
    if seed < 0 or seed > MAX_SEED:
        raise ValueError("seed must be between 0 and %d, got %d" % (MAX_SEED, seed))
    prompt = str(prompt)
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError("prompt is too long (%d characters, max %d)" % (len(prompt), MAX_PROMPT_CHARS))
    slots = sorted({int(r) for r in refs})
    if any(s not in REF_SLOTS for s in slots):
        raise ValueError("reference slots must be 1, 2 or 3, got %r" % (slots,))
    return {"seed": seed, "prompt_chars": len(prompt), "has_refs": slots,
            "created": (now or datetime.now()).isoformat(timespec="seconds")}


def parse_meta(text):
    """Pure function. Read meta.json text. Returns (seed, has_refs). Raises ValueError naming meta.json when wrong."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        raise ValueError("%s is not valid JSON: save the bundle again" % META_FILE)
    if not isinstance(data, dict) or not isinstance(data.get("seed"), int) or isinstance(data.get("seed"), bool):
        raise ValueError("%s has no whole-number seed: save the bundle again" % META_FILE)
    seed = data["seed"]
    if seed < 0 or seed > MAX_SEED:
        raise ValueError("%s has a seed outside 0..%d: save the bundle again" % (META_FILE, MAX_SEED))
    refs = data.get("has_refs", [])
    if not isinstance(refs, list) or any((not isinstance(r, int)) or r not in REF_SLOTS for r in refs):
        raise ValueError("%s has a bad has_refs list: save the bundle again" % META_FILE)
    return seed, sorted(set(refs))


def bundle_choices(entries):
    """Pure function. `entries` is a list of (folder_name, has_latent). Sorted names that hold a latent, or ['(none)']."""
    names = sorted({str(n) for n, ok in entries if ok}, key=lambda s: (s.lower(), s))
    return names or [NO_BUNDLES]


def bundles_root(output_dir):
    return safe_join(output_dir, BUNDLE_ROOT)


def list_bundles(output_dir):
    """Folder names under output/sy_bundles that hold latent.safetensors."""
    base = bundles_root(output_dir)
    entries = []
    if os.path.isdir(base):
        for n in os.listdir(base):
            p = os.path.join(base, n)
            if os.path.isdir(p):
                entries.append((n, os.path.isfile(os.path.join(p, LATENT_FILE))))
    return bundle_choices(entries)


def bundle_folder(output_dir, name):
    """The full folder path of a bundle under output/sy_bundles (not created)."""
    if str(name) == NO_BUNDLES:
        raise ValueError("no bundles were found: save a bundle first, then pick it in the list")
    return safe_join(bundles_root(output_dir), clean_bundle_name(name))


def write_bundle(output_dir, name, latent, prompt, seed, refs, now=None):
    """Write the bundle folder. `refs` maps slot number to a PIL picture. Returns (folder_name, folder_path)."""
    from safetensors.torch import save_file
    if not isinstance(latent, dict):
        raise ValueError("latent input is not a latent: connect a LATENT output")
    tensors = {str(k): v.detach().cpu().contiguous() for k, v in latent.items() if hasattr(v, "detach")}
    if not tensors:
        raise ValueError("latent holds no tensor to save: connect a LATENT output")
    clean = clean_bundle_name(name)
    meta = build_meta(seed, prompt, list(refs.keys()), now)
    folder = bundle_folder(output_dir, clean)
    os.makedirs(folder, exist_ok=True)
    save_file(tensors, os.path.join(folder, LATENT_FILE))
    with open(os.path.join(folder, PROMPT_FILE), "w", encoding="utf-8", newline="\n") as f:
        f.write(str(prompt))
    for slot, pil in refs.items():
        pil.save(os.path.join(folder, ref_file(slot)), format="PNG")
    with open(os.path.join(folder, META_FILE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f)
    return clean, folder


def read_bundle(output_dir, name):
    """Read a bundle. Returns (latent_dict, prompt, seed, folder, ref_1_numpy_or_None)."""
    folder = bundle_folder(output_dir, name)
    for fname in (LATENT_FILE, META_FILE):
        if not os.path.isfile(os.path.join(folder, fname)):
            raise ValueError("bundle is missing %s: %s. Save the bundle again." % (fname, os.path.basename(folder)))
    with open(os.path.join(folder, META_FILE), "r", encoding="utf-8") as f:
        seed, refs = parse_meta(f.read())
    from safetensors.torch import load as load_bytes
    with open(os.path.join(folder, LATENT_FILE), "rb") as f:  # read into memory so the file is not locked on Windows
        latent = load_bytes(f.read())
    prompt = ""
    pp = os.path.join(folder, PROMPT_FILE)
    if os.path.isfile(pp):
        with open(pp, "r", encoding="utf-8") as f:
            prompt = f.read()
    ref = None
    rp = os.path.join(folder, ref_file(1))
    if 1 in refs and os.path.isfile(rp):
        import numpy as np
        from PIL import Image
        with Image.open(rp) as im:
            ref = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    return latent, prompt, seed, folder, ref


class SYH3SaveBundle:
    DESCRIPTION = "Saves a latent, its prompt, seed and up to 3 reference pictures into one folder in the output folder."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("bundle",)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT", {"tooltip": "The latent to keep. Every tensor in it is saved."}),
                "prompt": ("STRING", {"forceInput": True, "tooltip": "The prompt text that made this latent."}),
                "seed": ("INT", {"forceInput": True, "min": 0, "max": MAX_SEED, "tooltip": "The seed that made this latent."}),
                "bundle_name": ("STRING", {"default": "h3-preview-001", "tooltip": "Folder name in output/sy_bundles. Same name overwrites that bundle."}),
            },
            "optional": {
                "reference_1": ("IMAGE", {"tooltip": "Optional picture saved as ref_1.png (first picture of the batch)."}),
                "reference_2": ("IMAGE", {"tooltip": "Optional picture saved as ref_2.png (first picture of the batch)."}),
                "reference_3": ("IMAGE", {"tooltip": "Optional picture saved as ref_3.png (first picture of the batch)."}),
            },
        }

    def run(self, latent, prompt, seed, bundle_name, reference_1=None, reference_2=None, reference_3=None):
        refs = {}
        for slot, img in zip(REF_SLOTS, (reference_1, reference_2, reference_3)):
            if img is not None:
                if int(img.shape[0]) < 1:
                    raise ValueError("reference_%d has no picture in its batch" % slot)
                refs[slot] = tensor_to_pil(img[0])
        name, _folder = write_bundle(root_folder("output"), bundle_name, latent, prompt, seed, refs)
        return (name,)


class SYH3LoadBundle:
    DESCRIPTION = "Loads a bundle made by H3 Save Bundle: the latent, prompt, seed, folder path and the first reference picture."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT", "STRING", "INT", "STRING", "IMAGE")
    RETURN_NAMES = ("latent", "prompt", "seed", "bundle_folder", "reference_1")

    @classmethod
    def INPUT_TYPES(cls):
        try:
            choices = list_bundles(root_folder("output"))
        except Exception:
            choices = [NO_BUNDLES]
        return {"required": {"bundle": (choices, {"tooltip": "A saved bundle folder from output/sy_bundles."})}}

    @classmethod
    def IS_CHANGED(cls, bundle):
        try:
            return os.path.getmtime(os.path.join(bundle_folder(root_folder("output"), bundle), LATENT_FILE))
        except Exception:
            return float("nan")

    def run(self, bundle):
        import torch
        latent, prompt, seed, folder, ref = read_bundle(root_folder("output"), bundle)
        if ref is None:
            image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
        else:
            image = torch.from_numpy(ref).unsqueeze(0)
        return (latent, prompt, seed, folder, image)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SaveBundle", SYH3SaveBundle)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3LoadBundle", SYH3LoadBundle)
