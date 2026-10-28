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
    return n
