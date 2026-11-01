"""Web helper for the Seed Vault table: one read-only route that lists the saved seeds. It never writes."""
try:
    from . import _sy_seed_vault as H
except ImportError:  # run as a plain file by the selftest
    import _sy_seed_vault as H

_routes_done = False


def register_routes():
    """Add GET /sy/seed_vault/list to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI."""
    global _routes_done
    if _routes_done:
        return True
    try:
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    async def listing(request):
        try:
            return web.json_response(H.view_data(request.query.get("collection", "")))
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=400)

    routes.get("/sy/seed_vault/list")(listing)
    _routes_done = True
    return True
