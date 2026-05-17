from any_tone.note_names import normalise_pitch_classes, pcs_to_note_names
from any_tone.schemas import ScaleDefinition


def build_manual_scale(
    pitch_classes: list[int] | tuple[int, ...],
    display_name: str = "Manual Scale",
) -> ScaleDefinition:
    pcs = normalise_pitch_classes(pitch_classes)

    if len(pcs) >= 12:
        raise ValueError("Manual any-tone scale must contain fewer than 12 pitch classes.")

    if len(pcs) < 2:
        raise ValueError("Manual any-tone scale must contain at least 2 pitch classes.")

    if len(set(pcs)) != len(pcs):
        raise ValueError("Manual any-tone scale cannot contain duplicate pitch classes.")

    return ScaleDefinition(
        scale_id="manual_scale",
        display_name=display_name,
        family="manual",
        variant="manual",
        tonic="manual",
        pitch_classes=pcs,
        note_names=pcs_to_note_names(pcs),
    )