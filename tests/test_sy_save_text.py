import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_save_text as m
import _sy_safe_paths as sp

NOW = datetime(2026, 10, 28, 14, 5, 9)


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError:
        return True
    return False


def run():
    n = 0
    assert m.text_file_name([], "t_{counter}", False, 0, NOW) == "t_00001.txt"; n += 1
    assert m.text_file_name(["t_00001.txt", "t_00002.txt"], "t_{counter}", False, 0, NOW) == "t_00003.txt"; n += 1
    assert m.text_file_name(["notes.txt"], "notes", True, 0, NOW) == "notes.txt"; n += 1
    assert m.text_file_name(["notes.txt"], "notes", False, 0, NOW) == "notes_00001.txt"; n += 1
    assert m.text_file_name([], "{date}", True, 0, NOW) == "2026-10-28.txt"; n += 1
    assert raises(m.text_file_name, [], "t_{counter}", True); n += 1
    assert raises(m.text_file_name, [], "../x", True); n += 1
    assert raises(m.text_file_name, [], "", True); n += 1
    # real file work in a temporary folder
    with tempfile.TemporaryDirectory() as tmp:
        folder = sp.safe_join(tmp, "sub")
        os.makedirs(folder)
        name = m.text_file_name(sp.list_files(folder), "log", True)
        path = os.path.join(folder, name)
        for line in ("one", "two"):
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write(line + "\n")
        assert open(path, encoding="utf-8").read() == "one\ntwo\n"; n += 1
        assert raises(sp.safe_join, tmp, "../sub"); n += 1
    assert m.SYSaveText.OUTPUT_NODE is True; n += 1
    # --- value pass A2: extension, empty text, time stamp, info line
    assert m.text_file_name([], "t_{counter}", False, 0, NOW, ".md") == "t_00001.md"; n += 1
    assert m.text_file_name(["t_00001.txt"], "t_{counter}", False, 0, NOW, ".json") == "t_00001.json"; n += 1
    assert m.text_file_name(["log.txt"], "log", True, 0, NOW, "csv") == "log.csv"; n += 1
    assert raises(m.text_file_name, [], "x", False, 0, NOW, ".exe"); n += 1
    assert m.prepare_text("hi") == "hi" and m.prepare_text("") == ""; n += 2
    assert m.prepare_text("  ", "skip") is None; n += 1
    assert raises(m.prepare_text, "", "error"); n += 1
    assert raises(m.prepare_text, "x", "sometimes"); n += 1
    assert raises(m.prepare_text, "x" * (m.MAX_CHARS + 1)); n += 1
    assert m.prepare_text("run ok", "save anyway", True, True, NOW) == "[2026-10-28 14:05:09] run ok"; n += 1
    assert m.prepare_text("", "save anyway", True, True, NOW) == ""; n += 1
    assert m.save_info("SY/a.txt", 5, False, False) == "Saved 5 characters to SY/a.txt (new file)"; n += 1
    assert m.save_info("SY/a.txt", 5, True, True, 42) == "Added 5 characters to the end of SY/a.txt (file is now 42 bytes)"; n += 1
    assert "more will be added" in m.save_info("SY/a.txt", 5, True, False); n += 1
    assert m.SYSaveText.RETURN_NAMES == ("saved_path", "info") and len(m.SYSaveText.RETURN_TYPES) == 2; n += 1
    assert m.SYSaveText().run("", "SY", "x", False, 0, "txt", "skip") == ("", "Skipped: the text was empty, so no file was written."); n += 1
    opt = m.SYSaveText.INPUT_TYPES()["optional"]
    assert opt["extension"][0] == m.EXTENSIONS and opt["on_empty"][0] == m.ON_EMPTY and opt["time_stamp"][1]["default"] is False; n += 1
    return n
