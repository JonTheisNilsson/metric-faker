Upload random metric fact to ServiceClarity via console.

usage: mf.py [-h] [--minutes MINUTES] [--start START] USER PASSWORD METRIC_ID

positional arguments:
  USER
  PASSWORD
  METRIC_ID

optional arguments:
  -h, --help            show this help message and exit
  --minutes MINUTES, -m MINUTES
                        Minutes between uploads (default: 60)
  --start START, -s START
                        Initial value (default: 100)



Because of the way serviceclarity is built this will return 202 even if metric id doesn't exist.
TODO: Check if metric id exist before posting.
