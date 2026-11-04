"""H3 Swap Prompt SY: writes the instruction for swapping one person in a video for the character in a reference picture."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

TAKE = {
    "face and hair": "the face and hair",
    "face, hair and body": "the face, hair and body",
    "whole look": "the face, hair, body and clothes",
}
VAGUE = ("the person", "the people", "someone", "them", "the human", "the character")
MAX_CHARS = 2000


def _clean(text):
    return " ".join(str(text or "").split())


def _keep_list(text):
    items = []
    for part in str(text or "").replace(";", "\n").replace(",", "\n").splitlines():
        part = _clean(part)
        if part and part not in items:
            items.append(part)
    return items


def _join(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def build_swap_prompt(target, keep="", take="whole look", reference="Picture 1", keep_expression=True, extra=""):
    """Pure function. Returns (prompt, notes).
    target: who in the source video is replaced, for example "the man in the purple shirt".
    keep: people or things that must stay as they are (comma or one per line).
    take: what the new person takes from the reference picture (a key of TAKE)."""
    target = _clean(target)
    reference = _clean(reference) or "Picture 1"
    extra = _clean(extra)
    if not target:
        raise ValueError("write who to replace in the video, for example: the man in the purple shirt")
    if take not in TAKE:
        raise ValueError("take must be one of: %s" % ", ".join(TAKE))
    keep_items = _keep_list(keep)
    low = target.lower()
    if low.startswith("the "):
        target_mid = target[0].lower() + target[1:]
    else:
        target_mid = target

    sentences = ["Swap %s with the character from %s." % (target_mid, reference)]
    sentences.append("The new person has %s of %s, not only the clothes." % (TAKE[take], reference))
    if take != "whole look":
        sentences.append("Keep the clothes %s wears in the video." % target_mid)
    if keep_items:
        sentences.append("Change only %s, not %s." % (target_mid, _join(keep_items)))
        sentences.append("%s stay%s exactly as in the video." % (_join(keep_items)[0].upper() + _join(keep_items)[1:],
                                                                "s" if len(keep_items) == 1 else ""))
    still = "the camera movement, the body movement, the timing, the background and the lighting"
    if keep_expression:
        still = "the camera movement, the body movement, the facial expressions, the timing, the background and the lighting"
    sentences.append("Keep %s of the source video." % still)
    if extra:
        sentences.append(extra if extra.endswith((".", "!", "?")) else extra + ".")
    prompt = " ".join(sentences)

    notes = []
    if low in VAGUE or low.split(" ")[:2] == ["the", "person"]:
        notes.append("target is vague: describe the person by clothes or place, for example the woman in the red dress on the left")
    if len(target.split()) < 3:
        notes.append("target is short: add a colour or a place so the model finds the right person")
    for k in keep_items:
        if k.lower() == low:
            notes.append("%s is both the target and in keep" % k)
    if len(prompt) > MAX_CHARS:
        notes.append("prompt has %d characters; more than %d may be cut off" % (len(prompt), MAX_CHARS))
    notes.append("tip: if only the clothes change, run 2 or 3 more seeds with the same prompt")
    return prompt, "\n".join(notes)


class SYH3SwapPrompt:
    DESCRIPTION = ("Writes the instruction for swapping one person in a video for the character in a reference picture "
                   "(a character swap with a reference-to-video model). It names who to replace, who to keep, "
                   "and asks for the new face and body so the model does not change only the clothes.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "target": ("STRING", {"default": "the woman in the blue shirt", "multiline": False, "tooltip": "Who to replace in the video. Name clothes or place: the man in the purple shirt, the girl on the left."}),
                "take": (list(TAKE), {"default": "whole look", "tooltip": "What the new person takes from the reference picture. Face and hair keeps the clothes from the video."}),
                "reference": ("STRING", {"default": "Picture 1", "multiline": False, "tooltip": "How the prompt names the reference picture or character sheet."}),
                "keep_expression": ("BOOLEAN", {"default": True, "tooltip": "On: ask to keep the facial expressions of the video too."}),
            },
            "optional": {
                "keep": ("STRING", {"default": "", "multiline": True, "tooltip": "Other people or things that must not change, one per line or split by commas. Example: the boy."}),
                "extra": ("STRING", {"default": "", "multiline": True, "tooltip": "One more sentence added at the end."}),
            },
        }

    def run(self, target, take, reference, keep_expression, keep="", extra=""):
        return build_swap_prompt(target, keep, take, reference, keep_expression, extra)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SwapPrompt", SYH3SwapPrompt)
NODE_DISPLAY_NAME_MAPPINGS["SYH3SwapPrompt"] = "H3 Swap Prompt SY"
