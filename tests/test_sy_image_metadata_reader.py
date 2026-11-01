import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_metadata_reader as m


def run():
    n = 0
    assert m.extract_metadata({"prompt": "{\"1\": {}}", "workflow": "{\"nodes\": []}", "other": "x"}) == ("{\"1\": {}}", "{\"nodes\": []}"); n += 1
    assert m.extract_metadata({}) == ("", ""); n += 1
    assert m.extract_metadata(None) == ("", ""); n += 1
    assert m.extract_metadata({"prompt": 5, "workflow": b"x"}) == ("", ""); n += 1
    try:
        m.extract_metadata({"prompt": "x" * 11}, limit=10)
        raise SystemExit("long text must raise")
    except ValueError:
        n += 1
    assert m.SYImageMetadataReader.RETURN_TYPES[:2] == ("STRING", "STRING") and len(m.SYImageMetadataReader.RETURN_TYPES) == 7; n += 1
    assert m.SYImageMetadataReader.RETURN_NAMES[:2] == ("prompt_text", "workflow_json"); n += 1
    # added value: A1111 text, ComfyUI prompt, info
    a1 = "a red fox\nin snow\nNegative prompt: blurry, bad\nlow quality\nSteps: 20, Sampler: Euler a, CFG scale: 7, Seed: 123, Size: 512x768, Model: foo, Lora hashes: \"x: 1, y: 2\""
    pos, neg, sets = m.parse_a1111(a1)
    assert pos == "a red fox\nin snow" and neg == "blurry, bad\nlow quality"; n += 1
    assert sets[0] == "Steps: 20" and "Seed: 123" in sets and "Size: 512x768" in sets and "Model: foo" in sets; n += 1
    assert m.parse_a1111("just a prompt") == ("just a prompt", "", []); n += 1
    assert m.parse_a1111("") == ("", "", []); n += 1
    assert m.parse_a1111(None) == ("", "", []); n += 1
    assert m.parse_a1111("p\nSteps: 5, Seed: 1") == ("p", "", ["Steps: 5", "Seed: 1"]); n += 1
    graph = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sdxl.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "a cat", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "ugly", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 768, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"seed": 42, "steps": 25, "cfg": 6.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
                                                  "positive": ["2", 0], "negative": ["3", 0], "model": ["1", 0], "latent_image": ["4", 0]}},
    }
    import json
    pos, neg, sets = m.parse_comfy_prompt(json.dumps(graph))
    assert pos == "a cat" and neg == "ugly"; n += 1
    assert "seed: 42" in sets and "steps: 25" in sets and "cfg: 6.5" in sets and "model: sdxl.safetensors" in sets and "size: 1024x768" in sets; n += 1
    graph["6"] = {"class_type": "FluxGuidance", "inputs": {"conditioning": ["2", 0], "guidance": 3.5}}
    graph["5"]["inputs"]["positive"] = ["6", 0]
    assert m.parse_comfy_prompt(json.dumps(graph))[0] == "a cat"; n += 1  # follows a guidance node back to the text
    assert m.parse_comfy_prompt("not json") == ("", "", []); n += 1
    assert m.parse_comfy_prompt("[1, 2]") == ("", "", []); n += 1
    assert m.parse_comfy_prompt("") == ("", "", []); n += 1
    assert m.parse_comfy_prompt(json.dumps({"1": 5, "2": {"inputs": None}})) == ("", "", []); n += 1
    params, pos, neg, sets, text = m.summarize_metadata({"prompt": json.dumps(graph), "workflow": "{}"}, (1024, 768))
    assert params == "" and pos == "a cat" and "steps: 25" in sets.split("\n") and text.startswith("Picture 1024x768. Found: ComfyUI prompt, ComfyUI workflow."); n += 1
    params, pos, neg, sets, text = m.summarize_metadata({"parameters": a1})
    assert params == a1 and pos == "a red fox\nin snow" and "Forge/A1111" in text; n += 1
    r = m.summarize_metadata({}, (10, 10))
    assert r[:4] == ("", "", "", "") and "No generation data found" in r[4] and r[4].startswith("Picture 10x10."); n += 1
    r = m.summarize_metadata({"prompt": "{\"1\": {\"inputs\": {}}}"})
    assert "Could not read a sampler" in r[4]; n += 1
    assert m.summarize_metadata(None)[4].startswith("No generation data"); n += 1
    spec = m.SYImageMetadataReader.INPUT_TYPES()
    assert list(spec["required"]) == ["file"] and list(spec["optional"]) == ["source"]; n += 1
    v = m.SYImageMetadataReader.IS_CHANGED("nope.png", "output")
    assert v != v; n += 1
    return n
