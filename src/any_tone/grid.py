from any_tone.schemas import ScaleDefinition, ScaleGrid
from any_tone.transformations import generate_allowed_transformations


def build_scale_grid(scale: ScaleDefinition) -> ScaleGrid:
    rows = generate_allowed_transformations(scale.pitch_classes)

    return ScaleGrid(
        scale=scale,
        rows=rows,
    )


def flatten_scale_grid(grid: ScaleGrid) -> list[dict]:
    records = []

    for row in grid.rows:
        for step_index, (pitch_class, note_name) in enumerate(
            zip(row.pitch_classes, row.note_names)
        ):
            records.append(
                {
                    "scale_id": grid.scale.scale_id,
                    "scale_name": grid.scale.display_name,
                    "scale_family": grid.scale.family,
                    "scale_variant": grid.scale.variant,
                    "scale_length": grid.scale.length,
                    "transformation_id": row.transformation_id,
                    "transformation_type": row.transformation_type,
                    "row_index": row.row_index,
                    "step_index": step_index,
                    "pitch_class": pitch_class,
                    "note_name": note_name,
                }
            )

    return records