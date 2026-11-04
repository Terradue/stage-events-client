# Event model reference

Import event and data models from `stage_events_client.models`. These Pydantic
v2 classes are generated from `schemas/openapi.yaml`. The tables describe their
current Python validation behavior. The [OpenAPI reference](../c4/class/schemas/openapi.html)
describes the HTTP contract.

## Common envelope

| Field | Required at construction | Default and constraints |
| --- | --- | --- |
| `source` | Yes | Three nonempty colon-separated components; pattern `^[^:]+:[^:]+:[^:]+$`. Convention: namespace, process identifier, step name. |
| `subject` | Yes | Same pattern as `source`. Convention: namespace, workflow UID, workflow name. |
| `partitionkey` | Yes | String, normally equal to `subject`. Only the CLI fills this automatically. |
| `data` | Yes | Data model corresponding to the event class. |
| `type` | No | Literal supplied by the event class; see below. |
| `specversion` | No | Literal `"1.0"`. |
| `datacontenttype` | No | Literal `"application/json"`. |

The generated envelope allows additional fields. It does not declare, require,
or generate `id`; callers can supply it as an extra attribute. The CLI has no
option for setting an event ID or other extra envelope attributes.

## Event data

Every data model requires `namespace: str`. All also accept optional nullable
`owner_id: str`, `properties: dict`, and `priority: str`, each defaulting to
`None`. Additional fields are allowed.

| CLI command | CloudEvent class | `type` | Data class | Additional required data fields |
| --- | --- | --- | --- | --- |
| `calendar` | `CalendarCloudEvent` | `calendar-event` | `CalendarData` | `event_time`, `start_time`, `end_time` |
| `submitted` | `SubmittedCloudEvent` | `submitted` | `SubmittedData` | None |
| `dismissed` | `DismissedCloudEvent` | `dismissed` | `DismissedData` | `status` |
| `prepared` | `PreparedCloudEvent` | `prepared` | `PreparedData` | `process_id`, `job_id`, `inputs` |
| `completed` | `CompletedCloudEvent` | `completed` | `CompletedData` | `process_id`, `job_id`, `usage`, `outputs` |
| `failed` | `FailedCloudEvent` | `failed` | `FailedData` | `process_id`, `job_id`, `usage` |
| `piped` | `PipedCloudEvent` | `piped` | `PipedData` | `process_id`, `job_id`, `entries` |
| `staged` | `StagedCloudEvent` | `staged` | `StagedData` | `process_id`, `job_id`, `outputs` |
| `ordered` | `OrderedCloudEvent` | `ordered` | `OrderedData` | `profile`, `order_id`, `entries` |

The required process, job, profile, and order identifiers are strings.

### Timestamps and statuses

Calendar timestamps are timezone-aware datetimes. `SubmittedData.time` and
`DismissedData.time` are optional timezone-aware datetimes, defaulting to `None`.
JSON values can use ISO timestamps with `Z` or an explicit offset. Naive
timestamps are rejected. The generated models do not enforce chronological
ordering between calendar timestamps.

`DismissedStatus` values are case-sensitive: `Unknown`, `Pending`, `Running`,
`Succeeded`, `Failed`, and `Error`. Python enum members are uppercase, for
example `DismissedStatus.RUNNING`.

### Process inputs and outputs

Prepared, completed, failed, piped, and staged data accept optional nullable
`process_version`, defaulting to `None`. A supplied string must match the
schema's semantic-version pattern, for example `1.2.0` or `1.2.0-rc.1+build.4`.

`PreparedData.inputs` and `CompletedData.outputs` are dictionaries with arbitrary
values. `StagedData.outputs`, `PipedData.entries`, and `OrderedData.entries`
map names to generated `FeatureCollection` models.

### Usage and failure details

`CompletedData.usage` and `FailedData.usage` require a `Usage` object, but its
fields are optional, so `{}` is accepted. It can hold start and finish times,
elapsed time, CPU, memory, disk, and task counts, plus per-child usage records.
Field names include their units, such as `elapsed_seconds`, `total_cpu_hours`,
and `total_ram_megabyte_hours`. Consult the generated OpenAPI for the complete
`Usage` and `ChildUsage` definitions.

`FailedData.exception` is optional and nullable. Its generated model is named
`Exception`; alias it on import, for example `Exception as EventException`,
to avoid shadowing Python's built-in exception class. It requires a URL-valued
`type` and accepts optional problem information including `status`, `title`,
`detail`, `instance`, `code`, and `errors`.

### GeoJSON payloads

!!! warning "Payload preservation in versions up to and including 1.3.0"

    `FeatureCollection.features` could convert STAC Item and GeoJSON Feature
    dictionaries into generated `Feature` and geometry models. Validation could
    coerce values (for example, integer coordinates into floats), and serialization
    could add default fields such as `geometry.bbox: null`. Accepting a dictionary
    did not guarantee that its JSON content would be preserved. Upgrade to 1.4.0
    or later for the preservation behavior described below.

Since 1.4.0, `FeatureCollection.features` accepts STAC Item and GeoJSON Feature
JSON objects as dictionaries. Their nested geometry, properties, assets, links,
and custom fields remain JSON data, without conversion into geometry models.
Validation and serialization preserve explicitly supplied nulls and numeric
types without adding defaults or removing fields inside each feature.

The generated module no longer provides `Feature` or the individual geometry
models. Supply feature dictionaries directly. These payloads are not validated
against STAC, GeoJSON geometry, or geospatial topology rules. Preservation refers
to JSON content, not original whitespace or byte formatting.

## Serialization

The endpoint sends `event.model_dump(mode="json")`. Datetimes and enums become
JSON-compatible values. Default values, `None` values, and allowed extra fields
are included; the sender does not use `exclude_none` or `exclude_unset`.

The event envelope is serialized around the preserved feature dictionaries.
Envelope defaults do not add fields inside those dictionaries. Do not apply a
global `exclude_none=True` as a workaround for older versions: it can remove
explicit nulls from model fields and cannot undo coercion during validation.

## Routing

The schema's `X-Kafka-Topic` pattern is:

```text
^[^.]+\.[^.]+\.(\d+[hmsd]\.calendar|prepared|submitted|completed|failed|piped|staged|dismissed|ordered)$
```

Examples are `workflows.demo-001.submitted` and
`workflows.demo-001.10m.calendar`. The first two components cannot contain dots.
The calendar duration uses digits followed by `h`, `m`, `s`, or `d`.

The OpenAPI parameter is required. In contrast, `x_kafka_topic=None` and omission
of CLI `--x-kafka-topic` omit the per-request header. The client does not validate
the topic pattern or infer a topic from the event. A shared HTTPX header can
still supply a value. Services enforcing the schema can reject missing or
invalid topic headers.
