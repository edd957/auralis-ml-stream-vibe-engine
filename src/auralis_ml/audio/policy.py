from auralis_ml.models import AudioFeatures, EnergyScore, VibeProfile


class VibePolicy:
    def choose(self, energy: EnergyScore, features: AudioFeatures | None = None) -> VibeProfile:
        features = features or AudioFeatures()
        tempo_ceiling = 1.16 if features.bpm < 150 else 1.08

        if energy.score >= 0.82:
            return VibeProfile(
                name="surge",
                tempo_factor=tempo_ceiling,
                bass_gain_db=7.0,
                treble_gain_db=3.0,
                reverb=0.08,
                pitch_shift_semitones=1.5,
            )
        if energy.score >= 0.62:
            return VibeProfile(
                name="lift",
                tempo_factor=1.08,
                bass_gain_db=4.5,
                treble_gain_db=1.5,
                reverb=0.12,
                pitch_shift_semitones=0.5,
            )
        if energy.score <= 0.28:
            return VibeProfile(
                name="cooldown",
                tempo_factor=0.96,
                bass_gain_db=-1.5,
                treble_gain_db=-2.0,
                reverb=0.38,
                pitch_shift_semitones=-0.5,
            )
        return VibeProfile(
            name="steady",
            tempo_factor=1.0,
            bass_gain_db=1.0,
            treble_gain_db=0.5,
            reverb=0.18,
            pitch_shift_semitones=0.0,
        )
