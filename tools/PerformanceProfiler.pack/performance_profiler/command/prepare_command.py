from performance_profiler.loader import Factory as LoaderFactory


class PrepareCommand:
    @classmethod
    def add_parser(cls, subparsers):
        parser = subparsers.add_parser("prepare", help="Prepare database")
        parser.add_argument("-l", "--loader", default="big_query")
        parser.set_defaults(handler=lambda args: cls().run(args))

    def run(self, args):
        loader = LoaderFactory.new_loader(args.loader, {})
        loader.prepare()
