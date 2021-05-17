import json
import re

from base64 import b64encode
from hashlib import sha1
from copy import copy
from performance_profiler.normalizer import SQLNormalizer


def to_hash_value(str):
    return b64encode(sha1(str.encode("utf-8")).digest()).decode("utf-8")


class RDBTransformer:
    def __init__(self):
        self.sql_normalizer = SQLNormalizer()
        self.query_map = {}

    def __query_id(self, query, queries):
        if query not in self.query_map:
            hash_value = to_hash_value(query)
            self.query_map[query] = hash_value
            normalized, structure = self.sql_normalizer.normalize(query)
            queries.append(
                {
                    "query": query,
                    "id": hash_value,
                    "identifier": to_hash_value(normalized),
                    "structure": json.dumps(structure),
                }
            )

        return self.query_map[query]

    def transform(self, data):
        build = copy(data["build"])
        build.pop("id")
        build["logs"] = []
        queries = []

        for orig in data["logs"]:
            log = copy(orig)

            query = log.pop("query")
            # ignore reconnecting log
            if re.match(r"(?:show variables|set names|\s*$)", query, re.IGNORECASE):
                continue

            log["query_id"] = self.__query_id(query, queries)
            build["logs"].append(log)

        return {
            "builds": [build],
            "queries": queries,
        }
