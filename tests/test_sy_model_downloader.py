import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "nodes"))
import sy_model_downloader as m

HF = "https://huggingface.co/org/repo/resolve/main/model.safetensors"


def run():
    n = 0

    def ok(cond, msg=""):
        nonlocal n
        assert cond, msg
        n += 1

    cls = m.SYModelDownloader
    ok(cls.RETURN_TYPES == () and cls.INPUT_TYPES() == {"required": {}} and cls().run() == ())
    ok(m.NODE_DISPLAY_NAME_MAPPINGS["SYModelDownloader"] == "Model Downloader SY")
    ok(m.NODE_CLASS_MAPPINGS["SYModelDownloader"] is cls and cls.CATEGORY == "SY/Notes")
    ok("button" in cls.DESCRIPTION and "Hugging Face" in cls.DESCRIPTION and "Civitai" in cls.DESCRIPTION)
    ok(cls.FUNCTION == "run")

    rows, probs = m.clean_models(None)
    ok(rows == [] and probs == [])
    rows, probs = m.clean_models({"sy_models": ""})
    ok(rows == [] and probs == [])
    good = {"folder": "loras", "file": "a.safetensors", "url": HF, "note": "n"}
    rows, probs = m.clean_models({"sy_models": json.dumps([good])})
    ok(len(rows) == 1 and rows[0]["file"] == "a.safetensors" and not probs)
    rows, probs = m.clean_models({"sy_models": [good, dict(good, file="b.gguf")]})
    ok(len(rows) == 2)
    rows, probs = m.clean_models({"sy_models": "{not json"})
    ok(rows == [] and "damaged" in probs[0])
    rows, probs = m.clean_models({"sy_models": "{}"})
    ok(rows == [] and "damaged" in probs[0])
    rows, probs = m.clean_models({"sy_models": json.dumps([good, dict(good, url="https://evil.com/a"), dict(good, file="A.safetensors"), 5])})
    ok(len(rows) == 1 and len(probs) == 3 and probs[0].startswith("Row 2"))
    rows, probs = m.clean_models({"sy_models": json.dumps([dict(good, sha256="ab" * 32)])})
    ok(rows[0]["sha256"] == "ab" * 32)
    rows, probs = m.clean_models({"sy_models": json.dumps([dict(good, folder="bogus")])})
    ok(rows == [] and "Allowed folders" in probs[0])

    # the browser file: no innerHTML, no hex colour, talks only to the download routes, never starts a run
    js = open(os.path.join(ROOT, "js", "sy_model_downloader.js"), encoding="utf-8").read()
    ok("innerHTML" not in js and "outerHTML" not in js and "insertAdjacentHTML" not in js)
    ok(not re.search(r"#[0-9a-fA-F]{6}\b", js))
    ok("SYModelDownloader" in js and "/sy/download/start" in js and "/sy/download/plan" in js and "/sy/download/check" in js)
    ok("queuePrompt" not in js and "graphToPrompt" not in js and "onExecuted" not in js)
    return n
