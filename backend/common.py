"""Shared helpers for building results.

Every module's ``solve(query)`` returns a plain dictionary so the frontend can
render it without knowing anything about the module that produced it.

Result contract
---------------
status   "ok" | "not_implemented" | "error"
title    short heading for the result                       (ok)
answer   final answer as plain text                         (ok, optional)
steps    list of {"title": str, "detail": str}              (ok, optional)
image    base64-encoded PNG, without a "data:" prefix       (ok, optional)
message  human-readable explanation                         (not_implemented, error)

The router adds ``module``, ``input`` and ``normalized`` to every result.
"""


def ok_result(title, answer=None, steps=None, image=None):
    result = {"status": "ok", "title": title}
    if answer is not None:
        result["answer"] = str(answer)
    if steps:
        result["steps"] = [
            {"title": str(s["title"]), "detail": str(s.get("detail", ""))} for s in steps
        ]
    if image:
        result["image"] = image
    return result


def error_result(message):
    return {"status": "error", "message": message}


def not_implemented(module_name, source_file):
    """Honest placeholder used by modules whose calculations are not built yet."""
    return {
        "status": "not_implemented",
        "message": (
            f"The {module_name} solver is not built yet. Your question reached "
            f"{source_file}, but no calculation was run."
        ),
        "source_file": source_file,
    }
