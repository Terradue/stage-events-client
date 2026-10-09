# stage-events-client

[![PyPI - Version](https://img.shields.io/pypi/v/stage-events-client.svg)](https://pypi.org/project/stage-events-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stage-events-client.svg)](https://pypi.org/project/stage-events-client)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Terradue/stage-events-client/package.yaml?branch=develop&event=push&label=build&logo=githubactions)](https://github.com/Terradue/stage-events-client/actions/workflows/package.yaml?query=branch%3Adevelop)
[![Code coverage](https://img.shields.io/codecov/c/github/Terradue/stage-events-client/develop?logo=codecov)](https://app.codecov.io/gh/Terradue-stage-events-client/tree/develop)

Python client for sending structured-mode
[CloudEvents 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
to the Stage Events API.

The package provides Pydantic models for the supported workflow events and
synchronous and asynchronous clients built on [HTTPX](https://www.python-httpx.org/).

## Documentation

The project documentation follows [Diátaxis](https://diataxis.fr/):

- [Tutorials](docs/tutorials/index.md): send your first event locally without a service.
- [How-to guides](docs/how-to/index.md): publish events, configure clients, and contribute changes.
- [Reference](docs/reference/index.md): CLI options, Python interfaces, and event fields.
- [Explanation](docs/explanation/index.md): event routing and schema-first architecture.

Browse the [documentation site](https://terradue.github.io/stage-events-client/)
or start at the [documentation index](docs/index.md).

## Requirements

- Python 3.10 or newer
- A Stage Events API endpoint
- A bearer token when authentication is enabled

## Installation

```console
python -m pip install stage-events-client
```

The command-line interface dependencies are optional. Enable the CLI explicitly
when installing the package:

```console
python -m pip install 'stage-events-client[cli]'
```

## Command-line interface

The `send-stage-event` executable provides one command for every supported
CloudEvent model:

```console
send-stage-event --help
send-stage-event submitted --help
```

Pass the complete destination URL as the command argument. There is no separate
base URL or endpoint-path setting:

```console
send-stage-event submitted \
  https://events.example.com/hooks/cloud-events \
  --source workflows:example-process:submit \
  --subject workflows:2f660c57:example-workflow \
  --data '{"namespace":"workflows","time":"2026-07-18T12:00:00Z"}' \
  --x-kafka-topic workflows.2f660c57.submitted \
  --token your-bearer-token
```

The available commands are `calendar`, `submitted`, `dismissed`, `prepared`,
`completed`, `failed`, `piped`, `staged`, and `ordered`. Each command validates
`--data` against its corresponding Pydantic model before sending the request.

`--data` accepts inline JSON, a JSON file prefixed with `@`, or `-` to read from
standard input:

```console
send-stage-event prepared https://events.example.com/cloud-events \
  --source workflows:example-process:prepare \
  --subject workflows:2f660c57:example-workflow \
  --data @prepared-data.json

cat submitted-data.json | send-stage-event submitted \
  https://events.example.com/cloud-events \
  --source workflows:example-process:submit \
  --subject workflows:2f660c57:example-workflow \
  --data -
```

The partition key defaults to the subject. Override it with `--partition-key`
when required. The `--x-kafka-topic` option is optional in the client, but the checked-in
OpenAPI contract requires the header. Supply it when your service enforces
that contract.

The bearer token can be supplied through `--token` or the
`STAGE_EVENTS_TOKEN` environment variable. Run a command with `--help` for TLS,
timeout, and all other options.

## Quick start

Create a client, construct an event, and send it with a Kafka topic:

```python
from datetime import datetime, timezone
from uuid import uuid4

from stage_events_client import AuthenticatedClient
from stage_events_client.api.default import send_cloud_event
from stage_events_client.models import SubmittedCloudEvent, SubmittedData

client = AuthenticatedClient(
    base_url="https://events.example.com",
    token="your-bearer-token",
)

subject = "workflows:2f660c57:example-workflow"
event = SubmittedCloudEvent(
    source="workflows:example-process:submit",
    subject=subject,
    partitionkey=subject,
    specversion="1.0",
    id=str(uuid4()),
    data=SubmittedData(
        namespace="workflows",
        time=datetime.now(timezone.utc),
    ),
)

with client:
    result = send_cloud_event.sync(
        client=client,
        body=event,
        x_kafka_topic="workflows.2f660c57.submitted",
    )

print(result)
```

Use `Client` instead when the API does not require authentication:

```python
from stage_events_client import Client

client = Client(base_url="https://events.example.com")
```

### Detailed responses

`sync` returns the parsed response body. Use `sync_detailed` when the status,
headers, or raw response body are also needed. In the client context above,
replace the `sync` call with:

```python
response = send_cloud_event.sync_detailed(
    client=client,
    body=event,
    x_kafka_topic="workflows.2f660c57.submitted",
)

print(response.status_code)
print(response.headers)
print(response.content)
print(response.parsed)
```

A successful `200` response is parsed as a string. Documented `400` responses
are parsed into the corresponding problem-details model. An undocumented status
returns `None` unless `raise_on_unexpected_status=True` is set on the client, in
which case `stage_events_client.errors.UnexpectedStatus` is raised.

### Async usage

Each endpoint has equivalent `asyncio` and `asyncio_detailed` functions:

```python
import asyncio


async def main() -> None:
    client = AuthenticatedClient(
        base_url="https://events.example.com",
        token="your-bearer-token",
    )
    async with client:
        result = await send_cloud_event.asyncio(
            client=client,
            body=event,
            x_kafka_topic="workflows.2f660c57.submitted",
        )
    print(result)


asyncio.run(main())
```

Do not use the same client instance in synchronous and asynchronous context
managers at the same time. Exiting a context closes its HTTPX client; create a
fresh client for subsequent contexts.

## Supported events

The request body can be any of the following models from
`stage_events_client.models`:

| Event type | Model |
| --- | --- |
| `calendar-event` | `CalendarCloudEvent` |
| `submitted` | `SubmittedCloudEvent` |
| `dismissed` | `DismissedCloudEvent` |
| `prepared` | `PreparedCloudEvent` |
| `completed` | `CompletedCloudEvent` |
| `failed` | `FailedCloudEvent` |
| `piped` | `PipedCloudEvent` |
| `staged` | `StagedCloudEvent` |
| `ordered` | `OrderedCloudEvent` |

The models validate event-specific payloads, timezone-aware timestamps,
semantic versions, and GeoJSON structures where applicable. Additional standard
CloudEvent attributes such as `id` and `specversion` are preserved by the
models.

### Event addressing

The API expects these values:

- `source`: three colon-separated components, normally
  `{namespace}:{process-id}:{step-name}`.
- `subject`: three colon-separated components, normally
  `{namespace}:{workflow-uid}:{workflow-name}`.
- `partitionkey`: usually the same value as `subject`.
- `x_kafka_topic`: a topic in the form
  `{namespace}.{workflow-uid}.{event-suffix}`, such as
  `workflows.2f660c57.submitted`.

Calendar topics use a duration followed by `.calendar`, for example
`workflows.2f660c57.10m.calendar`.

## Client configuration

Both `Client` and `AuthenticatedClient` accept shared headers, cookies, timeout,
TLS verification, redirect handling, and additional HTTPX options:

```python
import httpx

from stage_events_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="https://events.example.com",
    token="your-bearer-token",
    headers={"X-Correlation-ID": "request-id"},
    timeout=httpx.Timeout(30.0),
    verify_ssl="/path/to/ca-bundle.pem",
    follow_redirects=True,
    httpx_args={"proxy": "http://proxy.example.com:8080"},
    raise_on_unexpected_status=True,
)
```

TLS certificate verification is enabled by default. Setting `verify_ssl=False`
disables server certificate validation and should only be used in controlled
development environments.

The `with_*` methods return a new wrapper and also update any HTTPX clients
already created on the original wrapper:

```python
client = client.with_headers({"X-Correlation-ID": "new-request-id"})
client = client.with_cookies({"session": "value"})
client = client.with_timeout(httpx.Timeout(10.0))
```

The Python client defaults to `timeout=None` (no timeout); set an explicit
timeout for application requests.

An existing `httpx.Client` or `httpx.AsyncClient` can also be supplied with
`set_httpx_client` or `set_async_httpx_client`. Doing so overrides the generated
client configuration, so the HTTPX instance must define its own base URL and
other required settings, including authentication headers.

## Development

Install [Hatch](https://hatch.pypa.io/) and run the unit tests:

```console
hatch run test:test
```

Other useful checks are:

```console
hatch run test:test-cov
hatch run dev:format-check
hatch run dev:lint-check
hatch run dev:typecheck
hatch run dev:security
```

## License

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE.txt)
