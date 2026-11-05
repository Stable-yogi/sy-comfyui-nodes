"""Dataset Scene List SY: one character picture in, 40 scene prompts out (framing + place + light + action),
so one click makes a varied training set of the same character. Outputs are lists: ComfyUI runs the next node once per item."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DEFAULT_CHARACTER = "the person from <image1>"
DEFAULT_KEEP = "Keep the face, hair and clothes exactly the same as <image1>."
DEFAULT_STYLE = "realistic photo"
MAX_COUNT = 40

# framing key -> words used in the prompt
FRAMINGS = {
    "closeup": "close-up portrait",
    "headshoulders": "head and shoulders portrait",
    "halfbody": "half body photo",
    "fullbody": "full body photo",
    "side": "photo from the side",
    "threequarter": "three-quarter view photo",
    "behind": "photo from behind, looking back over the shoulder",
    "lowangle": "low angle photo",
    "highangle": "high angle photo",
    "sitting": "photo, sitting",
    "walking": "photo, walking",
    "laughing": "close-up laughing portrait",
}

# (framing key, short name part, scene words). The scene words follow "of {character}".
SCENES = (
    ("closeup", "kitchen", "in a kitchen with soft morning light from the window"),
    ("headshoulders", "street_night", "on a city street at night with glowing shop signs behind"),
    ("fullbody", "beach_sunset", "standing on a beach at sunset with warm orange light"),
    ("walking", "forest_path", "along a forest path with sunlight coming through the trees"),
    ("sitting", "library", "at a long wooden table in a quiet library"),
    ("halfbody", "office_desk", "at an office desk with a laptop and a notebook"),
    ("closeup", "cafe_window", "next to a cafe window with daylight on the face"),
    ("fullbody", "snowy_park", "in a snowy park with bare trees and fresh snow"),
    ("walking", "rain_umbrella", "on a rainy street holding an umbrella"),
    ("halfbody", "gym", "in a bright gym beside the weights"),
    ("side", "train_station", "on a train station platform waiting for the train"),
    ("threequarter", "mountain_view", "with a wide mountain view and a clear sky behind"),
    ("closeup", "studio_grey", "against a plain grey studio backdrop with even soft light"),
    ("fullbody", "studio_white", "against a plain white studio backdrop"),
    ("halfbody", "garden", "in a garden full of flowers on a sunny afternoon"),
    ("behind", "rooftop_dusk", "on a rooftop at dusk while the city lights come on"),
    ("highangle", "market", "between the colourful stalls of a busy outdoor market"),
    ("threequarter", "museum", "in a museum hall looking at a large painting"),
    ("halfbody", "car_interior", "in the passenger seat of a car with daylight through the window"),
    ("sitting", "bedroom_lamp", "on a bed in a bedroom lit by a warm lamp"),
    ("behind", "concert", "in a concert crowd under coloured stage lights"),
    ("walking", "desert_road", "on a long empty desert road under a hot sun"),
    ("sitting", "lake_dock", "on a wooden dock beside a calm lake in the early morning"),
    ("halfbody", "bookshop", "between tall shelves in a small bookshop"),
    ("side", "bridge", "on a stone bridge over a river with light mist"),
    ("lowangle", "subway", "inside a subway carriage with bright overhead lights"),
    ("halfbody", "art_studio", "painting at an easel in an art studio"),
    ("halfbody", "cooking", "cooking at a stove with steam rising from a pan"),
    ("sitting", "reading", "reading a book in an armchair next to a window"),
    ("headshoulders", "phone_call", "talking on a phone on a quiet street"),
    ("laughing", "coffee", "while holding a cup of coffee"),
    ("walking", "bicycle", "pushing a bicycle along a tree-lined road"),
    ("fullbody", "dog_park", "in a park playing with a dog on the grass"),
    ("closeup", "studio_dark", "against a plain dark studio backdrop with one soft side light"),
    ("highangle", "stairs", "on a wide staircase"),
    ("closeup", "golden_hour", "outdoors in golden hour light with blurred trees behind"),
    ("laughing", "picnic", "on a picnic blanket in a green field"),
    ("threequarter", "studio_beige", "against a plain beige studio wall with soft window light"),
    ("lowangle", "city_square", "standing in a city square with tall buildings above"),
    ("halfbody", "studio_blue", "against a plain light blue studio backdrop"),
)


def _templates():
    out = []
    for key, short, scene in SCENES:
        if key not in FRAMINGS:
            raise ValueError("internal: unknown framing %r" % key)
        out.append((key, short, "%s of {character} %s" % (FRAMINGS[key], scene)))
    return out


TEMPLATES = _templates()


def safe_name(text):
    """Pure function. Keeps letters, digits, underscore and dash; everything else becomes one underscore."""
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", str(text)).strip("_")
    return s or "scene"


def scene_prompts(character, count, keep_line, style, start_seed):
    """Pure function. Returns (prompts, seeds, names), each a list of `count` items (the first `count` templates)."""
    character = str(character).strip()
    if not character:
        raise ValueError("character is empty: write a few words for the character, for example 'the person from <image1>'")
    count = int(count)
    if not 1 <= count <= MAX_COUNT:
        raise ValueError("count must be between 1 and %d, got %d" % (MAX_COUNT, count))
    start_seed = int(start_seed)
    if start_seed < 0:
        raise ValueError("start_seed must be 0 or more, got %d" % start_seed)
    keep_line = str(keep_line).strip()
    style = str(style).strip()
    prompts, seeds, names = [], [], []
    for i in range(count):
        key, short, template = TEMPLATES[i]
        text = template.replace("{character}", character)
        if style:
            text += ", " + style
        text += "."
        if keep_line:
            text += " " + keep_line
        prompts.append(text)
        seeds.append(start_seed + i)
        names.append("%03d_%s_%s" % (i + 1, key, safe_name(short)))
    return prompts, seeds, names


def numbered_text(prompts):
    """Pure function. One numbered line per prompt, for reading."""
    return "\n".join("%d. %s" % (i + 1, p) for i, p in enumerate(prompts))


class SYDatasetSceneList:
    DESCRIPTION = ("Makes up to 40 different scene prompts for one character: close-ups, full body, side and back views, "
                   "indoor and outdoor places, plain backgrounds. Each output is a list, so one click makes one picture per scene.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "seed", "name", "all_prompts")
    OUTPUT_IS_LIST = (True, True, True, False)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character": ("STRING", {"default": DEFAULT_CHARACTER, "tooltip": "A few words that name the character in every prompt. <image1> points at the first picture."}),
                "count": ("INT", {"default": MAX_COUNT, "min": 1, "max": MAX_COUNT, "tooltip": "How many scenes to make. Less than 40 takes the first ones."}),
                "keep_line": ("STRING", {"default": DEFAULT_KEEP, "multiline": True, "tooltip": "A sentence added to every prompt so the character stays the same."}),
                "style": ("STRING", {"default": DEFAULT_STYLE, "tooltip": "The look of the pictures, added after each scene. Empty adds nothing."}),
                "start_seed": ("INT", {"default": 1, "min": 0, "max": 2 ** 53, "tooltip": "Seed of the first picture. Each next picture adds one."}),
            }
        }

    def run(self, character, count, keep_line, style, start_seed):
        prompts, seeds, names = scene_prompts(character, count, keep_line, style, start_seed)
        return (prompts, seeds, names, numbered_text(prompts))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DatasetSceneList", SYDatasetSceneList)
NODE_DISPLAY_NAME_MAPPINGS["SYDatasetSceneList"] = "Dataset Scene List SY"
