"""Small web helpers for the node buttons: the live size of the size nodes, and the .txt files of the input folder.

Both only read. The size comes from the same pure functions the nodes use, so the preview and the run always agree.
"""
import os

try:
    from ._sy_safe_paths import root_folder
    from .sy_resolution import compute_size
    from .sy_size_presets import preset_size
    from .sy_video_size_presets import video_size
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder
    from sy_resolution import compute_size
    from sy_size_presets import preset_size
    from sy_video_size_presets import video_size

MAX_FILES = 300
MAX_DEPTH = 3


def size_for(node, q):
    """Pure function. Width and height a size node would give for the settings in `q` (a dict of text values)."""
    if node == "SYResolution":
        w, h = compute_size(q.get("model_preset", "Custom"), q.get("aspect", "1:1"), q.get("orientation", "landscape"),
                            float(q.get("megapixels", 1.0)), int(q.get("multiple", 16)))
    elif node == "SYSizePresets":
        w, h = preset_size(q.get("preset", ""))
    elif node == "SYVideoSizePresets":
        w, h = video_size(q.get("resolution", "720p"), q.get("aspect", "16:9"), int(q.get("multiple", 16)))
    else:
        raise ValueError("not a size node: %r" % (node,))
    return {"width": w, "height": h, "megapixels": round(w * h / 1_000_000, 2)}


def list_text_files(base, max_files=MAX_FILES, max_depth=MAX_DEPTH):
    """Pure function. Relative paths (with /) of the .txt files under `base`, sorted, at most `max_files`."""
    base = os.path.realpath(base)
    found = []
    for root, dirs, files in os.walk(base):
        depth = 0 if root == base else os.path.relpath(root, base).count(os.sep) + 1
        if depth >= max_depth:
            dirs[:] = []
        dirs.sort(key=str.lower)
        for name in sorted(files, key=str.lower):
            if name.lower().endswith(".txt"):
                rel = os.path.relpath(os.path.join(root, name), base).replace("\\", "/")
                found.append(rel)
                if len(found) >= max_files:
                    return found
    return found


_routes_done = False


def register_routes():
    """Add the /sy/flagship routes to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    def answer(fn):
        async def handler(request):
            try:
                return web.json_response(await fn(request))
            except (ValueError, TypeError) as e:
                return web.json_response({"error": str(e)}, status=400)
        return handler

    async def _size(request):
        q = dict(request.rel_url.query)
        return size_for(q.pop("node", ""), q)

    async def _textfiles(request):
        return {"files": list_text_files(root_folder("input"))}

    routes.get("/sy/flagship/size")(answer(_size))
    routes.get("/sy/flagship/textfiles")(answer(_textfiles))
    _routes_done = True
    return True
