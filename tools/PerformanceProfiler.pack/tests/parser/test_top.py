import pytest

from performance_profiler.parser.top import Top

parser = Top()


def test_parse_v1(fixtures_dir):
    stream = open(fixtures_dir.joinpath("b-kyt-v1"), "rb")
    data = parser.parse(stream)
    assert data["version"] == 1
