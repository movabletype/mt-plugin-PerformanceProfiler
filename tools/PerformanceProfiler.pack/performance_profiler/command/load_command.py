import io
import sys
import json
import time
from multiprocessing import Pool
from itertools import islice

import performance_profiler.util as util
from performance_profiler.parser import Parser
from performance_profiler.transformer import Factory as TransformerFactory
from performance_profiler.loader import Factory as LoaderFactory

LOADER_POOL_SIZE = 2
DOWNLOADER_POOL_SIZE = 8
LOAD_CHUNK_SIZE = 256
DOWNLOAD_CHUNK_SIZE = 32
MAX_EXECUTION_SECONDS = 520


def load(loader_name, loader_opts, data):
    loader = LoaderFactory.new_loader(loader_name, loader_opts)
    loader.load(data)


def download(file, remove=False):
    return util.get_bytes(file, remove)


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
        start_time = time.time()

        parser = Parser()
        transformer = TransformerFactory.new_transformer("rdb")
        loader_opts = json.loads(args.loader_options)

        if len(args.files) == 0:
            files = ["/dev/stdin"]
        else:
            files = util.get_files(args.files)

        data_stash = {}
        data_count = 0
        loader_pool = Pool(processes=LOADER_POOL_SIZE)
        load_results = []

        def flush(waitResults=False):
            nonlocal data_count

            if data_count == 0:
                return

            r = loader_pool.apply_async(
                load, (args.loader, loader_opts, data_stash.copy())
            )
            load_results.append(r)

            data_stash.clear()
            data_count = 0

            # garbage collection
            if waitResults or len(load_results) >= LOADER_POOL_SIZE * 16:
                for r in load_results:
                    r.wait()
                load_results.clear()

        def callback(data):
            nonlocal data_count

            stream = io.BytesIO(data)
            try:
                data = parser.parse(stream)
            except Exception as e:
                print(f"parse error: {e}", file=sys.stderr)
                return

            try:
                data = transformer.transform(data)
            except Exception as e:
                print(f"transform error: {e}", file=sys.stderr)
                return

            for k in data.keys():
                if k in data_stash:
                    data_stash[k] += data[k]
                else:
                    data_stash[k] = data[k]

            data_count += 1
            if data_count >= LOAD_CHUNK_SIZE:
                flush()

        downloader_pool = Pool(processes=DOWNLOADER_POOL_SIZE)
        while True:
            results = []
            for f in islice(files, DOWNLOAD_CHUNK_SIZE):
                r = downloader_pool.apply_async(
                    download, (f, args.remove_files), callback=callback
                )
                results.append(r)
            for r in results:
                r.wait()

            if len(results) < DOWNLOAD_CHUNK_SIZE:
                break
            if time.time() - start_time > MAX_EXECUTION_SECONDS:
                break

        flush(waitResults=True)
