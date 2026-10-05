import re
import math

from backend.common import error_result, ok_result


INFO = {
    "id": "numerical",
    "name": "Numerical Methods",
    "symbol": "≈",
    "title": "Numerical Methods Solver",
    "short": "Root finding, integration and differential equation approximations.",
    "description": "Ask me to approximate roots, integrals and solutions of differential equations, with each iteration shown.",
    "placeholder": "Try: Find a root of x^3 - x - 2 using Newton's method",
    "examples": [
        "Find a root of x^3 - x - 2 using Newton's method",
        "Find root of x^2 - 4 using bisection from 0 to 3",
        "Find root of x^2 - 4 using secant with initial values 1 and 3"
    ]
}


def _find_method(text):
    text = str(text).lower()

    if "bisection" in text or "bisect" in text:
        return "bisection"

    if "newton" in text:
        return "newton"

    if "secant" in text:
        return "secant"

    return None


def _extract_function(text):
    text = text.lower().strip()

    # Remove common instructions
    patterns = [
        r"find\s+(?:a\s+)?root\s+of\s+",
        r"find\s+(?:the\s+)?root\s+of\s+",
        r"solve\s+",
    ]

    expression = text

    for pattern in patterns:
        expression = re.sub(pattern, "", expression)

    # Cut off method instructions
    expression = re.split(
        r"\s+(?:using|with|from|starting|initial)\s+",
        expression,
        maxsplit=1
    )[0]

    expression = expression.strip()

    # Natural language powers
    expression = expression.replace("squared", "^2")
    expression = expression.replace("square", "^2")
    expression = expression.replace("cubed", "^3")
    expression = expression.replace("cube", "^3")

    expression = expression.replace("^", "**")

    # Convert f(x) = 0 into f(x) - 0
    if "=" in expression:
        left, right = expression.split("=", 1)
        expression = f"({left})-({right})"

    # Support implicit multiplication such as 2x
    expression = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expression)

    return expression


def _make_function(expression):
    allowed = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
    }

    def f(x):
        namespace = dict(allowed)
        namespace["x"] = x

        return float(
            eval(
                expression,
                {"__builtins__": {}},
                namespace
            )
        )

    # Test expression
    f(1)

    return f


def _extract_numbers(text):
    return [
        float(x)
        for x in re.findall(
            r"(?<![a-zA-Z])[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
            text
        )
    ]


def _bisection(f, a, b, iterations=30):

    fa = f(a)
    fb = f(b)

    if fa == 0:
        return a, [f"f({a}) = 0, therefore the root is {a}."]

    if fb == 0:
        return b, [f"f({b}) = 0, therefore the root is {b}."]

    if fa * fb > 0:
        raise ValueError(
            "Bisection requires opposite signs at the two starting points."
        )

    steps = [
        f"Starting interval: [{a}, {b}]"
    ]

    for i in range(1, iterations + 1):

        c = (a + b) / 2
        fc = f(c)

        steps.append(
            f"Iteration {i}: "
            f"a = {a:.6f}, "
            f"b = {b:.6f}, "
            f"midpoint = {c:.6f}, "
            f"f(c) = {fc:.6f}"
        )

        if abs(fc) < 1e-8:
            return c, steps

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return (a + b) / 2, steps


def _newton(f, x0, iterations=30):

    steps = [
        f"Initial guess: x₀ = {x0}"
    ]

    h = 1e-6

    for i in range(1, iterations + 1):

        fx = f(x0)

        derivative = (
            f(x0 + h) - f(x0 - h)
        ) / (2 * h)

        if abs(derivative) < 1e-12:
            raise ValueError(
                "Derivative became too small."
            )

        x1 = x0 - fx / derivative

        steps.append(
            f"Iteration {i}: "
            f"x = {x0:.8f}, "
            f"f(x) = {fx:.8f}, "
            f"next x = {x1:.8f}"
        )

        if abs(x1 - x0) < 1e-8:
            return x1, steps

        x0 = x1

    return x0, steps


def _secant(f, x0, x1, iterations=30):

    steps = [
        f"Initial values: x₀ = {x0}, x₁ = {x1}"
    ]

    for i in range(1, iterations + 1):

        f0 = f(x0)
        f1 = f(x1)

        denominator = f1 - f0

        if abs(denominator) < 1e-12:
            raise ValueError(
                "Secant calculation failed because the denominator became too small."
            )

        x2 = x1 - f1 * (x1 - x0) / denominator

        steps.append(
            f"Iteration {i}: "
            f"x₀ = {x0:.8f}, "
            f"x₁ = {x1:.8f}, "
            f"x₂ = {x2:.8f}"
        )

        if abs(x2 - x1) < 1e-8:
            return x2, steps

        x0 = x1
        x1 = x2

    return x1, steps

def _format_steps(steps):
    return [
        {
            "title": f"Iteration {i + 1}",
            "detail": step
        }
        for i, step in enumerate(steps)
    ]

def solve(query):

    if not query or not query.strip():
        return error_result(
            "Please enter a numerical-method problem."
        )

    try:

        method = _find_method(query)

        if method is None:
            return error_result(
                "Please specify a numerical method: "
                "Bisection, Newton-Raphson, or Secant."
            )

        expression = _extract_function(query)

        function = _make_function(expression)

        numbers = _extract_numbers(query)

        if method == "bisection":

            if len(numbers) < 2:
                return error_result(
                    "For Bisection, provide two starting values."
                )

            a = numbers[-2]
            b = numbers[-1]

            root, steps = _bisection(
                function,
                a,
                b
            )

            return ok_result(
                "Bisection Method",
                answer=f"Approximate root: {root:.8f}",
                steps=_format_steps(steps)
            )

        if method == "newton":

            if len(numbers) < 1:
                return error_result(
                    "For Newton-Raphson, provide an initial guess."
                )

            x0 = numbers[-1]

            root, steps = _newton(
                function,
                x0
            )

            return ok_result(
                "Newton-Raphson Method",
                answer=f"Approximate root: {root:.8f}",
               steps=_format_steps(steps)
            )

        if method == "secant":

            if len(numbers) < 2:
                return error_result(
                    "For Secant, provide two initial values."
                )

            x0 = numbers[-2]
            x1 = numbers[-1]

            root, steps = _secant(
                function,
                x0,
                x1
            )

            return ok_result(
                "Secant Method",
                answer=f"Approximate root: {root:.8f}",
                steps=_format_steps(steps)
            )

    except Exception as e:

        return error_result(
            f"Could not solve this numerical problem. "
            f"Please check the equation and starting values."
        )