import pytest
import types

from performance_profiler.util.fs import get_files


class TestGetFiles:
    def file_contents(self):
        return b"contents"

    @pytest.fixture
    def gcs_files(self, gcs_bucket, gcs_prefix):
        files = {}
        for f in ["p1/01", "p1/02", "p2/01", "q1/01"]:
            files[f] = f"gs://{gcs_bucket.name}/{gcs_prefix}/{f}"
            blob = gcs_bucket.blob(f"{gcs_prefix}/{f}")
            blob.upload_from_string(self.file_contents())
        return files

    @pytest.fixture
    def fs_files(self, tmp_path):
        files = {}
        for f in ["01", "02"]:
            files[f] = f"{tmp_path}/{f}"
            open(files[f], "w")
        return files

    def test_gcs_prefix(self, gcs_bucket, gcs_prefix, gcs_files):
        files = get_files(
            [
                f"gs://{gcs_bucket.name}/{gcs_prefix}/p1/",
                f"gs://{gcs_bucket.name}/{gcs_prefix}/p2/",
            ]
        )

        assert type(files) is types.GeneratorType
        assert sorted(list(files)) == [
            gcs_files["p1/01"],
            gcs_files["p1/02"],
            gcs_files["p2/01"],
        ]

    def test_gcs_fullpath(self, gcs_bucket, gcs_prefix, gcs_files):
        files = get_files(
            [
                f"gs://{gcs_bucket.name}/{gcs_prefix}/p1/01",
            ]
        )

        assert type(files) is types.GeneratorType
        assert sorted(list(files)) == [
            gcs_files["p1/01"],
        ]

    def test_fs(self, fs_files):
        files = get_files(
            [
                fs_files["01"],
                fs_files["02"],
            ]
        )

        assert type(files) is types.GeneratorType
        assert sorted(list(files)) == [
            fs_files["01"],
            fs_files["02"],
        ]

    def test_gcs_and_fs(self, gcs_bucket, gcs_prefix, gcs_files, fs_files):
        files = get_files(
            [
                f"gs://{gcs_bucket.name}/{gcs_prefix}/p1/01",
                fs_files["01"],
            ]
        )

        assert type(files) is types.GeneratorType
        assert list(files) == [
            gcs_files["p1/01"],
            fs_files["01"],
        ]
