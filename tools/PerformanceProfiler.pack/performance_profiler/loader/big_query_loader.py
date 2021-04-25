from google.cloud import bigquery

DEFAULT_DATASET_ID = "kytprof"

TABLES = {
    "builds": {
        "time_partitioning": bigquery.TimePartitioning(
            type_="MONTH",
        ),
        "schema": [
            bigquery.SchemaField("id", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("version", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("product_version", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("instance_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("archive_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("runtime", "FLOAT64", mode="REQUIRED"),
        ],
    },
    "logs": {
        "time_partitioning": bigquery.TimePartitioning(
            type_="MONTH",
        ),
        "schema": [
            bigquery.SchemaField("build_id", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("runtime", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("package", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("line", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("query_id", "BYTES", mode="REQUIRED"),
        ],
    },
    "queries": {
        "time_partitioning": None,
        "schema": [
            bigquery.SchemaField("id", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("identifier", "BYTES", mode="REQUIRED"),
            bigquery.SchemaField("query", "STRING", mode="REQUIRED"),
        ],
    },
}

VIEWS = {
    "unique_queries": {
        "view_query": "SELECT DISTINCT id, identifier, query FROM {}.{}.queries"
    },
}


class BigQueryLoader:
    def __init__(self, opts):
        self.client = opts.get("client", bigquery.Client())
        self.project = opts.get("project", self.client.project)
        self.dataset_id = opts.get("dataset_id", DEFAULT_DATASET_ID)

    def load(self, data):
        for table_id in TABLES.keys():
            table_full_name = f"{self.project}.{self.dataset_id}.{table_id}"

            job_config = bigquery.LoadJobConfig(schema=TABLES[table_id]["schema"])
            job = self.client.load_table_from_json(
                data[table_id], table_full_name, job_config=job_config
            )
            job.result()

            print(f"Loaded {job.output_rows} rows into {table_full_name}.")

    def prepare(self):
        dataset = bigquery.Dataset(f"{self.project}.{self.dataset_id}")
        dataset.location = "asia-northeast1"
        dataset = self.client.create_dataset(dataset, exists_ok=True)

        print(f"Created dataset {dataset.project}.{dataset.dataset_id}")

        for table_id in TABLES.keys():
            table_full_name = f"{self.project}.{self.dataset_id}.{table_id}"

            table = bigquery.Table(table_full_name, schema=TABLES[table_id]["schema"])
            table.time_partitioning = TABLES[table_id]["time_partitioning"]
            table = self.client.create_table(table, exists_ok=True)
            print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

        for table_id in VIEWS.keys():
            table_full_name = f"{self.project}.{self.dataset_id}.{table_id}"

            table = bigquery.Table(table_full_name)
            table.view_query = VIEWS[table_id]["view_query"].format(
                self.project, self.dataset_id
            )
            table = self.client.create_table(table, exists_ok=True)
            print(f"Created view {table.project}.{table.dataset_id}.{table.table_id}")

    def tidyup(self):
        # TODO
        # dedup queries table
        raise Exception("not implemented")
