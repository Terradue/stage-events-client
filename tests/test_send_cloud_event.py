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

import json
import unittest
from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import httpx
from eoap_problems_registry import BadRequest, MissingRequestHeader, MissingRequestParameter
from pydantic import ValidationError

from stage_events_client import errors
from stage_events_client.api.default import send_cloud_event
from stage_events_client.client import Client
from stage_events_client.models import SubmittedCloudEvent, SubmittedData


def submitted_event() -> SubmittedCloudEvent:
    return SubmittedCloudEvent(
        source="namespace:process:step",
        subject="namespace:workflow-id:workflow-name",
        partitionkey="namespace:workflow-id:workflow-name",
        data=SubmittedData(namespace="namespace", time=datetime.now(ZoneInfo("UTC"))),
    )


class SendCloudEventTests(unittest.TestCase):
    def test_sync_omits_kafka_topic_header_when_not_provided(self) -> None:
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, text="accepted", request=request)

        httpx_client = httpx.Client(
            base_url="https://events.example.test",
            transport=httpx.MockTransport(handler),
        )
        client = Client(base_url="https://events.example.test").set_httpx_client(httpx_client)

        parsed = send_cloud_event.sync(client=client, body=submitted_event())

        self.assertEqual(parsed, "accepted")
        self.assertNotIn("X-Kafka-Topic", captured[0].headers)
        httpx_client.close()

    def test_sync_sends_structured_cloud_event_and_parses_success(self) -> None:
        captured: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured.append(request)
            return httpx.Response(200, text="accepted", request=request)

        httpx_client = httpx.Client(
            base_url="https://events.example.test",
            transport=httpx.MockTransport(handler),
        )
        client = Client(base_url="https://events.example.test").set_httpx_client(httpx_client)

        response = send_cloud_event.sync_detailed(
            client=client,
            body=submitted_event(),
            x_kafka_topic="workflow-events",
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.parsed, "accepted")
        self.assertEqual(captured[0].method, "POST")
        self.assertEqual(captured[0].url.path, "/cloud-events")
        self.assertEqual(captured[0].headers["X-Kafka-Topic"], "workflow-events")
        self.assertEqual(captured[0].headers["Content-Type"], "application/cloudevents+json")
        self.assertEqual(json.loads(captured[0].content)["type"], "submitted")
        httpx_client.close()

    def test_sync_parses_documented_problem_response(self) -> None:
        problem = {
            "type": "https://eoap.github.io/problems-registry/missing-request-header",
            "status": 400,
            "title": "Missing request header",
            "detail": "The request is missing an expected HTTP request header.",
            "errors": [{"detail": "X-Kafka-Topic is required", "header": "X-Kafka-Topic"}],
        }
        transport = httpx.MockTransport(
            lambda request: httpx.Response(400, json=problem, request=request)
        )
        httpx_client = httpx.Client(base_url="https://events.example.test", transport=transport)
        client = Client(base_url="https://events.example.test").set_httpx_client(httpx_client)

        parsed = send_cloud_event.sync(
            client=client,
            body=submitted_event(),
            x_kafka_topic="workflow-events",
        )

        assert isinstance(parsed, MissingRequestHeader)
        errors = parsed.errors
        assert errors is not None
        self.assertEqual(errors[0].header, "X-Kafka-Topic")
        httpx_client.close()

    def test_sync_parses_first_and_last_documented_problem_types(self) -> None:
        for problem_type in (BadRequest, MissingRequestParameter):
            with self.subTest(problem_type=problem_type.__name__):
                problem = problem_type()
                transport = httpx.MockTransport(
                    lambda request, problem=problem: httpx.Response(
                        400, json=problem.model_dump(mode="json"), request=request
                    )
                )
                with httpx.Client(
                    base_url="https://events.example.test", transport=transport
                ) as httpx_client:
                    client = Client(base_url="https://events.example.test").set_httpx_client(
                        httpx_client
                    )
                    parsed = send_cloud_event.sync(client=client, body=submitted_event())

                self.assertIsInstance(parsed, problem_type)
                self.assertEqual(parsed, problem)

    def test_sync_rejects_invalid_problem_responses(self) -> None:
        for payload, exception_type in (
            ([], TypeError),
            ({"type": "https://example.test/unknown-problem"}, ValidationError),
        ):
            with self.subTest(payload=payload):
                transport = httpx.MockTransport(
                    lambda request, payload=payload: httpx.Response(
                        400, json=payload, request=request
                    )
                )
                with httpx.Client(
                    base_url="https://events.example.test", transport=transport
                ) as httpx_client:
                    client = Client(base_url="https://events.example.test").set_httpx_client(
                        httpx_client
                    )
                    with self.assertRaises(exception_type):
                        send_cloud_event.sync(client=client, body=submitted_event())

    def test_unexpected_status_can_return_none(self) -> None:
        response = httpx.Response(503, content=b"unavailable")
        parsed = send_cloud_event._parse_response(
            client=Client(base_url="https://events.example.test"),
            response=response,
        )
        self.assertIsNone(parsed)

    def test_unexpected_status_can_raise(self) -> None:
        response = httpx.Response(503, content=b"unavailable")

        with self.assertRaises(errors.UnexpectedStatus) as raised:
            send_cloud_event._parse_response(
                client=Client(
                    base_url="https://events.example.test",
                    raise_on_unexpected_status=True,
                ),
                response=response,
            )

        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(raised.exception.content, b"unavailable")


class AsyncSendCloudEventTests(unittest.IsolatedAsyncioTestCase):
    async def test_asyncio_sends_event_and_returns_parsed_body(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(json.loads(request.content)["type"], "submitted")
            return httpx.Response(200, text="accepted asynchronously", request=request)

        httpx_client = httpx.AsyncClient(
            base_url="https://events.example.test",
            transport=httpx.MockTransport(handler),
        )
        client = Client(base_url="https://events.example.test").set_async_httpx_client(httpx_client)

        parsed = await send_cloud_event.asyncio(
            client=client,
            body=submitted_event(),
            x_kafka_topic="workflow-events",
        )

        self.assertEqual(parsed, "accepted asynchronously")
        await httpx_client.aclose()


if __name__ == "__main__":
    unittest.main()
