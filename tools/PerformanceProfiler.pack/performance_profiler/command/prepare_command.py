import json
from argparse import RawTextHelpFormatter
from performance_profiler.loader import Factory as LoaderFactory


class PrepareCommand:
    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser(
            "prepare",
            help="Prepare database",
            description="""
example:
```
# prepare big_query environment in asia-northeast1
$ ./main.py prepare -loader big_query --loader-options '{"location": "asia-northeast1"}'
```
""",
            formatter_class=RawTextHelpFormatter,
        )
        parser.add_argument("-l", "--loader", default="big_query")
        parser.add_argument("--loader-options", default="{}")
        parser.set_defaults(handler=lambda args: cls().run(args))

    def run(self, args):
        loader = LoaderFactory.new_loader(args.loader, json.loads(args.loader_options))
        loader.prepare()
