import sys
import json

import performance_profiler.util as util
from performance_profiler.parser import Parser
from performance_profiler.transformer import Factory as TransformerFactory
from performance_profiler.loader import Factory as LoaderFactory


class LoadCommand:
    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser("load", help="Load profile data into database")
        parser.add_argument("files", nargs="*")
        parser.add_argument("-l", "--loader", default="big_query")
        parser.add_argument("--loader-options", default="{}")
        parser.add_argument(
            "--remove-files", action="store_true", help="Remove files after loaded"
        )
        parser.set_defaults(handler=lambda args: cls().run(args))

    def run(self, args):
        parser = Parser()

        transformer = TransformerFactory.new_transformer("rdb")
        loader_opts = json.loads(args.loader_options)
        loader = LoaderFactory.new_loader(args.loader, loader_opts)

        if len(args.files) == 0:
            streams = [sys.stdin.buffer]
        else:
            streams = util.get_streams(args.files, remove=args.remove_files)

        for stream in streams:
            data = parser.parse(stream)
            data = transformer.transform(data)

            loader.load(data)
