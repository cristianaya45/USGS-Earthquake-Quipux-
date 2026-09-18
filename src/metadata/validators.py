def validate_magnitude(value: float) -> float:
    if value < -2 or value > 10:
        raise ValueError(f"magnitude out of plausible range: {value}")
    return value


def validate_latitude(value: float) -> float:
    if not -90 <= value <= 90:
        raise ValueError(f"latitude out of range: {value}")
    return value


def validate_longitude(value: float) -> float:
    if not -180 <= value <= 180:
        raise ValueError(f"longitude out of range: {value}")
    return value
