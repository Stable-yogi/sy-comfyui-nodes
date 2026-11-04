import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_h3_swap_prompt as m


def run():
    n = 0
    p, notes = m.build_swap_prompt("the man in the purple shirt", "", "whole look", "Picture 1", True, "")
    assert p == ("Swap the man in the purple shirt with the character from Picture 1. "
                 "The new person has the face, hair, body and clothes of Picture 1, not only the clothes. "
                 "Keep the camera movement, the body movement, the facial expressions, the timing, the background "
                 "and the lighting of the source video."), p; n += 1
    assert notes == "tip: if only the clothes change, run 2 or 3 more seeds with the same prompt", notes; n += 1
    p, _ = m.build_swap_prompt("The girl", "the boy", "whole look", "Picture 1", True, "")
    assert p.startswith("Swap the girl with") and "Change only the girl, not the boy. The boy stays exactly as in the video." in p, p; n += 1
    p, _ = m.build_swap_prompt("the girl in red", "the boy\nthe dog, the boy", "whole look", "Picture 1", True, "")
    assert "not the boy and the dog. The boy and the dog stay exactly" in p, p; n += 1
    p, _ = m.build_swap_prompt("the woman on the left", "", "face and hair", "the character sheet", False, "")
    assert "has the face and hair of the character sheet" in p and "Keep the clothes the woman on the left wears in the video." in p, p; n += 1
    assert "facial expressions" not in p; n += 1
    p, _ = m.build_swap_prompt("the man in the purple shirt", "", "face, hair and body", "", True, "she smiles at the end")
    assert "Picture 1" in p and p.endswith("She smiles at the end.") is False and p.endswith("she smiles at the end."), p; n += 1
    _, notes = m.build_swap_prompt("the person", "", "whole look", "Picture 1", True, "")
    assert "target is vague" in notes and "target is short" in notes, notes; n += 1
    _, notes = m.build_swap_prompt("the boy in blue", "the boy in blue", "whole look", "Picture 1", True, "")
    assert "both the target and in keep" in notes; n += 1
    _, notes = m.build_swap_prompt("the boy in blue", "", "whole look", "Picture 1", True, "x" * 2100)
    assert "2000" in notes; n += 1
    for bad in (("", "", "whole look"), ("  ", "", "whole look"), ("the man in red", "", "clothes only")):
        try:
            m.build_swap_prompt(*bad)
            raise SystemExit("bad input must raise: %r" % (bad,))
        except ValueError:
            n += 1
    assert m.SYH3SwapPrompt.RETURN_TYPES == ("STRING", "STRING"); n += 1
    assert m.SYH3SwapPrompt().run("the man in red", "whole look", "Picture 1", True)[0].startswith("Swap the man in red"); n += 1
    return n
