"""Matrix module for SciSolve."""

import re
import ast
import numpy as np
from backend.common import error_result, ok_result


INFO = {
    "id": "matrices",
    "name": "Matrices",
    "symbol": "▦",
    "title": "Matrix Solver",
    "short": "Perform matrix operations and calculations.",
    "description": "Add, subtract, multiply, transpose, find determinants and inverses.",
    "placeholder": "Try: Find determinant of [[1,2],[3,4]]",
    "examples": [
        "Add matrices [[1,2],[3,4]] and [[5,6],[7,8]]",
        "Find determinant of [[1,2],[3,4]]",
        "Find inverse of [[1,2],[3,4]]",
    ],
}


def _format_number(value):
    """Format a matrix number for readable output."""

    value = float(value)

    if abs(value) < 1e-10:
        value = 0

    if abs(value - round(value)) < 1e-10:
        return str(int(round(value)))

    return f"{value:.6f}".rstrip("0").rstrip(".")


def _format_matrix(matrix):
    """Convert a NumPy matrix into a readable string."""

    rows = []

    for row in matrix:
        rows.append(
            "[" + ", ".join(_format_number(x) for x in row) + "]"
        )

    return "[" + ", ".join(rows) + "]"


def _parse_matrices(text):
    """Extract matrices written like [[1,2],[3,4]]."""

    matrices = []

    # Find possible matrix expressions in the user's message.
    matches = re.findall(
        r"\[\s*\[.*?\]\s*(?:,\s*\[.*?\]\s*)+\]",
        text
    )

    for match in matches:
        try:
            value = ast.literal_eval(match)

            if not isinstance(value, list) or not value:
                continue

            if not all(isinstance(row, list) for row in value):
                continue

            if not all(row for row in value):
                raise ValueError("Matrix rows cannot be empty.")

            column_count = len(value[0])

            if any(len(row) != column_count for row in value):
                raise ValueError(
                    "Each row of a matrix must contain the same number of values."
                )

            if not all(
                isinstance(number, (int, float))
                and not isinstance(number, bool)
                for row in value
                for number in row
            ):
                raise ValueError("Matrix values must be numbers.")

            matrices.append(
                np.array(value, dtype=float)
            )

        except (ValueError, SyntaxError):
            raise ValueError(
                "Matrix values must be numbers."
            )

    if not matrices:
        raise ValueError(
            "I couldn't find a matrix. "
            "Use a format such as [[1,2],[3,4]]."
        )

    return matrices


def _detect_operation(text):
    text = text.lower()

    if "determinant" in text or re.search(r"\bdet\b", text):
        return "determinant"

    if "inverse" in text:
        return "inverse"

    if "transpose" in text:
        return "transpose"

    if "multiply" in text or "multiplication" in text:
        return "multiply"

    if re.search(r"\bsubtract\b|\bsubtraction\b", text):
        return "subtract"

    if re.search(r"\badd\b|\baddition\b", text):
        return "add"

    return None


def _add(a, b):
    if a.shape != b.shape:
        raise ValueError(
            "Matrix addition requires matrices of the same dimensions."
        )

    result = a + b

    steps = [
        {
            "title": "Check matrix dimensions",
            "detail": f"{a.shape[0]} × {a.shape[1]} matrices",
        },
        {
            "title": "Add corresponding elements",
            "detail": "Each element of the first matrix is added to the corresponding element of the second.",
        },
        {
            "title": "Result",
            "detail": _format_matrix(result),
        },
    ]

    return result, steps


def _subtract(a, b):
    if a.shape != b.shape:
        raise ValueError(
            "Matrix subtraction requires matrices of the same dimensions."
        )

    result = a - b

    steps = [
        {
            "title": "Check matrix dimensions",
            "detail": f"{a.shape[0]} × {a.shape[1]} matrices",
        },
        {
            "title": "Subtract corresponding elements",
            "detail": "Each element of the second matrix is subtracted from the corresponding element of the first.",
        },
        {
            "title": "Result",
            "detail": _format_matrix(result),
        },
    ]

    return result, steps


def _multiply(a, b):
    if a.shape[1] != b.shape[0]:
        raise ValueError(
            "Matrix multiplication is not possible. "
            "The number of columns in the first matrix must equal "
            "the number of rows in the second matrix."
        )

    result = a @ b

    steps = [
        {
            "title": "Check matrix dimensions",
            "detail": (
                f"{a.shape[0]} × {a.shape[1]} multiplied by "
                f"{b.shape[0]} × {b.shape[1]}"
            ),
        },
        {
            "title": "Multiply rows by columns",
            "detail": (
                "Each result element is obtained by multiplying "
                "corresponding row and column elements and adding them."
            ),
        },
        {
            "title": "Result",
            "detail": _format_matrix(result),
        },
    ]

    return result, steps


def _transpose(matrix):
    result = matrix.T

    steps = [
        {
            "title": "Write the original matrix",
            "detail": _format_matrix(matrix),
        },
        {
            "title": "Interchange rows and columns",
            "detail": "Rows become columns.",
        },
        {
            "title": "Result",
            "detail": _format_matrix(result),
        },
    ]

    return result, steps


def _determinant(matrix):
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            "A determinant can only be calculated for a square matrix."
        )

    determinant = np.linalg.det(matrix)

    if abs(determinant - round(determinant)) < 1e-10:
        determinant = round(determinant)

    steps = [
        {
            "title": "Check the matrix",
            "detail": (
                f"The matrix is {matrix.shape[0]} × "
                f"{matrix.shape[1]}, so it is square."
            ),
        },
        {
            "title": "Calculate the determinant",
            "detail": f"det(A) = {_format_number(determinant)}",
        },
    ]

    return determinant, steps


def _inverse(matrix):
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            "Only square matrices have an inverse."
        )

    determinant = np.linalg.det(matrix)

    if abs(determinant) < 1e-10:
        raise ValueError(
            "This matrix is singular, so it does not have an inverse."
        )

    inverse = np.linalg.inv(matrix)

    steps = [
        {
            "title": "Check the matrix",
            "detail": (
                f"The matrix is {matrix.shape[0]} × "
                f"{matrix.shape[1]} and therefore square."
            ),
        },
        {
            "title": "Check the determinant",
            "detail": f"det(A) = {_format_number(determinant)}",
        },
        {
            "title": "Calculate the inverse",
            "detail": "A⁻¹ is calculated using the matrix inverse operation.",
        },
        {
            "title": "Result",
            "detail": _format_matrix(inverse),
        },
    ]

    return inverse, steps


def solve(query):
    """Solve a matrix question."""

    try:
        if not query or not query.strip():
            return error_result(
                "Please enter a matrix question."
            )

        operation = _detect_operation(query)

        if operation is None:
            return error_result(
                "I couldn't identify the matrix operation. "
                "Try add, subtract, multiply, transpose, determinant, or inverse."
            )

        matrices = _parse_matrices(query)

        if operation in ("add", "subtract", "multiply"):
            if len(matrices) < 2:
                return error_result(
                    "This operation requires two matrices."
                )

        matrix_a = matrices[0]

        if operation == "add":
            result, steps = _add(matrix_a, matrices[1])
            answer = _format_matrix(result)
            title = "Matrix Addition"

        elif operation == "subtract":
            result, steps = _subtract(matrix_a, matrices[1])
            answer = _format_matrix(result)
            title = "Matrix Subtraction"

        elif operation == "multiply":
            result, steps = _multiply(matrix_a, matrices[1])
            answer = _format_matrix(result)
            title = "Matrix Multiplication"

        elif operation == "transpose":
            result, steps = _transpose(matrix_a)
            answer = _format_matrix(result)
            title = "Matrix Transpose"

        elif operation == "determinant":
            result, steps = _determinant(matrix_a)
            answer = _format_number(result)
            title = "Determinant"

        elif operation == "inverse":
            result, steps = _inverse(matrix_a)
            answer = _format_matrix(result)
            title = "Matrix Inverse"

        else:
            return error_result(
                "Unsupported matrix operation."
            )

        return ok_result(
            title,
            answer=answer,
            steps=steps,
        )

    except ValueError as exc:
        return error_result(str(exc))

    except Exception:
        return error_result(
            "I couldn't calculate that matrix problem. "
            "Please check the matrix format and try again."
        )