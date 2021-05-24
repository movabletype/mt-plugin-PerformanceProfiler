import copy
from google.cloud import bigquery

DEFAULT_DATASET_ID = "kytprof"

TABLES = {
    "builds": {
        "load_data_key": "builds",
        "time_partitioning": bigquery.TimePartitioning(
            type_="MONTH",
            field="timestamp",
        ),
        "clustering_fields": ["product_version"],
        "schema": [
            bigquery.SchemaField("version", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("product_version", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("instance_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("archive_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("runtime", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField(
                "logs",
                "RECORD",
                mode="REPEATED",
                fields=[
                    bigquery.SchemaField("runtime", "FLOAT64", mode="REQUIRED"),
                    bigquery.SchemaField("package", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("line", "INT64", mode="REQUIRED"),
                    bigquery.SchemaField("query_id", "BYTES", mode="REQUIRED"),
                ],
            ),
        ],
    },
    "queries": {
        "load_data_key": None,
        "time_partitioning": None,
        "clustering_fields": None,
        "schema": [
            bigquery.SchemaField("id", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("identifier", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("query", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("structure", "STRING", mode="REQUIRED"),
        ],
    },
}

TABLES["queries_buffer"] = copy.copy(TABLES["queries"])
TABLES["queries_buffer"]["load_data_key"] = "queries"


class BigQueryLoader:
    def __init__(self, opts):
        self.client = opts.get("client", bigquery.Client())
        self.project = opts.get("project", self.client.project)
        self.dataset_id = opts.get("dataset_id", DEFAULT_DATASET_ID)
        self.location = opts.get("location", None)

    def load(self, data):
        jobs = []
        for table_id in TABLES.keys():
            data_key = TABLES[table_id]["load_data_key"]
            if not data_key or data_key not in data:
                continue

            table_full_name = f"{self.project}.{self.dataset_id}.{table_id}"

            job_config = bigquery.LoadJobConfig(
                schema=TABLES[table_id]["schema"],
                time_partitioning=TABLES[table_id]["time_partitioning"],
                clustering_fields=TABLES[table_id]["clustering_fields"],
            )

            job = self.client.load_table_from_json(
                data[data_key], table_full_name, job_config=job_config
            )

            jobs.append(job)
            print(f"Created a LoadJob: {job.job_id} to insert into {table_full_name}.")

        return jobs

    def prepare(self):
        dataset = bigquery.Dataset(f"{self.project}.{self.dataset_id}")
        dataset.location = self.location
        dataset = self.client.create_dataset(dataset, exists_ok=True)

        print(f"Created dataset {dataset.project}.{dataset.dataset_id}")

        for table_id in TABLES.keys():
            table_full_name = f"{self.project}.{self.dataset_id}.{table_id}"

            table = bigquery.Table(table_full_name, schema=TABLES[table_id]["schema"])
            if TABLES[table_id]["time_partitioning"]:
                table.time_partitioning = TABLES[table_id]["time_partitioning"]
                table.require_partition_filter = True

            if TABLES[table_id]["clustering_fields"]:
                table.clustering_fields = TABLES[table_id]["clustering_fields"]

            table = self.client.create_table(table, exists_ok=True)
            print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

    def tidyup(self):
        dataset = f"{self.project}.{self.dataset_id}"

        buffer_table = self.client.get_table(f"{dataset}.queries_buffer")
        if buffer_table.num_rows == 0:
            # No newcomers
            return []

        jobs = []

        select_cols = ", ".join(map(lambda x: x.name, TABLES["queries"]["schema"]))
        job = self.client.query(
            f"""
-- add newcommers from queries_buffer to queries
CREATE OR REPLACE TABLE `{dataset}.queries`
AS
WITH all_queries AS (
  SELECT {select_cols} FROM `{dataset}.queries`
  UNION ALL
  SELECT {select_cols} FROM `{dataset}.queries_buffer`
)
SELECT DISTINCT {select_cols}
FROM all_queries;

-- delete known queries from queries_buffer
DELETE FROM `{dataset}.queries_buffer` qb
WHERE EXISTS (
  SELECT 1
  FROM `{dataset}.queries` q
  WHERE qb.id = q.id
);
        """
        )
        jobs.append(job)

        return jobs
