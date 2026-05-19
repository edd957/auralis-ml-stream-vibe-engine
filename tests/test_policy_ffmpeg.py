from auralis_ml.audio.ffmpeg import FfmpegCommandBuilder
from auralis_ml.audio.policy import VibePolicy
from auralis_ml.models import AudioFeatures, EnergyScore


def make_score(value: float) -> EnergyScore:
    return EnergyScore(
        score=value,
        sentiment=0.0,
        velocity=0.0,
        intensity=value,
        message_count=1,
        window_seconds=30,
    )


def test_policy_selects_surge_for_high_energy() -> None:
    profile = VibePolicy().choose(make_score(0.9), AudioFeatures(bpm=120))

    assert profile.name == "surge"
    assert profile.tempo_factor > 1.0
    assert profile.bass_gain_db > 0


def test_ffmpeg_command_contains_expected_filters() -> None:
    profile = VibePolicy().choose(make_score(0.2), AudioFeatures())
    plan = FfmpegCommandBuilder().build("input.wav", "output.m4a", profile)

    assert plan.command[0] == "ffmpeg"
    assert "atempo=" in plan.filter_graph
    assert "aecho=" in plan.filter_graph
