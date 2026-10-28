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


class SYPrecisionInfo:
    DESCRIPTION = "Shows how many bytes each number format uses per parameter and the file size for a model with N billion parameters."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT")
    RETURN_NAMES = ("text", "size_gb")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "parameters_billion": ("FLOAT", {"default": 12.0, "min": 0.01, "max": 10000.0, "step": 0.1, "tooltip": "Model size in billions of parameters, for example 12."}),
            "precision": ([ALL] + list(PRECISIONS), {"tooltip": "Number format to look up, or show the whole table."}),
        }}

    def run(self, parameters_billion, precision):
        text = table_text(parameters_billion, precision)
        gb = size_gb(parameters_billion, "fp16" if precision == ALL else precision)
        return (text, gb)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PrecisionInfo", SYPrecisionInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYPrecisionInfo"] = "Precision Info SY"
