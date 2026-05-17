from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

import random
import numpy as np


PitchClass = int
PitchClassRow = list[PitchClass]
RowFormType = Literal["P", "I", "R", "RI"]


# -------------------------
# Validation
# -------------------------

def validate_pitch_class(pc: int, modulus: int = 12) -> None:
    if not isinstance(pc, (int, np.integer)):
        raise TypeError("Pitch class must be an integer.")

    pc = int(pc)

    if pc < 0 or pc >= modulus:
        raise ValueError(f"Pitch class must be in range 0 to {modulus - 1}.")


def validate_row(row: Sequence[int], modulus: int = 12) -> None:
    if len(row) != modulus:
        raise ValueError(f"Row must contain exactly {modulus} pitch classes.")

    for pc in row:
        validate_pitch_class(pc, modulus=modulus)

    if set(int(pc) for pc in row) != set(range(modulus)):
        raise ValueError(
            f"Row must contain each pitch class from 0 to {modulus - 1} exactly once."
        )


# -------------------------
# Row operations
# -------------------------

def generate_row(modulus: int = 12, seed: int | None = None) -> PitchClassRow:
    rng = random.Random(seed)
    row = list(range(modulus))
    rng.shuffle(row)
    return row


def transpose_row(
    row: Sequence[int],
    interval: int,
    modulus: int = 12,
) -> PitchClassRow:
    return [(int(pc) + interval) % modulus for pc in row]


def normalise_row(
    row: Sequence[int],
    modulus: int = 12,
) -> PitchClassRow:
    validate_row(row, modulus=modulus)
    return transpose_row(row, -int(row[0]), modulus=modulus)


def invert_row(
    row: Sequence[int],
    axis: int = 0,
    modulus: int = 12,
) -> PitchClassRow:
    validate_pitch_class(axis, modulus=modulus)
    return [(2 * int(axis) - int(pc)) % modulus for pc in row]


def retrograde_row(row: Sequence[int]) -> PitchClassRow:
    return list(reversed([int(pc) for pc in row]))


def rotate_row(row: Sequence[int], steps: int) -> PitchClassRow:
    row = [int(pc) for pc in row]
    steps = steps % len(row)
    return row[steps:] + row[:steps]


# -------------------------
# Row forms
# -------------------------

@dataclass(frozen=True)
class RowForm:
    form_type: RowFormType
    transposition: int
    row: PitchClassRow

    @property
    def label(self) -> str:
        return f"{self.form_type}{self.transposition}"


@dataclass
class TwelveToneMaterial:
    raw_row: PitchClassRow
    normalise: bool = True
    modulus: int = 12

    def __post_init__(self) -> None:
        validate_row(self.raw_row, modulus=self.modulus)

        self.raw_row = [int(pc) for pc in self.raw_row]

        self.p0_row = (
            normalise_row(self.raw_row, modulus=self.modulus)
            if self.normalise
            else list(self.raw_row)
        )

        self.matrix = self._build_matrix()

    def _build_matrix(self) -> np.ndarray:
        first_col = invert_row(
            self.p0_row,
            axis=self.p0_row[0],
            modulus=self.modulus,
        )

        matrix = np.zeros((self.modulus, self.modulus), dtype=int)

        for i, start_pc in enumerate(first_col):
            interval = int(start_pc) - int(self.p0_row[0])
            matrix[i, :] = transpose_row(
                self.p0_row,
                interval,
                modulus=self.modulus,
            )

        return matrix

    def prime(self, transposition: int = 0) -> RowForm:
        n = transposition % self.modulus
        return RowForm("P", n, [int(pc) for pc in self.matrix[n, :]])

    def inversion(self, transposition: int = 0) -> RowForm:
        n = transposition % self.modulus
        return RowForm("I", n, [int(pc) for pc in self.matrix[:, n]])

    def retrograde(self, transposition: int = 0) -> RowForm:
        p = self.prime(transposition)
        return RowForm("R", p.transposition, retrograde_row(p.row))

    def retrograde_inversion(self, transposition: int = 0) -> RowForm:
        i = self.inversion(transposition)
        return RowForm("RI", i.transposition, retrograde_row(i.row))

    def get_form(
        self,
        form_type: RowFormType,
        transposition: int = 0,
    ) -> RowForm:
        if form_type == "P":
            return self.prime(transposition)

        if form_type == "I":
            return self.inversion(transposition)

        if form_type == "R":
            return self.retrograde(transposition)

        if form_type == "RI":
            return self.retrograde_inversion(transposition)

        raise ValueError(f"Unknown row form: {form_type}")

    def all_forms(self) -> dict[str, RowForm]:
        forms: dict[str, RowForm] = {}

        for n in range(self.modulus):
            for form_type in ["P", "I", "R", "RI"]:
                form = self.get_form(form_type, n)
                forms[form.label] = form

        return forms