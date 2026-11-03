import pytest


@pytest.fixture
def scratch_home(tmp_path, monkeypatch):
    root = tmp_path / "scratch"
    monkeypatch.setenv("SCRATCH_HOME", str(root))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    return root
