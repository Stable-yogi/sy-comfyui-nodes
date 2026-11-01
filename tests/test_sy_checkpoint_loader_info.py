import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_checkpoint_loader_info as m

N = [0]


def ok(cond, msg="check failed"):
    N[0] += 1
    if not cond:
        raise AssertionError(msg)


def raises(fn, *args):
    N[0] += 1
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError for %r" % (args,))


def run():
    ok(m.info_line("a.safetensors", 1536) == "a.safetensors (1.5 KB)")
    ok(m.info_line("b.ckpt", 6 * 1024 ** 3) == "b.ckpt (6.0 GB)")
    ok(m.info_line("c", 0) == "c (0 B)")
    raises(m.info_line, "x", -1)
    raises(m.SYCheckpointLoaderInfo().run, "../evil.ckpt")
    ok(m.SYCheckpointLoaderInfo.RETURN_TYPES == ("MODEL", "CLIP", "VAE", "STRING", "STRING"))
    ok(m.SYCheckpointLoaderInfo.RETURN_NAMES[:4] == ("model", "clip", "vae", "info") and m.SYCheckpointLoaderInfo.RETURN_NAMES[4] == "ckpt_name")
    spec = m.SYCheckpointLoaderInfo.INPUT_TYPES()
    ok(list(spec["required"]) == ["ckpt_name"] and list(spec["optional"]) == ["name_filter"])
    t = m.build_info("flux1-dev-fp8_e4m3fn.safetensors", 17 * 1024 ** 3)
    ok("flux1-dev-fp8_e4m3fn.safetensors | safetensors (safe format) | 17.0 GB | fp8" in t and "fp8 = numbers stored in 8 bits" in t and "Warning" not in t)
    t = m.build_info("old/model.ckpt", 4 * 1024 ** 3, "name_filter 'old' picked old/model.ckpt.", has_clip=True, has_vae=False)
    ok("older file format" in t and "no VAE inside" in t and "picked old/model.ckpt" in t and "no text encoder" not in t)
    ok("no text encoder" in m.build_info("a.safetensors", 5, has_clip=False))
    ok("may not be a full checkpoint" in m.build_info("sdxl_vae.safetensors", 5))
    ok("UnetLoaderGGUF" in m.build_info("m-Q4_K_M.gguf", 5))
    raises(m.check_size, "empty.safetensors", 0)
    raises(m.pick_with_filter, [], "a", "flux", "checkpoint")
    raises(m.pick_with_filter, ["a.safetensors"], "a.safetensors", "zzz", "checkpoint")
    ok(m.pick_with_filter(["a.safetensors", "Flux/b.safetensors"], "a.safetensors", "", "checkpoint") == ("a.safetensors", ""))
    ok(m.pick_with_filter(["a.safetensors", "Flux/b.safetensors"], "a.safetensors", " FLUX ", "checkpoint")[0] == "Flux/b.safetensors")
    ok("matched 2 files" in m.pick_with_filter(["x1.safetensors", "x2.safetensors"], "x2.safetensors", "x", "checkpoint")[1])
    raises(m.SYCheckpointLoaderInfo().run, "a.safetensors", "flux")  # no ComfyUI list here: plain refusal
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYCheckpointLoaderInfo"] == "Checkpoint Loader Info SY")
    return N[0]
