"""Shared pytest setup: live-test gating and requirement markers."""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("PHARMAKON_LIVE_TESTS") == "1":
        return
    skip_live = pytest.mark.skip(reason="live API test; set PHARMAKON_LIVE_TESTS=1 to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
