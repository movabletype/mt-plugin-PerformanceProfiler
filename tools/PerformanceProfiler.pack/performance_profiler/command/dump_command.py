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
            files = ["/dev/stdin"]
        else:
            files = util.get_files(args.files)

        for file in files:
            stream = util.get_stream(file)
            data = parser.parse(stream)
            print(json.dumps(data))
