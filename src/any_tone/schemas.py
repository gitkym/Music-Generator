from dataclasses import dataclass


@dataclass(frozen=True)
class ScaleDefinition:
    scale_id: str
    display_name: str
    family: str
    tonic: str
    pitch_classes: tuple[int, ...]
    note_names: tuple[str, ...]

    @property
    def length(self) -> int:
        return len(self.pitch_classes)


@dataclass(frozen=True)
class TransformationRow:
    transformation_id: str
    transformation_type: str
    row_index: int
    pitch_classes: tuple[int, ...]
    note_names: tuple[str, ...]


@dataclass(frozen=True)
class ScaleGrid:
    scale: ScaleDefinition
    rows: tuple[TransformationRow, ...]