from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Platform(StrEnum):
    demo = "demo"
    twitch = "twitch"
    youtube = "youtube"


class ChatMessage(BaseModel):
    author: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=500)
    platform: Platform = Platform.demo
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EnergyScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    sentiment: float = Field(ge=-1.0, le=1.0)
    velocity: float = Field(ge=0.0)
    intensity: float = Field(ge=0.0, le=1.0)
    message_count: int = Field(ge=0)
    window_seconds: int = Field(gt=0)


class AudioFeatures(BaseModel):
    bpm: float = Field(default=120.0, gt=0.0)
    rms_energy: float = Field(default=0.0, ge=0.0)
    spectral_centroid: float = Field(default=0.0, ge=0.0)
    key_hint: str = "unknown"


class VibeProfile(BaseModel):
    name: str
    tempo_factor: float
    bass_gain_db: float
    treble_gain_db: float
    reverb: float
    pitch_shift_semitones: float = 0.0
    compressor: bool = True


class FfmpegPlan(BaseModel):
    input_path: str
    output_path: str
    profile: VibeProfile
    filter_graph: str
    command: list[str]
