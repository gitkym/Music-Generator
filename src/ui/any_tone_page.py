from __future__ import annotations

from pathlib import Path

import streamlit as st

from any_tone.registry import TONICS
from pipeline.any_tone_generation_pipeline import run_any_tone_generation_pipeline
from processes.birth_death import BirthDeathConfig, MutationConfig


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCALE_FAMILIES = ["diatonic", "pentatonic", "diminished", "whole_tone", "arpeggio"]


def render_any_tone_page() -> None:
    st.title("Any-Tone Generator")
    st.caption("Scale-based birth-death process with generated piano audio and population video")

    controls = _render_any_tone_controls()

    if not controls["generate_button"]:
        st.info("Set parameters, then click Generate.")
        return

    with st.spinner("Generating music, audio, and video..."):
        result = run_any_tone_generation_pipeline(
            output_dir=PROJECT_ROOT / "generated",
            song_name=controls["song_name"],
            process_seed=controls["process_seed"],
            bpm=controls["bpm"],
            ticks_per_beat=controls["ticks_per_beat"],
            base_octave=controls["base_octave"],
            octave_span=controls["octave_span"],
            bd_config=controls["bd_config"],
            mutation_config=controls["mutation_config"],
            fps=controls["fps"],
            scale_id=controls["scale_id"],
            manual_pitch_classes=controls["manual_pitch_classes"],
            manual_display_name="Manual Any-Tone Scale",
        )

    _render_any_tone_result(result)


def _render_any_tone_controls() -> dict:
    st.subheader("Controls")

    with st.expander("Song Settings", expanded=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])

        with c1:
            song_name = st.text_input("Song name", value="any_tone_song_1")

        with c2:
            song_length = st.number_input("Song length", value=60.0, min_value=1.0, step=1.0)

        with c3:
            bpm = st.number_input("BPM", value=120, min_value=20, max_value=300, step=1)

        with c4:
            ticks_per_beat = st.number_input("Ticks per beat", value=480, min_value=24, step=24)

        with c5:
            fps = st.number_input("Video FPS", value=15, min_value=1, max_value=60, step=1)

    with st.expander("Any-Tone Material", expanded=True):
        c1, c2, c3 = st.columns(3)

        scale_id = None
        manual_pitch_classes = None

        with c1:
            input_mode = st.selectbox(
                "Scale input mode",
                ["Predefined scale", "Manual scale"],
                index=0,
            )

        if input_mode == "Predefined scale":
            with c2:
                tonic = st.selectbox("Tonic", TONICS, index=0)

            with c3:
                scale_family = st.selectbox("Scale family", SCALE_FAMILIES, index=0)

            if scale_family in ["diatonic", "pentatonic", "arpeggio"]:
                variant = st.selectbox("Variant", ["major", "minor"], index=0)
                scale_id = f"{_normalise_tonic_for_id(tonic)}_{scale_family}_{variant}"
            else:
                scale_id = f"{_normalise_tonic_for_id(tonic)}_{scale_family}"
                st.text_input("Variant", value="standard", disabled=True)

            st.caption(f"Selected scale ID: `{scale_id}`")

        else:
            manual_input = st.text_input(
                "Manual pitch classes",
                value="0, 2, 4, 7, 9",
                help="Enter unique integers from 0 to 11. Example: 0, 2, 4, 7, 9",
            )

            try:
                manual_pitch_classes = [
                    int(x.strip())
                    for x in manual_input.split(",")
                    if x.strip() != ""
                ]
            except Exception:
                manual_pitch_classes = None
                st.error("Manual scale must be a comma-separated list of integers.")

        c4, c5 = st.columns(2)

        with c4:
            base_octave = st.number_input("Base octave", value=4, min_value=0, max_value=9, step=1)

        with c5:
            octave_span = st.number_input("Octave span", value=3, min_value=1, max_value=8, step=1)

        st.markdown("**Allowed transformations:** rotation and retrograde rotation only.")

        r3c1, r3c2, r3c3, r3c4 = st.columns(4)

        with r3c1:
            st.number_input(
                "Transpose probability",
                value=0.0,
                min_value=0.0,
                max_value=0.0,
                step=0.0,
                disabled=True,
            )

        with r3c2:
            st.number_input(
                "Invert probability",
                value=0.0,
                min_value=0.0,
                max_value=0.0,
                step=0.0,
                disabled=True,
            )

        with r3c3:
            retrograde_probability = st.number_input(
                "Retrograde probability",
                value=0.25,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
            )

        with r3c4:
            rotate_probability = st.number_input(
                "Rotate probability",
                value=0.25,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
            )

    with st.expander("Population Dynamics", expanded=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            process_seed = st.number_input("Process seed", value=123, step=1)

        with c2:
            birth_rate = st.number_input(
                "Birth rate",
                value=0.12,
                min_value=0.0,
                step=0.01,
                format="%.4f",
            )

        with c3:
            death_rate = st.number_input(
                "Death rate",
                value=0.08,
                min_value=0.0,
                step=0.01,
                format="%.4f",
            )

        c4, c5, c6 = st.columns(3)

        with c4:
            initial_population = st.number_input("Initial population", value=2, min_value=0, step=1)

        with c5:
            min_population = st.number_input("Min population", value=1, min_value=0, step=1)

        with c6:
            max_population = st.number_input("Max population", value=12, min_value=1, step=1)

    with st.expander("Event Behaviour", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.selectbox("Note-rate mode", ["exponential"], index=0, disabled=True)

        with c2:
            note_rate_mean = st.number_input("Note-rate mean", value=2.5, min_value=0.01, step=0.1)

        with c3:
            note_rate_sd = st.number_input("Note-rate SD", value=0.35, min_value=0.0, step=0.05)

        with c4:
            st.number_input("Note-rate min", value=0.01, min_value=0.01, step=0.01, disabled=True)

        with c5:
            st.number_input("Note-rate max", value=999.0, min_value=0.01, step=1.0, disabled=True)

        d1, d2, d3, d4, d5 = st.columns(5)

        with d1:
            duration_mode = st.selectbox(
                "Duration mode",
                ["fixed", "normal", "uniform", "exponential"],
                index=1,
            )

        with d2:
            duration_mean = st.number_input("Duration mean", value=0.25, min_value=0.01, step=0.05)

        with d3:
            duration_sd = st.number_input("Duration SD", value=0.25, min_value=0.0, step=0.05)

        with d4:
            duration_min = st.number_input("Duration min", value=0.05, min_value=0.001, step=0.01)

        with d5:
            duration_max = st.number_input("Duration max", value=1.50, min_value=0.001, step=0.05)

        v1, v2, v3, v4, v5 = st.columns(5)

        with v1:
            velocity_mode = st.selectbox("Velocity mode", ["fixed", "normal", "uniform"], index=1)

        with v2:
            velocity_mean = st.number_input("Velocity mean", value=72, min_value=0, max_value=127, step=1)

        with v3:
            velocity_sd = st.number_input("Velocity SD", value=0.12, min_value=0.0, step=0.05)

        with v4:
            st.number_input("Velocity min", value=0, min_value=0, max_value=127, disabled=True)

        with v5:
            st.number_input("Velocity max", value=127, min_value=0, max_value=127, disabled=True)

    generate_button = st.button("Generate", use_container_width=True)

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
        transpose_probability=0.0,
        transpose_intervals=(),
        invert_probability=0.0,
        retrograde_probability=float(retrograde_probability),
        rotate_probability=float(rotate_probability),
        rotate_steps=tuple(range(1, 12)),
    )

    return {
        "generate_button": generate_button,
        "song_name": song_name,
        "scale_id": scale_id,
        "manual_pitch_classes": manual_pitch_classes,
        "process_seed": int(process_seed),
        "bpm": int(bpm),
        "ticks_per_beat": int(ticks_per_beat),
        "base_octave": int(base_octave),
        "octave_span": int(octave_span),
        "fps": int(fps),
        "bd_config": bd_config,
        "mutation_config": mutation_config,
    }


def _render_any_tone_result(result: dict) -> None:
    st.subheader("Generated material")

    scale = result["scale"]

    col1, col2 = st.columns(2)

    with col1:
        st.write("Selected scale")
        st.code(scale.display_name)

    with col2:
        st.write("Pitch classes")
        st.code(list(scale.pitch_classes))

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

    with st.expander("Any-tone rows"):
        row_records = []

        for row in result["scale_grid"].rows:
            row_records.append(
                {
                    "transformation_id": row.transformation_id,
                    "transformation_type": row.transformation_type,
                    "row_index": row.row_index,
                    "pitch_classes": list(row.pitch_classes),
                    "note_names": list(row.note_names),
                }
            )

        st.dataframe(row_records, use_container_width=True)


def _normalise_tonic_for_id(tonic: str) -> str:
    return tonic.lower().replace("#", "sharp")