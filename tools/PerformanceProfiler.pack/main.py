#!/usr/bin/env python

import argparse
from inspect import getmembers, isclass
import performance_profiler.command as command


def load_gcs_to_bigquery(event, context):
    if "attributes" in event:
        # via pubsub topic
        attr_dict = event.get("attributes")
    else:
        # via gcs tritter
        attr_dict = event

    # get bucket name and prefix
    bucket = attr_dict["bucket"]
    prefix = attr_dict["name"]

    main(
        [
            "load",
            "--loader",
            "big_query",
            "--remove-files",
            f"gs://{bucket}/{prefix}",
        ]
    )


def main(args=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for _, c in getmembers(command, isclass):
        c.add_parser(subparsers)

    args = parser.parse_args(args)
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
