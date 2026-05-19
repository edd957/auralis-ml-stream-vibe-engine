from auralis_ml.audio.features import AudioFeatureExtractor
from auralis_ml.audio.ffmpeg import FfmpegCommandBuilder
from auralis_ml.audio.policy import VibePolicy
from auralis_ml.models import EnergyScore, FfmpegPlan


class VibeEngine:
    def __init__(
        self,
        feature_extractor: AudioFeatureExtractor | None = None,
        policy: VibePolicy | None = None,
        command_builder: FfmpegCommandBuilder | None = None,
    ) -> None:
        self.feature_extractor = feature_extractor or AudioFeatureExtractor()
        self.policy = policy or VibePolicy()
        self.command_builder = command_builder or FfmpegCommandBuilder()

    def preview(self, input_path: str, output_path: str, energy: EnergyScore) -> FfmpegPlan:
        features = self.feature_extractor.extract(input_path)
        profile = self.policy.choose(energy, features)
        return self.command_builder.build(input_path, output_path, profile)
