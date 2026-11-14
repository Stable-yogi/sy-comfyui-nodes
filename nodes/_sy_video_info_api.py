"""Web helper for Video Frame Picker SY: one read-only route that tells the slider how many frames a video has.
  GET /sy/video/info?name=<video name in the input folder>  ->  {fps, frames, seconds, width, height}
Only files inside the ComfyUI input folder can be reached. Nothing is written, nothing leaves this PC."""
import os
import re

try:
    from .sy_video_frame_picker import VIDEO_EXT, video_info
except ImportError:  # run as a plain file by the selftest
    from sy_video_frame_picker import VIDEO_EXT, video_info

_DRIVE = re.compile(r"^[A-Za-z]:")
_routes_done = False


def check_video_name(name):
    """Pure function. A video name from the browser: relative, no '..', no drive letter, a video ending."""
    if not isinstance(name, str) or not name.strip() or "\x00" in name:
        raise ValueError("pick a video first")
    flat = name.replace("\\", "/")
    if flat.endswith(" [input]"):
        flat = flat[:-8]
    if flat.startswith("/") or _DRIVE.match(flat) or ".." in flat.split("/"):
        raise ValueError("the video must be a file inside the input folder")
    if os.path.splitext(flat)[1].lower() not in VIDEO_EXT:
        raise ValueError("this is not a video file: %s" % name)
    return name


def inside(path, root):
    """Pure function. True when the real path of `path` lies inside the real folder `root`."""
    try:
        real, base = os.path.realpath(path), os.path.realpath(root)
        return os.path.commonpath([real, base]) == base
    except (OSError, ValueError):
        return False


def register_routes():
    """Add GET /sy/video/info to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        import asyncio
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    async def info(request):
        try:
            import folder_paths
            name = check_video_name(request.rel_url.query.get("name", ""))
            path = folder_paths.get_annotated_filepath(name)
            if not inside(path, folder_paths.get_input_directory()) or not os.path.isfile(path):
                raise ValueError("video not found in the input folder: %s" % name)
            data = await asyncio.get_running_loop().run_in_executor(None, video_info, path)
            return web.json_response(data)
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)
        except Exception as e:  # a broken file: say so instead of a bare 500
            return web.json_response({"error": "could not read the video: %s" % e}, status=400)

    routes.get("/sy/video/info")(info)
    _routes_done = True
    return True
