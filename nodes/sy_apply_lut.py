"""Apply LUT SY: change the colours of a picture with a built-in look or a .cube colour table."""
import os

try:
    from ._sy_common import category, register, safe_join
    from ._sy_image_ops import need_image
    from ._sy_lut import BUILTIN_NAMES, MAX_FILE_BYTES, builtin_cube, parse_cube
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join
    from _sy_image_ops import need_image
    from _sy_lut import BUILTIN_NAMES, MAX_FILE_BYTES, builtin_cube, parse_cube

_FILE_CACHE = {}


def lut_choices(file_names):
    """Pure function. Built-in looks first, then every .cube file name (sorted, no duplicates)."""
    files = sorted({str(n) for n in (file_names or []) if str(n).lower().endswith(".cube")})
    return list(BUILTIN_NAMES) + files


def check_lut_name(name):
    """Pure function. Plain refusal for a file name that could leave the LUT folders."""
    s = str(name or "").replace("\\", "/")
    if not s.strip():
        raise ValueError("The LUT name is empty. Choose a look from the list.")
    if s.startswith("/") or ":" in s:
        raise ValueError("The LUT name %r points outside the LUT folders. Use only a file name from the list." % name)
    if any(p == ".." for p in s.split("/")):
        raise ValueError("The LUT name %r contains '..'. Use only a file name from the list." % name)
    if not s.lower().endswith(".cube"):
        raise ValueError("The LUT file %r is not a .cube file." % name)
    return s


def resolve_lut_path(name, folders):
    """Pure function. Find the file inside one of the given folders; refuse anything outside them."""
    s = check_lut_name(name)
    for base in folders:
        try:
            p = safe_join(base, *s.split("/"))
        except ValueError:
            continue
        if os.path.isfile(p):
            return p
    raise ValueError("The LUT file %r was not found in the LUT folders (models/luts or input/luts)." % name)


def lut_folders():
    """The two folders searched for .cube files. ComfyUI is imported only here, and a failure just gives an empty list."""
    out = []
    try:
        import folder_paths
        for p in (os.path.join(folder_paths.models_dir, "luts"), os.path.join(folder_paths.get_input_directory(), "luts")):
            out.append(p)
            try:
                folder_paths.add_model_folder_path("luts", p)
            except Exception:
                pass
    except Exception:
        pass
    return out


def list_lut_files():
    """Every .cube file in the LUT folders, as names relative to the folder."""
    names = []
    for base in lut_folders():
        if not os.path.isdir(base):
            continue
        for root, _dirs, files in os.walk(base):
            for f in files:
                if f.lower().endswith(".cube"):
                    names.append(os.path.relpath(os.path.join(root, f), base).replace("\\", "/"))
    return names


def read_lut_file(name):
    path = resolve_lut_path(name, lut_folders())
    size = os.path.getsize(path)
    if size > MAX_FILE_BYTES:
        raise ValueError("The LUT file %r is bigger than 20 MB. Use a smaller .cube file." % name)
    key = (path, os.path.getmtime(path), size)
    cube = _FILE_CACHE.get(key)
    if cube is None:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            cube = parse_cube(f.read())
        _FILE_CACHE.clear()
        _FILE_CACHE[key] = cube
    return cube


def pick_cube(lut, lut_text):
    """Pure function (plus the file read for a file name). Text wins over the list. Returns a cube dict or None for 'none'."""
    if lut_text and str(lut_text).strip():
        return parse_cube(str(lut_text))
    if lut == "none":
        return None
    if lut in BUILTIN_NAMES:
        return builtin_cube(lut)
    return read_lut_file(lut)


def apply_cube_tensor(rgb, cube, strength):
    """Torch part. rgb is [B,H,W,3] in 0..1. Trilinear sampling for 3D tables, linear for 1D, then a blend by strength."""
    import torch
    n = cube["size"]
    dev, dt = rgb.device, rgb.dtype
    table = torch.tensor(cube["table"], dtype=dt, device=dev).view(-1, 3)
    lo = torch.tensor(cube["domain_min"], dtype=dt, device=dev)
    hi = torch.tensor(cube["domain_max"], dtype=dt, device=dev)
    x = ((rgb - lo) / (hi - lo)).clamp(0.0, 1.0) * (n - 1)
    if cube["kind"] == "1D":
        i0 = x.floor().clamp(0, n - 2)
        f = x - i0
        i0 = i0.long()
        chans = []
        for c in range(3):
            a = table[i0[..., c], c]
            b = table[i0[..., c] + 1, c]
            chans.append(a * (1 - f[..., c]) + b * f[..., c])
        out = torch.stack(chans, dim=-1)
    else:
        i0 = x.floor().clamp(0, n - 2)
        f = x - i0
        i0 = i0.long()
        r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
        fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
        out = torch.zeros_like(rgb)
        for db in (0, 1):
            for dg in (0, 1):
                for dr in (0, 1):
                    w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                    idx = (b0 + db) * n * n + (g0 + dg) * n + (r0 + dr)
                    out = out + w * table[idx]
    s = float(strength)
    return rgb + (out - rgb) * s


class SYApplyLUT:
    DESCRIPTION = ("Changes the colours of a picture with a colour look. Pick a built-in look, or a .cube file from the "
                   "models/luts or input/luts folder, or paste the text of a .cube file into lut_text (the text wins). "
                   "Strength 0 keeps the picture, 1 gives the full look. A transparent background (alpha) stays as it was.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    @classmethod
    def INPUT_TYPES(cls):
        try:
            names = list_lut_files()
        except Exception:
            names = []
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture to colour. RGB or RGBA; transparency is kept."}),
                "lut": (lut_choices(names), {"default": "none", "tooltip": "A built-in look, or a .cube file from models/luts or input/luts."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 = original colours, 1 = the full look."}),
            },
            "optional": {
                "lut_text": ("STRING", {"default": "", "multiline": True, "tooltip": "Paste the text of a .cube file here. If filled, it is used instead of the list."}),
            },
        }

    def run(self, image, lut, strength=1.0, lut_text=""):
        need_image(image)
        if not 0.0 <= float(strength) <= 1.0:
            raise ValueError("strength must be between 0 and 1, got %s" % strength)
        if image.shape[-1] not in (3, 4):
            raise ValueError("Apply LUT needs a colour picture with 3 (RGB) or 4 (RGBA) channels, got %d." % image.shape[-1])
        cube = pick_cube(lut, lut_text)
        if cube is None or float(strength) == 0.0:
            return (image,)
        import torch
        rgb = apply_cube_tensor(image[..., :3], cube, strength).clamp(0.0, 1.0)
        if image.shape[-1] == 4:
            rgb = torch.cat([rgb, image[..., 3:4]], dim=-1)
        return (rgb.contiguous(),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ApplyLUT", SYApplyLUT)
NODE_DISPLAY_NAME_MAPPINGS["SYApplyLUT"] = "Apply LUT SY"
