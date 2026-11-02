"""Web helper for Resource Monitor SY: one read-only route, GET /sy/resources, that returns CPU, RAM and GPU numbers.
It reads only. psutil and pynvml are imported when the route is called; a missing one just leaves that meter out."""
try:
    from . import sy_resource_monitor as M
except ImportError:  # run as a plain file by the selftest
    import sy_resource_monitor as M

_routes_done = False
_nvml_state = {"ready": None}


def _nvml_ready():
    """Start NVML once. False when there is no NVIDIA driver or no pynvml."""
    if _nvml_state["ready"] is None:
        try:
            import pynvml
            pynvml.nvmlInit()
            _nvml_state["ready"] = True
        except Exception:
            _nvml_state["ready"] = False
    return _nvml_state["ready"]


def _read_gpus():
    gpus = []
    if _nvml_ready():
        try:
            import pynvml
            for i in range(pynvml.nvmlDeviceGetCount()):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(h)
                if isinstance(name, bytes):
                    name = name.decode("utf-8", "replace")
                mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                try:
                    util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
                except Exception:
                    util = None
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU)
                except Exception:
                    temp = None
                gpus.append({"name": name, "util": util, "vram_used": mem.used, "vram_total": mem.total, "temp": temp})
            return gpus
        except Exception:
            gpus = []
    try:  # no NVML: torch can still tell the memory
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                free, total = torch.cuda.mem_get_info(i)
                gpus.append({"name": torch.cuda.get_device_name(i), "util": None, "vram_used": total - free, "vram_total": total, "temp": None})
    except Exception:
        pass
    return gpus


def read_snapshot():
    """One reading of this PC as the dict build_snapshot makes."""
    cpu = ram_used = ram_total = None
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        ram_used, ram_total = vm.total - vm.available, vm.total
    except Exception:
        pass
    return M.build_snapshot(cpu, ram_used or 0, ram_total or 0, _read_gpus())


def register_routes():
    """Add GET /sy/resources to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    async def resources(request):
        return web.json_response(read_snapshot())

    routes.get("/sy/resources")(resources)
    _routes_done = True
    return True
