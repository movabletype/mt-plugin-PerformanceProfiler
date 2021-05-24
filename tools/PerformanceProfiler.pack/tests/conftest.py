import pytest
import os
import secrets
from pathlib import Path
from google.cloud import storage
from google.cloud import bigquery


def verify_google_application_credentials():
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        pytest.skip("Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set")
        return False
    return True


@pytest.fixture(scope="session")
def bq_client():
    if not verify_google_application_credentials():
        return

    return bigquery.Client()


@pytest.fixture(scope="session")
def gcs_bucket():
    if not verify_google_application_credentials():
        return

    bucket_name = os.getenv("TEST_GCS_BUCKET")
    client = storage.Client()
    return client.get_bucket(bucket_name)


@pytest.fixture(scope="module")
def gcs_prefix(gcs_bucket):
    prefix = secrets.token_hex()
    yield prefix
    blobs = gcs_bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        blob.delete()


@pytest.fixture(scope="session")
def fixtures_dir():
    return Path(__file__).parent.joinpath("fixtures")
