from pathlib import Path

from auralis_ml.models import FfmpegPlan, VibeProfile


class FfmpegCommandBuilder:
    def build(self, input_path: str, output_path: str, profile: VibeProfile) -> FfmpegPlan:
        filter_graph = self._filter_graph(profile)
        command = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-filter:a",
            filter_graph,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            output_path,
        ]
        return FfmpegPlan(
            input_path=input_path,
            output_path=output_path,
            profile=profile,
            filter_graph=filter_graph,
            command=command,
        )

    def validate_paths(self, input_path: str, output_path: str) -> tuple[Path, Path]:
        source = Path(input_path).expanduser().resolve()
        target = Path(output_path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"Input audio does not exist: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        return source, target

    @staticmethod
    def _filter_graph(profile: VibeProfile) -> str:
        tempo = max(0.5, min(2.0, profile.tempo_factor))
        pitch_rate = 2 ** (profile.pitch_shift_semitones / 12)
        bass = profile.bass_gain_db
        treble = profile.treble_gain_db
        reverb = max(0.0, min(1.0, profile.reverb))

        filters = [
            f"asetrate=44100*{pitch_rate:.5f}",
            "aresample=44100",
            f"atempo={tempo:.5f}",
            f"bass=g={bass:.2f}:f=110:w=0.60",
            f"treble=g={treble:.2f}:f=6000:w=0.50",
        ]
        if reverb > 0:
            filters.append(f"aecho=0.8:0.88:60:{reverb:.2f}")
        if profile.compressor:
            filters.append("acompressor=threshold=-16dB:ratio=3:attack=8:release=120")
        filters.append("alimiter=limit=0.95")
        return ",".join(filters)
