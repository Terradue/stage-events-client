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
from io import BytesIO

from stage_events_client.types import UNSET, File, Response, Unset


class SharedTypesTests(unittest.TestCase):
    def test_unset_is_falsey(self) -> None:
        self.assertIsInstance(UNSET, Unset)
        self.assertFalse(UNSET)

    def test_file_converts_to_httpx_tuple(self) -> None:
        payload = BytesIO(b"content")
        upload = File(payload=payload, file_name="result.json", mime_type="application/json")

        self.assertEqual(upload.to_tuple(), ("result.json", payload, "application/json"))

    def test_response_holds_raw_and_parsed_values(self) -> None:
        response = Response(
            status_code=HTTPStatus.OK,
            content=b"accepted",
            headers={"content-type": "text/plain"},
            parsed="accepted",
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.parsed, "accepted")


if __name__ == "__main__":
    unittest.main()
