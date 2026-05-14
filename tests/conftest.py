import pandas as pd 
import pytest

@pytest.fixture
def clean_integer_series():
    """A small series of clean integers — used as a baseline for several tests."""
    return pd.Series([1, 2, 3, 4, 5])