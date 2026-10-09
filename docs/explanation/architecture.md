# Events, routing, and client architecture

Stage Events Client is a publisher-side library. A workflow step describes an
occurrence with an event model, and the client posts that event to a Stage
Events endpoint. Routing and downstream processing happen outside this package.
The library neither connects directly to Kafka nor consumes events.

## Envelope and payload

A structured event carries its context and payload in the same JSON document.
`source` identifies the producing context, `subject` identifies the workflow,
and `type` distinguishes the occurrence. The `data` object contains fields
specific to that event type.

Separating the envelope from the data lets consumers identify related events
without needing to interpret every payload. For example, a `prepared` event
contains process inputs, while `staged` contains named feature collections.
Both can refer to the same workflow subject.

These names describe workflow occurrences, but the client does not implement a
state machine. It does not enforce event ordering or require that a submitted
event precede a completed event. Calendar and ordering events also have their
own payloads; the nine event types are not a mandatory linear sequence.

## Grouping and routing

The partition key groups related events and normally matches the subject.
The optional client argument `x_kafka_topic` is a separate HTTP header that
communicates a destination topic to the receiving service. The client does not
derive one from the other or check their consistency.

This separation matters when integrating a deployment: the client can construct
and send an event without a topic, while the checked-in OpenAPI declares that
header required. Local acceptance of a request is not a guarantee that the
service will accept it. See the [routing reference](../reference/events.md#routing).

## Request and response layers

```text
Python application or CLI
          |
          v
Generated Pydantic event model
          |
          v
send_cloud_event + Client / AuthenticatedClient
          |
          v
HTTPX -- HTTP POST --> Stage Events service
          |
          v
Text success, validated problem, or unexpected status
```

The CLI adds file/stdin input, command selection, token lookup, and exit codes.
It then calls the same synchronous detailed endpoint function as a Python
application. Async applications use the equivalent HTTPX async transport.

Model validation catches structural mistakes before transmission. Transport
errors describe failures in communication. HTTP responses describe what the
service returned, with 400 bodies validated against problem models from
`eoap_problems_registry`. These are different failure boundaries and call for
different handling.

The convenience functions return only the parsed value. Detailed functions
also expose status, headers, and raw bytes, making them useful when application
behavior depends on the HTTP result. Neither interface adds retries or confirms
downstream workflow completion.

## Schema as the source of truth

`schemas/openapi.yaml` defines the API, including references to shared schemas.
The Taskfile bundles it into `docs/c4/class/schemas/openapi.yaml` and generates
the HTML reference. The shared Terradue `json:create_models` task then generates
`src/stage_events_client/models.py` from the bundle.

This keeps schema-defined constraints and descriptions in one authoring
location. Hand-editing a generated model would create a second contract and
would be lost on regeneration. Follow the
[development guide](../how-to/development.md) to update the schema and regenerate.

The current generated models allow extension fields, and some nested structures
accept generic dictionaries. They validate the represented schema constraints;
they do not implement every semantic rule of CloudEvents, GeoJSON, or STAC.
For example, an event ID is not generated or required by the envelope model.
Applications must account for their receiving service's requirements as well as
the local model interface.
