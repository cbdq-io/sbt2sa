# sbns2sa
Extract data from Azure Service Bus Topics and load onto Blob Storage on a Storage Account.

If `CONTAINER_NAME` is set to `mycontainer`, `TOPICS_DIR` is set to `topics`,
`PATH_FORMAT` is set to `year=YYYY/month=MM/day=dd/hour=HH` and
`TOPIC_NAME` is set to `mytopic`, then the file path for the data to be
loaded to will be something like:

`azure://mycontainer/topics/mytopic/year=2025/month=02/day=24/hour=11/mytopic+0000000000000000042.bin.gz`

## Required Environment Variables

- `CONTAINER_NAME`: The container name within the storage account to load
  the data to.
- `MAX_MESSAGES_IN_BATCH`: The maximum number of messages to extract from the
  topic in a batch before loading onto the blob storage.  Default is 500.
- `SERVICE_BUS_CONNECTION_STRING`:  The connection string to connect to Azure
  Service Bus.
- `STORAGE_ACCOUNT_CONNECTION_STRING`: The connection string to connect to
  the Azure Storage Account.
- `SUBSCRIPTION_NAME`:  The name of the subscription to use to extract from
  the topic.
- `TOPIC_NAME`:  The name of the topic to extract from.
- `WAIT_TIME_SECONDS`: The length of time in seconds to wait for messages on
  the topic before continuing.  Default is 5.

## Optional Environment Variables

- `CHECK_FOR_DL_MESSAGES`: Check for the existence of and warn if any dead-
  letter messages are present on the topic/subscription.  Set to "1" to
  enable.  Default is "0".
- `MAX_RUNTIME_SECONDS`: Limits how long (in seconds) the archiver will spend
  on a single topic before moving on. Set to 0 (default) to disable this and
  rely on the usual idle detection logic; set to a positive number to enforce
  a maximum runtime per topic.
- `PATH_FORMAT`: The configuration to set the format of the data directories.
  The format set in this configuration converts the timestamp of the latest
  message in the block written to proper directory strings.  Within the
  provided string the following substutions will take place:
    - `YYYY` will be replaced by the year.
    - `MM` will be replaced by the zero padded month number.
    - `dd` will be replaced by the zero padded day number.
    - `HH` will be replaced by the zero padded hour number.
    - `mm` will be replaced by the zero padded minute number.

  Default is "".
= `PROMETHEUS_METRIC_NAME_PREFIX`: The prefix for any of the custom
  Prometheus metrics that are created.  The default is "".
- `PROMETHEUS_PORT`: Set the port for Prometheus metrics to be made
  available on when running `multi-topic-entrypoint.py`.  Default
  is "8000".
- `TOPICS_DIR`: The directory within the specified container to load the
  topics to.  Default is `topics`.
