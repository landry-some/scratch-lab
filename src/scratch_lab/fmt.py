"""Small helpers for human-readable output."""


def age(seconds):
    """45s, 12m, 3h, 5d."""
    seconds = max(0, int(seconds))
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if seconds >= size:
            return f"{seconds // size}{unit}"
    return f"{seconds}s"


def size(n):
    """812B, 4.0K, 1.3M, 2.1G."""
    if n < 1024:
        return f"{n}B"
    value = float(n)
    for unit in "KMGT":
        value /= 1024
        if value < 1024 or unit == "T":
            return f"{value:.1f}{unit}"


def table(rows):
    """Left-aligned columns separated by two spaces."""
    if not rows:
        return ""
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    lines = ["  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows]
    return "\n".join(lines)
