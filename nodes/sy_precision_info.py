"""Precision Info SY: a lookup table of number formats (fp16, fp8, ...) with bytes per parameter and size for N billion parameters."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ALL = "all (show table)"

# name: (bytes per parameter, note). GGUF values are approximate averages.
PRECISIONS = {
    "fp32": (4.0, "Full precision. Biggest files."),
    "fp16": (2.0, "Half precision. Common for models."),
    "bf16": (2.0, "Half precision with a wider range. Common for new models."),
    "fp8": (1.0, "8-bit float. About half of fp16."),
    "int8": (1.0, "8-bit whole numbers."),
    "nf4": (0.5, "4-bit. Small, some quality loss."),
    "fp4": (0.5, "4-bit float. Small, some quality loss."),
    "Q8_0 (gguf)": (1.0625, "About 8.5 bits per parameter."),
    "Q6_K (gguf)": (0.82, "About 6.6 bits per parameter."),
    "Q5_K_M (gguf)": (0.71, "About 5.7 bits per parameter."),
    "Q4_K_M (gguf)": (0.61, "About 4.9 bits per parameter."),
    "Q3_K_M (gguf)": (0.49, "About 3.9 bits per parameter."),
    "Q2_K (gguf)": (0.33, "About 2.6 bits per parameter. Clear quality loss."),
}


def size_gb(billions, dtype):
    """Pure function. Decimal GB for `billions` billion parameters in `dtype`."""
    b = float(billions)
    if b <= 0:
        raise ValueError("parameters (billions) must be more than 0, got %s" % b)
    if dtype not in PRECISIONS:
        raise ValueError("unknown precision %r. Pick one from the list." % dtype)
    return b * PRECISIONS[dtype][0]


def table_text(billions, dtype=ALL):
    """Pure function. Text table. Shows every row, or only `dtype`."""
    names = list(PRECISIONS) if dtype == ALL else [dtype]
    lines = ["Size for %g billion parameters (estimate):" % float(billions)]
    for n in names:
        bpp, note = PRECISIONS[n]
        lines.append("%s: %.4g bytes per parameter = %.2f GB. %s" % (n, bpp, size_gb(billions, n), note))
    return "\n".join(lines)


WORK_ROOM = 1.2  # 20 percent extra room for work memory


def fit_text(billions, dtype, card_gb, room=WORK_ROOM):
    """Pure function. Plain sentence: does this model fit in a card with `card_gb` GB of VRAM (0 = no card given)?"""
    card = float(card_gb)
    if card < 0:
        raise ValueError("card_vram_gb cannot be negative, got %s" % card)
    if card == 0:
        return "No card size given. Type your graphics card memory in card_vram_gb (for example 24) to see what fits."
    need = {n: size_gb(billions, n) * room for n in PRECISIONS}
    fits = [n for n in PRECISIONS if need[n] <= card]
    best = max(fits, key=lambda n: PRECISIONS[n][0]) if fits else None
    if dtype == ALL:
        if not fits:
            return "Nothing fits in %g GB for %g billion parameters, even the smallest format needs about %.1f GB." % (
                card, float(billions), min(need.values()))
        return "On a %g GB card (with 20%% room for work memory) these fit: %s. Best quality that fits: %s." % (
            card, ", ".join(fits), best)
    if dtype not in PRECISIONS:
        raise ValueError("unknown precision %r. Pick one from the list." % dtype)
    if need[dtype] <= card:
        return "%s fits in %g GB: needs about %.1f GB with 20%% room, %.1f GB spare." % (dtype, card, need[dtype], card - need[dtype])
    tail = "Largest format that fits: %s." % best if best else "No format fits, so use a smaller model or offload to the CPU."
    return "%s does NOT fit in %g GB: needs about %.1f GB with 20%% room, %.1f GB too much. %s" % (
        dtype, card, need[dtype], need[dtype] - card, tail)


class SYPrecisionInfo:
    DESCRIPTION = ("Shows how many bytes each number format uses per parameter and the file size for a model with N billion parameters. "
                   "Type your card memory in card_vram_gb and it also says which formats fit and the best one that does.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("text", "size_gb", "fit")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "parameters_billion": ("FLOAT", {"default": 12.0, "min": 0.01, "max": 10000.0, "step": 0.1, "tooltip": "Model size in billions of parameters, for example 12."}),
            "precision": ([ALL] + list(PRECISIONS), {"tooltip": "Number format to look up, or show the whole table. With the table, size_gb is the fp16 size."}),
        },
            "optional": {
                "card_vram_gb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 1.0, "tooltip": "Your graphics card memory in GB, for example 24. 0 turns the fit check off."}),
            }}

    def run(self, parameters_billion, precision, card_vram_gb=0.0):
        text = table_text(parameters_billion, precision)
        gb = size_gb(parameters_billion, "fp16" if precision == ALL else precision)
        return (text, gb, fit_text(parameters_billion, precision, card_vram_gb))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PrecisionInfo", SYPrecisionInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYPrecisionInfo"] = "Precision Info SY"
