import io
import os
from google.cloud import storage


def get_streams(files, remove=False):
    for file in files:
        if file.startswith("gs://"):
            bucket_name, prefix = file[5:].split("/", 1)

            client = storage.Client()
            bucket = client.get_bucket(bucket_name)

            while True:
                blobs = bucket.list_blobs(prefix=prefix)
                for blob in blobs:
                    contents = blob.download_as_string()
                    stream = io.BytesIO(contents)

                    if remove:
                        bucket.delete_blob(blob.name)

                    yield stream
                if not blobs.next_page_token:
                    break
        else:
            stream = open(file, "rb")

            if remove:
                os.remove(file)

            yield stream
