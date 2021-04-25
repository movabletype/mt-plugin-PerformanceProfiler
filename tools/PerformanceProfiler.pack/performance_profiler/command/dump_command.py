import sys
import json

import performance_profiler.util as util
from performance_profiler.parser import Parser


class DumpCommand:
    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser("dump", help="Dump profile data")
        parser.add_argument("files", nargs="*")
        parser.set_defaults(handler=lambda args: cls().run(args))

    def run(self, args):
        parser = Parser()

        if len(args.files) == 0:
            streams = [sys.stdin.buffer]
        else:
            streams = util.get_streams(args.files)

        for stream in streams:
            data = parser.parse(stream)
            print(json.dumps(data))
