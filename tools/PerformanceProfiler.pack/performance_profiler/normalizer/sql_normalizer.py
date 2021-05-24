import json
from moz_sql_parser import parse, format

PLACEHOLDER = "$v"


def sort_key(obj):
    if isinstance(obj, str):
        return obj
    else:
        return json.dumps(obj, sort_keys=True)


def sort_terms(term):
    for k in ["select", "from", "where", "and", "or", "value", "distinct"]:
        if k not in term:
            continue
        if isinstance(term[k], list):
            term[k] = sorted(term[k], key=sort_key)
            for child in [c for c in term[k] if isinstance(c, dict)]:
                sort_terms(child)
        if isinstance(term[k], dict):
            sort_terms(term[k])


def truncate_id_in(parsed):
    try:
        column = parsed["where"]["in"][0]
    except KeyError:
        return

    if column.endswith("_id"):
        parsed["where"]["in"] = [column, PLACEHOLDER]


class SQLNormalizer:
    def normalize(self, sql):
        sql = sql.replace("?", PLACEHOLDER)
        parsed = parse(sql)
        sort_terms(parsed)
        truncate_id_in(parsed)
        return (format(parsed).replace(PLACEHOLDER, "?"), parsed)
