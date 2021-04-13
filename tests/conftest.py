import os
import pytest
import warnings


@pytest.fixture(autouse=True)
def load_env():
    try:
        with open(".env") as f:
            for line in f.readlines():
                try:
                    name, value = line.strip().split("=", 1)
                    os.environ[name] = value
                except ValueError:
                    pass
    except FileNotFoundError:
        warnings.warn(".env file not found")