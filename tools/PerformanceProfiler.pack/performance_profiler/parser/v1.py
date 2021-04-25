import json
from struct import unpack

RECORD_LENGTH = 8
UNPACK_RECORD = "!HHHH"


class Parser:
    def parse(self, stream):
        logs = []

        while True:
            data = stream.read(RECORD_LENGTH)
            if data == b"":
                raise Exception("Unexpected EOF")
            if data == b"\x00" * RECORD_LENGTH:
                break

            l = unpack(UNPACK_RECORD, data)
            logs.append(
                {
                    "runtime": l[0] / 1000,
                    "package": l[1],
                    "line": l[2],
                    "query": l[3],
                }
            )

        queries = [q.decode("utf-8") for q in stream.read().split(b"\x00")]
        build_meta_data = json.loads(queries.pop(0))
        packages = build_meta_data.pop("packages")

        for l in logs:
            l["package"] = packages[l["package"]]
            l["query"] = queries[l["query"]]

        return {"build": build_meta_data, "logs": logs}
