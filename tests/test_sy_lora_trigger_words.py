import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_lora_trigger_words as m


def run():
    n = 0
    assert m.words_from_json(json.dumps({"trainedWords": ["cat style", "kitty"]})) == ["cat style", "kitty"]
    assert m.words_from_json(json.dumps({"activation text": "my word"})) == ["my word"]
    assert m.words_from_json(json.dumps({"civitai": {"trainedWords": ["deep"]}})) == ["deep"]
    assert m.words_from_json(json.dumps({"trigger_words": ["a", "a", "b"]})) == ["a", "b"]
    assert m.words_from_json(json.dumps({"other": 1})) == []
    assert m.words_from_txt("  hello \n world ") == ["hello world"]
    assert m.words_from_txt("   ") == []
    n += 7
    try:
        m.words_from_json("{bad")
        raise SystemExit("bad json must raise")
    except ValueError:
        n += 1
    with tempfile.TemporaryDirectory() as d:
        lora = os.path.join(d, "x.safetensors")
        open(lora, "wb").close()
        assert m.read_sidecar_words(lora) == []
        with open(os.path.join(d, "x.txt"), "w") as f:
            f.write("txt words")
        assert m.read_sidecar_words(lora) == ["txt words"]
        with open(os.path.join(d, "x.json"), "w") as f:
            json.dump({"trainedWords": ["json words"]}, f)
        assert m.read_sidecar_words(lora) == ["json words"]  # json wins
        n += 3
    assert m.SYLoraTriggerWords().run("None") == ("",)
    n += 1
    return n
