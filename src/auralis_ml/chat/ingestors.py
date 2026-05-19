import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from auralis_ml.models import ChatMessage, Platform


class DemoIngestor:
    """Deterministic chat source used for demos, tests, and local development."""

    def __init__(self, interval_seconds: float = 1.0) -> None:
        self.interval_seconds = interval_seconds
        self._messages = (
            "smooth start, keep it chill",
            "nice transition",
            "chat is waking up",
            "this drop is wild",
            "go faster, the room is on fire",
            "massive energy right now",
        )

    async def stream(self) -> AsyncIterator[ChatMessage]:
        index = 0
        while True:
            yield ChatMessage(
                author=f"demo_user_{index % 8}",
                message=self._messages[index % len(self._messages)],
                platform=Platform.demo,
                timestamp=datetime.now(UTC),
            )
            index += 1
            await asyncio.sleep(self.interval_seconds)


class YouTubePytchatIngestor:
    def __init__(self, video_id: str) -> None:
        self.video_id = video_id

    async def stream(self) -> AsyncIterator[ChatMessage]:
        try:
            import pytchat
        except ImportError as exc:
            raise RuntimeError("Install the chat extra to use YouTube ingestion.") from exc

        chat = pytchat.create(video_id=self.video_id)
        while chat.is_alive():
            for item in chat.get().sync_items():
                yield ChatMessage(
                    author=item.author.name,
                    message=item.message,
                    platform=Platform.youtube,
                    timestamp=datetime.now(UTC),
                )
            await asyncio.sleep(1)


class TwitchIrcIngestor:
    def __init__(self, channel: str, nick: str, token: str) -> None:
        self.channel = channel.lstrip("#")
        self.nick = nick
        self.token = token

    async def stream(self) -> AsyncIterator[ChatMessage]:
        try:
            import websockets
        except ImportError as exc:
            raise RuntimeError("Install the chat extra to use Twitch ingestion.") from exc

        uri = "wss://irc-ws.chat.twitch.tv:443"
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"PASS {self.token}")
            await websocket.send(f"NICK {self.nick}")
            await websocket.send(f"JOIN #{self.channel}")

            async for raw in websocket:
                if raw.startswith("PING"):
                    await websocket.send("PONG :tmi.twitch.tv")
                    continue
                if "PRIVMSG" not in raw:
                    continue
                author = raw.split("!", 1)[0].lstrip(":")
                message = raw.split("PRIVMSG", 1)[1].split(":", 1)[-1].strip()
                yield ChatMessage(
                    author=author,
                    message=message,
                    platform=Platform.twitch,
                    timestamp=datetime.now(UTC),
                )
