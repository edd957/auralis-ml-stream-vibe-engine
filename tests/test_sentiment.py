from auralis_ml.models import ChatMessage
from auralis_ml.nlp.sentiment import SentimentEnergyAnalyzer


def test_energy_increases_for_hype_messages() -> None:
    analyzer = SentimentEnergyAnalyzer("unused", window_seconds=30)
    calm = analyzer.analyze([ChatMessage(author="a", message="nice and calm")])
    hype = analyzer.analyze(
        [
            ChatMessage(author="a", message="this drop is wild!!!"),
            ChatMessage(author="b", message="go faster, massive hype"),
            ChatMessage(author="c", message="bass is fire"),
        ]
    )

    assert hype.score > calm.score
    assert hype.intensity > calm.intensity
