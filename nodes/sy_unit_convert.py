"""Unit Convert SY: converts a number between common units."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

QUANTITIES = ("length", "weight", "temperature", "speed", "data size", "time")

# Factor = how many base units one of this unit is. Bases: metre, kilogram, metre per second, byte, second.
# Data size uses steps of 1024 (1 kb = 1024 b). Temperature is handled apart (it goes through Celsius).
FACTORS = {
    "length": {"m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344},
    "weight": {"kg": 1.0, "g": 0.001, "mg": 0.000001, "lb": 0.45359237, "oz": 0.028349523125},
    "speed": {"m/s": 1.0, "km/h": 1.0 / 3.6, "mph": 0.44704, "kn": 1852.0 / 3600.0},
    "data size": {"b": 1.0, "kb": 1024.0, "mb": 1024.0 ** 2, "gb": 1024.0 ** 3, "tb": 1024.0 ** 4},
    "time": {"ms": 0.001, "s": 1.0, "min": 60.0, "h": 3600.0, "d": 86400.0},
}
TEMPERATURE_UNITS = ("c", "f", "k")


def units_of(quantity):
    """Pure function. The unit names allowed for a quantity."""
    if quantity not in QUANTITIES:
        raise ValueError("quantity must be one of: %s (got %r)" % (", ".join(QUANTITIES), quantity))
    if quantity == "temperature":
        return TEMPERATURE_UNITS
    return tuple(FACTORS[quantity])


def clean_unit(unit, quantity):
    """Pure function. Lower-cases and trims the unit, and refuses one that does not belong to the quantity."""
    allowed = units_of(quantity)
    u = str(unit).strip().lower()
    if u not in allowed:
        raise ValueError("%r is not a unit of %s. Use one of: %s" % (str(unit).strip(), quantity, ", ".join(allowed)))
    return u


def to_base(value, unit, quantity):
    """Pure function. Value in the base unit (Celsius for temperature)."""
    u = clean_unit(unit, quantity)
    if quantity == "temperature":
        if u == "c":
            return float(value)
        if u == "f":
            return (float(value) - 32.0) * 5.0 / 9.0
        return float(value) - 273.15
    return float(value) * FACTORS[quantity][u]


def from_base(value, unit, quantity):
    """Pure function. Turns a base-unit value into the given unit."""
    u = clean_unit(unit, quantity)
    if quantity == "temperature":
        if u == "c":
            return float(value)
        if u == "f":
            return float(value) * 9.0 / 5.0 + 32.0
        return float(value) + 273.15
    return float(value) / FACTORS[quantity][u]


def _fmt(x, precision):
    s = "%.*f" % (precision, x)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


def convert(value, quantity, from_unit, to_unit, precision=4):
    """Pure function. Returns (result, text). The result is rounded to precision decimals."""
    v = float(value)
    if math.isnan(v) or math.isinf(v):
        raise ValueError("value must be a normal number, not nan or infinity")
    precision = int(precision)
    if precision < 0 or precision > 12:
        raise ValueError("precision must be 0 to 12, got %d" % precision)
    fu = clean_unit(from_unit, quantity)
    tu = clean_unit(to_unit, quantity)
    base = to_base(v, fu, quantity)
    if quantity == "temperature" and base < -273.15 - 1e-9:
        raise ValueError("%s %s is below absolute zero: use a higher temperature" % (_fmt(v, 6), fu))
    result = round(from_base(base, tu, quantity), precision)
    if result == 0:
        result = 0.0   # no negative zero
    text = "%s %s = %s %s" % (_fmt(v, 6), fu, _fmt(result, precision), tu)
    return (result, text)


class SYUnitConvert:
    DESCRIPTION = ("Converts a number between common units of length, weight, temperature, speed, data size or "
                   "time. Type the unit names; a unit that does not fit the quantity is refused with a list.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("result", "text")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 1.0, "min": -1e15, "max": 1e15, "step": 0.001, "tooltip": "The number to convert."}),
                "quantity": (list(QUANTITIES), {"default": "length", "tooltip": "What kind of unit this is. Data size uses steps of 1024."}),
                "from_unit": ("STRING", {"default": "m", "tooltip": "Unit of the value. length: m km cm mm in ft yd mi. weight: kg g mg lb oz. temperature: c f k."}),
                "to_unit": ("STRING", {"default": "ft", "tooltip": "Unit you want. speed: m/s km/h mph kn. data size: b kb mb gb tb. time: ms s min h d."}),
                "precision": ("INT", {"default": 4, "min": 0, "max": 12, "tooltip": "How many decimals the result is rounded to."}),
            }
        }

    def run(self, value, quantity, from_unit, to_unit, precision):
        return convert(value, quantity, from_unit, to_unit, precision)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "UnitConvert", SYUnitConvert)
NODE_DISPLAY_NAME_MAPPINGS["SYUnitConvert"] = "Unit Convert SY"
