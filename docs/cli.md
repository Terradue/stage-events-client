# CLI reference

The optional `stage-events-client[cli]` extra provides `send-stage-event`.
For complete examples, see [send events from the command line](how-to/send-from-cli.md).

## Invocation

```text
send-stage-event [--version] [-h | --help]
send-stage-event COMMAND URL [OPTIONS]
```

`URL` must be an absolute HTTP or HTTPS URL with no fragment. Its path and query
string are preserved; an empty path becomes `/`. No endpoint path is appended.

## Commands

| Command | Event model | Event type |
| --- | --- | --- |
| `calendar` | `CalendarCloudEvent` | `calendar-event` |
| `submitted` | `SubmittedCloudEvent` | `submitted` |
| `dismissed` | `DismissedCloudEvent` | `dismissed` |
| `prepared` | `PreparedCloudEvent` | `prepared` |
| `completed` | `CompletedCloudEvent` | `completed` |
| `failed` | `FailedCloudEvent` | `failed` |
| `piped` | `PipedCloudEvent` | `piped` |
| `staged` | `StagedCloudEvent` | `staged` |
| `ordered` | `OrderedCloudEvent` | `ordered` |

All commands share the options below. Each validates its data against the
corresponding [event data model](reference/events.md#event-data).

## Options

| Option | Required | Default | Meaning |
| --- | --- | --- | --- |
| `--source TEXT` | Yes | — | Three nonempty colon-separated components. |
| `--subject TEXT` | Yes | — | Three nonempty colon-separated components. |
| `--data JSON\|@FILE\|-` | Yes | — | Data object as inline JSON, a UTF-8 JSON file, or stdin. |
| `--partition-key TEXT` | No | Subject | Grouping key; an empty value also falls back to the subject. |
| `--x-kafka-topic TEXT` | No | Omitted | Per-request topic header; see the contract distinction below. |
| `--token TEXT` | No | `STAGE_EVENTS_TOKEN` | Token without `Bearer`; explicit option takes precedence. |
| `--timeout FLOAT` | No | `30.0` | Positive HTTPX timeout in seconds. |
| `--verify-ssl / --no-verify-ssl` | No | Verification enabled | Whether to verify the server TLS certificate. |
| `-h / --help` | No | — | Show help and exit. |

`--data` must resolve to an object, not an array or scalar. It contains the
payload fields, not the CloudEvent envelope. The command determines `type`,
`specversion` defaults to `1.0`, and `datacontenttype` to `application/json`.
There are no CLI options for an event ID, arbitrary envelope extensions,
custom authentication schemes, redirect following, or a CA bundle path.

`X-Kafka-Topic` is optional in the CLI but required by the checked-in OpenAPI
contract. Its pattern is not validated locally. See [routing](reference/events.md#routing).
TLS verification should remain enabled for production requests.

## Environment variables

`STAGE_EVENTS_TOKEN` is the CLI's token fallback. A nonempty token causes the
request to carry `Authorization: Bearer TOKEN`. Without one, the CLI uses the
unauthenticated client. There is no CLI environment-variable setting for the
endpoint URL or topic.

## Output and exit status

| Outcome | Output | Exit status |
| --- | --- | --- |
| HTTP 200 | Response text on stdout when nonempty | `0` |
| Usage, URL, JSON, file-input, or option error | Diagnostic on stderr | `2` |
| Event model validation error | Validation diagnostic on stderr | `1` |
| HTTPX failure or unexpected HTTP status | Diagnostic on stderr | `1` |
| Valid documented HTTP 400 problem | Formatted problem JSON on stderr | `1` |

The CLI enables `raise_on_unexpected_status=True`. Even other 2xx statuses,
including 201 and 204, fail before the CLI's success branch. Malformed HTTP 400
bodies can raise unhandled parsing exceptions rather than a formatted diagnostic.
See [diagnose failed requests](how-to/handle-errors.md).
