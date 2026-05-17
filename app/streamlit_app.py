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
    ## 12-Tone Generator

    The 12-Tone Generator uses a classic 12-pitch-class row as its source material. The row contains each pitch class from `0–11` exactly once.

    In this mode:

    - The input row can be randomly generated or manually entered
    - The row is normalised into a Prime row
    - The system derives Prime, Inversion, Retrograde, and Retrograde-Inversion forms
    - Transposition, inversion, retrograde, and rotation can occur during the birth-death process
    - This mode is the closer one to traditional 12-tone serial logic
    """)

    st.markdown("""
    ## Any-Tone Generator

    The Any-Tone Generator uses a selected pitch-class collection rather than a full 12-tone row.

    The predefined collections are:

    - **Diatonic**: 7 notes
    - **Pentatonic**: 5 notes
    - **Diminished**: 8 notes
    - **Whole tone**: 6 notes
    - **Arpeggio**: 3 notes

    In this mode:

    - The user selects a tonic and a scale family, or enters a manual pitch-class collection
    - The selected collection is expanded into a scale grid
    - The grid is generated using rotations and retrograde rotations
    - Transposition and inversion are disabled
    - The perceived major/minor quality is left to musical motion, register, repetition, and context rather than predefined major/minor mappings
    """)

    st.markdown("""
    ## Birth-Death Process

    A birth-death process is a stochastic process describing populations that evolve through random births and deaths over time.

    In this app:

    - Each active voice is treated as an evolving entity
    - Voices emit note events while alive
    - Voices may reproduce or terminate
    - Child voices inherit pitch material with possible mutations
    - Population size evolves dynamically through time
    - Event timings are generated from exponential waiting times

    The same broad population logic is used by both generator modes. The difference is the pitch material supplied to the process.
    """)

    st.markdown("---")

    st.header("Shared Song Settings")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Song name** | Output filename prefix used for MIDI, WAV and MP4 generation |
    | **Song length** | Total process runtime in seconds |
    | **BPM** | Tempo used when converting event times into MIDI timing |
    | **Ticks per beat** | MIDI timing resolution |
    | **Video FPS** | Frame rate of the rendered population animation |
    """)

    st.header("12-Tone Material")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Row source** | Selects between randomly generated or manually entered 12-tone rows |
    | **Row seed** | Random seed used when generating 12-tone rows |
    | **Manual input row** | User-defined ordered 12-pitch-class sequence |
    | **Input row** | Final 12-tone row entering the system |
    | **Prime row** | Normalised row where first pitch class is mapped to 0 |
    | **Transpose intervals** | Allowed chromatic transposition offsets for row mutation |
    | **Transpose probability** | Probability of transposition mutation during birth |
    | **Invert probability** | Probability of inversion mutation during birth |
    | **Retrograde probability** | Probability of retrograde mutation during birth |
    | **Rotate probability** | Probability of cyclic rotation mutation during birth |
    """)

    st.header("Any-Tone Material")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Scale input mode** | Selects between predefined pitch collections and manual pitch-class input |
    | **Tonic** | Starting pitch class used to build the selected collection |
    | **Scale family** | Diatonic, pentatonic, diminished, whole tone, or arpeggio |
    | **Manual pitch classes** | User-defined ordered pitch-class collection with fewer than 12 notes |
    | **Selected scale ID** | Internal ID for the selected any-tone collection |
    | **Allowed transformations** | Rotation and retrograde rotation only |
    | **Retrograde probability** | Probability of reversing a child row during birth |
    | **Rotate probability** | Probability of cyclically rotating a child row during birth |
    """)

    st.header("Shared Event Behaviour")

    st.markdown("""
    | Parameter | Description |
    |---|---|
    | **Base octave** | Central octave used for MIDI pitch mapping |
    | **Octave span** | Number of octaves available for note placement |
    | **Process seed** | Random seed for stochastic population evolution |
    | **Birth rate** | Rate parameter controlling voice reproduction frequency |
    | **Death rate** | Rate parameter controlling voice termination frequency |
    | **Initial population** | Number of voices active at process start |
    | **Min population** | Lower bound for active voices |
    | **Max population** | Upper bound for active voices |
    | **Note-rate mean** | Mean event density / note activity |
    | **Note-rate SD** | Variability of note-event timing |
    | **Duration mode** | Statistical model governing note durations |
    | **Duration mean** | Average note duration |
    | **Duration SD** | Variability of note durations |
    | **Duration min/max** | Lower and upper duration bounds |
    | **Velocity mode** | Statistical model governing MIDI velocities |
    | **Velocity mean** | Average MIDI velocity |
    | **Velocity SD** | Variability of MIDI velocity |
    """)

    st.stop()


if page == "Any-Tone Generator":
    render_any_tone_page()
    st.stop()


st.title("12-Tone Generator")
st.caption("12-tone birth-death process with generated piano audio and population video")

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