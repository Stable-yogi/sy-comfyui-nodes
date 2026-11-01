"""Small web helpers for Power Lora Loader SY: a preview picture and the training tags of one LoRA file.

Two read-only routes:
  GET /sy/lora/preview?name=<lora name>  a picture that sits next to the LoRA file (same base name), 2 MB at most
  GET /sy/lora/info?name=<lora name>     the most used training tags, read from the safetensors header only
Only files inside the ComfyUI loras folders can be reached. Nothing is written, nothing leaves this PC.
"""
import json
import os
import re
import struct

PREVIEW_ENDINGS = (".preview.png", ".preview.jpg", ".preview.jpeg", ".preview.webp", ".png", ".jpg", ".jpeg", ".webp")
MAX_PREVIEW_BYTES = 2 * 1024 * 1024
MAX_HEADER_BYTES = 8 * 1024 * 1024
TOP_TAGS = 10
_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
_DRIVE = re.compile(r"^[A-Za-z]:")


def check_lora_name(name):
    """Pure function. A LoRA name from the browser must be a relative path without '..', a drive letter or a leading slash."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("The LoRA name is empty. Pick a LoRA in the list first.")
    if "\x00" in name:
        raise ValueError("The LoRA name contains a character that is not allowed.")
    flat = name.replace("\\", "/")
    if flat.startswith("/") or _DRIVE.match(flat):
        raise ValueError("The LoRA name must be a path inside the loras folder, not an absolute path or a drive letter.")
    if ".." in flat.split("/"):
        raise ValueError("The LoRA name must not contain '..'.")
    return name


def inside_roots(path, roots):
    """Pure function. True when the real path of `path` lies inside one of the real folders in `roots`."""
    try:
        real = os.path.realpath(path)
    except (OSError, ValueError):
        return False
    for root in roots or ():
        base = os.path.realpath(root)
        try:
            if os.path.commonpath([base, real]) == base and real != base:
                return True
        except ValueError:  # different drives
            continue
    return False


def lora_path(name, get_full_path, roots):
    """Find the file of a LoRA name. get_full_path is folder_paths.get_full_path wrapped for 'loras'."""
    check_lora_name(name)
    path = get_full_path(name)
    if not path or not os.path.isfile(path):
        raise ValueError("The LoRA '%s' was not found in the loras folders." % name)
    if not inside_roots(path, roots):
        raise ValueError("The LoRA '%s' is outside the loras folders." % name)
    return path


def find_preview(lora_file, roots):
    """The picture that belongs to a LoRA file, or None. Same base name, one of PREVIEW_ENDINGS, 2 MB at most."""
    base = os.path.splitext(lora_file)[0]
    for ending in PREVIEW_ENDINGS:
        cand = base + ending
        if not os.path.isfile(cand) or not inside_roots(cand, roots):
            continue
        try:
            if os.path.getsize(cand) > MAX_PREVIEW_BYTES:
                continue
        except OSError:
            continue
        return cand
    return None


def mime_of(path):
    return _MIME.get(os.path.splitext(path)[1].lower(), "application/octet-stream")


def read_st_header(path, cap=MAX_HEADER_BYTES):
    """The JSON header of a .safetensors file as a dict. Reads the 8-byte length and the header, nothing else."""
    with open(path, "rb") as f:
        head = f.read(8)
        if len(head) < 8:
            raise ValueError("This file is too short to be a safetensors file.")
        (size,) = struct.unpack("<Q", head)
        if size < 2 or size > cap:
            raise ValueError("The header of this file is missing or larger than %d MB, so it was not read." % (cap // (1024 * 1024)))
        raw = f.read(size)
    if len(raw) < size:
        raise ValueError("This safetensors file is cut off: its header is incomplete.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise ValueError("The header of this file is not readable.")
    if not isinstance(data, dict):
        raise ValueError("The header of this file is not readable.")
    return data


def top_tags(tag_frequency_json, n=TOP_TAGS):
    """Pure function. The n most used tags from the ss_tag_frequency text (or dict) of a trained LoRA.

    The data is {dataset folder: {tag: count}}. Counts of the same tag add up. Ties keep the first-seen order.
    Bad or missing data gives an empty list.
    """
    data = tag_frequency_json
    if isinstance(data, (str, bytes)):
        try:
            data = json.loads(data)
        except ValueError:
            return []
    if not isinstance(data, dict):
        return []
    totals, order = {}, []
    for folder in data.values():
        if not isinstance(folder, dict):
            continue
        for tag, count in folder.items():
            t = str(tag).strip()
            if not t or isinstance(count, bool) or not isinstance(count, (int, float)):
                continue
            if t not in totals:
                totals[t] = 0
                order.append(t)
            totals[t] += count
    ranked = sorted(order, key=lambda t: (-totals[t], order.index(t)))
    return ranked[:max(0, int(n))]


def lora_info(path):
    """{'tags': [...], 'triggers': [...]} from the header of one LoRA file. Empty lists when there is nothing."""
    meta = read_st_header(path).get("__metadata__", {})
    if not isinstance(meta, dict):
        meta = {}
    triggers = []
    for key in ("modelspec.trigger_phrase", "trigger_words", "trigger_word", "ss_trigger_words"):
        val = str(meta.get(key, "")).strip()
        if val:
            triggers = [t.strip() for t in re.split(r"[,\n]+", val) if t.strip()][:TOP_TAGS]
            break
    return {"tags": top_tags(meta.get("ss_tag_frequency"), TOP_TAGS), "triggers": triggers}


_routes_done = False


def register_routes():
    """Add the two /sy/lora routes to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    def _find(request):
        import folder_paths
        name = request.rel_url.query.get("name", "")
        roots = folder_paths.get_folder_paths("loras")
        return lora_path(name, lambda n: folder_paths.get_full_path("loras", n), roots), roots

    async def preview(request):
        try:
            path, roots = _find(request)
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)
        pic = find_preview(path, roots)
        if not pic:
            return web.Response(status=404)
        return web.FileResponse(pic, headers={"Content-Type": mime_of(pic), "Cache-Control": "max-age=60"})

    async def info(request):
        try:
            path, _roots = _find(request)
            if not path.lower().endswith(".safetensors"):
                raise ValueError("Only .safetensors files carry readable training tags.")
            return web.json_response(lora_info(path))
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)

    routes.get("/sy/lora/preview")(preview)
    routes.get("/sy/lora/info")(info)
    _routes_done = True
    return True
