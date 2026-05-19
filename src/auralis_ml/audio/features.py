from pathlib import Path

from auralis_ml.models import AudioFeatures


class AudioFeatureExtractor:
    def extract(self, input_path: str) -> AudioFeatures:
        path = Path(input_path)
        if not path.exists():
            return AudioFeatures()

        try:
            import librosa
            import numpy as np
        except ImportError:
            return AudioFeatures()

        samples, sample_rate = librosa.load(path, mono=True, duration=90)
        tempo, _ = librosa.beat.beat_track(y=samples, sr=sample_rate)
        rms = float(np.mean(librosa.feature.rms(y=samples)))
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=samples, sr=sample_rate)))

        return AudioFeatures(
            bpm=float(tempo) if tempo else 120.0,
            rms_energy=rms,
            spectral_centroid=centroid,
            key_hint="unknown",
        )
