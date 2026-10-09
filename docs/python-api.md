# Python API reference

Import clients from `stage_events_client`, event models from
`stage_events_client.models`, and sending functions from
`stage_events_client.api.default.send_cloud_event`.
For complete examples, see [use the Python client](how-to/use-python.md).

## Clients

`Client` sends unauthenticated requests. `AuthenticatedClient` adds an
authentication header when constructing its HTTPX client.

| Constructor argument | Default | Meaning |
| --- | --- | --- |
| `base_url` | Required | HTTPX base URL for endpoint paths. |
| `headers` | Empty dictionary | Shared request headers. |
| `cookies` | Empty dictionary | Shared cookies. |
| `timeout` | `None` | `httpx.Timeout` or `None`; the default disables timeouts. |
| `verify_ssl` | `True` | Boolean, CA bundle path, or `ssl.SSLContext`. |
| `follow_redirects` | `False` | Follow HTTP redirects. |
| `httpx_args` | Empty dictionary | Additional HTTPX constructor keyword arguments. |
| `raise_on_unexpected_status` | `False` | Raise on statuses other than documented 200 and 400. |

`AuthenticatedClient` additionally accepts:

| Argument | Default | Meaning |
| --- | --- | --- |
| `token` | Required | Credential value. |
| `prefix` | `"Bearer"` | Authentication scheme; empty string sends the token alone. |
| `auth_header_name` | `"Authorization"` | Header used for authentication. |

The Python API does not load tokens or URLs from environment variables.

### Lifecycle and configuration methods

| Method | Behavior |
| --- | --- |
| `get_httpx_client()` | Lazily create or return the cached synchronous HTTPX client. |
| `get_async_httpx_client()` | Lazily create or return the cached asynchronous HTTPX client. |
| `set_httpx_client(client)` | Install a synchronous HTTPX client and return the wrapper. |
| `set_async_httpx_client(async_client)` | Install an asynchronous HTTPX client and return the wrapper. |
| `with_headers(headers)` | Return a new wrapper with merged headers. |
| `with_cookies(cookies)` | Return a new wrapper with merged cookies. |
| `with_timeout(timeout)` | Return a new wrapper with the supplied timeout. |

The `with_*` methods also update already-created HTTPX clients on the original
wrapper. They are not side-effect-free copies. Prefer configuring a client
before opening its context.

Use `with client:` or `async with client:` to manage connection resources.
Exiting closes the corresponding HTTPX client. Do not re-enter a closed client;
create a fresh wrapper. Injected HTTPX clients must supply their own base URL,
authentication, and HTTP settings because injection bypasses wrapper
configuration. The wrapper context also manages their lifecycle.

## Endpoint functions

All arguments are keyword-only. Each function posts a supported CloudEvent with
`Content-Type: application/cloudevents+json` and serializes the body using
`model_dump(mode="json")`.

| Function | Return | Custom `path` argument |
| --- | --- | --- |
| `sync` | Parsed value | No |
| `sync_detailed` | `Response` | Yes |
| `asyncio` | Awaitable yielding the parsed value | No |
| `asyncio_detailed` | Awaitable yielding `Response` | Yes |

| Argument | Required | Default | Meaning |
| --- | --- | --- | --- |
| `client` | Yes | — | `Client` or `AuthenticatedClient`. |
| `body` | Yes | — | One of the nine [CloudEvent models](reference/events.md#event-data). |
| `x_kafka_topic` | No | `None` | Per-request topic header; omitted when `None`. |
| `path` | Detailed functions only | `/cloud-events` | Request path, optionally including a query string. |

The topic is forwarded without local pattern validation. The OpenAPI marks it
required despite its optional Python signature; see [routing](reference/events.md#routing).

## Responses and exceptions

`stage_events_client.types.Response` contains:

| Attribute | Value |
| --- | --- |
| `status_code` | `http.HTTPStatus`. |
| `content` | Raw response bytes. |
| `headers` | HTTP response headers. |
| `parsed` | Text, a documented problem model, or `None`. |

| Response | Parsed result |
| --- | --- |
| HTTP 200 | Response text, including an empty string for an empty body; no JSON decoding. |
| HTTP 400 | Validated problem model from `eoap_problems_registry`. |
| Other standard HTTP status, flag disabled | `None`. |
| Other standard HTTP status, flag enabled | Raises `stage_events_client.errors.UnexpectedStatus`. |

`UnexpectedStatus` exposes integer `status_code` and byte `content` attributes.
HTTP 400 is not raised by this flag. Its recognized problem types are:

- `BadRequest`
- `InvalidBodyPropertyFormat`
- `InvalidBodyPropertyValue`
- `InvalidParameters`
- `InvalidRequestHeaderFormat`
- `InvalidRequestParameterFormat`
- `InvalidRequestParameterValue`
- `MissingBodyProperty`
- `MissingRequestHeader`
- `MissingRequestParameter`

Import these response classes from `eoap_problems_registry`, even though the
generated models module also contains similarly named classes.

Transport exceptions propagate from HTTPX, including `httpx.TimeoutException`
and `httpx.RequestError`. Malformed 400 bodies can raise JSON decoding errors,
`TypeError`, or Pydantic `ValidationError`. A nonstandard status not represented
by `http.HTTPStatus` raises `ValueError` while building a detailed response,
regardless of the unexpected-status flag. No automatic retries are performed.

See [diagnose failed requests](how-to/handle-errors.md) for handling guidance.
