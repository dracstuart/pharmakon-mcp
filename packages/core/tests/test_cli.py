import pytest

from pharmakon_core import __version__
from pharmakon_core.cli import main


@pytest.mark.req("REQ-CORE-061")
def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"pharmakon {__version__}"
