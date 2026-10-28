"""Small web helpers for the SY file nodes: list folders, show the path a save would use, open a folder.

Owner decision 2026-10-28: the Save and Load nodes may open Explorer and list folders, but ONLY inside the ComfyUI
output and input folders. Every path goes through safe_join, and only picture files may be opened.
This is the one audited place that calls os.startfile (listed in ALLOW in tests/run_selftest.py and in the standard).
"""
import os

try:
    from ._sy_safe_paths import (FORMATS, IMAGE_EXTENSIONS, date_subfolder, list_files, plan_names,
                                 root_folder, safe_join)
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import (FORMATS, IMAGE_EXTENSIONS, date_subfolder, list_files, plan_names,
                                root_folder, safe_join)

ROOTS = ("output", "input")
MAX_DIRS = 200


def _root(root):
    if root not in ROOTS:
        raise ValueError("root must be output or input, got %r" % (root,))
    return root_folder(root)


def list_folder(root, sub=""):
    """Sub folders and the number of pictures of one folder inside the output or input folder."""
    base = _root(root)
    folder = safe_join(base, sub)
    dirs, images = [], 0
    if os.path.isdir(folder):
        dirs = sorted((n for n in os.listdir(folder) if os.path.isdir(os.path.join(folder, n))), key=str.lower)[:MAX_DIRS]
        images = len(list_files(folder, IMAGE_EXTENSIONS))
    rel = os.path.relpath(folder, os.path.realpath(base))
    return {"root": root, "root_path": os.path.realpath(base), "sub": "" if rel == "." else rel.replace("\\", "/"),
            "exists": os.path.isdir(folder), "dirs": dirs, "images": images}


def plan_save(subfolder, pattern, fmt, seed=0, width=0, height=0, batch=1, model="", input_name="", date_folder=False, now=None):
    """The path the next save would use (first picture). Nothing is written."""
    if fmt not in FORMATS:
        raise ValueError("format must be png, jpg or webp, got %r" % (fmt,))
    base = _root("output")
    sub = date_subfolder(subfolder, now) if date_folder else subfolder
    folder = safe_join(base, sub)
    extra = {"model": model, "input": input_name, "width": width, "height": height, "batch": batch}
    name = plan_names(list_files(folder), pattern, FORMATS[fmt], 1, seed, now, extra=extra)[0]
    rel = os.path.relpath(folder, os.path.realpath(base))
    rel = "" if rel == "." else rel.replace("\\", "/")
    return {"root_path": os.path.realpath(base), "sub": rel, "filename": name,
            "full": os.path.join(folder, name)}


def open_target(root, sub="", filename=None):
    """Open a folder, or one picture of it, with the system viewer. Returns the path that was opened."""
    base = _root(root)
    target = safe_join(base, sub)
    if filename:
        name = os.path.basename(str(filename).replace("\\", "/"))
        if name != filename or os.path.splitext(name)[1].lower() not in IMAGE_EXTENSIONS:
            raise ValueError("only picture files can be opened: %r" % (filename,))
        target = safe_join(target, name)
        if not os.path.isfile(target):
            raise ValueError("the file is not there: %s" % name)
    elif not os.path.isdir(target):
        raise ValueError("the folder does not exist yet: save a picture first")
    if not hasattr(os, "startfile"):
        raise ValueError("opening Explorer works on Windows only")
    os.startfile(target)  # audited: only inside the output or input folder, only folders or picture files
    return target


_routes_done = False


def register_routes():
    """Add the three /sy/folder routes to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
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
                data = await fn(request)
                return web.json_response(data)
            except ValueError as e:
                return web.json_response({"error": str(e)}, status=400)
        return handler

    async def _list(request):
        q = request.rel_url.query
        return list_folder(q.get("root", "output"), q.get("sub", ""))

    async def _plan(request):
        q = request.rel_url.query
        num = lambda k, d=0: int(q.get(k, d) or d)  # noqa: E731
        return plan_save(q.get("sub", ""), q.get("pattern", "image_{counter}"), q.get("format", "png"), num("seed"),
                         num("width"), num("height"), num("batch", 1), q.get("model", ""), q.get("input", ""),
                         q.get("date_folder", "") in ("1", "true"))

    async def _open(request):
        body = await request.json()
        path = open_target(body.get("root", "output"), body.get("sub", ""), body.get("filename"))
        return {"opened": path}

    routes.get("/sy/folder/list")(answer(_list))
    routes.get("/sy/folder/plan")(answer(_plan))
    routes.post("/sy/folder/open")(answer(_open))
    _routes_done = True
    return True
