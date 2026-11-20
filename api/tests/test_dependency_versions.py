"""Verify that installed dependencies match the exact pins in pyproject.toml."""

import re
from importlib import metadata
from pathlib import Path

import pytest


PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
PIN = re.compile(
    r"""["'](?P<name>[A-Za-z0-9][A-Za-z0-9_.-]*)"""
    r"""(?:\[[^]"']+\])?\s*==\s*"""
    r"""(?P<version>[A-Za-z0-9][A-Za-z0-9_.!+-]*)["']"""
)


def _declared_pins():
    text = PYPROJECT.read_text(encoding="utf-8")
    pins = [(match.group("name"), match.group("version")) for match in PIN.finditer(text)]
    assert pins, f"No exact dependency pins found in {PYPROJECT}"
    return pins


@pytest.mark.parametrize(("name", "pin"), _declared_pins())
def test_dependency_version_matches_pin(name, pin):
    assert metadata.version(name) == pin