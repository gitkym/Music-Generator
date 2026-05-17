SHARP_NOTE_NAMES = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

NOTE_TO_PC = {v: k for k, v in SHARP_NOTE_NAMES.items()}


def pc_to_note_name(pitch_class: int) -> str:
    return SHARP_NOTE_NAMES[pitch_class % 12]


def pcs_to_note_names(pitch_classes: list[int] | tuple[int, ...]) -> tuple[str, ...]:
    return tuple(pc_to_note_name(pc) for pc in pitch_classes)


def normalise_pitch_classes(pitch_classes: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    return tuple(int(pc) % 12 for pc in pitch_classes)