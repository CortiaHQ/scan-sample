"""Verify that installed dependencies match the exact pins in pyproject.toml."""

from importlib import metadata

import pytest


PINS = {
    "fastapi": "0.95.0",
    "starlette": "0.26.1",
    "pydantic": "1.10.2",
    "uvicorn": "0.20.0",
    "requests": "2.28.1",
    "urllib3": "1.26.12",
    "Jinja2": "3.1.2",
    "python-multipart": "0.0.5",
    "cryptography": "39.0.0",
    "PyYAML": "6.0",
    "certifi": "2022.12.7",
    "pytest": "7.2.0",
    "httpx": "0.23.3",
}


@pytest.mark.parametrize(("name", "pin"), PINS.items())
def test_dependency_version_matches_pin(name, pin):
    assert metadata.version(name) == pin
