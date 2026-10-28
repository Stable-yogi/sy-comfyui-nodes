import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_math_expression as m

N = 0


def eq(text, want, **kw):
    global N
    got = m.evaluate(text, **kw)
    if isinstance(want, float):
        assert math.isclose(got, want, rel_tol=1e-9), (text, got, want)
    else:
        assert got == want and type(got) is int, (text, got, want)
    N += 1


def bad(text, word, **kw):
    global N
    try:
        m.evaluate(text, **kw)
    except ValueError as e:
        assert word.lower() in str(e).lower(), (text, str(e), word)
        N += 1
        return
    raise AssertionError("must raise: %r" % (text,))


def run():
    global N
    N = 0
    # basics and precedence
    eq("1+2*3", 7)
    eq("(1+2)*3", 9)
    eq("2*3+4*5", 26)
    eq("10-4-3", 3)
    eq("100/10/5", 2.0)
    eq("7//2", 3)
    eq("-7//2", -4)
    eq("7%3", 1)
    eq("-7%3", 2)
    eq("2**3**2", 512)
    eq("2**-1", 0.5)
    eq("-2**2", -4)
    eq("(-2)**2", 4)
    eq("2*3**2", 18)
    eq("10-2*3**2/6", 7.0)
    eq("1.5+.5", 2.0)
    eq("1e3", 1000.0)
    eq("2e-1*10", 2.0)
    eq("  3 \t + 4 ", 7)
    # unary minus
    eq("-5", -5)
    eq("--5", 5)
    eq("-(-5)", 5)
    eq("+5", 5)
    eq("3 - -2", 5)
    eq("-a", -4.0, a=4.0)
    eq("2*-3", -6)
    # variables
    eq("a*2+b-c", 9.0, a=3.0, b=4.0, c=1.0)
    eq("a", 0.0)
    # functions
    eq("min(3,1,2)", 1)
    eq("max(3,1,2)", 3)
    eq("max(a,b)", 5.5, a=5.5, b=2.0)
    eq("abs(-3.5)", 3.5)
    eq("round(2.5)", 3)
    eq("round(-2.5)", -3)
    eq("round(3.14159,2)", 3.14)
    eq("floor(-1.2)", -2)
    eq("ceil(1.2)", 2)
    eq("sqrt(16)", 4.0)
    eq("min(max(1,5),3)", 3)
    eq("floor(a/b)", 2, a=7.0, b=3.0)
    # outputs
    assert m.to_outputs(2.5) == (3, 2.5)
    assert m.to_outputs(-2.5) == (-3, -2.5)
    assert m.to_outputs(7) == (7, 7.0)
    assert m.SYMathExpression().run("a+1", a=1.4)[0] == 2
    N += 4
    # division by zero
    bad("1/0", "division by zero")
    bad("5//0", "division by zero")
    bad("5%0", "division by zero")
    bad("1/(a-a)", "division by zero", a=3.0)
    bad("0**-1", "division by zero")
    # bad tokens and syntax
    bad("1 $ 2", "unexpected character")
    bad("a; b", "unexpected character")
    bad("__import__('os')", "unexpected character")
    bad("a.b", "unexpected")
    bad("x+1", "unknown name")
    bad("d", "unknown name")
    bad("open", "unknown name")
    bad("sqrt", "needs brackets")
    bad("sqrt(-1)", "negative")
    bad("min()", "takes")
    bad("abs(1,2)", "takes")
    bad("round(1.5,0.5)", "whole number")
    bad("(1+2", "closing bracket")
    bad("1+2)", "unexpected")
    bad("1+", "ends too early")
    bad("1 2", "unexpected")
    bad("*3", "unexpected")
    bad("", "empty")
    bad("   ", "empty")
    bad("(-8)**0.5", "negative number")
    bad("10**10**10", "too large")
    bad("9.0**999999", "too large")
    bad("1e308*10", "too large")
    # long input limit (500) and nesting limit (50)
    eq("1" + "+1" * 249, 250)  # 499 characters
    eq("1+" * 249 + "1", 250)
    bad("1" + "+1" * 250 + "+", "too long")  # 502 characters
    bad("1" * 501, "too long")
    assert len("1" * 500) == 500
    eq("(" * 50 + "7" + ")" * 50, 7)
    bad("(" * 51 + "7" + ")" * 51, "nested too deeply")
    eq("-" * 50 + "7", 7)
    bad("-" * 51 + "7", "nested too deeply")
    bad("min(" * 51 + "1" + ")" * 51, "nested too deeply")
    bad(None, "text")
    bad("a", "normal number", a=float("nan"))
    assert m.SYMathExpression.RETURN_TYPES == ("INT", "FLOAT")
    N += 2
    return N
