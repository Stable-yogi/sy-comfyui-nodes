import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_text_chunker as m


def run():
    n = 0
    assert m.split_chunks("abc", 10, 0) == ["abc"]; n += 1
    assert m.split_chunks("abcdefghij", 4, 0) == ["abcd", "efgh", "ij"]; n += 1
    assert m.split_chunks("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]; n += 1
    words = ("alpha beta gamma delta epsilon zeta eta theta " * 20).strip()
    for ov in (0, 5, 20):
        ch = m.split_chunks(words, 40, ov)
        assert all(len(c) <= 40 for c in ch); n += 1
        assert ch[0] == words[:len(ch[0])] and ch[-1] == words[-len(ch[-1]):]; n += 1
    ch = m.split_chunks("one two three four five six", 10, 0)
    assert "".join(ch) == "one two three four five six"; n += 1
    assert all(not c.strip().startswith(("hree", "our")) for c in ch); n += 1
    big = "x" * 1000
    assert len(m.split_chunks(big, 7, 6)) > 100 and m.split_chunks(big, 7, 6)[-1].endswith("x"); n += 1
    assert m.pick_chunk(["a", "b"], 1) == "b"; n += 1
    for call in (lambda: m.split_chunks("", 5, 0), lambda: m.split_chunks("a", 0, 0),
                 lambda: m.split_chunks("a", 5, 5), lambda: m.split_chunks("a", 5, -1),
                 lambda: m.pick_chunk(["a"], 1), lambda: m.pick_chunk(["a"], -1), lambda: m.split_chunks(4, 5, 0)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYTextChunker().run("abcdefghij", 4, 0, 2)[:2] == ("ij", 3); n += 1
    return n + _extra()


def _extra():
    n = 0
    L = ["a", "b", "c"]
    assert m.pick_chunk(L, 4, "wrap around") == "b"; n += 1
    assert m.pick_chunk(L, 9, "stay on the last") == "c"; n += 1
    assert m.pick_chunk(L, 1, "wrap around") == "b"; n += 1
    for call in (lambda: m.pick_chunk(L, -1, "wrap around"), lambda: m.pick_chunk(L, 3), lambda: m.pick_chunk(L, 0, "nope")):
        try:
            call()
            raise SystemExit("bad index must raise")
        except ValueError:
            n += 1
    try:
        m.pick_chunk(L, 3)
    except ValueError as e:
        assert "wrap around" in str(e); n += 1
    assert m.chunk_info(L, 1, 1, 5) == "Piece 2 of 3 (1 characters, overlap 5)"; n += 1
    assert m.chunk_info(L, 4, 1, 0).endswith("index 4 was moved to 1"); n += 1
    out = m.SYTextChunker().run("abcdefghij", 4, 0, 5, "wrap around")
    assert out[0] == "ij"; n += 1
    assert out[1] == 3 and out[2] == ["abcd", "efgh", "ij"] and out[3].startswith("Piece 3 of 3"); n += 1
    assert m.SYTextChunker.OUTPUT_IS_LIST == (False, False, True, False); n += 1
    assert len(m.SYTextChunker.RETURN_TYPES) == len(m.SYTextChunker.RETURN_NAMES) == len(m.SYTextChunker.OUTPUT_IS_LIST); n += 1
    return n
