import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_loader_name_picker as m

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
    ok(m.folder_key("clip") == "text_encoders")
    ok(m.folder_key("unet") == "diffusion_models")
    ok(m.folder_key("upscale_models") == "upscale_models")
    raises(m.folder_key, "embeddings")
    ok(m.pick_name("loras", "a.safetensors", ["a.safetensors", "b.safetensors"]) == "a.safetensors")
    raises(m.pick_name, "loras", "z.safetensors", ["a.safetensors"])
    raises(m.pick_name, "vae", "a", [])
    raises(m.pick_name, "nope", "a", ["a"])
    ok(m.split_name("sub/dir\\model.v2.safetensors") == ("sub/dir\\model.v2.safetensors", "model.v2"))
    ok(m.split_name("plain") == ("plain", "plain"))
    raises(m.SYLoaderNamePicker().run, "checkpoints", "x.safetensors")  # no ComfyUI list here
    by = {"checkpoints": ["sdxl.safetensors", "Flux/flux_dev.safetensors"], "loras": ["style.safetensors"], "vae": ["ae.safetensors"],
          "clip": [], "unet": [], "upscale_models": []}
    r = m.resolve("checkpoints", "sdxl.safetensors", "", by)
    ok(r[0] == "sdxl.safetensors" and r[2] == 1 and r[1] == "checkpoints: sdxl.safetensors")
    r = m.resolve("checkpoints", "sdxl.safetensors", "FLUX dev", by)
    ok(r[0] == "Flux/flux_dev.safetensors" and r[2] == 1 and "picked" in r[1])
    ok("in the loras list" in m.wrong_folder_message("checkpoints", "style.safetensors", by) and "Change folder to loras" in m.wrong_folder_message("checkpoints", "style.safetensors", by))
    ok(m.wrong_folder_message("checkpoints", "nothing.safetensors", by) == "")
    try:
        m.resolve("checkpoints", "style.safetensors", "", by)
        raise AssertionError("wrong folder must raise")
    except ValueError as e:
        ok("Change folder to loras" in str(e))
    raises(m.resolve, "checkpoints", "sdxl.safetensors", "zzz", by)
    raises(m.resolve, "nope", "a", "", by)
    raises(m.resolve, "clip", "a", "", by)  # empty folder: plain refusal
    ok(m.folders_holding("ae.safetensors", by) == ["vae"])
    spec = m.SYLoaderNamePicker.INPUT_TYPES()
    ok(list(spec["required"]) == ["folder", "name"] and list(spec["optional"]) == ["name_filter"])
    ok(m.SYLoaderNamePicker.RETURN_TYPES == ("STRING", "STRING", "INT", "STRING") and m.SYLoaderNamePicker.RETURN_NAMES[:2] == ("name", "name_no_ext"))
    return N[0]
