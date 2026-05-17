from __future__ import annotations

import streamlit as st

from material.twelve_tone import (
    generate_row,
    TwelveToneMaterial,
    validate_row,
)

from processes.birth_death import (
    BirthDeathConfig,
    MutationConfig,
)


def render_navigation() -> str:
    st.sidebar.title("Stochastic Music")
    return st.sidebar.radio(
        "Page",
        ["Generator", "Glossary"],
        index=0,
    )


def _parse_int_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(x.strip()) for x in text.split(",") if x.strip())


def _parse_row(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def _format_row(row: list[int] | None) -> str:
    if row is None:
        return ""
    return ", ".join(str(x) for x in row)


def render_controls():
    st.subheader("Controls")

    input_row = None
    prime_row = []
    row_valid = True
    config_valid = True

    with st.expander("Song Settings", expanded=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])

        with c1:
            song_name = st.text_input("Song name", value="song_1")

        with c2:
            song_length = st.number_input("Song length", value=60.0, min_value=1.0, step=1.0)

        with c3:
            bpm = st.number_input("BPM", value=120, min_value=20, max_value=300, step=1)

        with c4:
            ticks_per_beat = st.number_input("Ticks per beat", value=480, min_value=24, step=24)

        with c5:
            fps = st.number_input("Video FPS", value=15, min_value=1, max_value=60, step=1)

    with st.expander("Serial Material", expanded=True):
        c1, c2, c3 = st.columns([1, 1, 2])

        with c1:
            row_source = st.selectbox("Row source", ["Random", "Manual"], index=0)

        with c2:
            row_seed = st.number_input(
                "Row seed",
                value=42,
                step=1,
                disabled=(row_source == "Manual"),
            )

        with c3:
            manual_row_text = st.text_input(
                "Manual input row",
                value="0,1,2,3,4,5,6,7,8,9,10,11",
                disabled=(row_source == "Random"),
            )

        try:
            if row_source == "Random":
                input_row = generate_row(modulus=12, seed=int(row_seed))
            else:
                input_row = _parse_row(manual_row_text)
                validate_row(input_row)

            material_preview = TwelveToneMaterial(raw_row=input_row, normalise=True)
            prime_row = material_preview.p0_row

        except Exception as exc:
            row_valid = False
            input_row = None
            prime_row = []
            st.error(f"Invalid row: {exc}")

        c4, c5 = st.columns(2)

        with c4:
            st.text_input("Input row", value=_format_row(input_row), disabled=True)

        with c5:
            st.text_input("Prime row", value=_format_row(prime_row), disabled=True)

        r2c1, r2c2, r2c3, r2c4 = st.columns(4)

        with r2c1:
            base_octave = st.number_input("Base octave", value=4, min_value=0, max_value=9, step=1)

        with r2c2:
            octave_span = st.number_input("Octave span", value=3, min_value=1, max_value=8, step=1)

        with r2c3:
            transpose_intervals_text = st.text_input(
                "Transpose intervals",
                value="-6,-5,-3,-2,1,2,3,5,6",
            )

        with r2c4:
            rotate_steps_text = st.text_input("Rotate steps", value="1,2,3,4,5,6")

        r3c1, r3c2, r3c3, r3c4 = st.columns(4)

        with r3c1:
            transpose_probability = st.number_input(
                "Transpose probability", value=0.45, min_value=0.0, max_value=1.0, step=0.05
            )

        with r3c2:
            invert_probability = st.number_input(
                "Invert probability", value=0.20, min_value=0.0, max_value=1.0, step=0.05
            )

        with r3c3:
            retrograde_probability = st.number_input(
                "Retrograde probability", value=0.25, min_value=0.0, max_value=1.0, step=0.05
            )

        with r3c4:
            rotate_probability = st.number_input(
                "Rotate probability", value=0.25, min_value=0.0, max_value=1.0, step=0.05
            )

    with st.expander("Population Dynamics", expanded=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            process_seed = st.number_input("Process seed", value=123, step=1)

        with c2:
            birth_rate = st.number_input(
                "Birth rate", value=0.12, min_value=0.0, step=0.01, format="%.4f"
            )

        with c3:
            death_rate = st.number_input(
                "Death rate", value=0.08, min_value=0.0, step=0.01, format="%.4f"
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

    try:
        transpose_intervals = _parse_int_tuple(transpose_intervals_text)
        rotate_steps = _parse_int_tuple(rotate_steps_text)
    except Exception as exc:
        config_valid = False
        transpose_intervals = ()
        rotate_steps = ()
        st.error(f"Invalid mutation configuration: {exc}")

    if not row_valid or not config_valid:
        generate_button = False

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

    return {
        "generate_button": generate_button,
        "song_name": song_name,
        "row_seed": int(row_seed),
        "input_row": input_row,
        "prime_row": prime_row,
        "process_seed": int(process_seed),
        "bpm": int(bpm),
        "ticks_per_beat": int(ticks_per_beat),
        "base_octave": int(base_octave),
        "octave_span": int(octave_span),
        "fps": int(fps),
        "bd_config": bd_config,
        "mutation_config": mutation_config,
    }