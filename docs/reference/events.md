# Event model reference

Import event and data models from `stage_events_client.models`. These Pydantic
v2 classes are generated from the schema bundle. The tables describe their
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

The generated module includes `FeatureCollection`, `Feature`, `Point`,
`LineString`, `Polygon`, `MultiPoint`, `MultiLineString`, `MultiPolygon`, and
`GeometryCollection`. Coordinate lengths and geometry literals have generated
constraints. A `Feature` requires `properties` and `geometry` keys, although
both may be null.

`FeatureCollection.features` also accepts dictionaries, so acceptance of a
collection does not guarantee that every feature has passed strict geometry
validation. These models do not provide complete STAC or geospatial topology
validation.

## Serialization

The endpoint sends `event.model_dump(mode="json")`. Datetimes and enums become
JSON-compatible values. Default values, `None` values, and allowed extra fields
are included; the sender does not use `exclude_none` or `exclude_unset`.

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
