"""Helper: run a ComfyUI core node by its name, for the SY nodes that build on core nodes."""


def core(node_name, who, /, **kwargs):
    """Runs the core node `name`. Works for the old and the new node style, so a ComfyUI update does not break it.
    `who` is the SY node name used in the error text."""
    import nodes as comfy_nodes
    cls = comfy_nodes.NODE_CLASS_MAPPINGS.get(node_name)
    if cls is None:
        raise ValueError("this ComfyUI has no core node %r, so %s cannot run" % (node_name, who))
    out = getattr(cls(), cls.FUNCTION)(**kwargs)
    if isinstance(out, dict) and "result" in out:
        out = out["result"]
    if hasattr(out, "result") and not isinstance(out, (tuple, list)):
        out = out.result
    return tuple(out) if isinstance(out, (tuple, list)) else (out,)


def is_out_of_memory(exc):
    """True when the error is a graphics-card or system memory shortage."""
    try:
        import comfy.model_management as mm
        if isinstance(exc, mm.OOM_EXCEPTION):
            return True
    except Exception:
        pass
    text = str(exc).lower()
    return "out of memory" in text or "allocation on device" in text
