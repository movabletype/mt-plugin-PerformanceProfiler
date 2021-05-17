import pytest
import argparse
import json
import os
import shutil

from performance_profiler.command.load_command import LoadCommand
import performance_profiler.command.load_command as load_command
import performance_profiler.util

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
LoadCommand.add_parser(subparsers)


class TestRun:
    @pytest.fixture(autouse=True)
    def monkeypatch_to_constants(self, monkeypatch):
        monkeypatch.setattr(load_command, "LOAD_CHUNK_SIZE", 3)
        monkeypatch.setattr(load_command, "MAX_EXECUTION_SECONDS", 1)

    @pytest.fixture
    def files(self, fixtures_dir, tmp_path):
        files = []
        for i in range(10):
            file = f"{tmp_path}/{i}"
            shutil.copy(fixtures_dir.joinpath("b-kyt-v1"), file)
            files.append(file)
        return files

    @pytest.fixture
    def infinite_get_files(self, files, monkeypatch):
        def infinite_get_files(_):
            while True:
                yield files[0]

        monkeypatch.setattr(performance_profiler.util, "get_files", infinite_get_files)

    def run(self, cmd):
        args = parser.parse_args(cmd.split(" "))
        args.handler(args)

    def test_run(self, files, tmp_path):
        outfile = f"{tmp_path}/out"

        self.run(f'load -l file --loader-options {{"file":"{outfile}"}} {files[0]}')
        result = json.load(open(outfile))

        assert len(result["builds"]) == 1
        assert sum(map(lambda x: len(x["logs"]), result["builds"])) == 1
        assert len(result["queries"]) == 1
        assert os.path.exists(files[0])

    def test_run_remove(self, files, tmp_path):
        outfile = f"{tmp_path}/out"

        self.run(
            f'load -l file --loader-options {{"file":"{outfile}"}} --remove-files {files[0]}'
        )
        result = json.load(open(outfile))

        assert len(result["builds"]) == 1
        assert sum(map(lambda x: len(x["logs"]), result["builds"])) == 1
        assert len(result["queries"]) == 1
        assert not os.path.exists(files[0])

    def test_run_multiple(self, files, tmp_path):
        outfile = f"{tmp_path}/out"

        self.run(
            f'load -l file --loader-options {{"file":"{outfile}"}} '
            + " ".join([files[i] for i in range(10)])
        )
        result = json.load(open(outfile))

        assert len(result["builds"]) == 10
        assert sum(map(lambda x: len(x["logs"]), result["builds"])) == 10
        assert len(result["queries"]) == 1

    def test_run_timeout(self, files, tmp_path, infinite_get_files):
        outfile = f"{tmp_path}/out"

        self.run(f'load -l file --loader-options {{"file":"{outfile}"}} {files[0]}')
        result = json.load(open(outfile))

        assert len(result["builds"]) > 1
