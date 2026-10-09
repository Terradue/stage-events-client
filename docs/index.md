# Stage Events Client

`stage-events-client` sends workflow events to the Stage Events HTTP API.
Use its Python library for synchronous or asynchronous applications, or the
optional `send-stage-event` command for shell scripts and workflow steps.
The package provides validated models for nine event types and sends them as
JSON with the `application/cloudevents+json` content type.

Python 3.10 or newer is required. Sending to a deployed service requires its
endpoint URL and, when enabled, a bearer token. The introductory tutorial runs
locally without a service or credentials.

## Choose your starting point

The documentation follows [Diátaxis](https://diataxis.fr/), separating learning,
practical tasks, technical lookup, and background understanding.

| Your goal | Start here |
| --- | --- |
| Learn by constructing and sending an event locally | [Tutorials](tutorials/index.md) |
| Send real events, configure a client, or contribute changes | [How-to guides](how-to/index.md) |
| Look up command options, Python interfaces, and event fields | [Reference](reference/index.md) |
| Understand event routing, validation, and the schema workflow | [Explanation](explanation/index.md) |

## Install

For the Python library:

```console
python -m pip install stage-events-client
```

For the library and command-line interface:

```console
python -m pip install 'stage-events-client[cli]'
```

The client publishes events over HTTP. It does not provide an event receiver,
Kafka consumer, workflow scheduler, or service deployment.
