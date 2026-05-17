import streamlit as st

from any_tone.generator import generate_any_tone_records
from any_tone.registry import TONICS


SCALE_FAMILIES = ["diatonic", "pentatonic", "diminished", "whole_tone", "arpeggio"]


def render_any_tone_page() -> None:
    st.header("Any-Tone Generator")

    st.info(
        "This page currently tests scale-grid generation only. "
        "It is not yet connected to the full audio/video pipeline."
    )

    input_mode = st.radio(
        "Scale input mode",
        ["Predefined scale", "Manual scale"],
        horizontal=True,
    )

    if input_mode == "Predefined scale":
        _render_predefined_scale_ui()
    else:
        _render_manual_scale_ui()


def _render_predefined_scale_ui() -> None:
    tonic = st.selectbox("Tonic", TONICS, index=0)

    scale_family = st.selectbox(
        "Scale family",
        SCALE_FAMILIES,
        index=0,
    )

    if scale_family in ["diatonic", "pentatonic", "arpeggio"]:
        variant = st.selectbox("Variant", ["major", "minor"], index=0)
        scale_id = f"{_normalise_tonic_for_id(tonic)}_{scale_family}_{variant}"
    else:
        scale_id = f"{_normalise_tonic_for_id(tonic)}_{scale_family}"

    st.caption(f"Selected scale ID: `{scale_id}`")

    if st.button("Generate any-tone grid", key="generate_predefined_any_tone_grid"):
        records = generate_any_tone_records(scale_id=scale_id)

        st.subheader("Generated scale grid")
        st.dataframe(records, use_container_width=True)


def _render_manual_scale_ui() -> None:
    manual_input = st.text_input(
        "Manual pitch classes",
        value="0, 2, 4, 7, 9",
        help="Enter unique integers from 0 to 11. Example: 0, 2, 4, 7, 9",
    )

    if st.button("Generate manual any-tone grid", key="generate_manual_any_tone_grid"):
        try:
            pitch_classes = [
                int(x.strip())
                for x in manual_input.split(",")
                if x.strip() != ""
            ]

            records = generate_any_tone_records(
                manual_pitch_classes=pitch_classes,
                manual_display_name="Manual Any-Tone Scale",
            )

            st.subheader("Generated manual scale grid")
            st.dataframe(records, use_container_width=True)

        except Exception as exc:
            st.error(f"Could not generate manual scale: {exc}")


def _normalise_tonic_for_id(tonic: str) -> str:
    return tonic.lower().replace("#", "sharp")