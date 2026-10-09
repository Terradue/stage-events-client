# Diagnose failed requests

Distinguish invalid event data, transport failures, and server responses before
deciding whether to resend an event.

## Fix local validation errors

Pydantic validates event construction before transmission. Check the field path
in the error and compare it with the [event reference](../reference/events.md).
Common causes include a source or subject without three colon-separated parts,
a timestamp without a timezone, or a process version such as `1.2` rather than
`1.2.0`.

For the CLI, check that `--data` contains a JSON object with the data fields,
that an `@` file is readable, and that the URL is absolute HTTP or HTTPS without
a fragment. Invalid JSON or CLI usage generally exits with status `2`; event
model validation exits with status `1`.

## Handle Python responses

Use a detailed function and enable `raise_on_unexpected_status`. In an existing
client context with your constructed `event`, use:

```python
from http import HTTPStatus

import httpx

from stage_events_client.api.default import send_cloud_event
from stage_events_client.errors import UnexpectedStatus

try:
    response = send_cloud_event.sync_detailed(
        client=client,
        body=event,
        x_kafka_topic="workflows.demo-001.submitted",
    )
except httpx.TimeoutException:
    print("The request timed out; check whether the service received the event.")
except httpx.RequestError as exc:
    print(f"Transport failure: {exc}")
except UnexpectedStatus as exc:
    print(f"Undocumented HTTP status: {exc.status_code}")
else:
    if response.status_code == HTTPStatus.OK:
        print(response.parsed)
    elif response.status_code == HTTPStatus.BAD_REQUEST:
        print(response.parsed)
```

HTTP 400 responses are returned as problem objects, not raised as
`UnexpectedStatus`. For type-specific handling, import problem classes from
`eoap_problems_registry`, for example `MissingRequestHeader`; those are the
classes the endpoint parser returns.

Malformed 400 bodies are separate parsing failures: invalid JSON raises
`ValueError` (including JSON decoding errors), a non-object raises `TypeError`,
and an object that fails problem validation raises Pydantic `ValidationError`.
These exceptions propagate even when `raise_on_unexpected_status=False`.
The CLI does not turn these parsing failures into its usual formatted API error.

## Diagnose service errors

| Symptom | Action |
| --- | --- |
| Missing `X-Kafka-Topic` problem | Supply the header; the OpenAPI contract requires it even though the client permits omission. |
| Invalid topic header | Use the documented routing pattern; the client forwards topic strings without validating the pattern. |
| HTTP 401 or 403 | Check the token and endpoint access with the service operator. |
| HTTP 404 or redirect | Check the complete endpoint path; redirects are not followed by default. |
| HTTP 201 or 204 treated as unexpected | The client documents only 200 as success; check the service contract. |
| TLS verification failure | Configure the trusted CA rather than disabling verification for production. |
| Timeout or connection failure | Check reachability and timeout settings; determine whether the event was accepted before resending. |

The package has no automatic retry, deduplication, or delivery confirmation
beyond the HTTP response. A timeout does not establish that the server rejected
the event. Coordinate retry behavior with your service's delivery guarantees.

See [response reference](../python-api.md#responses-and-exceptions) for the
complete status and exception behavior.
