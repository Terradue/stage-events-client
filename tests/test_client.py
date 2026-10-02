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

import httpx

from stage_events_client.client import AuthenticatedClient, Client


class ClientTests(unittest.TestCase):
    def test_client_builds_httpx_client_from_configuration(self) -> None:
        transport = httpx.MockTransport(lambda request: httpx.Response(200, request=request))
        client = Client(
            base_url="https://events.example.test/api",
            headers={"X-Default": "value"},
            cookies={"session": "cookie"},
            follow_redirects=True,
            httpx_args={"transport": transport},
        )

        httpx_client = client.get_httpx_client()
        self.assertIs(httpx_client, client.get_httpx_client())
        self.assertEqual(httpx_client.base_url, httpx.URL("https://events.example.test/api/"))
        self.assertEqual(httpx_client.headers["X-Default"], "value")
        self.assertEqual(httpx_client.cookies["session"], "cookie")
        self.assertTrue(httpx_client.follow_redirects)
        httpx_client.close()

    def test_authenticated_client_adds_bearer_token(self) -> None:
        client = AuthenticatedClient(base_url="https://events.example.test", token="secret")
        httpx_client = client.get_httpx_client()

        self.assertEqual(httpx_client.headers["Authorization"], "Bearer secret")
        httpx_client.close()

    def test_authenticated_client_supports_unprefixed_custom_header(self) -> None:
        client = AuthenticatedClient(
            base_url="https://events.example.test",
            token="api-key",
            prefix="",
            auth_header_name="X-API-Key",
        )
        httpx_client = client.get_httpx_client()

        self.assertEqual(httpx_client.headers["X-API-Key"], "api-key")
        httpx_client.close()

    def test_with_methods_return_updated_clients(self) -> None:
        original = Client(
            base_url="https://events.example.test",
            headers={"A": "one"},
            cookies={"first": "one"},
        )

        updated = original.with_headers({"B": "two"}).with_cookies({"second": "two"})

        self.assertIsNot(updated, original)
        self.assertEqual(updated._headers, {"A": "one", "B": "two"})
        self.assertEqual(updated._cookies, {"first": "one", "second": "two"})


class AsyncClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_authenticated_client_adds_token(self) -> None:
        client = AuthenticatedClient(base_url="https://events.example.test", token="secret")
        httpx_client = client.get_async_httpx_client()

        self.assertIs(httpx_client, client.get_async_httpx_client())
        self.assertEqual(httpx_client.headers["Authorization"], "Bearer secret")
        await httpx_client.aclose()


if __name__ == "__main__":
    unittest.main()
