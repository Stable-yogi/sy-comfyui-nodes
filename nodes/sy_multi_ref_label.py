"""Multi Ref Label SY: labels up to four reference pictures as Image 1..4 and adds the task."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def label_refs(refs, task):
    """Pure function. refs is a list of strings (empty = not used). Returns (text, ref_count)."""
    lines = []
    for i, desc in enumerate(refs, start=1):
        d = " ".join(str(desc or "").split())
        if d:
            lines.append("Image %d: %s" % (i, d))
    if not lines:
        raise ValueError("no reference is filled: describe at least one of ref_1 to ref_4")
    t = str(task or "").strip()
    if not t:
        raise ValueError("task is empty: say what the model should do with the pictures")
    return "\n".join(lines) + "\n\n" + t, len(lines)


class SYMultiRefLabel:
    DESCRIPTION = "Labels your reference pictures as 'Image 1', 'Image 2' and so on, then adds the task. Use it when an edit model gets several pictures."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "ref_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task": ("STRING", {"default": "", "multiline": True, "tooltip": "What the model should do, using the names Image 1, Image 2 and so on."}),
            },
            "optional": {
                "ref_1": ("STRING", {"default": "", "tooltip": "Short description of the first picture. Leave empty if unused."}),
                "ref_2": ("STRING", {"default": "", "tooltip": "Short description of the second picture. Leave empty if unused."}),
                "ref_3": ("STRING", {"default": "", "tooltip": "Short description of the third picture. Leave empty if unused."}),
                "ref_4": ("STRING", {"default": "", "tooltip": "Short description of the fourth picture. Leave empty if unused."}),
            },
        }

    def run(self, task, ref_1="", ref_2="", ref_3="", ref_4=""):
        return label_refs([ref_1, ref_2, ref_3, ref_4], task)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MultiRefLabel", SYMultiRefLabel)
