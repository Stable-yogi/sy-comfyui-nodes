"""Setup Doctor SY: checks this ComfyUI (Manager, node packs, start settings, model folders, file places) and says each fix in plain words."""
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

GB = 1024 ** 3
MANAGER_NAMES = ("comfyui-manager", "comfyui_manager")
# Folders a normal image or video workflow reads. An empty one is worth a line, not an error.
MAIN_FOLDERS = ("checkpoints", "diffusion_models", "loras", "vae", "text_encoders", "upscale_models")
TEXT_ENCODER_WORDS = ("t5xxl", "umt5", "clip_l", "clip_g", "text_encoder", "qwen_2.5_vl", "qwen2.5_vl", "qwen3vl", "qwen3_vl", "gemma", "llava_llama")
UPSCALER_WORDS = ("esrgan", "realesr", "4x-", "4x_", "2x-", "2x_", "_x2", "_x4", "x4plus", "swinir", "dat_")


def manager_found(pack_dirs):
    """Pure function. True when one of the node pack folder names is ComfyUI Manager."""
    return any(os.path.basename(str(d)).lower().rstrip("/\\") in MANAGER_NAMES for d in pack_dirs)


def failed_packs(pack_dirs, loaded_dirs):
    """Pure function. Node pack folders that exist but did not load (hidden, disabled and cache folders are skipped)."""
    loaded = {os.path.normcase(os.path.abspath(str(d))) for d in loaded_dirs}
    out = []
    for d in pack_dirs:
        name = os.path.basename(str(d).rstrip("/\\"))
        low = name.lower()
        if not name or low.startswith((".", "__")) or low.endswith(".disabled") or low.endswith((".py", ".pyc", ".txt", ".md", ".bak", ".example", ".json")):
            continue
        if os.path.normcase(os.path.abspath(str(d))) not in loaded:
            out.append(name)
    return sorted(out, key=str.lower)


def flag_notes(flags):
    """Pure function. `flags` maps start setting names to their values. Returns plain lines for settings that change speed or memory."""
    notes = []
    if flags.get("cpu"):
        notes.append("ComfyUI runs on the processor only (--cpu). Pictures take minutes. Remove --cpu from the start file if you have an NVIDIA card.")
    if flags.get("novram"):
        notes.append("--novram is on: every model stays in normal memory. Very slow; use it only when nothing else works.")
    elif flags.get("lowvram"):
        notes.append("--lowvram is on: models are moved to the card piece by piece. Slower, but big models fit on a small card.")
    if flags.get("highvram") or flags.get("gpu_only"):
        notes.append("--highvram or --gpu-only is on: models stay on the card. Fast, but a second big model can run out of memory.")
    if flags.get("force_fp32"):
        notes.append("--force-fp32 is on: everything runs in full precision. Uses about twice the memory and is slower.")
    if flags.get("disable_smart_memory"):
        notes.append("--disable-smart-memory is on: models are unloaded after every run. Saves memory, but each run loads again.")
    return notes


def classify_misplaced(folder, name, size_bytes):
    """Pure function. Returns (better_folder, why) when a file looks like it sits in the wrong model folder, else None.
    It only reads the file name and size; it never opens the file."""
    low = os.path.basename(str(name)).lower()
    gb = (size_bytes or 0) / GB
    if folder in ("checkpoints", "diffusion_models", "unet"):
        if "lora" in low and gb < 3:
            return "loras", "the name says LoRA"
        if "vae" in low and 0 < gb < 1.5 and not any(w in low for w in ("_with_vae", "-with-vae", "bakedvae", "baked_vae", "baked-vae")):
            return "vae", "the name says VAE and the file is small (%.2f GB)" % gb
        if any(w in low for w in TEXT_ENCODER_WORDS):
            return "text_encoders", "the name says text encoder"
        if low.endswith(".pth") and any(w in low for w in UPSCALER_WORDS):
            return "upscale_models", "the name says upscale model"
    if folder == "loras" and gb > 3 and "lora" not in low:
        return "checkpoints or diffusion_models", "the name does not say LoRA and the file is big (%.1f GB), so it is likely a full model" % gb
    if folder == "vae":
        if any(w in low for w in TEXT_ENCODER_WORDS):
            return "text_encoders", "the name says text encoder"
        if gb > 2 and "vae" not in low:
            return "checkpoints or diffusion_models", "the name does not say VAE and the file is big (%.1f GB)" % gb
    return None


def build_report(version, packs_failed, has_manager, flag_lines, empty_folders, misplaced, sy_version="", device_line=""):
    """Pure function. Returns (report, fix_list, problem_count). `misplaced` = [(folder, name, better, why), ...]."""
    fixes = []
    lines = ["SETUP DOCTOR", "ComfyUI %s%s" % (version or "(version unknown)", (", SY Nodes %s" % sy_version) if sy_version else "")]
    if device_line:
        lines.append(device_line)
    lines.append("")
    if has_manager:
        lines.append("OK   ComfyUI Manager is installed.")
    else:
        lines.append("TIP  ComfyUI Manager is not installed. It is not needed to run workflows, but it installs missing node packs with one click.")
    if packs_failed:
        lines.append("FIX  %d node pack%s did not load: %s" % (len(packs_failed), "" if len(packs_failed) == 1 else "s", ", ".join(packs_failed)))
        fixes.append("Node packs that did not load (%s): read the lines that say IMPORT FAILED in the ComfyUI window, "
                     "then update the pack or install what it needs. Workflows that use these nodes show them red." % ", ".join(packs_failed))
    else:
        lines.append("OK   Every node pack folder loaded.")
    for note in flag_lines:
        lines.append("NOTE " + note)
    for folder in empty_folders:
        lines.append("NOTE models/%s is empty." % folder)
    for folder, name, better, why in misplaced:
        lines.append("FIX  %s is in models/%s, but %s: it belongs in models/%s." % (name, folder, why, better))
        fixes.append("Move %s from models/%s to models/%s, then press R in ComfyUI (refresh) or restart." % (name, folder, better))
    problems = len(fixes)
    lines.append("")
    lines.append("Nothing to fix." if problems == 0 else "%d thing%s to fix (see fix_list)." % (problems, "" if problems == 1 else "s"))
    return "\n".join(lines), "\n".join("%d. %s" % (i + 1, f) for i, f in enumerate(fixes)), problems


def _sy_version():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(root, "pyproject.toml"), "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"\'')
    except OSError:
        pass
    return ""


def _device_line():
    try:
        import torch
        if torch.cuda.is_available():
            i = torch.cuda.current_device()
            p = torch.cuda.get_device_properties(i)
            return "Graphics card: %s, %.0f GB, PyTorch %s" % (p.name, p.total_memory / GB, torch.__version__)
        return "No NVIDIA graphics card seen by PyTorch %s." % torch.__version__
    except Exception:
        return ""


def gather_model_files(folder_paths, folders):
    """Returns {folder: [(name, size_bytes)]} from ComfyUI's own lists."""
    out = {}
    for folder in folders:
        try:
            names = folder_paths.get_filename_list(folder)
        except Exception:
            continue
        rows = []
        for n in names:
            try:
                p = folder_paths.get_full_path(folder, n)
                rows.append((n, os.path.getsize(p) if p else 0))
            except OSError:
                rows.append((n, 0))
        out[folder] = rows
    return out


class SYSetupDoctor:
    DESCRIPTION = ("Checks this ComfyUI and says each fix in plain words: is ComfyUI Manager there, did every node pack load, "
                   "which start settings slow it down, which model folders are empty, and which model files sit in the wrong folder. "
                   "It only reads; it never moves or changes a file.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("report", "fix_list", "problem_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "check_node_packs": ("BOOLEAN", {"default": True, "tooltip": "Look for node packs that did not load (they make red nodes)."}),
            "check_start_settings": ("BOOLEAN", {"default": True, "tooltip": "Explain start settings such as --lowvram or --cpu that change speed or memory."}),
            "check_model_places": ("BOOLEAN", {"default": True, "tooltip": "Look for empty model folders and for files in the wrong folder (by name and size)."}),
        }}

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")  # always look again: files may have moved since the last run

    def run(self, check_node_packs=True, check_start_settings=True, check_model_places=True):
        try:
            import folder_paths  # inside ComfyUI only
            import nodes as comfy_nodes
        except ImportError:
            raise ValueError("Setup Doctor SY reads ComfyUI's own settings and folders, so it only runs inside ComfyUI.")
        try:
            from comfyui_version import __version__ as version
        except Exception:
            version = ""
        pack_dirs = []
        for base in folder_paths.get_folder_paths("custom_nodes"):
            try:
                pack_dirs.extend(os.path.join(base, n) for n in os.listdir(base) if os.path.isdir(os.path.join(base, n)))
            except OSError:
                continue
        has_manager = manager_found(pack_dirs)
        if not has_manager:
            try:
                import importlib.util
                has_manager = importlib.util.find_spec("comfyui_manager") is not None  # pip-installed Manager
            except Exception:
                pass
        packs = failed_packs(pack_dirs, getattr(comfy_nodes, "LOADED_MODULE_DIRS", {}).values()) if check_node_packs else []
        flags = []
        if check_start_settings:
            try:
                from comfy.cli_args import args
                flags = flag_notes(vars(args))
            except Exception:
                flags = []
        empty, misplaced = [], []
        if check_model_places:
            files = gather_model_files(folder_paths, MAIN_FOLDERS)
            empty = [f for f in MAIN_FOLDERS if f in files and not files[f]]
            seen = set()  # one folder can be listed under two names (checkpoints and diffusion_models): report each file once
            for folder, rows in files.items():
                for name, size in rows:
                    hit = classify_misplaced(folder, name, size)
                    if hit and name not in seen:
                        seen.add(name)
                        misplaced.append((folder, name, hit[0], hit[1]))
        report, fixes, count = build_report(version, packs, has_manager, flags, empty, misplaced, _sy_version(), _device_line())
        return {"ui": {"text": [report]}, "result": (report, fixes, count)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SetupDoctor", SYSetupDoctor)
