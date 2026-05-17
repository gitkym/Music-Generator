from any_tone.grid import build_scale_grid, flatten_scale_grid
from any_tone.manual import build_manual_scale
from any_tone.registry import get_scale
from any_tone.schemas import ScaleGrid


def generate_any_tone_grid(
    scale_id: str | None = None,
    manual_pitch_classes: list[int] | tuple[int, ...] | None = None,
    manual_display_name: str = "Manual Scale",
) -> ScaleGrid:
    if scale_id and manual_pitch_classes is not None:
        raise ValueError("Provide either scale_id or manual_pitch_classes, not both.")

    if scale_id:
        scale = get_scale(scale_id)
    elif manual_pitch_classes is not None:
        scale = build_manual_scale(
            pitch_classes=manual_pitch_classes,
            display_name=manual_display_name,
        )
    else:
        raise ValueError("Either scale_id or manual_pitch_classes must be provided.")

    return build_scale_grid(scale)


def generate_any_tone_records(
    scale_id: str | None = None,
    manual_pitch_classes: list[int] | tuple[int, ...] | None = None,
    manual_display_name: str = "Manual Scale",
) -> list[dict]:
    grid = generate_any_tone_grid(
        scale_id=scale_id,
        manual_pitch_classes=manual_pitch_classes,
        manual_display_name=manual_display_name,
    )

    return flatten_scale_grid(grid)