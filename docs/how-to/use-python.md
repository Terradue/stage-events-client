# Use the Python client in an application

Install `stage-events-client` and obtain your service URL and bearer token.
The examples below read configuration from `STAGE_EVENTS_BASE_URL` and
`STAGE_EVENTS_TOKEN`. These are explicit application reads: the Python client
does not load environment variables itself.

## Send an authenticated event

```python
import os

import httpx

from stage_events_client import AuthenticatedClient
from stage_events_client.api.default import send_cloud_event
from stage_events_client.models import SubmittedCloudEvent, SubmittedData

event = SubmittedCloudEvent(
    source="workflows:example-process:submit",
    subject="workflows:demo-001:example-workflow",
    partitionkey="workflows:demo-001:example-workflow",
    data=SubmittedData(namespace="workflows"),
)
client = AuthenticatedClient(
    base_url=os.environ["STAGE_EVENTS_BASE_URL"],
    token=os.environ["STAGE_EVENTS_TOKEN"],
    timeout=httpx.Timeout(30.0),
    raise_on_unexpected_status=True,
)

with client:
    response = send_cloud_event.sync_detailed(
        client=client,
        body=event,
        x_kafka_topic="workflows.demo-001.submitted",
    )

print(response.status_code)
print(response.parsed)
```

Set the base URL to the service origin, for example `https://events.example.com`.
The default request path is `/cloud-events`. For an unauthenticated service,
construct `Client` without `token` instead.

A returned response can represent an error: check its status using the
[error-handling guide](handle-errors.md). The client does not retry requests.

## Use a custom endpoint

Pass `path="/hooks/cloud-events"` to `sync_detailed` or `asyncio_detailed`.
The convenience functions `sync` and `asyncio` do not accept `path`.
If using a base URL with an API prefix, check the final HTTPX URL to avoid
duplicating that prefix. The CLI accepts a complete URL instead.

## Send asynchronously

Use the same `event` constructed above with a fresh client:

```python
import asyncio


async def main() -> None:
    client = AuthenticatedClient(
        base_url=os.environ["STAGE_EVENTS_BASE_URL"],
        token=os.environ["STAGE_EVENTS_TOKEN"],
        timeout=httpx.Timeout(30.0),
        raise_on_unexpected_status=True,
    )
    async with client:
        response = await send_cloud_event.asyncio_detailed(
            client=client,
            body=event,
            x_kafka_topic="workflows.demo-001.submitted",
        )
    print(response.status_code, response.parsed)


asyncio.run(main())
```

In an application with an existing event loop, await `main()` instead of calling
`asyncio.run`. Keep a client context open for multiple sends to reuse its HTTP
connection pool. Exiting closes the underlying HTTPX client; create a fresh
client for a later context. Use separate instances for sync and async work.

## Configure HTTP

Supply shared headers, cookies, a timeout, or redirect handling at construction.
The Python default `timeout=None` disables HTTPX timeouts, so set an explicit
timeout for application requests. Redirect following defaults to `False`.

For a private certificate authority, build an SSL context:

```python
import ssl

client = AuthenticatedClient(
    base_url=os.environ["STAGE_EVENTS_BASE_URL"],
    token=os.environ["STAGE_EVENTS_TOKEN"],
    headers={"X-Correlation-ID": "demo-001"},
    timeout=httpx.Timeout(30.0),
    verify_ssl=ssl.create_default_context(cafile="/path/to/ca-bundle.pem"),
)
```

Additional HTTPX constructor settings, such as `proxy` or `transport`, can be
passed in `httpx_args`. Do not repeat arguments already supplied by the wrapper,
such as `timeout`, inside `httpx_args`.

To inject an existing HTTPX client, use `set_httpx_client` or
`set_async_httpx_client`. Configure the base URL, authentication headers, timeout,
and TLS directly on that instance; injection bypasses the wrapper's settings,
including automatic bearer authentication. Entering and exiting the wrapper's
context also enters and closes the injected client.

See the [Python reference](../python-api.md) for defaults and method behavior.
