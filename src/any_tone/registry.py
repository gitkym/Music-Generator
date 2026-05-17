from any_tone.note_names import NOTE_TO_PC, pcs_to_note_names
from any_tone.schemas import ScaleDefinition


SCALE_INTERVALS = {
    "diatonic": {
        "family": "diatonic",
        "intervals": [0, 2, 4, 5, 7, 9, 11],
    },
    "pentatonic": {
        "family": "pentatonic",
        "intervals": [0, 2, 4, 7, 9],
    },
    "diminished": {
        "family": "diminished",
        "intervals": [0, 1, 3, 4, 6, 7, 9, 10],
    },
    "whole_tone": {
        "family": "whole_tone",
        "intervals": [0, 2, 4, 6, 8, 10],
    },
    "arpeggio": {
        "family": "arpeggio",
        "intervals": [0, 4, 7],
    },
}


TONICS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _build_scale(scale_key: str, tonic: str) -> ScaleDefinition:
    spec = SCALE_INTERVALS[scale_key]
    tonic_pc = NOTE_TO_PC[tonic]

    pitch_classes = tuple((tonic_pc + interval) % 12 for interval in spec["intervals"])
    note_names = pcs_to_note_names(pitch_classes)

    scale_id = f"{tonic.lower().replace('#', 'sharp')}_{scale_key}"
    display_name = f"{tonic} {spec['family'].replace('_', ' ').title()}"

    return ScaleDefinition(
        scale_id=scale_id,
        display_name=display_name,
        family=spec["family"],
        tonic=tonic,
        pitch_classes=pitch_classes,
        note_names=note_names,
    )


def build_scale_registry() -> dict[str, ScaleDefinition]:
    registry = {}

    for scale_key in SCALE_INTERVALS:
        for tonic in TONICS:
            scale = _build_scale(scale_key, tonic)
            registry[scale.scale_id] = scale

    return registry


SCALE_REGISTRY = build_scale_registry()


def get_scale(scale_id: str) -> ScaleDefinition:
    if scale_id not in SCALE_REGISTRY:
        available = ", ".join(sorted(SCALE_REGISTRY))
        raise KeyError(f"Unknown scale_id: {scale_id}. Available scales: {available}")

    return SCALE_REGISTRY[scale_id]


def list_scales() -> list[ScaleDefinition]:
    return sorted(SCALE_REGISTRY.values(), key=lambda x: x.display_name)