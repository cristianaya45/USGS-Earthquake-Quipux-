import pytest

from metadata.validators import validate_latitude, validate_longitude, validate_magnitude


def test_validate_magnitude_accepts_normal_values():
    assert validate_magnitude(4.2) == 4.2


def test_validate_magnitude_rejects_out_of_range():
    with pytest.raises(ValueError):
        validate_magnitude(15)


def test_validate_latitude_rejects_out_of_range():
    with pytest.raises(ValueError):
        validate_latitude(95)


def test_validate_longitude_rejects_out_of_range():
    with pytest.raises(ValueError):
        validate_longitude(-200)
