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
}
FORMATS = {
    "one paragraph": "Write one flowing paragraph.",
    "comma phrases": "Write short phrases separated by commas.",
}


def enhance_request(idea, length="medium", style="any style", output_format="one paragraph", notes=""):
    """Pure function. Builds the request text only; it never calls an LLM."""
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
    lines.append("Reply with the prompt only.")
    return "\n".join(lines)


class SYPromptEnhanceRequest:
    DESCRIPTION = "Wraps a short idea in a clear request for an LLM, with length and style choices. It only builds the text."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("request",)

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
            },
        }

    def run(self, idea, length, style, output_format, notes=""):
        return (enhance_request(idea, length, style, output_format, notes),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptEnhanceRequest", SYPromptEnhanceRequest)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptEnhanceRequest"] = "Prompt Enhance Request SY"
