# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Send structured CloudEvents and validate API responses."""

from http import HTTPStatus
from typing import Annotated, Any

import httpx
from eoap_problems_registry import (
    BadRequest,
    InvalidBodyPropertyFormat,
    InvalidBodyPropertyValue,
    InvalidParameters,
    InvalidRequestHeaderFormat,
    InvalidRequestParameterFormat,
    InvalidRequestParameterValue,
    MissingBodyProperty,
    MissingRequestHeader,
    MissingRequestParameter,
)
from pydantic import Field, TypeAdapter

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models import (
    CalendarCloudEvent,
    CompletedCloudEvent,
    DismissedCloudEvent,
    FailedCloudEvent,
    OrderedCloudEvent,
    PipedCloudEvent,
    PreparedCloudEvent,
    StagedCloudEvent,
    SubmittedCloudEvent,
)
from ...types import Response


def _get_kwargs(
    *,
    body: CalendarCloudEvent
    | CompletedCloudEvent
    | DismissedCloudEvent
    | FailedCloudEvent
    | OrderedCloudEvent
    | PipedCloudEvent
    | PreparedCloudEvent
    | StagedCloudEvent
    | SubmittedCloudEvent,
    x_kafka_topic: str | None,
    path: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if x_kafka_topic is not None:
        headers["X-Kafka-Topic"] = x_kafka_topic

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": path,
    }

    _kwargs["json"] = body.model_dump(mode="json")

    headers["Content-Type"] = "application/cloudevents+json"

    _kwargs["headers"] = headers
    return _kwargs


ProblemResponse = (
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
)


def _parse_response_400(data: object) -> ProblemResponse:
    """Validate a problem response against the documented models in order.

    Raises:
        TypeError: If the response is not a JSON object.
        ValueError: If no documented problem model accepts the response.
    """
    if not isinstance(data, dict):
        raise TypeError()

    response_adapter: TypeAdapter[ProblemResponse] = TypeAdapter(
        Annotated[ProblemResponse, Field(union_mode="left_to_right")]
    )
    return response_adapter.validate_python(data)


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
    | None
):
    if response.status_code == 200:
        return response.text

    if response.status_code == 400:
        return _parse_response_400(response.json())

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CalendarCloudEvent
    | CompletedCloudEvent
    | DismissedCloudEvent
    | FailedCloudEvent
    | OrderedCloudEvent
    | PipedCloudEvent
    | PreparedCloudEvent
    | StagedCloudEvent
    | SubmittedCloudEvent,
    x_kafka_topic: str | None = None,
    path: str = "/cloud-events",
) -> Response[
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
]:
    """Send CloudEvent.

     Sends a structured-mode CloudEvent.

    For more information, see [CloudEvents - Version
    1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

    Args:
        x_kafka_topic (str | None): Optional Kafka topic sent in the
            ``X-Kafka-Topic`` request header.
        body (CalendarCloudEvent | CompletedCloudEvent | DismissedCloudEvent | FailedCloudEvent |
            OrderedCloudEvent | PipedCloudEvent | PreparedCloudEvent | StagedCloudEvent |
            SubmittedCloudEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequest | InvalidBodyPropertyFormat | InvalidBodyPropertyValue | InvalidParameters | InvalidRequestHeaderFormat | InvalidRequestParameterFormat | InvalidRequestParameterValue | MissingBodyProperty | MissingRequestHeader | MissingRequestParameter | str]
    """

    kwargs = _get_kwargs(body=body, x_kafka_topic=x_kafka_topic, path=path)

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CalendarCloudEvent
    | CompletedCloudEvent
    | DismissedCloudEvent
    | FailedCloudEvent
    | OrderedCloudEvent
    | PipedCloudEvent
    | PreparedCloudEvent
    | StagedCloudEvent
    | SubmittedCloudEvent,
    x_kafka_topic: str | None = None,
) -> (
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
    | None
):
    """Send CloudEvent.

     Sends a structured-mode CloudEvent.

    For more information, see [CloudEvents - Version
    1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

    Args:
        x_kafka_topic (str | None): Optional Kafka topic sent in the
            ``X-Kafka-Topic`` request header.
        body (CalendarCloudEvent | CompletedCloudEvent | DismissedCloudEvent | FailedCloudEvent |
            OrderedCloudEvent | PipedCloudEvent | PreparedCloudEvent | StagedCloudEvent |
            SubmittedCloudEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequest | InvalidBodyPropertyFormat | InvalidBodyPropertyValue | InvalidParameters | InvalidRequestHeaderFormat | InvalidRequestParameterFormat | InvalidRequestParameterValue | MissingBodyProperty | MissingRequestHeader | MissingRequestParameter | str
    """

    return sync_detailed(
        client=client,
        body=body,
        x_kafka_topic=x_kafka_topic,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CalendarCloudEvent
    | CompletedCloudEvent
    | DismissedCloudEvent
    | FailedCloudEvent
    | OrderedCloudEvent
    | PipedCloudEvent
    | PreparedCloudEvent
    | StagedCloudEvent
    | SubmittedCloudEvent,
    x_kafka_topic: str | None = None,
    path: str = "/cloud-events",
) -> Response[
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
]:
    """Send CloudEvent.

     Sends a structured-mode CloudEvent.

    For more information, see [CloudEvents - Version
    1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

    Args:
        x_kafka_topic (str | None): Optional Kafka topic sent in the
            ``X-Kafka-Topic`` request header.
        body (CalendarCloudEvent | CompletedCloudEvent | DismissedCloudEvent | FailedCloudEvent |
            OrderedCloudEvent | PipedCloudEvent | PreparedCloudEvent | StagedCloudEvent |
            SubmittedCloudEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BadRequest | InvalidBodyPropertyFormat | InvalidBodyPropertyValue | InvalidParameters | InvalidRequestHeaderFormat | InvalidRequestParameterFormat | InvalidRequestParameterValue | MissingBodyProperty | MissingRequestHeader | MissingRequestParameter | str]
    """

    kwargs = _get_kwargs(body=body, x_kafka_topic=x_kafka_topic, path=path)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CalendarCloudEvent
    | CompletedCloudEvent
    | DismissedCloudEvent
    | FailedCloudEvent
    | OrderedCloudEvent
    | PipedCloudEvent
    | PreparedCloudEvent
    | StagedCloudEvent
    | SubmittedCloudEvent,
    x_kafka_topic: str | None = None,
) -> (
    BadRequest
    | InvalidBodyPropertyFormat
    | InvalidBodyPropertyValue
    | InvalidParameters
    | InvalidRequestHeaderFormat
    | InvalidRequestParameterFormat
    | InvalidRequestParameterValue
    | MissingBodyProperty
    | MissingRequestHeader
    | MissingRequestParameter
    | str
    | None
):
    """Send CloudEvent.

     Sends a structured-mode CloudEvent.

    For more information, see [CloudEvents - Version
    1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

    Args:
        x_kafka_topic (str | None): Optional Kafka topic sent in the
            ``X-Kafka-Topic`` request header.
        body (CalendarCloudEvent | CompletedCloudEvent | DismissedCloudEvent | FailedCloudEvent |
            OrderedCloudEvent | PipedCloudEvent | PreparedCloudEvent | StagedCloudEvent |
            SubmittedCloudEvent):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BadRequest | InvalidBodyPropertyFormat | InvalidBodyPropertyValue | InvalidParameters | InvalidRequestHeaderFormat | InvalidRequestParameterFormat | InvalidRequestParameterValue | MissingBodyProperty | MissingRequestHeader | MissingRequestParameter | str
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            x_kafka_topic=x_kafka_topic,
        )
    ).parsed
