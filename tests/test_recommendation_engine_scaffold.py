import pathlib


def test_project_scaffold():
    assert (pathlib.Path(__file__).resolve().parents[1] / "src" / "main.py").exists()

