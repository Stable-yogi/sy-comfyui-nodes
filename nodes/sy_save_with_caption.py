"""Save With Caption SY: saves a picture and a same-name .txt caption next to it, for making training sets."""
try:
    from ._sy_safe_paths import save_images
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import save_images
    from _sy_common import category, register

CAPTION_MODES = ["same for all", "one line per picture"]


def clean_caption(text):
    """Pure function. Tidies a tag caption: one line, one space between words, no stray commas, repeated tags removed
    (the first one is kept, upper and lower case count as the same)."""
    flat = " ".join(str(text).split())
    seen, tags = set(), []
    for part in flat.split(","):
        tag = part.strip()
        if tag and tag.lower() not in seen:
            seen.add(tag.lower())
            tags.append(tag)
    return ", ".join(tags)


def apply_trigger(text, trigger):
    """Pure function. Puts the trigger word first and removes it from the rest of the caption, so it appears once."""
    trig = " ".join(str(trigger).split()).strip(", ")
    if not trig:
        return str(text)
    rest = [t.strip() for t in str(text).split(",") if t.strip() and t.strip().lower() != trig.lower()]
    return ", ".join([trig] + rest)


def caption_list(caption, count, mode="same for all", trigger="", clean=False):
    """Pure function. One caption text per picture. A single caption is used for every picture.

    mode "one line per picture": each non-empty line is the caption of one picture (or one line for all of them).
    trigger puts a trigger word first (once). clean tidies spaces, stray commas and repeated tags.
    """
    count = int(count)
    if count < 1:
        raise ValueError("nothing to save: no pictures")
    if mode not in CAPTION_MODES:
        raise ValueError("caption_mode must be one of: %s" % ", ".join(CAPTION_MODES))
    text = str(caption)
    if mode == CAPTION_MODES[1]:
        lines = [ln for ln in text.replace("\r", "\n").split("\n") if ln.strip()]
        if len(lines) == 1:
            lines = lines * count
        elif lines and len(lines) != count:
            raise ValueError("the caption has %d lines but there are %d pictures: give one line per picture, or a single line for all" % (len(lines), count))
        texts = lines
    else:
        texts = [text] * count
    if not texts or not any(t.strip() for t in texts):
        if not str(trigger).strip():
            raise ValueError("the caption is empty: type the caption text")
        texts = [""] * count
    out = []
    for t in texts:
        if clean:
            t = clean_caption(t)
        if str(trigger).strip():
            t = apply_trigger(t, trigger)
        if not t.strip():
            raise ValueError("the caption is empty: type the caption text")
        out.append(t)
    return out


def save_info(ui, captions):
    """Pure function. A plain line telling what was saved."""
    n = len(ui)
    where = (ui[0].get("subfolder") or "(output folder)") if n else ""
    words = max(len(c.split()) for c in captions) if captions else 0
    line = "Saved %d picture%s and %d caption file%s to %s (longest caption: %d words)." % (
        n, "" if n == 1 else "s", len(captions), "" if len(captions) == 1 else "s", where, words)
    if words > 150:
        line += " Long captions can be cut short by some trainers."
    return line


class SYSaveWithCaption:
    DESCRIPTION = ("Saves each picture plus a text file with the same name holding the caption. Good for making training datasets. "
                   "Can put a trigger word first (once), tidy tag captions (spaces, stray commas, repeated tags) and give one caption line per picture. "
                   "Never overwrites: a taken name gets the next number.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("saved_paths", "info", "caption_used")
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The pictures to save."}),
                "caption": ("STRING", {"default": "", "multiline": True, "tooltip": "Text written to the .txt file next to each picture."}),
                "subfolder": ("STRING", {"default": "SY/dataset", "tooltip": "Folder inside the output folder. It is created if missing."}),
                "filename_pattern": ("STRING", {"default": "img_{counter}", "tooltip": "File name without extension. Tokens: {date} {time} {seed} {counter}."}),
                "format": (["png", "jpg", "webp"], {"default": "png", "tooltip": "Picture file type."}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "tooltip": "Quality for jpg and webp. Png ignores it."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 53, "tooltip": "Number used for the {seed} token."}),
            },
            "optional": {
                "caption_mode": (CAPTION_MODES, {"default": "same for all", "tooltip": "same for all: one caption for every picture. one line per picture: line 1 for picture 1, and so on."}),
                "trigger_word": ("STRING", {"default": "", "tooltip": "A word put first in every caption, once, for example sks_style. Empty does nothing."}),
                "clean_tags": ("BOOLEAN", {"default": False, "tooltip": "Tidy a comma caption: one line, no double spaces or stray commas, repeated tags removed."}),
            },
        }

    def run(self, images, caption, subfolder, filename_pattern, format, quality, seed, caption_mode="same for all",
            trigger_word="", clean_tags=False):
        caps = caption_list(caption, images.shape[0], caption_mode, trigger_word, bool(clean_tags))
        paths, ui = save_images(images, subfolder, filename_pattern, format, quality, seed, captions=caps)
        return {"ui": {"images": ui}, "result": ("\n".join(paths), save_info(ui, caps), caps[0])}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveWithCaption", SYSaveWithCaption)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveWithCaption"] = "Save With Caption SY"
