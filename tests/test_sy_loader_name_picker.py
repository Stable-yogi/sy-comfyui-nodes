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
    ok(m.SYLoaderNamePicker.RETURN_TYPES == ("STRING", "STRING"))
    return N[0]
