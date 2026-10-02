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
from datetime import datetime, timezone

from pydantic import ValidationError

from stage_events_client.models import (
    CalendarCloudEvent,
    Feature,
    FeatureCollection,
    Point,
    PreparedData,
    SubmittedCloudEvent,
)


class CloudEventModelTests(unittest.TestCase):
    def test_submitted_event_accepts_extra_cloud_event_attributes(self) -> None:
        event = SubmittedCloudEvent.model_validate(
            {
                "source": "namespace:process:step",
                "subject": "namespace:workflow-id:workflow-name",
                "partitionkey": "namespace:workflow-id:workflow-name",
                "specversion": "1.0",
                "id": "event-id",
                "data": {
                    "namespace": "namespace",
                    "time": "2026-07-17T12:00:00Z",
                },
            }
        )

        self.assertEqual(event.type, "submitted")
        self.assertEqual(event.data.time, datetime(2026, 7, 17, 12, tzinfo=timezone.utc))
        self.assertEqual(event.model_dump()["specversion"], "1.0")

    def test_source_and_subject_must_have_three_colon_separated_parts(self) -> None:
        with self.assertRaises(ValidationError):
            SubmittedCloudEvent.model_validate(
                {
                    "source": "not-a-valid-source",
                    "subject": "namespace:id:name",
                    "partitionkey": "namespace:id:name",
                    "data": {"namespace": "namespace"},
                }
            )

    def test_calendar_event_requires_timezone_aware_datetimes(self) -> None:
        common = {
            "source": "namespace:process:step",
            "subject": "namespace:id:name",
            "partitionkey": "namespace:id:name",
            "data": {
                "namespace": "namespace",
                "event_time": "2026-07-17T12:00:00",
                "start_time": "2026-07-17T12:00:00Z",
                "end_time": "2026-07-17T13:00:00Z",
            },
        }

        with self.assertRaises(ValidationError):
            CalendarCloudEvent.model_validate(common)

    def test_process_version_must_be_semantic_version(self) -> None:
        valid = PreparedData(
            namespace="namespace",
            process_id="processor",
            process_version="1.2.3-rc.1+build.4",
            job_id="job-id",
            inputs={},
        )
        self.assertEqual(valid.process_version, "1.2.3-rc.1+build.4")

        with self.assertRaises(ValidationError):
            PreparedData(
                namespace="namespace",
                process_id="processor",
                process_version="1.2",
                job_id="job-id",
                inputs={},
            )

    def test_geojson_models_validate_and_serialize_nested_geometry(self) -> None:
        collection = FeatureCollection(
            features=[
                Feature(
                    properties={"title": "result"},
                    geometry=Point(coordinates=[12.5, 41.9]),
                )
            ]
        )

        dumped = collection.model_dump()
        self.assertEqual(dumped["type"], "FeatureCollection")
        self.assertEqual(dumped["features"][0]["geometry"]["type"], "Point")
        self.assertEqual(dumped["features"][0]["geometry"]["coordinates"], [12.5, 41.9])


if __name__ == "__main__":
    unittest.main()
