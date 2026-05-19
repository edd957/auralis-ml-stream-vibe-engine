from collections import deque
from datetime import UTC, datetime, timedelta
from typing import Protocol

from redis import Redis

from auralis_ml.models import ChatMessage


class ChatBuffer(Protocol):
    def push(self, message: ChatMessage) -> None: ...

    def recent(self, window_seconds: int) -> list[ChatMessage]: ...


class InMemoryChatBuffer:
    def __init__(self, max_messages: int = 10_000) -> None:
        self._messages: deque[ChatMessage] = deque(maxlen=max_messages)

    def push(self, message: ChatMessage) -> None:
        self._messages.append(message)

    def recent(self, window_seconds: int) -> list[ChatMessage]:
        cutoff = datetime.now(UTC) - timedelta(seconds=window_seconds)
        return [message for message in self._messages if message.timestamp >= cutoff]


class RedisChatBuffer:
    def __init__(self, redis_url: str, key: str = "auralis:chat") -> None:
        self._redis = Redis.from_url(redis_url, decode_responses=True)
        self._key = key

    def push(self, message: ChatMessage) -> None:
        encoded = message.model_dump_json()
        self._redis.zadd(self._key, {encoded: message.timestamp.timestamp()})

    def recent(self, window_seconds: int) -> list[ChatMessage]:
        now = datetime.now(UTC).timestamp()
        cutoff = now - window_seconds
        self._redis.zremrangebyscore(self._key, 0, cutoff)
        rows = self._redis.zrangebyscore(self._key, cutoff, now)
        return [ChatMessage.model_validate_json(row) for row in rows]


def create_chat_buffer(redis_url: str | None) -> ChatBuffer:
    if redis_url:
        return RedisChatBuffer(redis_url)
    return InMemoryChatBuffer()
