import argparse
import subprocess

from auralis_ml.audio.ffmpeg import FfmpegCommandBuilder
from auralis_ml.audio.policy import VibePolicy
from auralis_ml.models import AudioFeatures, EnergyScore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an adaptive Auralis ML audio file.")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--energy", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    score = EnergyScore(
        score=max(0.0, min(1.0, args.energy)),
        sentiment=0.0,
        velocity=0.0,
        intensity=max(0.0, min(1.0, args.energy)),
        message_count=0,
        window_seconds=30,
    )
    profile = VibePolicy().choose(score, AudioFeatures())
    builder = FfmpegCommandBuilder()
    source, target = builder.validate_paths(args.input, args.output)
    plan = builder.build(str(source), str(target), profile)
    subprocess.run(plan.command, check=True)


if __name__ == "__main__":
    main()
