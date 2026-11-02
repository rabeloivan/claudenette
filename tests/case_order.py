"""Stable progression: small inputs, ordinary cases, boundaries, then stress."""

def input_order(value):
    if isinstance(value, int):
        return (3 if abs(value) >= 65536 else 2 if value < 0 else 0 if value <= 1 else 1,
                abs(value))
    if isinstance(value, str):
        return (3 if len(value) > 128 else 2 if any(ord(c) < 32 or ord(c) > 126 for c in value)
                else 3 if value.lstrip('+-').isdigit() and len(value.lstrip('+-').lstrip('0'))>5
                else 2 if value.startswith(('+','-')) else 0 if len(value)<=1 else 1, len(value))
    parts = [input_order(item) for item in value]
    return (max((part[0] for part in parts), default=0), sum(part[1] for part in parts))


def unique_cases(existing, added, key=lambda case: case):
    """Keep existing stronger diagnostics when the same input already exists."""
    result, seen = [], set()
    for case in [*existing, *added]:
        identity = repr(key(case))
        if identity not in seen:
            seen.add(identity)
            result.append(case)
    return result
