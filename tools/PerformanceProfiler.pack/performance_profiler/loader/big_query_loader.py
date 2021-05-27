import copy
from google.cloud import bigquery
from google.cloud import bigquery_v2

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
            bigquery.SchemaField("id", "BYTES", mode="REQUIRED"),
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

VIEWS = {
    "logs_agg": {
        "clustering_fields": ["product_version"],
        "mview_query": """
SELECT
  product_version,
  HLL_COUNT.INIT(builds.id, 18) build_hll,
  HLL_COUNT.INIT(builds.instance_id, 18) instance_hll,
  COUNT(logs.runtime) log_count,
  MAX(logs.runtime) max_runtime,
  AVG(logs.runtime) avg_runtime,
  package,
  line,
  query_id
FROM
  {dataset}.builds builds,
  UNNEST(logs) logs
WHERE timestamp >= "2000-01-01"
GROUP BY
  product_version,
  package,
  line,
  query_id
        """,
    },
}

ROUTINES = {
    "from_tables": {
        "type_": "SCALAR_FUNCTION",
        "language": "JavaScript",
        "arguments": [
            bigquery.RoutineArgument(
                name="structure",
                data_type=bigquery_v2.types.StandardSqlDataType(
                    type_kind=bigquery_v2.types.StandardSqlDataType.TypeKind.STRING
                ),
            )
        ],
        "return_type": bigquery_v2.types.StandardSqlDataType(
            type_kind=bigquery_v2.types.StandardSqlDataType.TypeKind.ARRAY,
            array_element_type=bigquery_v2.types.StandardSqlDataType(
                type_kind=bigquery_v2.types.StandardSqlDataType.TypeKind.STRING
            ),
        ),
        "description": """
Extract table names from FROM clause.

Example:
SELECT
  id, identifier, query
FROM
  kytprof.queries, UNNEST(kytprof.from_tables(structure)) AS table
WHERE table = 'mt_author';
""",
        "body": f"""
var obj = JSON.parse(structure);
return typeof obj.from === 'string' ? [obj.from] : obj.from;
        """,
    },
    "n_days_ago": {
        "type_": "SCALAR_FUNCTION",
        "arguments": [
            bigquery.RoutineArgument(
                name="n",
                data_type=bigquery_v2.types.StandardSqlDataType(
                    type_kind=bigquery_v2.types.StandardSqlDataType.TypeKind.INT64
                ),
            )
        ],
        "return_type": bigquery_v2.types.StandardSqlDataType(
            type_kind=bigquery_v2.types.StandardSqlDataType.TypeKind.TIMESTAMP
        ),
        "description": """
Get the timestamp of n days ago

Example:
SELECT COUNT(id)
FROM kytprof.builds
WHERE timestamp > kytprof.n_days_ago(90) AND product_version = '7.7.0'
""",
        "body": f"""
DATE_SUB(CURRENT_TIMESTAMP(), interval n DAY)
        """,
    },
}


class BigQueryLoader:
    def __init__(self, opts):
        self.client = opts.get("client", bigquery.Client())
        self.project = opts.get("project", self.client.project)
        self.dataset_id = opts.get("dataset_id", DEFAULT_DATASET_ID)
        self.location = opts.get("location", None)
        self.dataset = f"{self.project}.{self.dataset_id}"  # shorthand

    def load(self, data):
        jobs = []
        for table_id in TABLES.keys():
            data_key = TABLES[table_id]["load_data_key"]
            if not data_key or data_key not in data:
                continue

            table_full_name = f"{self.dataset}.{table_id}"

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

    def _create_routine(self, routine_id):
        routine_full_name = f"{self.dataset}.{routine_id}"

        routine = bigquery.Routine(routine_full_name, **ROUTINES[routine_id])
        routine = self.client.create_routine(routine, exists_ok=True)
        print(
            f"Created routine {routine.project}.{routine.dataset_id}.{routine.routine_id}"
        )

    def prepare(self):
        dataset = bigquery.Dataset(f"{self.dataset}")
        dataset.location = self.location
        dataset = self.client.create_dataset(dataset, exists_ok=True)

        print(f"Created dataset {dataset.project}.{dataset.dataset_id}")

        for table_id in TABLES.keys():
            self._create_table(table_id)

        for table_id in VIEWS.keys():
            self._create_view(table_id)

        for routine_id in ROUTINES.keys():
            self._create_routine(routine_id)

    def _count_new_queries(self):
        return list(
            self.client.query(
                f"""
SELECT COUNT(qb.id) FROM `{self.dataset}.queries_buffer` qb
WHERE NOT EXISTS (
  SELECT 1
  FROM `{self.dataset}.queries` q
  WHERE qb.id = q.id
);
        """
            ).result()
        )[0][0]

    def _add_new_queries(self):
        select_cols = ", ".join(map(lambda x: x.name, TABLES["queries"]["schema"]))
        self.client.query(
            f"""
-- add newcommers from queries_buffer to queries
INSERT INTO `{self.dataset}.queries`
SELECT DISTINCT {select_cols} FROM `{self.dataset}.queries_buffer` qb
WHERE NOT EXISTS (
  SELECT 1
  FROM `{self.dataset}.queries` q
  WHERE qb.id = q.id
);
        """
        ).result()

    def tidyup(self):
        buffer_table = self.client.get_table(f"{self.dataset}.queries_buffer")
        if buffer_table.num_rows == 0:
            # nothing to do
            return

        new_queries_count = self._count_new_queries()
        if new_queries_count > 0:
            print(f"we are going to add new queries: {new_queries_count}")
            self._add_new_queries()

        self.client.delete_table(buffer_table)
        self._create_table("queries_buffer")

    def _create_table(self, table_id):
        table_full_name = f"{self.dataset}.{table_id}"

        table = bigquery.Table(table_full_name, schema=TABLES[table_id]["schema"])
        if TABLES[table_id]["time_partitioning"]:
            table.time_partitioning = TABLES[table_id]["time_partitioning"]
            table.require_partition_filter = True

        if TABLES[table_id]["clustering_fields"]:
            table.clustering_fields = TABLES[table_id]["clustering_fields"]

        table = self.client.create_table(table, exists_ok=True)
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")

    def _create_view(self, table_id):
        table_full_name = f"{self.dataset}.{table_id}"

        if "view_query" in VIEWS[table_id]:
            table = bigquery.Table(table_full_name)
            table.view_query = VIEWS[table_id]["view_query"]
            table = self.client.create_table(table, exists_ok=True)
        elif "mview_query" in VIEWS[table_id]:
            # XXX: google-cloud-bigquery@1.26.1 does not support "mview_query"
            opts = ""
            if "clustering_fields" in VIEWS[table_id]:
                opts += "CLUSTER BY " + ",".join(VIEWS[table_id]["clustering_fields"])

            self.client.query(
                f"""
CREATE MATERIALIZED VIEW IF NOT EXISTS {table_full_name} {opts} AS
{VIEWS[table_id]["mview_query"].format(dataset=self.dataset)}
            """
            ).result()

        print(f"Created view {table_full_name}.{table_id}")
