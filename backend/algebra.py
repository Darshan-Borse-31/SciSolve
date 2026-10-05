"""Algebra module for SciSolve."""
import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)
from backend.common import error_result, ok_result

INFO = {
    "id": "algebra",
    "name": "Algebra",
    "symbol": "x²",
    "title": "Algebra Solver",
    "short": "Solve equations, simplify, factor and expand expressions.",
    "description": "Ask me to solve equations, simplify expressions, factor polynomials, etc.",
    "placeholder": "Try: Solve x^2 - 5x + 6 = 0",
    "examples": [
        "Solve x^2 - 5x + 6 = 0",
        "Factor x^2 - 9",
        "Simplify (x^2 - 1)/(x - 1)"
    ]
}

_TRANSFORMS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

_ALLOWED = re.compile(r"^[A-Za-z0-9_\s+\-*/^=().,]+$")
_LOCAL = {"sqrt": sp.sqrt, "pi": sp.pi, "E": sp.E}

_WORD_REPLACEMENTS = (
    (r"\bto\s+the\s+power\s+of\b", "^"),
    (r"\bto\s+the\s+power\b", "^"),
    (r"\bpower\s+(\d+)\b", r"^\1"),
    (r"\bpower\s+of\b", "^"),
    (r"\bsquare\s+root\s+of\b", "sqrt"),
    (r"\bsquare\s+root\b", "sqrt"),
    (r"\bsquared\b", "^2"),
    (r"\bsquare\b", "^2"),
    (r"\bcubed\b", "^3"),
    (r"\bcube\b", "^3"),
    (r"\bdivided\s+by\b", "/"),
    (r"\bmultiplied\s+by\b", "*"),
    (r"\btimes\b", "*"),
    (r"\bplus\b", "+"),
    (r"\bminus\b", "-"),
    (r"\bequals?\s+to\b", "="),
    (r"\bequal\s+to\b", "="),
    (r"\bequals\b", "="),
)

def _naturalize(query):
    text = query.strip().lower()
    for pattern, replacement in _WORD_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)

    text = re.sub(
        r"^\s*(please\s+)?(can\s+you\s+)?"
        r"(solve|find\s+the\s+roots?|find\s+roots?|"
        r"factor|factorize|simplify|expand)\s*(?:for|of)?\s*",
        "",
        text,
    )

    text = re.sub(r"\s+", " ", text).strip()
    for word, number in (("zero", "0"), ("one", "1"), ("two", "2"), ("three", "3")):
        text = re.sub(rf"\b{word}\b", number, text)
    return text

def _symbols_for(text):
    names = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", text))
    names -= {"sqrt", "pi", "e", "E"}
    local = dict(_LOCAL)
    for name in sorted(names):
        local[name] = sp.Symbol(name)
    return local

def _parse(text):
    if not text or len(text) > 500:
        raise ValueError("Please enter a shorter algebra expression.")
    if not _ALLOWED.fullmatch(text):
        raise ValueError(
            "I couldn't read that as a supported algebra expression. "
            "Try numbers, variables, +, -, *, /, ^, parentheses or sqrt."
        )
    return parse_expr(
        text,
        local_dict=_symbols_for(text),
        transformations=_TRANSFORMS,
        evaluate=True,
    )

def _equation_parts(text):
    if "=" in text:
        left, right = text.split("=", 1)
        if not left.strip() or not right.strip():
            raise ValueError("Please put an expression on both sides of '='.")
        return _parse(left.strip()), _parse(right.strip())
    return _parse(text), sp.Integer(0)

def _main_symbol(expr):
    symbols = sorted(expr.free_symbols, key=lambda s: str(s))
    return symbols[0] if symbols else None

def _solve(expression_text):
    left, right = _equation_parts(expression_text)
    equation = sp.Eq(left, right)
    expr = sp.expand(left - right)
    symbol = _main_symbol(expr)

    if symbol is None:
        if sp.simplify(expr) == 0:
            return ok_result(
                "Equation solved",
                answer="Infinitely many solutions.",
                steps=[
                    {"title": "Simplify", "detail": f"{left} = {right}"},
                    {"title": "Result", "detail": "Both sides are identical."},
                ],
            )
        return ok_result(
            "Equation solved",
            answer="No solution.",
            steps=[
                {"title": "Move everything to one side", "detail": f"{expr} = 0"},
                {"title": "Result", "detail": "The equation is inconsistent."},
            ],
        )

    degree = sp.degree(expr, symbol)
    solutions = sp.solve(equation, symbol)

    steps = [
        {"title": "Write the equation", "detail": f"{equation}"},
        {"title": "Move everything to one side", "detail": f"{sp.factor(expr)} = 0"},
    ]

    if degree == 1:
        steps.append({
            "title": "Solve the linear equation",
            "detail": f"{symbol} = {solutions[0] if solutions else 'no solution'}",
        })
    elif degree == 2:
        a = sp.expand(expr).coeff(symbol, 2)
        b = sp.expand(expr).coeff(symbol, 1)
        c = sp.expand(expr).coeff(symbol, 0)
        disc = sp.simplify(b**2 - 4*a*c)
        steps.append({
            "title": "Identify the quadratic coefficients",
            "detail": f"a = {a}, b = {b}, c = {c}",
        })
        steps.append({
            "title": "Calculate the discriminant",
            "detail": f"Δ = b² - 4ac = {disc}",
        })
        factored = sp.factor(expr)
        if factored != expr:
            steps.append({
                "title": "Factor the quadratic",
                "detail": f"{expr} = {factored}",
            })
    else:
        steps.append({
            "title": "Solve the polynomial",
            "detail": f"Using SymPy to solve {expr} = 0 for {symbol}.",
        })

    answer = ", ".join(f"{symbol} = {s}" for s in solutions) if solutions else "No real solution found."
    return ok_result("Equation solved", answer=answer, steps=steps)

def solve(query):
    try:
        raw = query.strip()
        text = _naturalize(raw)
        if not text:
            return error_result("Please enter an algebra problem.")

        lowered = raw.lower()
        if re.search(r"\b(factor|factorize)\b", lowered):
            operation = "factor"
        elif re.search(r"\bsimplify\b", lowered):
            operation = "simplify"
        elif re.search(r"\bexpand\b", lowered):
            operation = "expand"
        else:
            operation = "solve"

        if operation == "solve":
            return _solve(text)

        expr = _parse(text)

        if operation == "factor":
            result = sp.factor(expr)
            return ok_result(
                "Expression factored",
                answer=str(result),
                steps=[
                    {"title": "Read the expression", "detail": str(expr)},
                    {"title": "Factor", "detail": f"{expr} → {result}"},
                ],
            )

        if operation == "simplify":
            result = sp.cancel(sp.simplify(expr))
            return ok_result(
                "Expression simplified",
                answer=str(result),
                steps=[
                    {"title": "Read the expression", "detail": str(expr)},
                    {"title": "Simplify", "detail": f"{expr} → {result}"},
                ],
            )

        if operation == "expand":
            result = sp.expand(expr)
            return ok_result(
                "Expression expanded",
                answer=str(result),
                steps=[
                    {"title": "Read the expression", "detail": str(expr)},
                    {"title": "Expand", "detail": f"{expr} → {result}"},
                ],
            )

        return error_result("I couldn't determine the algebra operation.")

    except (ValueError, TypeError, SyntaxError):

        return error_result(
        "I couldn't understand that as an algebra problem. "
        "Try something like: Solve x^2 - 5x + 6 = 0"
    )

    except Exception:

        return error_result(
        "I couldn't solve that algebra problem. Check the expression and try again."
    )
