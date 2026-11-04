import pytest
from pydantic import ValidationError

from gasstoragelevel import GasStorageLevel


def test_gas_storage_level_accepts_numeric_level() -> None:
    storage = GasStorageLevel(level=12.5)

    assert storage.level == 12.5


def test_gas_storage_level_rejects_non_numeric_level() -> None:
    with pytest.raises(ValidationError):
        GasStorageLevel(level="full")
