import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_sentence_pick as m


def run():
    n = 0

    def eq(got, want):
        nonlocal n
        assert got == want, "got %r, wanted %r" % (got, want)
        n += 1

    t = "A fox ran. Was it fast? Yes! It won."
    eq(m.split_sentences(t), ["A fox ran.", "Was it fast?", "Yes!", "It won."])
    eq(m.split_sentences("Dr. Smith met Mr. Jones. They talked."), ["Dr. Smith met Mr. Jones.", "They talked."])
    eq(m.split_sentences("Pi is 3.14 today. Fine."), ["Pi is 3.14 today.", "Fine."])
    eq(m.split_sentences("J. K. Rowling wrote it. Good."), ["J. K. Rowling wrote it.", "Good."])
    eq(m.split_sentences('He said "stop." Then left.'), ['He said "stop."', "Then left."])
    eq(m.split_sentences("No end mark"), ["No end mark"])
    eq(m.split_sentences("Wait... what? ok"), ["Wait...", "what?", "ok"])
    eq(m.split_sentences("One.\nTwo."), ["One.", "Two."])
    eq(m.split_sentences(""), [])
    eq(m.sentence_pick(t, "first_n", 2), ("A fox ran. Was it fast?", 4))
    eq(m.sentence_pick(t, "last_n", 2), ("Yes! It won.", 4))
    eq(m.sentence_pick(t, "first_n", 99), (t, 4))
    eq(m.sentence_pick(t, "index", 1, 2), ("Yes!", 4))
    eq(m.sentence_pick(t, "all_numbered"), ("1. A fox ran.\n2. Was it fast?\n3. Yes!\n4. It won.", 4))
    eq(m.sentence_pick("", "first_n"), ("", 0))
    eq(m.SYSentencePick().run(t, "index", 1, 3), ("It won.", 4))
    for args in ((t, "index", 1, 4), (t, "nope"), (t, "first_n", 0), ("", "index", 1, 0)):
        try:
            m.sentence_pick(*args)
            raise SystemExit("bad args must raise: %r" % (args,))
        except ValueError:
            n += 1
    try:
        m.split_sentences("x" * (m.MAX_INPUT + 1))
        raise SystemExit("too long input must raise")
    except ValueError:
        n += 1
    eq(m.SYSentencePick.RETURN_TYPES, ("STRING", "INT"))
    return n
