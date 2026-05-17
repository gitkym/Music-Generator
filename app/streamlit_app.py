from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


# -------------------------
# Local imports
# -------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

from ui.widgets import render_sidebar
from pipeline.generation_pipeline import run_generation_pipeline


# -------------------------
# App setup
# -------------------------

st.set_page_config(
    page_title="Stochastic Music Generator",
    layout="wide",
)

st.title("Stochastic Music Generator")
st.caption("12-tone birth-death process prototype with generated piano audio and population video")


# -------------------------
# Controls
# -------------------------

controls = render_sidebar()


# -------------------------
# Main app
# -------------------------

if not controls["generate_button"]:
    st.info("Set parameters in the sidebar, then click Generate.")
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
    )


# -------------------------
# Summary
# -------------------------

st.subheader("Generated material")

col1, col2 = st.columns(2)

with col1:
    st.write("Raw row")
    st.code(result["raw_row"])

with col2:
    st.write("P0 row")
    st.code(result["p0_row"])


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


# -------------------------
# Video playback
# -------------------------

st.subheader("Population video with audio")

video_path = Path(result["video_path"])

if video_path.exists():
    st.video(str(video_path))
else:
    st.error(f"Video file was not created: {video_path}")


# -------------------------
# Downloads
# -------------------------

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


# -------------------------
# Event data
# -------------------------

st.subheader("Event data")

with st.expander("Pitch events"):
    st.dataframe(pitch_df, use_container_width=True)

with st.expander("Population events"):
    st.dataframe(population_df, use_container_width=True)