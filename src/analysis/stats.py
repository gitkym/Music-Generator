import pandas as pd

from processes.birth_death import (
    PitchClassEvent,
    PopulationEvent,
)


# -------------------------
# Dataframe utilities
# -------------------------


def pitch_events_to_dataframe(
    pitch_events: list[PitchClassEvent],
) -> pd.DataFrame:
    return pd.DataFrame([event.__dict__ for event in pitch_events])



def population_events_to_dataframe(
    population_events: list[PopulationEvent],
) -> pd.DataFrame:
    return pd.DataFrame([event.__dict__ for event in population_events])