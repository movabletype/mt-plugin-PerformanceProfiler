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
