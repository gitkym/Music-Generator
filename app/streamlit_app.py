from __future__ import annotations

import sys
from pathlib import Path
from io import BytesIO

import numpy as np
import pandas as pd
import pretty_midi
import streamlit as st
import plotly.graph_objects as go
from scipy.io import wavfile


# -------------------------
# Import local src package
# -------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from material.twelve_tone import generate_row, TwelveToneMaterial
from processes.birth_death import BirthDeathConfig, MutationConfig, BirthDeathToneRowProcess
from rendering.midi import pitch_events_to_midi
from analysis.stats import pitch_events_to_dataframe, population_events_to_dataframe


# -------------------------
# Helpers
# -------------------------

def synthesize_midi_to_wav_bytes(midi_path: Path, sample_rate: int = 44100) -> bytes:
    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    audio = midi_data.synthesize(fs=sample_rate)

    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak

    audio_int16 = np.int16(audio * 32767)

    buffer = BytesIO()
    wavfile.write(buffer, sample_rate, audio_int16)
    buffer.seek(0)

    return buffer.read()


def build_population_animation(pop_df: pd.DataFrame, song_length: float, step_seconds: float) -> go.Figure:
    frame_times = np.arange(0, song_length + step_seconds, step_seconds)

    population_at_frame = []

    for t in frame_times:
        past_events = pop_df[pop_df["time"] <= t]
        if past_events.empty:
            population_at_frame.append(0)
        else:
            population_at_frame.append(int(past_events["population_size"].iloc[-1]))

    anim_df = pd.DataFrame(
        {
            "time": frame_times,
            "population_size": population_at_frame,
        }
    )

    max_pop = max(1, int(anim_df["population_size"].max()) + 1)

    frames = []

    for i in range(len(anim_df)):
        frame_data = anim_df.iloc[: i + 1]

        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=frame_data["time"],
                        y=frame_data["population_size"],
                        mode="lines+markers",
                        line_shape="hv",
                    )
                ],
                name=str(i),
            )
        )

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[anim_df["time"].iloc[0]],
                y=[anim_df["population_size"].iloc[0]],
                mode="lines+markers",
                line_shape="hv",
            )
        ],
        frames=frames,
    )

    fig.update_layout(
        title="Active voices over time",
        xaxis_title="Time (seconds)",
        yaxis_title="Active voices",
        xaxis=dict(range=[0, song_length]),
        yaxis=dict(range=[0, max_pop]),
        height=450,
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": int(step_seconds * 1000), "redraw": True},
                                "fromcurrent": True,
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
    )

    return fig


# -------------------------
# App
# -------------------------

st.set_page_config(page_title="Stochastic Music Generator", layout="wide")

st.title("Stochastic Music Generator")
st.caption("12-tone birth-death process prototype")

with st.sidebar:
    st.header("Seeds")

    row_seed = st.number_input("Row seed", value=42, step=1)
    process_seed = st.number_input("Process seed", value=123, step=1)

    st.header("Song / MIDI")

    song_name = st.text_input("Song name", value="birth_death_streamlit_test")
    song_length = st.number_input("Song length seconds", value=60.0, min_value=1.0, step=1.0)
    bpm = st.number_input("BPM", value=120, min_value=20, max_value=300, step=1)
    ticks_per_beat = st.number_input("Ticks per beat", value=480, min_value=24, step=24)
    base_octave = st.number_input("Base octave", value=4, min_value=0, max_value=9, step=1)
    octave_span = st.number_input("Octave span", value=3, min_value=1, max_value=8, step=1)

    st.header("Birth-death")

    initial_population = st.number_input("Initial population", value=2, min_value=0, step=1)
    min_population = st.number_input("Min population", value=1, min_value=0, step=1)
    max_population = st.number_input("Max population", value=12, min_value=1, step=1)

    birth_rate = st.number_input("Birth rate", value=0.12, min_value=0.0, step=0.01, format="%.4f")
    death_rate = st.number_input("Death rate", value=0.08, min_value=0.0, step=0.01, format="%.4f")

    st.header("Notes")

    note_rate_mean = st.number_input("Note rate mean", value=2.5, min_value=0.01, step=0.1)
    note_rate_sd = st.number_input("Note rate SD", value=0.35, min_value=0.0, step=0.05)

    duration_mean = st.number_input("Duration mean", value=0.25, min_value=0.01, step=0.05)
    duration_sd = st.number_input("Duration SD", value=0.25, min_value=0.0, step=0.05)
    duration_mode = st.selectbox("Duration mode", ["fixed", "normal", "uniform", "exponential"], index=1)
    duration_min = st.number_input("Duration min", value=0.05, min_value=0.001, step=0.01)
    duration_max = st.number_input("Duration max", value=1.50, min_value=0.001, step=0.05)

    velocity_mean = st.number_input("Velocity mean", value=72, min_value=0, max_value=127, step=1)
    velocity_sd = st.number_input("Velocity SD", value=0.12, min_value=0.0, step=0.05)
    velocity_mode = st.selectbox("Velocity mode", ["fixed", "normal", "uniform"], index=1)

    st.header("Mutations")

    transpose_probability = st.number_input("Transpose probability", value=0.45, min_value=0.0, max_value=1.0, step=0.05)
    transpose_intervals_text = st.text_input("Transpose intervals", value="-6,-5,-3,-2,1,2,3,5,6")

    invert_probability = st.number_input("Invert probability", value=0.20, min_value=0.0, max_value=1.0, step=0.05)
    retrograde_probability = st.number_input("Retrograde probability", value=0.25, min_value=0.0, max_value=1.0, step=0.05)
    rotate_probability = st.number_input("Rotate probability", value=0.25, min_value=0.0, max_value=1.0, step=0.05)
    rotate_steps_text = st.text_input("Rotate steps", value="1,2,3,4,5,6")

    animation_step_seconds = st.number_input("Animation step seconds", value=0.25, min_value=0.01, step=0.05)

    generate_button = st.button("Generate")


if generate_button:
    output_dir = PROJECT_ROOT / "generated" / "midi"
    output_dir.mkdir(parents=True, exist_ok=True)

    midi_path = output_dir / f"{song_name}.mid"

    transpose_intervals = tuple(int(x.strip()) for x in transpose_intervals_text.split(",") if x.strip())
    rotate_steps = tuple(int(x.strip()) for x in rotate_steps_text.split(",") if x.strip())

    raw_row = generate_row(modulus=12, seed=int(row_seed))
    material = TwelveToneMaterial(raw_row=raw_row, normalise=True)

    input_rows = [
        material.get_form("P", 0).row,
        material.get_form("I", 0).row,
        material.get_form("R", 0).row,
        material.get_form("RI", 0).row,
    ]

    bd_config = BirthDeathConfig(
        song_length=float(song_length),
        initial_population=int(initial_population),
        min_population=int(min_population),
        max_population=int(max_population),
        birth_rate=float(birth_rate),
        death_rate=float(death_rate),
        note_rate_mean=float(note_rate_mean),
        note_rate_sd=float(note_rate_sd),
        duration_mean=float(duration_mean),
        duration_sd=float(duration_sd),
        duration_mode=duration_mode,
        duration_min=float(duration_min),
        duration_max=float(duration_max),
        velocity_mean=int(velocity_mean),
        velocity_sd=float(velocity_sd),
        velocity_mode=velocity_mode,
        seed=int(process_seed),
    )

    mutation_config = MutationConfig(
        transpose_probability=float(transpose_probability),
        transpose_intervals=transpose_intervals,
        invert_probability=float(invert_probability),
        retrograde_probability=float(retrograde_probability),
        rotate_probability=float(rotate_probability),
        rotate_steps=rotate_steps,
    )

    process = BirthDeathToneRowProcess(
        rows=input_rows,
        config=bd_config,
        mutation_config=mutation_config,
    )

    pitch_events, population_events = process.run()

    saved_path = pitch_events_to_midi(
        pitch_events=pitch_events,
        output_path=midi_path,
        bpm=int(bpm),
        ticks_per_beat=int(ticks_per_beat),
        base_octave=int(base_octave),
        octave_span=int(octave_span),
    )

    pitch_df = pitch_events_to_dataframe(pitch_events)
    pop_df = population_events_to_dataframe(population_events)

    st.subheader("Generated material")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Raw row")
        st.code(raw_row)

    with col2:
        st.write("P0 row")
        st.code(material.p0_row)

    st.subheader("Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Notes", len(pitch_events))
    c2.metric("Voices", process.next_voice_id)
    c3.metric("Max population", int(pop_df["population_size"].max()) if not pop_df.empty else 0)
    c4.metric("Mean population", round(float(pop_df["population_size"].mean()), 2) if not pop_df.empty else 0)

    st.subheader("Audio preview")

    wav_bytes = synthesize_midi_to_wav_bytes(saved_path)
    st.audio(wav_bytes, format="audio/wav")

    with open(saved_path, "rb") as file:
        st.download_button(
            label="Download MIDI",
            data=file,
            file_name=saved_path.name,
            mime="audio/midi",
        )

    st.subheader("Active voices animation")

    fig = build_population_animation(
        pop_df=pop_df,
        song_length=float(song_length),
        step_seconds=float(animation_step_seconds),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Event data")

    with st.expander("Pitch events"):
        st.dataframe(pitch_df)

    with st.expander("Population events"):
        st.dataframe(pop_df)

else:
    st.info("Set parameters in the sidebar, then click Generate.")