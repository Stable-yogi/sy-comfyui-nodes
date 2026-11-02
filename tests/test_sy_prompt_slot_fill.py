import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_prompt_slot_fill as m


def run():
    n = [0]

    def eq(got, want):
        n[0] += 1
        assert got == want, "got %r want %r" % (got, want)

    def raises(fn, *a, **k):
        n[0] += 1
        try:
            fn(*a, **k)
        except ValueError:
            return
        raise AssertionError("expected ValueError")

    t = "[subject], [place], [light], [style]"
    eq(m.fill_slots(t, {"subject": "a cat", "place": "a roof", "light": "dusk", "style": "oil"}), ("a cat, a roof, dusk, oil", []))
    eq(m.fill_slots(t, {"subject": "a cat", "light": "dusk"}), ("a cat, dusk", ["place", "style"]))
    eq(m.fill_slots(t, {"place": "a roof"}), ("a roof", ["subject", "light", "style"]))
    eq(m.fill_slots(t, {}), ("", ["subject", "place", "light", "style"]))
    eq(m.fill_slots("[a] and [a]", {}), ("and", ["a"]))
    eq(m.fill_slots("photo of [subject]  in  [place]", {"subject": "x", "place": "y"}), ("photo of x in y", []))
    eq(m.fill_slots("[subject], ,  [place],", {"subject": "x"}), ("x", ["place"]))
    eq(m.fill_slots("no slots here", {"a": "b"}), ("no slots here", []))
    eq(m.fill_slots("[ subject ]", {"subject": "x"}), ("x", []))
    eq(m.fill_slots("[subject]", {"subject": "   "}), ("", ["subject"]))
    eq(m.clean_commas(", a, , b ,"), "a, b")
    eq(m.clean_commas("a  b"), "a b")
    node = m.SYPromptSlotFill()
    eq(node.run("[subject], [place], [mood]", slot_1_name="subject", slot_1="a fox", slot_2_name="place"), ("a fox", "place, mood"))
    eq(node.run("[hero]", slot_1_name="hero", slot_1="Ann"), ("Ann", ""))
    raises(node.run, "[a]", slot_1_name="a", slot_2_name="a")
    spec = m.SYPromptSlotFill.INPUT_TYPES()
    eq(len(spec["optional"]), 6)
    eq(spec["required"]["slot_6_name"][1]["default"], "extra")
    eq(m.NODE_DISPLAY_NAME_MAPPINGS["SYPromptSlotFill"], "Prompt Slot Fill SY")
    return n[0]
