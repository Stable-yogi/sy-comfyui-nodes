"""Math Expression SY: works out a typed formula with a small safe parser (no code is ever run)."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_LENGTH = 500
MAX_DEPTH = 50
MAX_BITS = 4096
VARIABLES = ("a", "b", "c")
FUNCTIONS = {"min": (1, None), "max": (1, None), "abs": (1, 1), "round": (1, 2),
             "floor": (1, 1), "ceil": (1, 1), "sqrt": (1, 1)}


def _round_half_away(x, digits=0):
    if isinstance(x, int) and digits >= 0:
        return x
    scale = 10 ** digits
    r = math.floor(abs(x) * scale + 0.5) / scale
    r = r if x >= 0 else -r
    return int(r) if digits == 0 else r


def tokenize(text):
    """Turn the text into a list of (kind, value, position). Kinds: num, name, op, end."""
    tokens = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch in " \t\r\n":
            i += 1
        elif (ch.isascii() and ch.isdigit()) or (ch == "." and i + 1 < n and text[i + 1].isascii() and text[i + 1].isdigit()):
            j = i
            while j < n and text[j].isascii() and text[j].isdigit():
                j += 1
            is_float = False
            if j < n and text[j] == ".":
                is_float = True
                j += 1
                while j < n and text[j].isascii() and text[j].isdigit():
                    j += 1
            if j < n and text[j] in "eE":
                k = j + 1
                if k < n and text[k] in "+-":
                    k += 1
                if k < n and text[k].isascii() and text[k].isdigit():
                    while k < n and text[k].isascii() and text[k].isdigit():
                        k += 1
                    is_float = True
                    j = k
            raw = text[i:j]
            tokens.append(("num", float(raw) if is_float else int(raw), i))
            i = j
        elif ch.isascii() and (ch.isalpha() or ch == "_"):
            j = i
            while j < n and text[j].isascii() and (text[j].isalnum() or text[j] == "_"):
                j += 1
            tokens.append(("name", text[i:j], i))
            i = j
        elif text.startswith("**", i):
            tokens.append(("op", "**", i))
            i += 2
        elif text.startswith("//", i):
            tokens.append(("op", "//", i))
            i += 2
        elif ch in "+-*/%(),":
            tokens.append(("op", ch, i))
            i += 1
        else:
            raise ValueError("Unexpected character %r at position %d. Allowed: numbers, a b c, + - * / // %% **, "
                             "brackets, and the functions %s." % (ch, i + 1, " ".join(FUNCTIONS)))
    tokens.append(("end", None, n))
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self.t = tokens
        self.p = 0
        self.vars = variables
        self.depth = 0

    def peek(self):
        return self.t[self.p]

    def take(self):
        tok = self.t[self.p]
        self.p += 1
        return tok

    def is_op(self, value):
        k, v, _ = self.peek()
        return k == "op" and v == value

    def enter(self):
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise ValueError("The formula is nested too deeply (more than %d levels). Make it simpler." % MAX_DEPTH)

    def leave(self):
        self.depth -= 1

    def where(self):
        k, v, pos = self.peek()
        return "the end of the formula" if k == "end" else "position %d" % (pos + 1)

    def parse(self):
        value = self.expr()
        if self.peek()[0] != "end":
            raise ValueError("Unexpected %r at %s. Check for a missing operator or an extra bracket." % (self.peek()[1], self.where()))
        return value

    def expr(self):
        v = self.term()
        while self.is_op("+") or self.is_op("-"):
            op = self.take()[1]
            r = self.term()
            v = v + r if op == "+" else v - r
            self.check(v)
        return v

    def term(self):
        v = self.unary()
        while self.peek()[0] == "op" and self.peek()[1] in ("*", "/", "//", "%"):
            op = self.take()[1]
            r = self.unary()
            if op == "*":
                v = v * r
            else:
                if r == 0:
                    raise ValueError("Division by zero: the right side of %s is 0. Change the formula so it never divides by 0." % op)
                v = v / r if op == "/" else (v // r if op == "//" else v % r)
            self.check(v)
        return v

    def unary(self):
        if self.is_op("-") or self.is_op("+"):
            op = self.take()[1]
            self.enter()
            v = self.unary()
            self.leave()
            return -v if op == "-" else v
        return self.power()

    def power(self):
        base = self.primary()
        if self.is_op("**"):
            self.take()
            self.enter()
            exp = self.unary()  # right to left, and allows 2 ** -1
            self.leave()
            return self.do_pow(base, exp)
        return base

    def do_pow(self, base, exp):
        if base == 0 and exp < 0:
            raise ValueError("Division by zero: 0 cannot be raised to a negative power.")
        if isinstance(base, int) and isinstance(exp, int) and exp >= 0:
            if abs(base) > 1 and exp * abs(base).bit_length() > MAX_BITS:
                raise ValueError("The result of ** is too large. Use smaller numbers.")
            return base ** exp
        try:
            r = math.pow(base, exp)
        except OverflowError:
            raise ValueError("The result of ** is too large. Use smaller numbers.")
        except ValueError:
            raise ValueError("A negative number cannot be raised to a fractional power.")
        return self.check(r)

    def check(self, v):
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("The result is too large or not a number. Use smaller numbers.")
        if isinstance(v, int) and v.bit_length() > MAX_BITS:
            raise ValueError("The result is too large. Use smaller numbers.")
        return v

    def primary(self):
        kind, val, pos = self.take()
        if kind == "num":
            return val
        if kind == "op" and val == "(":
            self.enter()
            v = self.expr()
            self.leave()
            self.close()
            return v
        if kind == "name":
            if val in FUNCTIONS:
                return self.call(val)
            if val in VARIABLES:
                return self.vars[val]
            raise ValueError("Unknown name %r at position %d. Use a, b, c or one of: %s." % (val, pos + 1, " ".join(FUNCTIONS)))
        if kind == "end":
            raise ValueError("The formula ends too early. Something is missing after the last operator or bracket.")
        raise ValueError("Unexpected %r at position %d. A number, a name or a bracket should be here." % (val, pos + 1))

    def close(self):
        if not self.is_op(")"):
            raise ValueError("A closing bracket ) is missing near %s." % self.where())
        self.take()

    def call(self, name):
        if not self.is_op("("):
            raise ValueError("The function %s needs brackets, like %s(a)." % (name, name))
        self.take()
        self.enter()
        args = []
        if not self.is_op(")"):
            args.append(self.expr())
            while self.is_op(","):
                self.take()
                args.append(self.expr())
        self.leave()
        self.close()
        lo, hi = FUNCTIONS[name]
        if len(args) < lo or (hi is not None and len(args) > hi):
            want = "at least %d" % lo if hi is None else (str(lo) if lo == hi else "%d to %d" % (lo, hi))
            raise ValueError("%s takes %s value(s), but got %d." % (name, want, len(args)))
        return self.check(self.apply(name, args))

    def apply(self, name, args):
        if name == "min":
            return min(args)
        if name == "max":
            return max(args)
        if name == "abs":
            return abs(args[0])
        if name == "floor":
            return math.floor(args[0])
        if name == "ceil":
            return math.ceil(args[0])
        if name == "sqrt":
            if args[0] < 0:
                raise ValueError("sqrt of a negative number (%s) is not allowed." % args[0])
            return math.sqrt(args[0])
        digits = 0
        if len(args) == 2:
            if args[1] != int(args[1]) or abs(args[1]) > 15:
                raise ValueError("The second value of round must be a whole number from -15 to 15.")
            digits = int(args[1])
        return _round_half_away(args[0], digits)


def evaluate(text, a=0.0, b=0.0, c=0.0):
    """Pure function. Returns the result as an int or a float. Raises ValueError with a plain message."""
    if not isinstance(text, str):
        raise ValueError("The formula must be text.")
    if len(text) > MAX_LENGTH:
        raise ValueError("The formula is too long (%d characters). The limit is %d." % (len(text), MAX_LENGTH))
    if text.strip() == "":
        raise ValueError("The formula is empty. Type something like a * 2 + b.")
    variables = {"a": a, "b": b, "c": c}
    for k, v in variables.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or (isinstance(v, float) and not math.isfinite(v)):
            raise ValueError("Variable %s must be a normal number." % k)
    return _Parser(tokenize(text), variables).parse()


def to_outputs(value):
    """Returns (int_value, float_value). The int is the nearest whole number (halves go away from 0)."""
    if isinstance(value, int):
        return value, float(value)
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1), float(value)


class SYMathExpression:
    DESCRIPTION = "Works out a formula you type, like a * 2 + b. Uses a, b, c and min max abs round floor ceil sqrt. Safe: it only does maths."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "expression": ("STRING", {"default": "a + b", "multiline": False, "tooltip": "The formula. Use + - * / // % ** brackets, a b c and functions."}),
            },
            "optional": {
                "a": num("Value for the letter a in the formula."),
                "b": num("Value for the letter b in the formula."),
                "c": num("Value for the letter c in the formula."),
            },
        }

    def run(self, expression, a=0.0, b=0.0, c=0.0):
        return to_outputs(evaluate(expression, a, b, c))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MathExpression", SYMathExpression)
NODE_DISPLAY_NAME_MAPPINGS["SYMathExpression"] = "Math Expression SY"
