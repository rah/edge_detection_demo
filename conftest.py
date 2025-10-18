"""
Configuration for pytest.
"""
import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI (deselect with '-m \"not gui\"')"
    )
