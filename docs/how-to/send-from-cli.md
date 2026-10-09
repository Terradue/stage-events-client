# Send events from the command line

Install the CLI extra and obtain the complete endpoint URL from your service
operator:

```console
python -m pip install 'stage-events-client[cli]'
send-stage-event submitted --help
```

Replace the example URL below with your destination. The CLI uses exactly the
path and query string you supply; it does not append `/cloud-events`.

## Authenticate

For an authenticated service, have your shell or CI secret store populate
`STAGE_EVENTS_TOKEN` with the token value, without the `Bearer` prefix. The CLI
adds that prefix. You can also use `--token`, which takes precedence over the
environment variable. Without either value, the CLI sends an unauthenticated
request.

## Send inline data

```console
send-stage-event submitted https://events.example.com/cloud-events \
  --source workflows:example-process:submit \
  --subject workflows:demo-001:example-workflow \
  --data '{"namespace":"workflows","time":"2026-07-18T12:00:00Z"}' \
  --x-kafka-topic workflows.demo-001.submitted
```

`--data` contains only the event-specific data object, not the full CloudEvent.
The command supplies the event type and defaults the partition key to the
subject. Use `--partition-key` to override this grouping value.

The client allows you to omit `--x-kafka-topic`, but the checked-in OpenAPI
contract marks the header as required. Supply it for services enforcing that
contract. Its format is described in the [event reference](../reference/events.md#routing).

## Send a file or standard input

Save this object as `prepared-data.json`:

```json
{
  "namespace": "workflows",
  "process_id": "example-process",
  "process_version": "1.2.0",
  "job_id": "demo-001",
  "inputs": {"area": "s3://example-bucket/area.geojson"}
}
```

Send the file with the `prepared` command:

```console
send-stage-event prepared https://events.example.com/cloud-events \
  --source workflows:example-process:prepare \
  --subject workflows:demo-001:example-workflow \
  --data @prepared-data.json \
  --x-kafka-topic workflows.demo-001.prepared
```

For a pipeline, use `--data -`. This shell example reads the same file through
standard input:

```console
send-stage-event prepared https://events.example.com/cloud-events \
  --source workflows:example-process:prepare \
  --subject workflows:demo-001:example-workflow \
  --data - \
  --x-kafka-topic workflows.demo-001.prepared < prepared-data.json
```

Choose another command and matching payload using the
[event model table](../reference/events.md#event-data).

## Set a timeout and check the result

Add `--timeout 10` to any command to set a ten-second HTTPX timeout. TLS
verification is enabled by default. The CLI has no dedicated CA bundle option;
use the [Python configuration guide](use-python.md#configure-http) when you need
an explicit SSL context.

A documented HTTP 200 response produces exit status `0` and prints its text
when nonempty. Check the exit status in your script before continuing. See
[diagnose failed requests](handle-errors.md) for input, transport, and API errors,
and the [CLI reference](../cli.md) for all options.
