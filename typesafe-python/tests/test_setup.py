import os
import unittest
from unittest.mock import Mock, patch

import httpx2

from main import JevLib


def make_http_client():
    client = Mock(spec=httpx2.Client)
    client.timeout = 10.0 
    return client


class TestJevLibContextManager(unittest.TestCase):
    @patch.dict(os.environ, {"TEST_TYPESAFE_API_KEY": "test-key"})
    def test_closes_client_after_context(self):
        http_client = make_http_client()

        with JevLib(
            api_key="TEST_TYPESAFE_API_KEY",
            http_client=http_client,
        ) as jevlib:
            self.assertIsInstance(jevlib, JevLib)
            http_client.close.assert_not_called()

        http_client.close.assert_called_once_with()

    @patch.dict(os.environ, {"TEST_TYPESAFE_API_KEY": "test-key"})
    def test_closes_client_after_exception(self):
        http_client = make_http_client()

        with self.assertRaisesRegex(RuntimeError, "failed!"):
            with JevLib(
                api_key="TEST_TYPESAFE_API_KEY",
                http_client=http_client,
            ):
                raise RuntimeError("failed!")

        http_client.close.assert_called_once_with()

    @patch.dict(os.environ, {}, clear=True)
    def test_rejects_missing_api_key_environment_variable(self):
        with self.assertRaisesRegex(
            RuntimeError,
            r"Missing required environment variable: \$MISSING_API_KEY",
        ):
            JevLib(api_key="MISSING_API_KEY")

    @patch.dict(os.environ, {"EMPTY_API_KEY": "   "})
    def test_rejects_empty_api_key_environment_variable(self):
        with self.assertRaisesRegex(
            RuntimeError,
            r"Required environment variable is empty: \$EMPTY_API_KEY",
        ):
            JevLib(api_key="EMPTY_API_KEY")


if __name__ == "__main__":
    unittest.main()
