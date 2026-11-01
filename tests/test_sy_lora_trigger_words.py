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
    assert m.SYLoraTriggerWords().run("None") == ("", "", "No LoRA picked.")
    n += 1
    assert m.merge_triggers("a dog", ["sks", "cat style"]) == ("sks, cat style, a dog", ["sks", "cat style"]); n += 1
    assert m.merge_triggers("a dog in CAT STYLE", ["sks", "cat style"]) == ("sks, a dog in CAT STYLE", ["sks"]); n += 1
    assert m.merge_triggers("sks dog", ["sks"]) == ("sks dog", []); n += 1
    assert m.merge_triggers("", ["a", "b"]) == ("a, b", ["a", "b"]); n += 1
    assert m.merge_triggers(None, []) == ("", []); n += 1
    assert m.trigger_info("sub/x.safetensors", [], "") == "No trigger words found for sub/x.safetensors. Put a x.txt (words) or x.json (trainedWords) file next to the LoRA."; n += 1
    assert m.trigger_info("x", ["a"], "x.json") == "1 trigger word from x.json."; n += 1
    assert m.trigger_info("x", ["a", "b"], "x.txt", ["a"]) == "2 trigger words from x.txt. 1 added to the prompt, 1 already there."; n += 1
    with tempfile.TemporaryDirectory() as d2:
        lora2 = os.path.join(d2, "y.safetensors")
        open(lora2, "wb").close()
        assert m.read_sidecar_ex(lora2) == ([], "")
        with open(os.path.join(d2, "y.civitai.info"), "w") as f2:
            json.dump({"trainedWords": ["civ word"]}, f2)
        assert m.read_sidecar_ex(lora2) == (["civ word"], "y.civitai.info")
        with open(os.path.join(d2, "y.txt"), "w") as f2:
            f2.write("txt first")
        assert m.read_sidecar_ex(lora2) == (["txt first"], "y.txt")
    assert m.SYLoraTriggerWords().run("None", ", ", " keep me ") == ("", "keep me", "No LoRA picked."); n += 1
    assert m.SYLoraTriggerWords.RETURN_NAMES == ("trigger_words", "prompt", "info"); n += 1
    return n
