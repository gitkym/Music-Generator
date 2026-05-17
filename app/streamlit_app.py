from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from ui.widgets import render_navigation, render_controls
from pipeline.generation_pipeline import run_generation_pipeline
from ui.any_tone_page import render_any_tone_page


st.set_page_config(
    page_title="Stochastic Music Generator",
    layout="wide",
)

page = render_navigation()


if page == "Glossary":

    st.title("Glossary")

    st.markdown("""
    ## 12-Tone Method

    The 12-tone method is a compositional system developed by Arnold Schoenberg in which all 12 pitch classes are organised into an ordered sequence called a tone row.

    In this app:

    - A tone row is represented numerically using pitch classes `0–11`
    - The row acts as the base musical material for all generated voices
    - Transformations such as:
        - transposition
        - inversion
        - retrograde
        - rotation
      are probabilistically applied during the birth-death process
    - The app internally normalises rows into a Prime (P0) form for consistent transformation logic

    The system here is intentionally mechanical and stochastic rather than stylistically “human”.
    """)

    st.markdown("""
    ## Birth-Death Process

    A birth-death process is a stochastic process describing populations that evolve through random births and deaths over time.

    In this app:

    - Each active voice is treated as an evolving entity
    - Voices emit note events while alive
    - Voices may:
        - reproduce (birth)
        - terminate (death)
    - Child voices inherit tone-row material with possible mutations
    - Population size evolves dynamically through time
    - Event timings are generated from exponential waiting times

    The result is a continuously evolving population of interacting serial generators.
    """)

    st.markdown("---")

    st.header("Song Settings")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Song name** | Output filename prefix used for MIDI, WAV and MP4 generation |
    | **Song length** | Total process runtime in seconds |
    | **BPM** | Tempo used when converting event times into MIDI timing |
    | **Ticks per beat** | MIDI timing resolution |
    | **Video FPS** | Frame rate of the rendered population animation |
    """)

    st.header("Serial Material")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Row source** | Selects between randomly generated or manually entered tone rows |
    | **Row seed** | Random seed used when generating tone rows |
    | **Manual input row** | User-defined ordered pitch-class sequence |
    | **Input row** | Final row entering the system |
    | **Prime row** | Normalised row where first pitch class is mapped to 0 |
    | **Base octave** | Central octave used for MIDI pitch mapping |
    | **Octave span** | Number of octaves available for note placement |
    | **Transpose intervals** | Allowed transposition offsets for row mutation |
    | **Rotate steps** | Allowed cyclic row rotations |
    | **Transpose probability** | Probability of transposition mutation during birth |
    | **Invert probability** | Probability of inversion mutation during birth |
    | **Retrograde probability** | Probability of retrograde mutation during birth |
    | **Rotate probability** | Probability of cyclic rotation mutation during birth |
    """)

    st.header("Population Dynamics")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Process seed** | Random seed for stochastic population evolution |
    | **Birth rate** | Rate parameter controlling voice reproduction frequency |
    | **Death rate** | Rate parameter controlling voice termination frequency |
    | **Initial population** | Number of voices active at process start |
    | **Min population** | Lower bound for active voices |
    | **Max population** | Upper bound for active voices |
    """)

    st.header("Event Behaviour")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Note-rate mode** | Statistical model governing inter-event waiting times |
    | **Note-rate mean** | Mean event density / note activity |
    | **Note-rate SD** | Variability of note-event timing |
    | **Note-rate min/max** | Reserved bounds for future timing controls |
    | **Duration mode** | Statistical model governing note durations |
    | **Duration mean** | Average note duration |
    | **Duration SD** | Variability of note durations |
    | **Duration min/max** | Lower and upper duration bounds |
    | **Velocity mode** | Statistical model governing MIDI velocities |
    | **Velocity mean** | Average MIDI velocity |
    | **Velocity SD** | Variability of MIDI velocity |
    | **Velocity min/max** | Reserved bounds for future velocity clamping |
    """)

    st.stop()


if page == "Any-Tone Generator":
    render_any_tone_page()
    st.stop()


st.title("Stochastic Music Generator")
st.caption("12-tone birth-death process prototype with generated piano audio and population video")

controls = render_controls()

if not controls["generate_button"]:
    st.info("Set parameters, then click Generate.")
    st.stop()

with st.spinner("Generating music, audio, and video..."):
    result = run_generation_pipeline(
        output_dir=PROJECT_ROOT / "generated",
        song_name=controls["song_name"],
        row_seed=controls["row_seed"],
        process_seed=controls["process_seed"],
        bpm=controls["bpm"],
        ticks_per_beat=controls["ticks_per_beat"],
        base_octave=controls["base_octave"],
        octave_span=controls["octave_span"],
        bd_config=controls["bd_config"],
        mutation_config=controls["mutation_config"],
        fps=controls["fps"],
        input_row=controls["input_row"],
    )

st.subheader("Generated material")

col1, col2 = st.columns(2)

with col1:
    st.write("Input row")
    st.code(result["input_row"])

with col2:
    st.write("Prime row")
    st.code(result["prime_row"])

st.subheader("Summary")

pitch_df = result["pitch_df"]
population_df = result["population_df"]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Notes", len(result["pitch_events"]))
c2.metric("Voices", result["voice_count"])

if not population_df.empty:
    c3.metric("Max population", int(population_df["population_size"].max()))
    c4.metric("Mean population", round(float(population_df["population_size"].mean()), 2))
else:
    c3.metric("Max population", 0)
    c4.metric("Mean population", 0)

st.subheader("Population video with audio")

video_path = Path(result["video_path"])

if video_path.exists():
    st.video(str(video_path))
else:
    st.error(f"Video file was not created: {video_path}")

st.subheader("Downloads")

download_col1, download_col2, download_col3 = st.columns(3)

with download_col1:
    midi_path = Path(result["midi_path"])
    if midi_path.exists():
        with open(midi_path, "rb") as file:
            st.download_button(
                label="Download MIDI",
                data=file,
                file_name=midi_path.name,
                mime="audio/midi",
                use_container_width=True,
            )

with download_col2:
    wav_path = Path(result["wav_path"])
    if wav_path.exists():
        with open(wav_path, "rb") as file:
            st.download_button(
                label="Download WAV",
                data=file,
                file_name=wav_path.name,
                mime="audio/wav",
                use_container_width=True,
            )

with download_col3:
    if video_path.exists():
        with open(video_path, "rb") as file:
            st.download_button(
                label="Download MP4",
                data=file,
                file_name=video_path.name,
                mime="video/mp4",
                use_container_width=True,
            )

st.subheader("Event data")

with st.expander("Pitch events"):
    st.dataframe(pitch_df, use_container_width=True)

with st.expander("Population events"):
    st.dataframe(population_df, use_container_width=True)