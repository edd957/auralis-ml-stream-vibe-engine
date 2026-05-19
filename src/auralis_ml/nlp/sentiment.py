import math
import re
from collections.abc import Sequence

from auralis_ml.models import ChatMessage, EnergyScore

POSITIVE_TERMS = {
    "amazing",
    "fire",
    "good",
    "great",
    "hype",
    "insane",
    "love",
    "massive",
    "nice",
    "wild",
}
NEGATIVE_TERMS = {"bad", "boring", "dead", "hate", "slow", "tired", "weak"}
ENERGY_TERMS = {"bass", "drop", "fast", "faster", "go", "hard", "hype", "speed", "wild"}


class SentimentEnergyAnalyzer:
    def __init__(
        self,
        model_name: str,
        window_seconds: int,
        enable_transformers: bool = False,
    ) -> None:
        self.model_name = model_name
        self.window_seconds = window_seconds
        self._pipeline = None
        if enable_transformers:
            self._pipeline = self._load_pipeline(model_name)

    def analyze(self, messages: Sequence[ChatMessage]) -> EnergyScore:
        if not messages:
            return EnergyScore(
                score=0.15,
                sentiment=0.0,
                velocity=0.0,
                intensity=0.0,
                message_count=0,
                window_seconds=self.window_seconds,
            )

        texts = [message.message for message in messages]
        sentiment = (
            self._transformer_sentiment(texts)
            if self._pipeline
            else self._lexical_sentiment(texts)
        )
        intensity = self._intensity(texts)
        velocity = len(messages) / self.window_seconds

        velocity_score = min(1.0, velocity / 2.0)
        sentiment_lift = (sentiment + 1.0) / 2.0
        score = 0.45 * intensity + 0.35 * velocity_score + 0.20 * sentiment_lift

        return EnergyScore(
            score=round(max(0.0, min(1.0, score)), 4),
            sentiment=round(sentiment, 4),
            velocity=round(velocity, 4),
            intensity=round(intensity, 4),
            message_count=len(messages),
            window_seconds=self.window_seconds,
        )

    @staticmethod
    def _load_pipeline(model_name: str):
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("Install the ml extra to enable Transformers inference.") from exc
        return pipeline("sentiment-analysis", model=model_name)

    def _transformer_sentiment(self, texts: Sequence[str]) -> float:
        assert self._pipeline is not None
        batch = [text[:300] for text in texts]
        outputs = self._pipeline(batch, truncation=True)
        scores = []
        for output in outputs:
            label = str(output["label"]).lower()
            confidence = float(output["score"])
            if "negative" in label or label.endswith("_0"):
                scores.append(-confidence)
            elif "positive" in label or label.endswith("_2"):
                scores.append(confidence)
            else:
                scores.append(0.0)
        return sum(scores) / len(scores)

    @staticmethod
    def _lexical_sentiment(texts: Sequence[str]) -> float:
        total = 0.0
        for text in texts:
            tokens = set(re.findall(r"[a-z']+", text.lower()))
            total += len(tokens & POSITIVE_TERMS) - len(tokens & NEGATIVE_TERMS)
        return math.tanh(total / max(1, len(texts)))

    @staticmethod
    def _intensity(texts: Sequence[str]) -> float:
        joined = " ".join(texts)
        tokens = re.findall(r"[a-z']+", joined.lower())
        if not tokens:
            return 0.0
        energy_hits = sum(1 for token in tokens if token in ENERGY_TERMS)
        exclamation_lift = min(0.25, joined.count("!") * 0.03)
        uppercase_lift = min(
            0.25,
            sum(1 for char in joined if char.isupper()) / max(20, len(joined)),
        )
        lexical = min(1.0, energy_hits / max(3, len(texts)))
        return min(1.0, lexical + exclamation_lift + uppercase_lift)
