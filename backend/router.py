"""Input normalization and routing.

Flow: normalize the text -> pick the module the user selected -> call
``module.solve(normalized_text)``. Intent detection (is this "solve",
"simplify", "plot"...?) belongs inside each module, because the words that
matter differ from one subject to the next.

To add a module: create backend/<name>.py with ``INFO`` and ``solve()``,
then add it to ``_MODULES`` below.
"""
from backend import algebra, formulas, graphing, matrices, numerical, statistics
from backend.common import error_result

# Order here is the order shown in the sidebar, cards and landing page.
_MODULES = (algebra, statistics, matrices, numerical, formulas, graphing)
_REGISTRY = {m.INFO["id"]: m for m in _MODULES}

MAX_QUERY_LENGTH = 2000

# Typographic symbols that students paste or type, mapped to plain input.
_SYMBOLS = str.maketrans(
    {
        "\u2212": "-", "\u2013": "-", "\u2014": "-",   # minus, en dash, em dash
        "\u00d7": "*", "\u00b7": "*", "\u22c5": "*",   # multiplication signs
        "\u00f7": "/",
        "\u00b2": "^2", "\u00b3": "^3",
        "\u221a": "sqrt", "\u03c0": "pi",
        "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    }
)


def list_modules():
    return [dict(m.INFO) for m in _MODULES]


def normalize(text):
    """Tidy raw input without changing its meaning.

    Converts typographic symbols, collapses repeated spaces and trims blank
    lines. Line breaks are kept because later modules (e.g. matrices) may
    accept one row per line.
    """
    text = text.translate(_SYMBOLS)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(lines).strip()


def solve(module_id, text):
    """Return ``(result_dict, http_status)``."""
    module = _REGISTRY.get(module_id)
    if module is None:
        return error_result("Unknown module. Select a module from the menu."), 404

    if len(text) > MAX_QUERY_LENGTH:
        return error_result(f"Keep your question under {MAX_QUERY_LENGTH} characters."), 400

    normalized = normalize(text)
    if not normalized:
        return error_result("Type a question first."), 400

    try:
        result = module.solve(normalized)
    except Exception:  # a module bug must not crash the server
        return error_result("Something went wrong while solving this. Try rephrasing."), 500

    result["module"] = module_id
    result["input"] = text.strip()
    result["normalized"] = normalized
    return result, 200
