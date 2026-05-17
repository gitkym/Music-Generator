from __future__ import annotations

from pathlib import Path

from any_tone.generator import generate_any_tone_grid
from processes.birth_death import BirthDeathConfig, MutationConfig
from processes.any_tone_birth_death import BirthDeathAnyToneProcess

from rendering.midi import pitch_events_to_midi
from audio.synthesis import synthesize_midi_to_wav
from video.population_video import render_population_video
from video.combine import combine_audio_and_video

from analysis.stats import (
    pitch_events_to_dataframe,
    population_events_to_dataframe,
)


def run_any_tone_generation_pipeline(
    output_dir: str | Path,
    song_name: str,
    process_seed: int,
    bpm: int,
    ticks_per_beat: int,
    base_octave: int,
    octave_span: int,
    bd_config: BirthDeathConfig,
    mutation_config: MutationConfig,
    fps: int = 15,
    scale_id: str | None = None,
    manual_pitch_classes: list[int] | tuple[int, ...] | None = None,
    manual_display_name: str = "Manual Any-Tone Scale",
):
    output_dir = Path(output_dir)

    midi_dir = output_dir / "midi"
    audio_dir = output_dir / "audio"
    video_dir = output_dir / "video"

    midi_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    grid = generate_any_tone_grid(
        scale_id=scale_id,
        manual_pitch_classes=manual_pitch_classes,
        manual_display_name=manual_display_name,
    )

    input_rows = [list(row.pitch_classes) for row in grid.rows]

    bd_config.seed = int(process_seed)

    process = BirthDeathAnyToneProcess(
        rows=input_rows,
        config=bd_config,
        mutation_config=mutation_config,
    )

    pitch_events, population_events = process.run()

    midi_path = midi_dir / f"{song_name}.mid"

    pitch_events_to_midi(
        pitch_events=pitch_events,
        output_path=midi_path,
        bpm=bpm,
        ticks_per_beat=ticks_per_beat,
        base_octave=base_octave,
        octave_span=octave_span,
        track_name="birth_death_anytone",
    )

    wav_path = audio_dir / f"{song_name}.wav"

    synthesize_midi_to_wav(
        midi_path=midi_path,
        wav_path=wav_path,
    )

    population_df = population_events_to_dataframe(population_events)

    silent_video_path = video_dir / f"{song_name}_silent.mp4"

    render_population_video(
        pop_df=population_df,
        output_path=silent_video_path,
        song_length=bd_config.song_length,
        fps=fps,
        title="Any-tone birth-death active voices over time",
    )

    final_video_path = video_dir / f"{song_name}.mp4"

    combine_audio_and_video(
        video_path=silent_video_path,
        audio_path=wav_path,
        output_path=final_video_path,
    )

    pitch_df = pitch_events_to_dataframe(pitch_events)

    return {
        "mode": "any_tone",
        "scale": grid.scale,
        "scale_grid": grid,
        "input_rows": input_rows,
        "input_row": list(grid.scale.pitch_classes),
        "raw_row": list(grid.scale.pitch_classes),
        "p0_row": list(grid.scale.pitch_classes),
        "prime_row": list(grid.scale.pitch_classes),
        "pitch_events": pitch_events,
        "population_events": population_events,
        "pitch_df": pitch_df,
        "population_df": population_df,
        "midi_path": midi_path,
        "wav_path": wav_path,
        "video_path": final_video_path,
        "voice_count": process.next_voice_id,
    }