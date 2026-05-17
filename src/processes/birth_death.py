from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import random
import numpy as np

from material.twelve_tone import (
    PitchClassRow,
    validate_row,
    transpose_row,
    invert_row,
    retrograde_row,
    rotate_row,
)


VelocityMode = Literal["fixed", "normal", "uniform"]
DurationMode = Literal["fixed", "normal", "uniform", "exponential"]


@dataclass
class MutationConfig:
    transpose_probability: float = 0.35
    transpose_intervals: tuple[int, ...] = (-6, -5, -3, -2, 1, 2, 3, 5, 6)

    invert_probability: float = 0.15
    retrograde_probability: float = 0.20
    rotate_probability: float = 0.20
    rotate_steps: tuple[int, ...] = (1, 2, 3, 4, 5, 6)

    note_rate_mutation_probability: float = 0.35
    note_rate_multiplier_range: tuple[float, float] = (0.70, 1.40)

    duration_mutation_probability: float = 0.35
    duration_multiplier_range: tuple[float, float] = (0.70, 1.40)

    velocity_mutation_probability: float = 0.35
    velocity_shift_range: tuple[int, int] = (-14, 14)
    velocity_sd_range: tuple[float, float] = (0.00, 0.25)


@dataclass
class BirthDeathConfig:
    song_length: float = 90.0
    initial_population: int = 2
    min_population: int = 1
    max_population: int = 10

    birth_rate: float = 0.08
    death_rate: float = 0.06

    note_rate_mean: float = 2.5
    note_rate_sd: float = 0.35

    duration_mean: float = 0.25
    duration_sd: float = 0.25
    duration_mode: DurationMode = "normal"
    duration_min: float = 0.05
    duration_max: float = 2.00

    velocity_mean: int = 72
    velocity_sd: float = 0.10
    velocity_mode: VelocityMode = "normal"

    seed: int | None = None


@dataclass
class ToneRowVoice:
    voice_id: int
    row: PitchClassRow
    birth_time: float
    note_rate: float

    duration_mean: float = 0.25
    duration_sd: float = 0.25
    duration_mode: DurationMode = "normal"
    duration_min: float = 0.05
    duration_max: float = 2.00

    velocity_mean: int = 72
    velocity_sd: float = 0.10
    velocity_mode: VelocityMode = "normal"

    current_index: int = 0
    death_time: float | None = None
    parent_id: int | None = None
    mutation_history: list[str] = field(default_factory=list)

    @property
    def is_alive(self) -> bool:
        return self.death_time is None

    def next_pitch_class(self) -> tuple[int, int, int]:
        row_index = self.current_index % len(self.row)
        row_cycle = self.current_index // len(self.row)
        pc = int(self.row[row_index])
        self.current_index += 1
        return pc, row_index, row_cycle


@dataclass
class PitchClassEvent:
    time: float
    duration: float
    voice_id: int
    pitch_class: int
    velocity: int
    row_index: int
    row_cycle: int
    parent_id: int | None = None


@dataclass
class PopulationEvent:
    time: float
    event_type: str
    voice_id: int
    population_size: int
    parent_id: int | None = None
    mutation_history: str = ""


@dataclass
class BirthDeathToneRowProcess:
    rows: list[PitchClassRow]
    config: BirthDeathConfig
    mutation_config: MutationConfig

    voices: dict[int, ToneRowVoice] = field(default_factory=dict)
    pitch_events: list[PitchClassEvent] = field(default_factory=list)
    population_events: list[PopulationEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.config.seed)
        self.np_rng = np.random.default_rng(self.config.seed)
        self.next_voice_id = 0

        if not self.rows:
            raise ValueError("At least one tone row must be provided.")

        for row in self.rows:
            validate_row(row)

    def alive_voices(self) -> list[ToneRowVoice]:
        return [voice for voice in self.voices.values() if voice.is_alive]

    def population_size(self) -> int:
        return len(self.alive_voices())

    def sample_note_rate(self) -> float:
        rate = self.rng.normalvariate(
            self.config.note_rate_mean,
            self.config.note_rate_mean * self.config.note_rate_sd,
        )
        return max(rate, 0.01)

    def sample_duration(self, voice: ToneRowVoice) -> float:
        if voice.duration_mode == "fixed":
            duration = voice.duration_mean
        elif voice.duration_mode == "uniform":
            duration = self.rng.uniform(voice.duration_min, voice.duration_max)
        elif voice.duration_mode == "exponential":
            duration = self.np_rng.exponential(voice.duration_mean)
        else:
            duration = self.rng.normalvariate(
                voice.duration_mean,
                voice.duration_mean * voice.duration_sd,
            )

        return float(max(voice.duration_min, min(voice.duration_max, duration)))

    def sample_velocity(self, voice: ToneRowVoice) -> int:
        if voice.velocity_mode == "fixed":
            velocity = voice.velocity_mean
        elif voice.velocity_mode == "uniform":
            lo = max(0, int(voice.velocity_mean * (1 - voice.velocity_sd)))
            hi = min(127, int(voice.velocity_mean * (1 + voice.velocity_sd)))
            velocity = self.rng.randint(lo, hi)
        else:
            velocity = self.rng.normalvariate(
                voice.velocity_mean,
                voice.velocity_mean * voice.velocity_sd,
            )

        return int(max(0, min(127, round(velocity))))

    def create_initial_voice(self, time: float) -> ToneRowVoice:
        row = list(self.rng.choice(self.rows))

        voice = ToneRowVoice(
            voice_id=self.next_voice_id,
            row=row,
            birth_time=time,
            note_rate=self.sample_note_rate(),
            duration_mean=self.config.duration_mean,
            duration_sd=self.config.duration_sd,
            duration_mode=self.config.duration_mode,
            duration_min=self.config.duration_min,
            duration_max=self.config.duration_max,
            velocity_mean=self.config.velocity_mean,
            velocity_sd=self.config.velocity_sd,
            velocity_mode=self.config.velocity_mode,
            mutation_history=["initial"],
        )

        self.voices[voice.voice_id] = voice
        self.next_voice_id += 1

        return voice

    def choose_parent(self) -> ToneRowVoice:
        alive = self.alive_voices()

        if not alive:
            raise ValueError("Cannot choose parent when no voices are alive.")

        return self.rng.choice(alive)

    def mutate_row(self, row: PitchClassRow) -> tuple[PitchClassRow, list[str]]:
        mc = self.mutation_config
        mutated = list(row)
        history = []

        if self.rng.random() < mc.transpose_probability:
            interval = self.rng.choice(mc.transpose_intervals)
            mutated = transpose_row(mutated, interval)
            history.append(f"T{interval:+d}")

        if self.rng.random() < mc.invert_probability:
            mutated = invert_row(mutated, axis=mutated[0])
            history.append("I")

        if self.rng.random() < mc.retrograde_probability:
            mutated = retrograde_row(mutated)
            history.append("R")

        if self.rng.random() < mc.rotate_probability:
            steps = self.rng.choice(mc.rotate_steps)
            mutated = rotate_row(mutated, steps)
            history.append(f"ROT{steps}")

        validate_row(mutated)

        return mutated, history or ["copy"]

    def mutate_note_rate(self, parent_rate: float) -> float:
        mc = self.mutation_config

        if self.rng.random() >= mc.note_rate_mutation_probability:
            return parent_rate

        lo, hi = mc.note_rate_multiplier_range

        return max(0.01, parent_rate * self.rng.uniform(lo, hi))

    def mutate_duration_profile(self, parent: ToneRowVoice) -> tuple[float, list[str]]:
        mc = self.mutation_config

        if self.rng.random() >= mc.duration_mutation_probability:
            return parent.duration_mean, []

        lo, hi = mc.duration_multiplier_range
        multiplier = self.rng.uniform(lo, hi)

        duration_mean = max(
            parent.duration_min,
            min(parent.duration_max, parent.duration_mean * multiplier),
        )

        return duration_mean, [f"DURx{multiplier:.2f}"]

    def mutate_velocity_profile(self, parent: ToneRowVoice) -> tuple[int, float, list[str]]:
        mc = self.mutation_config

        if self.rng.random() >= mc.velocity_mutation_probability:
            return parent.velocity_mean, parent.velocity_sd, []

        shift = self.rng.randint(*mc.velocity_shift_range)
        velocity_mean = int(max(0, min(127, parent.velocity_mean + shift)))
        velocity_sd = self.rng.uniform(*mc.velocity_sd_range)

        return velocity_mean, velocity_sd, [f"VEL{shift:+d}"]

    def create_child_voice(self, time: float) -> ToneRowVoice:
        parent = self.choose_parent()

        child_row, row_history = self.mutate_row(parent.row)
        child_note_rate = self.mutate_note_rate(parent.note_rate)
        child_duration_mean, duration_history = self.mutate_duration_profile(parent)
        velocity_mean, velocity_sd, velocity_history = self.mutate_velocity_profile(parent)

        mutation_history = row_history + duration_history + velocity_history

        voice = ToneRowVoice(
            voice_id=self.next_voice_id,
            row=child_row,
            birth_time=time,
            note_rate=child_note_rate,
            duration_mean=child_duration_mean,
            duration_sd=parent.duration_sd,
            duration_mode=parent.duration_mode,
            duration_min=parent.duration_min,
            duration_max=parent.duration_max,
            velocity_mean=velocity_mean,
            velocity_sd=velocity_sd,
            velocity_mode=parent.velocity_mode,
            parent_id=parent.voice_id,
            mutation_history=mutation_history,
        )

        self.voices[voice.voice_id] = voice
        self.next_voice_id += 1

        return voice

    def kill_voice(self, time: float) -> ToneRowVoice | None:
        alive = self.alive_voices()

        if not alive:
            return None

        voice = self.rng.choice(alive)
        voice.death_time = time

        return voice

    def generate_initial_population(self) -> None:
        for _ in range(self.config.initial_population):
            voice = self.create_initial_voice(time=0.0)

            self.population_events.append(
                PopulationEvent(
                    time=0.0,
                    event_type="birth",
                    voice_id=voice.voice_id,
                    population_size=self.population_size(),
                    mutation_history="initial",
                )
            )

    def generate_voice_notes_until(
        self,
        voice: ToneRowVoice,
        start_time: float,
        end_time: float,
    ) -> None:
        t = start_time

        while t < end_time and voice.is_alive:
            t += self.np_rng.exponential(1 / voice.note_rate)

            if t >= end_time:
                break

            pc, row_index, row_cycle = voice.next_pitch_class()

            self.pitch_events.append(
                PitchClassEvent(
                    time=t,
                    duration=self.sample_duration(voice),
                    voice_id=voice.voice_id,
                    pitch_class=pc,
                    velocity=self.sample_velocity(voice),
                    row_index=row_index,
                    row_cycle=row_cycle,
                    parent_id=voice.parent_id,
                )
            )

    def next_population_wait(self) -> float:
        n = self.population_size()

        if n == 0:
            total_rate = self.config.birth_rate
        else:
            total_rate = (self.config.birth_rate * n) + (self.config.death_rate * n)

        return self.np_rng.exponential(1 / max(total_rate, 1e-9))

    def choose_birth_or_death(self) -> str:
        n = self.population_size()

        if n <= self.config.min_population:
            return "birth"

        if n >= self.config.max_population:
            return "death"

        birth_intensity = self.config.birth_rate * n
        death_intensity = self.config.death_rate * n
        birth_probability = birth_intensity / (birth_intensity + death_intensity)

        return "birth" if self.rng.random() < birth_probability else "death"

    def run(self) -> tuple[list[PitchClassEvent], list[PopulationEvent]]:
        self.generate_initial_population()

        current_time = 0.0

        while current_time < self.config.song_length:
            next_time = min(
                current_time + self.next_population_wait(),
                self.config.song_length,
            )

            for voice in self.alive_voices():
                self.generate_voice_notes_until(
                    voice=voice,
                    start_time=current_time,
                    end_time=next_time,
                )

            current_time = next_time

            if current_time >= self.config.song_length:
                break

            event_type = self.choose_birth_or_death()

            if event_type == "birth":
                if self.population_size() == 0:
                    voice = self.create_initial_voice(current_time)
                else:
                    voice = self.create_child_voice(current_time)
            else:
                voice = self.kill_voice(current_time)

            if voice is not None:
                self.population_events.append(
                    PopulationEvent(
                        time=current_time,
                        event_type=event_type,
                        voice_id=voice.voice_id,
                        population_size=self.population_size(),
                        parent_id=voice.parent_id,
                        mutation_history=", ".join(voice.mutation_history),
                    )
                )

        return self.pitch_events, self.population_events