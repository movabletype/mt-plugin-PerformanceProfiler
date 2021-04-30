import pytest
import argparse

from performance_profiler.command.tidyup_command import TidyupCommand
from performance_profiler.loader.big_query_loader import BigQueryLoader

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
TidyupCommand.add_parser(subparsers)


def run(cmd):
    args = parser.parse_args(cmd.split(" "))
    args.handler(args)


def test_run(monkeypatch):
    count = 0

    def inc_count(self):
        nonlocal count
        count += 1

    monkeypatch.setattr(BigQueryLoader, "tidyup", inc_count)

    run("tidyup --loader big_query")

    assert count == 1
