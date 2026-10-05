"""Statistics module for SciSolve."""

import re
import math
from collections import Counter

from backend.common import error_result, ok_result


INFO = {
    "id": "statistics",
    "name": "Statistics",
    "symbol": "Σ",
    "title": "Statistics Solver",
    "short": "Calculate mean, median, mode, variance and standard deviation.",
    "description": "Analyze numerical data using common statistical measures.",
    "placeholder": "Try: Find mean of 10, 20, 30, 40, 50",
    "examples": [
        "Find mean of 10, 20, 30, 40, 50",
        "Calculate median of 5, 2, 8, 1, 9",
        "Find standard deviation of 10, 12, 14, 16, 18",
    ],
}


def _extract_numbers(text):
    """Extract numerical values from the user's question."""

    # Remove common phrases so numbers in the question itself
    # are not accidentally interpreted as data.
    cleaned = re.sub(
        r"\b(find|calculate|compute|what|is|the|mean|average|"
        r"median|mode|variance|standard|deviation|of|for|data|"
        r"values|range|please)\b",
        " ",
        text.lower(),
    )

    numbers = re.findall(
        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",
        cleaned,
    )

    return [float(number) for number in numbers]


def _format_number(value):
    """Make numbers easier to read."""

    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))

    return f"{value:.6f}".rstrip("0").rstrip(".")


def _data_string(data):
    return ", ".join(_format_number(x) for x in data)


def _mean(data):
    total = sum(data)
    n = len(data)
    result = total / n

    steps = [
        {
            "title": "Add all values",
            "detail": f"{_data_string(data)} = {_format_number(total)}",
        },
        {
            "title": "Count the values",
            "detail": f"n = {n}",
        },
        {
            "title": "Divide the sum by the count",
            "detail": (
                f"Mean = {total:g} / {n} = "
                f"{_format_number(result)}"
            ),
        },
    ]

    return result, steps


def _median(data):
    ordered = sorted(data)
    n = len(ordered)

    if n % 2 == 1:
        middle = ordered[n // 2]
        calculation = f"Median = {_format_number(middle)}"
        result = middle

    else:
        left = ordered[n // 2 - 1]
        right = ordered[n // 2]
        result = (left + right) / 2

        calculation = (
            f"Median = ({_format_number(left)} + "
            f"{_format_number(right)}) / 2 = "
            f"{_format_number(result)}"
        )

    steps = [
        {
            "title": "Arrange the values",
            "detail": _data_string(ordered),
        },
        {
            "title": "Count the values",
            "detail": f"n = {n}",
        },
        {
            "title": "Find the middle value",
            "detail": calculation,
        },
    ]

    return result, steps


def _mode(data):
    counts = Counter(data)
    highest = max(counts.values())

    if highest == 1:
        result = "No mode"
        steps = [
            {
                "title": "Count the frequency of each value",
                "detail": "Every value occurs only once.",
            },
            {
                "title": "Result",
                "detail": "There is no mode.",
            },
        ]
    else:
        modes = sorted(
            value for value, count in counts.items()
            if count == highest
        )

        result = ", ".join(_format_number(x) for x in modes)

        frequency_text = ", ".join(
            f"{_format_number(x)} occurs {counts[x]} time(s)"
            for x in sorted(counts)
        )

        steps = [
            {
                "title": "Count the frequency of each value",
                "detail": frequency_text,
            },
            {
                "title": "Find the highest frequency",
                "detail": f"Highest frequency = {highest}",
            },
            {
                "title": "Result",
                "detail": f"Mode = {result}",
            },
        ]

    return result, steps


def _variance(data, sample=False):
    mean = sum(data) / len(data)

    squared_differences = [
        (x - mean) ** 2
        for x in data
    ]

    divisor = len(data) - 1 if sample else len(data)
    variance = sum(squared_differences) / divisor

    variance_type = "Sample" if sample else "Population"

    squared_text = ", ".join(
        _format_number(x) for x in squared_differences
    )

    steps = [
        {
            "title": "Calculate the mean",
            "detail": f"Mean = {_format_number(mean)}",
        },
        {
            "title": "Calculate squared differences",
            "detail": f"(x - mean)² = {squared_text}",
        },
        {
            "title": "Divide by the appropriate count",
            "detail": (
                f"{variance_type} variance = "
                f"sum of squared differences / {divisor}"
            ),
        },
        {
            "title": "Result",
            "detail": (
                f"{variance_type} variance = "
                f"{_format_number(variance)}"
            ),
        },
    ]

    return variance, steps


def _standard_deviation(data, sample=False):
    variance, variance_steps = _variance(data, sample)

    result = math.sqrt(variance)

    variance_type = "Sample" if sample else "Population"

    steps = variance_steps + [
        {
            "title": "Take the square root",
            "detail": (
                f"Standard deviation = √{_format_number(variance)} "
                f"= {_format_number(result)}"
            ),
        }
    ]

    return result, steps


def _detect_operation(text):
    text = text.lower()

    if "standard deviation" in text:
        return "standard_deviation"

    if "variance" in text:
        return "variance"

    if re.search(r"\bmode\b", text):
        return "mode"

    if re.search(r"\bmedian\b", text):
        return "median"

    if re.search(r"\b(mean|average)\b", text):
        return "mean"

    if re.search(r"\brange\b", text):
        return "range"

    return None


def solve(query):
    """Solve a statistics question."""

    try:
        if not query or not query.strip():
            return error_result(
                "Please enter a statistics question with some numerical data."
            )

        operation = _detect_operation(query)

        if operation is None:
            return error_result(
                "I couldn't identify the statistics operation. "
                "Try mean, median, mode, variance, standard deviation, or range."
            )

        data = _extract_numbers(query)

        if len(data) < 1:
            return error_result(
                "I couldn't find numerical data. "
                "Example: Find mean of 10, 20, 30."
            )

        if operation in ("median", "mode", "variance", "standard_deviation"):
            if len(data) < 2:
                return error_result(
                    "Please provide at least two numerical values."
                )

        if operation == "mean":
            result, steps = _mean(data)
            answer = _format_number(result)
            title = "Mean"

        elif operation == "median":
            result, steps = _median(data)
            answer = _format_number(result)
            title = "Median"

        elif operation == "mode":
            answer, steps = _mode(data)
            title = "Mode"

        elif operation == "variance":
            result, steps = _variance(data)
            answer = _format_number(result)
            title = "Population Variance"

        elif operation == "standard_deviation":
            result, steps = _standard_deviation(data)
            answer = _format_number(result)
            title = "Population Standard Deviation"

        elif operation == "range":
            minimum = min(data)
            maximum = max(data)
            result = maximum - minimum

            steps = [
                {
                    "title": "Find the minimum value",
                    "detail": f"Minimum = {_format_number(minimum)}",
                },
                {
                    "title": "Find the maximum value",
                    "detail": f"Maximum = {_format_number(maximum)}",
                },
                {
                    "title": "Calculate the range",
                    "detail": (
                        f"Range = {_format_number(maximum)} - "
                        f"{_format_number(minimum)} = "
                        f"{_format_number(result)}"
                    ),
                },
            ]

            answer = _format_number(result)
            title = "Range"

        else:
            return error_result("Unsupported statistics operation.")

        return ok_result(
            title,
            answer=answer,
            steps=steps,
        )

    except Exception:
        return error_result(
            "I couldn't calculate that statistics problem. "
            "Please check the data and try again."
        )