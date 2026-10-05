import re
import math

from backend.common import error_result, ok_result


INFO = {
    "id": "formulas",
    "name": "Scientific Formulas",
    "symbol": "ƒ",
    "title": "Scientific Formulas",
    "short": "Evaluate common physics and chemistry formulas for given values.",
    "description": "Ask me to evaluate a standard formula from the values you provide.",
    "placeholder": "Try: Kinetic energy of a 2 kg object moving at 3 m/s",
    "examples": [
        "Kinetic energy of a 2 kg object moving at 3 m/s",
        "Force of 10 kg mass accelerating at 5 m/s^2",
        "Ohm's law with voltage 12 V and resistance 4 ohms",
        "Pressure of 1 mol ideal gas at 300 K in 0.02 m^3",
        "Period of a pendulum of length 1.5 m"
    ]
}


def _numbers(query):
    """Extract numerical values from the query."""
    return [
        float(x)
        for x in re.findall(
            r"(?<![a-zA-Z])[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
            query
        )
    ]


def _has(query, *words):
    query = query.lower()
    return all(word in query for word in words)


def solve(query):

    if not query or not query.strip():
        return error_result(
            "Please enter a scientific formula problem."
        )

    try:
        text = query.lower()
        values = _numbers(query)

        # ---------------------------------------------------------
        # KINETIC ENERGY
        # KE = 1/2 m v²
        # ---------------------------------------------------------
        if "kinetic energy" in text:

            if len(values) < 2:
                return error_result(
                    "Please provide mass and velocity. "
                    "Example: Kinetic energy of a 2 kg object moving at 3 m/s"
                )

            mass = values[0]
            velocity = values[1]

            if mass < 0:
                return error_result("Mass cannot be negative.")

            ke = 0.5 * mass * velocity ** 2

            steps = [
                f"Given mass: m = {mass} kg",
                f"Given velocity: v = {velocity} m/s",
                "Formula: KE = ½ × m × v²",
                f"KE = ½ × {mass} × ({velocity})²",
                f"KE = {ke:.4f} J"
            ]

            return ok_result(
                "Kinetic Energy",
                answer=f"{ke:.4f} J",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        # ---------------------------------------------------------
        # POTENTIAL ENERGY
        # PE = mgh
        # ---------------------------------------------------------
        if "potential energy" in text:

            if len(values) < 2:
                return error_result(
                    "Please provide mass and height."
                )

            mass = values[0]
            height = values[1]

            g = 9.81

            if len(values) >= 3:
                g = values[2]

            pe = mass * g * height

            steps = [
                f"Mass: m = {mass} kg",
                f"Height: h = {height} m",
                f"Acceleration due to gravity: g = {g} m/s²",
                "Formula: PE = mgh",
                f"PE = {mass} × {g} × {height}",
                f"PE = {pe:.4f} J"
            ]

            return ok_result(
                "Potential Energy",
                answer=f"{pe:.4f} J",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        # ---------------------------------------------------------
        # FORCE
        # F = ma
        # ---------------------------------------------------------
        if "force" in text and "ohm" not in text:

            if len(values) < 2:
                return error_result(
                    "Please provide mass and acceleration."
                )

            mass = values[0]
            acceleration = values[1]

            force = mass * acceleration

            steps = [
                f"Mass: m = {mass} kg",
                f"Acceleration: a = {acceleration} m/s²",
                "Formula: F = ma",
                f"F = {mass} × {acceleration}",
                f"F = {force:.4f} N"
            ]

            return ok_result(
                "Force",
                answer=f"{force:.4f} N",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        # ---------------------------------------------------------
        # OHM'S LAW
        # V = IR
        # ---------------------------------------------------------
        if "ohm" in text or "ohm's law" in text:

            if len(values) < 2:
                return error_result(
                    "Please provide voltage and resistance."
                )

            voltage = values[0]
            resistance = values[1]

            if resistance == 0:
                return error_result(
                    "Resistance cannot be zero."
                )

            current = voltage / resistance

            steps = [
                f"Voltage: V = {voltage} V",
                f"Resistance: R = {resistance} Ω",
                "Formula: I = V / R",
                f"I = {voltage} / {resistance}",
                f"I = {current:.4f} A"
            ]

            return ok_result(
                "Ohm's Law",
                answer=f"Current = {current:.4f} A",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        # ---------------------------------------------------------
        # IDEAL GAS LAW
        # PV = nRT
        # R = 8.314
        # ---------------------------------------------------------
        if (
            "ideal gas" in text
            or "gas law" in text
            or ("pressure" in text and "temperature" in text)
        ):

            if len(values) < 3:
                return error_result(
                    "Please provide three values: moles, temperature "
                    "and volume."
                )

            n = values[0]
            temperature = values[1]
            volume = values[2]

            R = 8.314

            if volume == 0:
                return error_result(
                    "Volume cannot be zero."
                )

            pressure = (n * R * temperature) / volume

            steps = [
                f"Amount of gas: n = {n} mol",
                f"Temperature: T = {temperature} K",
                f"Volume: V = {volume} m³",
                f"Gas constant: R = {R} J/(mol·K)",
                "Formula: PV = nRT",
                "Rearrange: P = nRT / V",
                f"P = ({n} × {R} × {temperature}) / {volume}",
                f"P = {pressure:.4f} Pa"
            ]

            return ok_result(
                "Ideal Gas Law",
                answer=f"Pressure = {pressure:.4f} Pa",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        # ---------------------------------------------------------
        # SIMPLE PENDULUM
        # T = 2π√(L/g)
        # ---------------------------------------------------------
        if "pendulum" in text:

            if len(values) < 1:
                return error_result(
                    "Please provide the length of the pendulum."
                )

            length = values[0]
            g = 9.81

            if len(values) >= 2:
                g = values[1]

            if length < 0:
                return error_result(
                    "Pendulum length cannot be negative."
                )

            period = 2 * math.pi * math.sqrt(length / g)

            steps = [
                f"Length: L = {length} m",
                f"Acceleration due to gravity: g = {g} m/s²",
                "Formula: T = 2π√(L/g)",
                f"T = 2π√({length}/{g})",
                f"T = {period:.4f} s"
            ]

            return ok_result(
                "Simple Pendulum",
                answer=f"Period = {period:.4f} s",
                steps=[
                    {
                        "title": f"Step {i + 1}",
                        "detail": step
                    }
                    for i, step in enumerate(steps)
                ]
            )

        return error_result(
            "I couldn't identify the scientific formula. "
            "Try Kinetic Energy, Potential Energy, Force, "
            "Ohm's Law, Ideal Gas Law, or Pendulum."
        )

    except Exception:
        return error_result(
            "Could not calculate the formula. "
            "Please check the values in your question."
        )