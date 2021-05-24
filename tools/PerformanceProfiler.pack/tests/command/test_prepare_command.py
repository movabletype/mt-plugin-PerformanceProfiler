import pytest
import argparse

from performance_profiler.command.prepare_command import PrepareCommand
from performance_profiler.loader.big_query_loader import BigQueryLoader

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
PrepareCommand.add_parser(subparsers)


def run(cmd):
    args = parser.parse_args(cmd.split(" "))
    args.handler(args)


def test_run(monkeypatch):
    count = 0

    def inc_count(self):
        nonlocal count
        count += 1

    monkeypatch.setattr(BigQueryLoader, "prepare", inc_count)

    run("prepare --loader big_query")

    assert count == 1
