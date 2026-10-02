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

import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from stage_events_client.cli import EVENT_MODELS, main
from stage_events_client.client import AuthenticatedClient, Client
from stage_events_client.models import SubmittedCloudEvent
from stage_events_client.types import Response


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_exposes_one_command_per_cloud_event_model(self) -> None:
        result = self.runner.invoke(main, ["--help"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(set(main.commands), set(EVENT_MODELS))
        for command_name in EVENT_MODELS:
            self.assertIn(command_name, result.output)

    @patch("stage_events_client.cli.send_cloud_event.sync_detailed")
    def test_submitted_accepts_complete_url_and_sends_event(self, send: MagicMock) -> None:
        send.return_value = Response(
            status_code=HTTPStatus.OK,
            content=b"accepted",
            headers={},
            parsed="accepted",
        )

        result = self.runner.invoke(
            main,
            [
                "submitted",
                "https://events.example.test/hooks/cloud-events?tenant=demo",
                "--source",
                "namespace:process:step",
                "--subject",
                "namespace:workflow-id:workflow-name",
                "--data",
                '{"namespace": "namespace", "time": "2026-07-18T12:00:00Z"}',
                "--x-kafka-topic",
                "namespace.workflow-id.submitted",
            ],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, "accepted\n")
        kwargs = send.call_args.kwargs
        self.assertIsInstance(kwargs["client"], Client)
        self.assertEqual(kwargs["client"]._base_url, "https://events.example.test")
        self.assertEqual(kwargs["path"], "/hooks/cloud-events?tenant=demo")
        self.assertIsInstance(kwargs["body"], SubmittedCloudEvent)
        self.assertEqual(kwargs["body"].partitionkey, kwargs["body"].subject)
        self.assertEqual(kwargs["x_kafka_topic"], "namespace.workflow-id.submitted")

    @patch("stage_events_client.cli.send_cloud_event.sync_detailed")
    def test_token_uses_authenticated_client_and_topic_is_optional(self, send: MagicMock) -> None:
        send.return_value = Response(
            status_code=HTTPStatus.OK,
            content=b"",
            headers={},
            parsed="",
        )

        result = self.runner.invoke(
            main,
            [
                "submitted",
                "https://events.example.test/cloud-events",
                "--source",
                "namespace:process:step",
                "--subject",
                "namespace:workflow-id:workflow-name",
                "--data",
                '{"namespace": "namespace"}',
                "--token",
                "secret",
            ],
        )

        self.assertEqual(result.exit_code, 0, result.output)
        kwargs = send.call_args.kwargs
        self.assertIsInstance(kwargs["client"], AuthenticatedClient)
        self.assertEqual(kwargs["x_kafka_topic"], None)

    def test_rejects_relative_url(self) -> None:
        result = self.runner.invoke(
            main,
            [
                "submitted",
                "/cloud-events",
                "--source",
                "namespace:process:step",
                "--subject",
                "namespace:workflow-id:workflow-name",
                "--data",
                '{"namespace": "namespace"}',
            ],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("absolute HTTP or HTTPS URL", result.output)

    def test_rejects_non_object_data(self) -> None:
        result = self.runner.invoke(
            main,
            [
                "submitted",
                "https://events.example.test/cloud-events",
                "--source",
                "namespace:process:step",
                "--subject",
                "namespace:workflow-id:workflow-name",
                "--data",
                "[]",
            ],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("must contain a JSON object", result.output)


if __name__ == "__main__":
    unittest.main()
