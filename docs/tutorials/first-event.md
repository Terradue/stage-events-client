# Send your first event locally

In this tutorial, you will create a workflow submission event and send it through
the Python client. An in-memory HTTP transport will stand in for the service so
you can inspect the request and get a predictable response without credentials.

You need Python 3.10 or newer and a terminal. Allow about ten minutes.

## Set up an environment

Create a working directory and a virtual environment:

```console
mkdir stage-events-tutorial
cd stage-events-tutorial
python -m venv .venv
source .venv/bin/activate
python -m pip install stage-events-client
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## Create an event

Create `first_event.py` with the following content:

```python
import json
from datetime import datetime, timezone

import httpx

from stage_events_client import Client
from stage_events_client.api.default import send_cloud_event
from stage_events_client.models import SubmittedCloudEvent, SubmittedData

subject = "workflows:demo-001:example-workflow"
event = SubmittedCloudEvent(
    source="workflows:example-process:submit",
    subject=subject,
    partitionkey=subject,
    data=SubmittedData(
        namespace="workflows",
        time=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
    ),
)

print(event.type)
print(event.data.namespace)
```

Run it:

```console
python first_event.py
```

You should see:

```text
submitted
workflows
```

The event class supplies the `submitted` type. Its `data` is validated as
`SubmittedData`. The `subject` identifies this workflow, and we use the same
value for `partitionkey` to group its related events.

## Send and inspect the request

Append this code to the same file:

```python
def accept_event(request: httpx.Request) -> httpx.Response:
    """Inspect the tutorial request and simulate an accepting service."""
    payload = json.loads(request.content)
    print(request.method, request.url.path)
    print(request.headers["Content-Type"])
    print(request.headers["X-Kafka-Topic"])
    print(payload["type"], payload["data"]["namespace"])
    return httpx.Response(200, text="accepted", request=request)


client = Client(
    base_url="https://events.example.test",
    timeout=httpx.Timeout(30.0),
    httpx_args={"transport": httpx.MockTransport(accept_event)},
)

with client:
    response = send_cloud_event.sync_detailed(
        client=client,
        body=event,
        x_kafka_topic="workflows.demo-001.submitted",
    )

print(int(response.status_code), response.parsed)
```

Run the script again. After the first two lines, it should print:

```text
POST /cloud-events
application/cloudevents+json
workflows.demo-001.submitted
submitted workflows
200 accepted
```

You have exercised model construction, JSON serialization, request headers,
and response parsing. The transport runs inside your process; it has not sent
an event to a real server. `accepted` is the simulated response text, not a
fixed message guaranteed by a deployed service.

## Observe validation

Change the source to `"example-process"` and run the script again. Construction
raises a Pydantic `ValidationError` because the source must have three nonempty
colon-separated components. No request is made. Restore the original source
to get the successful output again.

## Next steps

- [Send events from the command line](../how-to/send-from-cli.md) to publish to a real endpoint.
- [Use the Python client in an application](../how-to/use-python.md) for authentication and async requests.
- [Event model reference](../reference/events.md) for other payload types.
