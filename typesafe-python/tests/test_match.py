import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import httpx2
from pydantic import BaseModel
from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

from main import JevLib


class MatchResponse(BaseModel):
    selected: str


def make_jevlib() -> JevLib:
    jevlib = JevLib.__new__(JevLib)
    jevlib.client = Mock(spec=TypeSafeClient)
    return jevlib


class TestJevLibMatch(unittest.TestCase):
    def test_returns_selected_label(self):
        jevlib = make_jevlib()
        jevlib.client.system_one.return_value = SimpleNamespace(
            choices={"match": SimpleNamespace(choice="returns")},
        )

        selected = jevlib.match(
            "My shoes arrived in the wrong size.",
            "Which team should handle this?",
            {
                "returns": "Exchanges and wrong items",
                "shipping": "Delivery status and delays",
            },
        )

        self.assertEqual(selected, "returns")

    def test_builds_choice_and_forwards_system_one_options(self):
        jevlib = make_jevlib()
        jevlib.client.system_one.return_value = SimpleNamespace(
            choices={"match": SimpleNamespace(choice="shipping")},
        )
        state = {"ticket": {"message": "Where is my order?"}}
        question = {"task": "Choose the responsible team"}
        criteria = {
            "returns": {"applies_to": ["exchanges", "wrong items"]},
            "shipping": None,
        }
        retry = RetryPolicy(max_retries=0)
        timeout = httpx2.Timeout(5.0)
        extra_headers = {"x-trace-id": "match-test"}
        extra_body = {"metadata": {"source": "unit-test"}}

        selected = jevlib.match(
            state,
            question,
            criteria,
            model="jev-latest",
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )

        self.assertEqual(selected, "shipping")
        jevlib.client.system_one.assert_called_once_with(
            state,
            {
                "match": Choice(
                    instructions=question,
                    criteria=criteria,
                ),
            },
            model="jev-latest",
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
            response_model=None,
        )

    def test_returns_custom_response_model_unchanged(self):
        jevlib = make_jevlib()
        response = MatchResponse(selected="returns")
        jevlib.client.system_one.return_value = response

        result = jevlib.match(
            "I need a different size.",
            "Which team should handle this?",
            {"returns": "Exchanges", "shipping": "Delivery questions"},
            response_model=MatchResponse,
        )

        self.assertIs(result, response)
        self.assertIs(
            jevlib.client.system_one.call_args.kwargs["response_model"],
            MatchResponse,
        )


if __name__ == "__main__":
    unittest.main()
