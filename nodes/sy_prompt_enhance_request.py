"""Prompt Enhance Request SY: wraps a short idea in a clear request that asks an LLM to write a better image prompt."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LENGTHS = {"short": "about 30 words", "medium": "about 70 words", "long": "about 150 words"}
STYLES = {
    "photo": "a realistic photograph, with camera, lens and light details",
    "cinematic": "a cinematic film still, with mood, lighting and camera angle",
    "anime": "an anime illustration, with clean lines and bold colour",
    "painting": "a painting, with brush texture, palette and light",
    "3d render": "a 3D render, with materials, lighting and depth",
    "product shot": "a clean product photo, with surface, light and background",
    "any style": "the style that best fits the idea",
    "watercolor": "a watercolor painting, with soft washes, paper texture and gentle edges",
    "line art": "clean line art, with confident strokes and little or no shading",
    "pixel art": "pixel art, with a small palette, hard edges and a clear silhouette",
    "fantasy art": "fantasy art, with rich detail, dramatic light and a sense of wonder",
}
FORMATS = {
    "one paragraph": "Write one flowing paragraph.",
    "comma phrases": "Write short phrases separated by commas.",
    "bullet points": "Write a short bullet list with one detail on each line.",
}


def enhance_request(idea, length="medium", style="any style", output_format="one paragraph", notes="", avoid="", also_negative=False):
    """Pure function. Builds the request text only; it never calls an LLM.
    avoid: things the prompt must not contain. also_negative: ask for a second line that starts with 'Negative:'."""
    if not isinstance(idea, str) or not idea.strip():
        raise ValueError("idea is empty: write a short idea such as 'a fox in the snow'")
    if length not in LENGTHS:
        raise ValueError("length must be one of: %s (got %r)" % (", ".join(LENGTHS), length))
    if style not in STYLES:
        raise ValueError("style must be one of: %s (got %r)" % (", ".join(STYLES), style))
    if output_format not in FORMATS:
        raise ValueError("output_format must be one of: %s (got %r)" % (", ".join(FORMATS), output_format))
    if not isinstance(notes, str):
        raise ValueError("notes must be text, got %s" % type(notes).__name__)
    lines = [
        "Rewrite the idea below as a detailed image prompt.",
        "Idea: " + idea.strip(),
        "Style: " + STYLES[style] + ".",
        "Length: " + LENGTHS[length] + ".",
        FORMATS[output_format],
        "Keep the idea and add only things that fit it. Do not add text, names or watermarks.",
    ]
    if notes.strip():
        lines.append("Also respect these notes: " + notes.strip())
    if not isinstance(avoid, str):
        raise ValueError("avoid must be text, got %s" % type(avoid).__name__)
    if avoid.strip():
        lines.append("Do not include: " + " ".join(avoid.split()))
    if also_negative:
        lines.append("Reply with the prompt, then a second line that starts with 'Negative:' and lists what to avoid.")
    else:
        lines.append("Reply with the prompt only.")
    return "\n".join(lines)


def request_info(idea, length="medium", style="any style", output_format="one paragraph", avoid="", also_negative=False):
    """Pure function. One plain line saying what the request asks for."""
    words = len(str(idea).split())
    info = "Asks for %s %s prompt (%s, %s) from an idea of %d word%s." % (
        length, style, LENGTHS[length], output_format, words, "" if words == 1 else "s")
    extras = []
    if str(avoid).strip():
        extras.append("an avoid list")
    if also_negative:
        extras.append("a negative line")
    if extras:
        info += " Also asks for " + " and ".join(extras) + "."
    if len(str(idea)) > 600:
        info += " WARNING: the idea is long; a short idea works best."
    return info


class SYPromptEnhanceRequest:
    DESCRIPTION = ("Wraps a short idea in a clear request for an LLM, with length and style choices. It only builds the text. "
                   "Can add an avoid list and ask for a second Negative line. An info line sums up the request.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("request", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "idea": ("STRING", {"multiline": True, "default": "", "tooltip": "Your short idea, for example: a fox in the snow."}),
                "length": (list(LENGTHS), {"default": "medium", "tooltip": "How long the finished prompt should be."}),
                "style": (list(STYLES), {"default": "any style", "tooltip": "The look the finished prompt should describe."}),
                "output_format": (list(FORMATS), {"default": "one paragraph", "tooltip": "A flowing paragraph or short comma phrases."}),
            },
            "optional": {
                "notes": ("STRING", {"multiline": True, "default": "", "tooltip": "Extra wishes, for example: no people, warm colours."}),
                "avoid": ("STRING", {"default": "", "tooltip": "Things the finished prompt must not contain, for example: text, hands."}),
                "also_negative": ("BOOLEAN", {"default": False, "tooltip": "On: ask for a second line that starts with Negative: and lists what to avoid."}),
            },
        }

    def run(self, idea, length, style, output_format, notes="", avoid="", also_negative=False):
        text = enhance_request(idea, length, style, output_format, notes, avoid, also_negative)
        return text, request_info(idea, length, style, output_format, avoid, also_negative)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptEnhanceRequest", SYPromptEnhanceRequest)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptEnhanceRequest"] = "Prompt Enhance Request SY"
