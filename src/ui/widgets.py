from __future__ import annotations

import streamlit as st

from processes.birth_death import (
    BirthDeathConfig,
    MutationConfig,
)


def render_sidebar():
    st.sidebar.header("Seeds")

    row_seed = st.sidebar.number_input(
        "Row seed",
        value=42,
        step=1,
    )

    process_seed = st.sidebar.number_input(
        "Process seed",
        value=123,
        step=1,
    )

    st.sidebar.header("Song")

    song_name = st.sidebar.text_input(
        "Song name",
        value="birth_death_streamlit_test",
    )

    bpm = st.sidebar.number_input(
        "BPM",
        value=120,
        min_value=20,
        max_value=300,
        step=1,
    )

    song_length = st.sidebar.number_input(
        "Song length seconds",
        value=60.0,
        min_value=1.0,
        step=1.0,
    )

    ticks_per_beat = st.sidebar.number_input(
        "Ticks per beat",
        value=480,
        min_value=24,
        step=24,
    )

    base_octave = st.sidebar.number_input(
        "Base octave",
        value=4,
        min_value=0,
        max_value=9,
        step=1,
    )

    octave_span = st.sidebar.number_input(
        "Octave span",
        value=3,
        min_value=1,
        max_value=8,
        step=1,
    )

    st.sidebar.header("Population")

    initial_population = st.sidebar.number_input(
        "Initial population",
        value=2,
        min_value=0,
        step=1,
    )

    min_population = st.sidebar.number_input(
        "Min population",
        value=1,
        min_value=0,
        step=1,
    )

    max_population = st.sidebar.number_input(
        "Max population",
        value=12,
        min_value=1,
        step=1,
    )

    birth_rate = st.sidebar.number_input(
        "Birth rate",
        value=0.12,
        min_value=0.0,
        step=0.01,
        format="%.4f",
    )

    death_rate = st.sidebar.number_input(
        "Death rate",
        value=0.08,
        min_value=0.0,
        step=0.01,
        format="%.4f",
    )

    st.sidebar.header("Notes")

    note_rate_mean = st.sidebar.number_input(
        "Note rate mean",
        value=2.5,
        min_value=0.01,
        step=0.1,
    )

    note_rate_sd = st.sidebar.number_input(
        "Note rate SD",
        value=0.35,
        min_value=0.0,
        step=0.05,
    )

    duration_mean = st.sidebar.number_input(
        "Duration mean",
        value=0.25,
        min_value=0.01,
        step=0.05,
    )

    duration_sd = st.sidebar.number_input(
        "Duration SD",
        value=0.25,
        min_value=0.0,
        step=0.05,
    )

    duration_mode = st.sidebar.selectbox(
        "Duration mode",
        ["fixed", "normal", "uniform", "exponential"],
        index=1,
    )

    duration_min = st.sidebar.number_input(
        "Duration min",
        value=0.05,
        min_value=0.001,
        step=0.01,
    )

    duration_max = st.sidebar.number_input(
        "Duration max",
        value=1.50,
        min_value=0.001,
        step=0.05,
    )

    velocity_mean = st.sidebar.number_input(
        "Velocity mean",
        value=72,
        min_value=0,
        max_value=127,
        step=1,
    )

    velocity_sd = st.sidebar.number_input(
        "Velocity SD",
        value=0.12,
        min_value=0.0,
        step=0.05,
    )

    velocity_mode = st.sidebar.selectbox(
        "Velocity mode",
        ["fixed", "normal", "uniform"],
        index=1,
    )

    st.sidebar.header("Mutations")

    transpose_probability = st.sidebar.number_input(
        "Transpose probability",
        value=0.45,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
    )

    transpose_intervals_text = st.sidebar.text_input(
        "Transpose intervals",
        value="-6,-5,-3,-2,1,2,3,5,6",
    )

    invert_probability = st.sidebar.number_input(
        "Invert probability",
        value=0.20,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
    )

    retrograde_probability = st.sidebar.number_input(
        "Retrograde probability",
        value=0.25,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
    )

    rotate_probability = st.sidebar.number_input(
        "Rotate probability",
        value=0.25,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
    )

    rotate_steps_text = st.sidebar.text_input(
        "Rotate steps",
        value="1,2,3,4,5,6",
    )

    fps = st.sidebar.number_input(
        "Video FPS",
        value=15,
        min_value=1,
        max_value=60,
        step=1,
    )

    generate_button = st.sidebar.button(
        "Generate",
        use_container_width=True,
    )

    transpose_intervals = tuple(
        int(x.strip())
        for x in transpose_intervals_text.split(",")
        if x.strip()
    )

    rotate_steps = tuple(
        int(x.strip())
        for x in rotate_steps_text.split(",")
        if x.strip()
    )

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
        "process_seed": int(process_seed),
        "bpm": int(bpm),
        "ticks_per_beat": int(ticks_per_beat),
        "base_octave": int(base_octave),
        "octave_span": int(octave_span),
        "fps": int(fps),
        "bd_config": bd_config,
        "mutation_config": mutation_config,
    }