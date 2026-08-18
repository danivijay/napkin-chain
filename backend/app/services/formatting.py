"""Human-readable magnitudes. 12500 reads as '12.5K', not '12,500'."""

_UNITS: list[tuple[float, str]] = [
    (1e12, "T"),
    (1e9, "B"),
    (1e6, "M"),
    (1e3, "K"),
]


def humanize(value: float, unit: str = "") -> str:
    magnitude = abs(value)
    formatted: str
    for threshold, suffix in _UNITS:
        if magnitude >= threshold:
            scaled = value / threshold
            formatted = f"{scaled:.1f}".rstrip("0").rstrip(".") + suffix
            break
    else:
        if magnitude >= 100 or magnitude == int(magnitude):
            formatted = f"{value:,.0f}"
        elif magnitude >= 1:
            formatted = f"{value:.1f}".rstrip("0").rstrip(".")
        else:
            formatted = f"{value:.3g}"
    return f"{formatted} {unit}".strip()
