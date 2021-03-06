## Requirements

* Python 3.7

## Installation

```
$ pip install -r requirements.txt
```

## Usage

```
$ ./main.py --help
usage: main.py [-h] {dump,load,prepare,tidyup} ...

positional arguments:
  {dump,load,prepare,tidyup}
    dump                Dump profile data
    load                Load profile data into database
    prepare             Prepare database
    tidyup              Tidy up database

optional arguments:
  -h, --help            show this help message and exit
```

## Deployment

```
$ make deploy            # deploy cloud functions
$ make install-scheduler # install schedulers that invokes cloud functions
```

### Variables

* PROJECT
    * if unset, we try to get from `gcloud config get-value project`.
* FUNCIONS\_REGION : region for the Cloud Functions
    * if unset, we try to get from `gcloud config get-value functions/region`.
* SCHEDULER\_TIME\_ZONE : time zone for the Cloud Scheduler
* SRC\_BUCKET : source bucket

## Test

```
$ make test
```

### Environment variable

You can set the following variables for complete testing, including BigQuery.

* `GOOGLE_APPLICATION_CREDENTIALS`
    * Credentials for testing.
    * See also: https://cloud.google.com/docs/authentication/production
* `TEST_GCS_BUCKET`
    * Bucket name for testing.
