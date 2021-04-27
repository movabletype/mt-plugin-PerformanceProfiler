from google.cloud import storage


def get_files(files):
    for file in files:
        if file.startswith("gs://"):
            bucket_name, prefix = file[5:].split("/", 1)

            client = storage.Client()
            bucket = client.get_bucket(bucket_name)

            while True:
                blobs = bucket.list_blobs(prefix=prefix)
                for blob in blobs:
                    yield f"gs://{bucket_name}/{blob.name}"
                if not blobs.next_page_token:
                    break
        else:
            yield file
