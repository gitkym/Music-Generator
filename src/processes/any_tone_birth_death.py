from __future__ import annotations

from dataclasses import dataclass, field

from processes.birth_death import (
    BirthDeathConfig,
    MutationConfig,
    ToneRowVoice,
    PitchClassEvent,
    PopulationEvent,
    BirthDeathToneRowProcess,
)

from any_tone.transformations import rotate_row, retrograde_row


def validate_any_tone_row(row: list[int] | tuple[int, ...]) -> None:
    if len(row) < 2:
        raise ValueError("Any-tone row must contain at least 2 pitch classes.")

    if len(row) >= 12:
        raise ValueError("Any-tone row must contain fewer than 12 pitch classes.")

    for pc in row:
        if not isinstance(pc, int):
            raise TypeError("Any-tone pitch classes must be integers.")

        if pc < 0 or pc > 11:
            raise ValueError("Any-tone pitch classes must be in range 0 to 11.")

    if len(set(row)) != len(row):
        raise ValueError("Any-tone row cannot contain duplicate pitch classes.")


@dataclass
class BirthDeathAnyToneProcess(BirthDeathToneRowProcess):
    rows: list[list[int]]
    config: BirthDeathConfig
    mutation_config: MutationConfig

    voices: dict[int, ToneRowVoice] = field(default_factory=dict)
    pitch_events: list[PitchClassEvent] = field(default_factory=list)
    population_events: list[PopulationEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rng = __import__("random").Random(self.config.seed)
        self.np_rng = __import__("numpy").random.default_rng(self.config.seed)
        self.next_voice_id = 0

        if not self.rows:
            raise ValueError("At least one any-tone row must be provided.")

        for row in self.rows:
            validate_any_tone_row(row)

    def mutate_row(self, row: list[int]) -> tuple[list[int], list[str]]:
        mc = self.mutation_config
        mutated = list(row)
        history = []

        if self.rng.random() < mc.retrograde_probability:
            mutated = list(retrograde_row(tuple(mutated)))
            history.append("RET")

        if self.rng.random() < mc.rotate_probability:
            valid_steps = tuple(step for step in mc.rotate_steps if step % len(mutated) != 0)

            if valid_steps:
                steps = self.rng.choice(valid_steps)
                mutated = list(rotate_row(tuple(mutated), steps))
                history.append(f"ROT{steps}")

        validate_any_tone_row(mutated)

        return mutated, history or ["copy"]