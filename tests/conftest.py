"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Sample data fixture for tests."""
    return {}


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory fixture."""
    return tmp_path
