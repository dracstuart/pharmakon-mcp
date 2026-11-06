"""Architecture rules that keep pharmakon-core independent of any front end."""

import re
import subprocess
import sys
from importlib.metadata import requires

import pytest


@pytest.mark.req("REQ-CORE-060")
def test_core_does_not_declare_mcp_dependency():
    declared = requires("pharmakon-core") or []
    names = [re.split(r"[\s;<>=!~\[]", req, maxsplit=1)[0].lower() for req in declared]
    assert "mcp" not in names


@pytest.mark.req("REQ-CORE-060")
def test_importing_core_does_not_load_mcp():
    code = "import sys, pharmakon_core; sys.exit('mcp' in sys.modules)"
    assert subprocess.run([sys.executable, "-c", code]).returncode == 0
