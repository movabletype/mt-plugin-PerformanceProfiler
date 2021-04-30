import pytest
import argparse
import json

from performance_profiler.command.dump_command import DumpCommand
from performance_profiler.parser import Parser

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
DumpCommand.add_parser(subparsers)


def run(cmd):
    args = parser.parse_args(cmd.split(" "))
    args.handler(args)


def test_run(fixtures_dir, capsys):
    file = fixtures_dir.joinpath("b-kyt-v1")
    run(f"dump {file}")

    expected = Parser().parse(open(file, "rb"))

    captured = capsys.readouterr()
    assert json.loads(captured.out) == expected
