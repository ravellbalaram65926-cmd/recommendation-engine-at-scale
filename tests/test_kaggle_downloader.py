import zipfile

import pytest

from scripts.download_kaggle import extract_archives


def test_extracts_dataset_archives(tmp_path):
    with zipfile.ZipFile(tmp_path / "dataset.zip", "w") as archive:
        archive.writestr("ratings.csv", "userId,movieId,rating\n1,2,4.0\n")

    extract_archives(tmp_path)

    assert (tmp_path / "ratings.csv").read_text(encoding="utf-8") == "userId,movieId,rating\n1,2,4.0\n"


def test_rejects_archive_path_traversal(tmp_path):
    with zipfile.ZipFile(tmp_path / "unsafe.zip", "w") as archive:
        archive.writestr("../outside.txt", "unsafe")

    with pytest.raises(ValueError, match="Unsafe archive path"):
        extract_archives(tmp_path)
