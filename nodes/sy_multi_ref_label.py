"""Multi Ref Label SY: labels up to four reference pictures as Image 1..4 and adds the task."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def _label_word(label):
    word = " ".join(str(label or "").split())
    if len(word) > 30:
        raise ValueError("label is too long: %d characters (limit 30)" % len(word))
    return word or "Image"


def label_refs(refs, task, label="Image", task_first=False, renumber=False):
    """Pure function. refs is a list of strings (empty = not used). Returns (text, ref_count).
    renumber=True counts the filled slots 1, 2, 3 instead of keeping the slot numbers."""
    word = _label_word(label)
    lines = []
    for i, desc in enumerate(refs, start=1):
        d = " ".join(str(desc or "").split())
        if d:
            lines.append("%s %d: %s" % (word, len(lines) + 1 if renumber else i, d))
    if not lines:
        raise ValueError("no reference is filled: describe at least one of ref_1 to ref_4")
    t = str(task or "").strip()
    if not t:
        raise ValueError("task is empty: say what the model should do with the pictures")
    block = "\n".join(lines)
    return ((t + "\n\n" + block) if task_first else (block + "\n\n" + t)), len(lines)


def refs_info(refs, task, label="Image", renumber=False):
    """Pure function. One plain line: which labels were written, and a warning when the task names a picture that has no description."""
    word = _label_word(label)
    used = []
    for i, desc in enumerate(refs, start=1):
        if " ".join(str(desc or "").split()):
            used.append(len(used) + 1 if renumber else i)
    info = "%d reference%s labelled: %s." % (len(used), "" if len(used) == 1 else "s", ", ".join("%s %d" % (word, n) for n in used))
    named = {int(x) for x in re.findall(re.escape(word) + r"\s+(\d{1,3})\b", str(task or ""), re.I)}
    missing = sorted(n for n in named if n not in used)
    if missing:
        info += " WARNING: the task names %s, which has no description." % ", ".join("%s %d" % (word, n) for n in missing)
    return info


class SYMultiRefLabel:
    DESCRIPTION = ("Labels your reference pictures as 'Image 1', 'Image 2' and so on, then adds the task. Use it when an edit model gets several pictures. "
                   "Can put the task first, renumber the pictures without gaps, and warns when the task names a picture you did not describe.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("prompt", "ref_count", "info")

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
                "label": ("STRING", {"default": "Image", "tooltip": "The word used before each number, for example Image or Picture."}),
                "task_first": ("BOOLEAN", {"default": False, "tooltip": "On: write the task before the list of pictures."}),
                "renumber": ("BOOLEAN", {"default": False, "tooltip": "On: number the filled slots 1, 2, 3 with no gaps."}),
            },
        }

    def run(self, task, ref_1="", ref_2="", ref_3="", ref_4="", label="Image", task_first=False, renumber=False):
        refs = [ref_1, ref_2, ref_3, ref_4]
        text, count = label_refs(refs, task, label, task_first, renumber)
        return text, count, refs_info(refs, task, label, renumber)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MultiRefLabel", SYMultiRefLabel)
