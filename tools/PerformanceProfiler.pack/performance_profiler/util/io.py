import io
import os
from google.cloud import storage


def get_bytes(file, remove=False):
    if file.startswith("gs://"):
        bucket_name, file_name = file[5:].split("/", 1)

        client = storage.Client()
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob(file_name)
        contents = blob.download_as_string()
        if remove:
            blob.delete()
        return contents
    else:
        contents = open(file, "rb").read()
        if remove:
            os.remove(file)
        return contents


def get_stream(file, remove=False):
    data = get_bytes(file, remove)
    return io.BytesIO(data)
