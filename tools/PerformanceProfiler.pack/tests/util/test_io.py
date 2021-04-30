import pytest
import os

from performance_profiler.util.fs import get_files
from performance_profiler.util.io import get_bytes, get_stream


class TestGetBytes:
    def file_contents(self):
        return b"contents"

    @pytest.fixture
    def gcs_files(self, gcs_bucket, gcs_prefix):
        files = {}
        for f in ["p1/01"]:
            files[f] = f"gs://{gcs_bucket.name}/{gcs_prefix}/{f}"
            blob = gcs_bucket.blob(f"{gcs_prefix}/{f}")
            blob.upload_from_string(self.file_contents())
        return files

    @pytest.fixture
    def fs_files(self, tmp_path):
        files = {}
        for f in ["01", "02"]:
            files[f] = f"{tmp_path}/{f}"
            fh = open(files[f], "w")
            fh.write(self.file_contents().decode("utf-8"))
        return files

    def test_gcs(self, gcs_files):
        assert get_bytes(gcs_files["p1/01"]) == self.file_contents()
        assert len(list(get_files([gcs_files["p1/01"]]))) == 1

    def test_gcs_remove(self, gcs_files):
        assert get_bytes(gcs_files["p1/01"], remove=True) == self.file_contents()
        assert len(list(get_files([gcs_files["p1/01"]]))) == 0

    def test_fs(self, fs_files):
        assert get_bytes(fs_files["01"]) == self.file_contents()
        assert os.path.exists(fs_files["01"])

    def test_fs_remove(self, fs_files):
        assert get_bytes(fs_files["01"], remove=True) == self.file_contents()
        assert not os.path.exists(fs_files["01"])


class TestGetStream:
    def file_contents(self):
        return b"contents"

    @pytest.fixture
    def gcs_files(self, gcs_bucket, gcs_prefix):
        files = {}
        for f in ["p1/01"]:
            files[f] = f"gs://{gcs_bucket.name}/{gcs_prefix}/{f}"
            blob = gcs_bucket.blob(f"{gcs_prefix}/{f}")
            blob.upload_from_string(self.file_contents())
        return files

    @pytest.fixture
    def fs_files(self, tmp_path):
        files = {}
        for f in ["01", "02"]:
            files[f] = f"{tmp_path}/{f}"
            fh = open(files[f], "w")
            fh.write(self.file_contents().decode("utf-8"))
        return files

    def test_gcs(self, gcs_files):
        assert get_bytes(gcs_files["p1/01"]) == self.file_contents()
        assert len(list(get_files([gcs_files["p1/01"]]))) == 1

    def test_gcs_remove(self, gcs_bucket, gcs_prefix, gcs_files):
        assert get_bytes(gcs_files["p1/01"], remove=True) == self.file_contents()
        assert len(list(get_files([gcs_files["p1/01"]]))) == 0

    def test_fs(self, fs_files):
        assert get_bytes(fs_files["01"]) == self.file_contents()
        assert os.path.exists(fs_files["01"])

    def test_fs_remove(self, fs_files):
        assert get_bytes(fs_files["01"], remove=True) == self.file_contents()
        assert not os.path.exists(fs_files["01"])
