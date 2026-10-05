import re
import base64
from io import BytesIO

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

from backend.common import error_result, ok_result


INFO = {
    "id": "graphing",
    "name": "Graphing",
    "symbol": "y=",
    "title": "Graph Plotter",
    "short": "Plot functions and see where they cross the axes.",
    "description": "Ask me to plot one or more functions over a range you choose.",
    "placeholder": "Try: Plot y = x^2 - 5x + 6 from -1 to 6",
    "examples": [
        "Plot y = x^2 - 5x + 6 from -1 to 6",
        "Plot sin(x) and cos(x) from 0 to 2*pi",
        "Plot y = 1/x from -5 to 5"
    ]
}


def _normalize_expression(expr):
    """Convert common user notation into SymPy-friendly notation."""

    expr = expr.strip()

    expr = expr.replace("^", "**")
    expr = expr.replace("π", "pi")

    # Square root notation
    expr = re.sub(
        r"sqrt\s*\(\s*([^)]+)\s*\)",
        r"sqrt(\1)",
        expr,
        flags=re.IGNORECASE
    )

    return expr


def _extract_range(query):
    """Extract 'from A to B' if supplied."""

    match = re.search(
        r"from\s+(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)",
        query.lower()
    )

    if match:
        start = float(match.group(1))
        end = float(match.group(2))

        if start >= end:
            raise ValueError("The graph range must have the first value smaller than the second.")

        return start, end

    return -10.0, 10.0


def _extract_functions(query):
    """Extract one or more functions from a graphing query."""

    text = query.strip()

    # Remove the range portion.
    text = re.sub(
        r"\s+from\s+-?\d+(?:\.\d+)?\s+to\s+-?\d+(?:\.\d+)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove common graphing instructions.
    text = re.sub(
        r"^\s*(plot|graph|draw)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Split multiple functions.
    parts = re.split(r"\s+(?:and|,)\s+", text, flags=re.IGNORECASE)

    functions = []

    for part in parts:
        part = part.strip()

        # Remove "y =" if present.
        part = re.sub(
            r"^\s*y\s*=\s*",
            "",
            part,
            flags=re.IGNORECASE
        )

        if part:
            functions.append(part)

    return functions


def _make_image(functions, start, end):
    """Create a graph and return it as a base64 PNG."""

    x = sp.symbols("x")

    plt.figure(figsize=(8, 5))

    plotted = []

    for function in functions:
        expression_text = _normalize_expression(function)

        try:
            expression = parse_expr(
    expression_text,
    local_dict={
        "x": x,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "sqrt": sp.sqrt,
        "log": sp.log,
        "ln": sp.log,
        "exp": sp.exp,
        "pi": sp.pi
    },
    transformations=TRANSFORMATIONS
)

            if expression.free_symbols - {x}:
                raise ValueError(
                    f"Unsupported variable in expression: {function}"
                )

            func = sp.lambdify(x, expression, "numpy")

            x_values = np.linspace(start, end, 1000)

            with np.errstate(
                divide="ignore",
                invalid="ignore",
                over="ignore"
            ):
                y_values = func(x_values)

            y_values = np.asarray(y_values, dtype=float)

            # Remove invalid/infinite values.
            y_values = np.where(
                np.isfinite(y_values),
                y_values,
                np.nan
            )

            plt.plot(
                x_values,
                y_values,
                linewidth=2,
                label=f"y = {function}"
            )

            plotted.append(function)

        except Exception:
            raise ValueError(
                f"I couldn't understand the function '{function}'. "
                "Try expressions such as x^2, sin(x), cos(x), or 1/x."
            )

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("SciSolve Graph")

    plt.grid(True, alpha=0.25)

    if len(plotted) > 1:
        plt.legend()

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(
        buffer,
        format="png",
        dpi=120,
        bbox_inches="tight"
    )

    plt.close()

    buffer.seek(0)

    encoded = base64.b64encode(buffer.read()).decode("utf-8")

    return encoded


def solve(query):
    if not query or not query.strip():
        return error_result("Please enter a function to graph.")

    try:
        start, end = _extract_range(query)

        functions = _extract_functions(query)

        if not functions:
            return error_result(
                "Please provide a function. "
                "Example: Plot y = x^2 from -5 to 5"
            )

        image = _make_image(functions, start, end)

        steps = [
            {
                "title": "Function",
                "detail": ", ".join(
                    f"y = {function}" for function in functions
                )
            },
            {
                "title": "Range",
                "detail": f"x from {start:g} to {end:g}"
            },
            {
                "title": "Method",
                "detail": "The function was evaluated at 1000 points using NumPy and plotted with Matplotlib."
            }
        ]

        return ok_result(
            "Graph Generated",
            answer=f"Plotted {len(functions)} function(s) successfully.",
            steps=steps,
            image=image
        )

    except ValueError as error:
        return error_result(str(error))

    except Exception:
        return error_result(
            "Could not generate the graph. "
            "Please check the function and try again."
        )