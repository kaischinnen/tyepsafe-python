import os
from collections.abc import Mapping
from types import TracebackType
from typing import Self, TypeVar, overload

import httpx2
from pydantic import BaseModel

from typesafe_sdk import (
    Choice,
    JSONContent,
    JSONValue,
    Noul,
    RetryPolicy,
    TypeSafeClient,
)


ResponseT = TypeVar("ResponseT", bound=BaseModel)


class JevLib:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        headers: Mapping[str, str] | None = None,
        transport: httpx2.BaseTransport | None = None,
        http_client: httpx2.Client | None = None,
        base_url: str | None = None,
    ) -> None:
        self.setup_api_key(api_key)
        self.setup_client(
            model=model,
            retry=retry,
            timeout=timeout,
            headers=headers,
            transport=transport,
            http_client=http_client,
            base_url=base_url,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.client.close()

    def setup_client(
        self,
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        headers: Mapping[str, str] | None = None,
        transport: httpx2.BaseTransport | None = None,
        http_client: httpx2.Client | None = None,
        base_url: str | None = None,
    ) -> None:
        self.client = TypeSafeClient(
            api_key=self.TYPESAFE_API_KEY,
            model=model,
            retry=retry,
            timeout=timeout,
            headers=headers,
            transport=transport,
            http_client=http_client,
            base_url=base_url,
        )

    def setup_api_key(self, api_key: str | None = None) -> None:
        if api_key is not None:
            self.TYPESAFE_API_KEY = api_key
            return

        try:
            self.TYPESAFE_API_KEY = os.environ["TYPESAFE_API_KEY"]
        except KeyError:
            raise RuntimeError("Missing required environment variable: $TYPESAFE_API_KEY") from None

    def feels(
        self,
        state: JSONContent,
        question: str,
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
    ) -> float:
        result = self.client.system_one(
            state,
            {
                "feels": Noul(instructions=question),
            },
            model=model,
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )

        return result.nouls["feels"].noul

    @overload
    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: None = None,
    ) -> str: ...

    @overload
    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: type[ResponseT],
    ) -> ResponseT: ...

    def match(
        self,
        state: JSONContent,
        question: JSONContent,
        criteria: Mapping[str, JSONContent | None],
        *,
        model: str | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | httpx2.Timeout | None = None,
        extra_headers: Mapping[str, str] | None = None,
        extra_body: Mapping[str, JSONValue | None] | None = None,
        response_model: type[ResponseT] | None = None,
    ) -> str | ResponseT:
        """Select the criterion that best matches ``state``.

        The selected criterion name is returned by default. When ``response_model``
        is supplied, the custom parsed response is returned unchanged.
        """
        questions = {
            "match": Choice(instructions=question, criteria=criteria),
        }

        if response_model is not None:
            return self.client.system_one(
                state,
                questions,
                model=model,
                retry=retry,
                timeout=timeout,
                extra_headers=extra_headers,
                extra_body=extra_body,
                response_model=response_model,
            )

        result = self.client.system_one(
            state,
            questions,
            model=model,
            retry=retry,
            timeout=timeout,
            extra_headers=extra_headers,
            extra_body=extra_body,
            response_model=None,
        )

        return result.choices["match"].choice
