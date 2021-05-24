import pytest
import json
import io
import secrets

from performance_profiler.loader.file_loader import FileLoader


class TestLoad:
    @pytest.fixture
    def file(self, tmp_path):
        return f"{tmp_path}/{secrets.token_hex()}"

    @pytest.fixture
    def loader(self, file):
        return FileLoader({"file": file})

    def test_load(self, loader, file):
        data = {"a": "b", "c": "d"}
        loader.load(data)
        f = open(file)
        assert json.loads(f.read()) == data
