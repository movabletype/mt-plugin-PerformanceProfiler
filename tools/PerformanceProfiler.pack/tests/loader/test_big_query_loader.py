import pytest
import secrets
import base64
from google.cloud import bigquery

from performance_profiler.loader.big_query_loader import BigQueryLoader, TABLES


class TestLoad:
    @pytest.fixture
    def dataset(self, bq_client):
        dataset_id = secrets.token_hex()
        dataset = bigquery.Dataset(f"{bq_client.project}.{dataset_id}")

        yield dataset

        bq_client.delete_dataset(dataset, delete_contents=True)

    @pytest.fixture
    def loader(self, dataset):
        return BigQueryLoader({"dataset_id": dataset.dataset_id})

    def test_prepare(self, bq_client, dataset, loader):
        loader.prepare()

        for t in TABLES.keys():
            table_full_name = f"{dataset.project}.{dataset.dataset_id}.{t}"
            table = bigquery.Table(table_full_name)
            assert bq_client.get_table(table)

    def test_load(self, loader):
        loader.prepare()

        data = {
            "builds": [
                {
                    "version": "1",
                    "product_version": "1",
                    "instance_id": "x",
                    "file": "x",
                    "archive_type": "index",
                    "timestamp": "2020-01-01T00:00:00Z",
                    "runtime": 0.001,
                    "logs": [
                        {
                            "package": "x",
                            "line": 1,
                            "runtime": 0.001,
                            "query_id": base64.b64encode(b"x").decode("utf-8"),
                        }
                    ],
                }
            ],
            "queries": [
                {
                    "id": base64.b64encode(b"x").decode("utf-8"),
                    "query": "x",
                    "identifier": base64.b64encode(b"x").decode("utf-8"),
                    "structure": "x",
                }
            ],
        }
        jobs = loader.load(data)

        for j in jobs:
            try:
                j.result()
            except Exception as e:
                raise Exception(j.errors)
            assert j.output_rows == 1

    def test_tidyup(self, bq_client, dataset, loader):
        loader.prepare()

        data = {
            "builds": [
                {
                    "version": "1",
                    "product_version": "1",
                    "instance_id": "x",
                    "file": "x",
                    "archive_type": "index",
                    "timestamp": "2020-01-01T00:00:00Z",
                    "runtime": 0.001,
                    "logs": [
                        {
                            "package": "x",
                            "line": 1,
                            "runtime": 0.001,
                            "query_id": base64.b64encode(b"x").decode("utf-8"),
                        }
                    ],
                }
            ],
            "queries": [
                {
                    "id": base64.b64encode(b"x").decode("utf-8"),
                    "query": "x",
                    "identifier": base64.b64encode(b"x").decode("utf-8"),
                    "structure": "x",
                },
                {
                    "id": base64.b64encode(b"x").decode("utf-8"),
                    "query": "x",
                    "identifier": base64.b64encode(b"x").decode("utf-8"),
                    "structure": "x",
                },
                {
                    "id": base64.b64encode(b"y").decode("utf-8"),
                    "query": "y",
                    "identifier": base64.b64encode(b"y").decode("utf-8"),
                    "structure": "y",
                },
            ],
        }
        jobs = loader.load(data)

        for j in jobs:
            j.result()

        def select_queries(table):
            queries_table_name = f"{dataset.project}.{dataset.dataset_id}.{table}"
            res = bq_client.query(
                f"""
SELECT query FROM {queries_table_name} ORDER BY query ASC
            """
            ).result()

            return list(map(lambda r: r.query, res))

        assert select_queries("queries_buffer") == ["x", "x", "y"]
        assert select_queries("queries") == []

        jobs = loader.tidyup()

        for j in jobs:
            try:
                j.result()
            except Exception as e:
                raise Exception(j.errors)

        assert select_queries("queries_buffer") == []
        assert select_queries("queries") == ["x", "y"]
