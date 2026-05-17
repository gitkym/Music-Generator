from any_tone.note_names import pcs_to_note_names
from any_tone.schemas import TransformationRow


def rotate_row(row: tuple[int, ...], n: int) -> tuple[int, ...]:
    n = n % len(row)
    return row[n:] + row[:n]


def retrograde_row(row: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(reversed(row))


def generate_rotation_rows(row: tuple[int, ...]) -> tuple[TransformationRow, ...]:
    rows = []

    for idx in range(len(row)):
        transformed = rotate_row(row, idx)

        rows.append(
            TransformationRow(
                transformation_id=f"ROT_{idx}",
                transformation_type="rotation",
                row_index=idx,
                pitch_classes=transformed,
                note_names=pcs_to_note_names(transformed),
            )
        )

    return tuple(rows)


def generate_retrograde_rows(row: tuple[int, ...]) -> tuple[TransformationRow, ...]:
    retrograde = retrograde_row(row)
    rows = []

    for idx in range(len(retrograde)):
        transformed = rotate_row(retrograde, idx)

        rows.append(
            TransformationRow(
                transformation_id=f"RET_{idx}",
                transformation_type="retrograde_rotation",
                row_index=idx,
                pitch_classes=transformed,
                note_names=pcs_to_note_names(transformed),
            )
        )

    return tuple(rows)


def generate_allowed_transformations(row: tuple[int, ...]) -> tuple[TransformationRow, ...]:
    return generate_rotation_rows(row) + generate_retrograde_rows(row)