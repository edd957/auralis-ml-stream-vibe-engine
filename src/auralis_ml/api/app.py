from fastapi import FastAPI

from auralis_ml import __version__
from auralis_ml.chat.buffer import create_chat_buffer
from auralis_ml.config import Settings
from auralis_ml.engine import VibeEngine
from auralis_ml.models import ChatMessage, EnergyScore, FfmpegPlan, VibeProfile
from auralis_ml.nlp.sentiment import SentimentEnergyAnalyzer


def create_app() -> FastAPI:
    settings = Settings()
    buffer = create_chat_buffer(settings.redis_url)
    analyzer = SentimentEnergyAnalyzer(
        model_name=settings.sentiment_model,
        window_seconds=settings.window_seconds,
        enable_transformers=settings.enable_transformers,
    )
    engine = VibeEngine()

    app = FastAPI(
        title="Auralis ML",
        version=__version__,
        description="Real-time stream vibe engine powered by chat NLP and FFmpeg.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post("/chat", response_model=ChatMessage)
    def ingest_chat(message: ChatMessage) -> ChatMessage:
        buffer.push(message)
        return message

    @app.post("/chat/batch", response_model=list[ChatMessage])
    def ingest_chat_batch(messages: list[ChatMessage]) -> list[ChatMessage]:
        for message in messages:
            buffer.push(message)
        return messages

    @app.get("/energy", response_model=EnergyScore)
    def energy() -> EnergyScore:
        messages = buffer.recent(settings.window_seconds)
        return analyzer.analyze(messages)

    @app.get("/engine/profile", response_model=VibeProfile)
    def profile() -> VibeProfile:
        score = analyzer.analyze(buffer.recent(settings.window_seconds))
        return engine.policy.choose(score)

    @app.get("/engine/preview", response_model=FfmpegPlan)
    def preview(input: str, output: str = "outputs/auralis-output.m4a") -> FfmpegPlan:
        score = analyzer.analyze(buffer.recent(settings.window_seconds))
        return engine.preview(input, output, score)

    return app


def main() -> None:
    import uvicorn

    uvicorn.run("auralis_ml.api.app:create_app", factory=True, host="0.0.0.0", port=8000)
