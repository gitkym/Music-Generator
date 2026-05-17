from __future__ import annotations

from pathlib import Path

from material.twelve_tone import (
    generate_row,
    TwelveToneMaterial,
)

from processes.birth_death import (
    BirthDeathConfig,
    MutationConfig,
    BirthDeathToneRowProcess,
)

from rendering.midi import (
    pitch_events_to_midi,
)

from audio.synthesis import (
    synthesize_midi_to_wav,
)

from video.population_video import (
    render_population_video,
)

from video.combine import (
    combine_audio_and_video,
)

from analysis.stats import (
    pitch_events_to_dataframe,
    population_events_to_dataframe,
)


def run_generation_pipeline(
    output_dir: str | Path,
    song_name: str,
    row_seed: int,
    process_seed: int,
    bpm: int,
    ticks_per_beat: int,
    base_octave: int,
    octave_span: int,
    bd_config: BirthDeathConfig,
    mutation_config: MutationConfig,
    fps: int = 15,
):
    output_dir = Path(output_dir)

    midi_dir = output_dir / "midi"
    audio_dir = output_dir / "audio"
    video_dir = output_dir / "video"

    midi_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    raw_row = generate_row(
        modulus=12,
        seed=row_seed,
    )

    material = TwelveToneMaterial(
        raw_row=raw_row,
        normalise=True,
    )

    input_rows = [
        material.get_form("P", 0).row,
        material.get_form("I", 0).row,
        material.get_form("R", 0).row,
        material.get_form("RI", 0).row,
    ]

    process = BirthDeathToneRowProcess(
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
    )

    wav_path = audio_dir / f"{song_name}.wav"

    synthesize_midi_to_wav(
        midi_path=midi_path,
        wav_path=wav_path,
    )

    pop_df = population_events_to_dataframe(population_events)

    silent_video_path = video_dir / f"{song_name}_silent.mp4"

    render_population_video(
        pop_df=pop_df,
        output_path=silent_video_path,
        song_length=bd_config.song_length,
        fps=fps,
    )

    final_video_path = video_dir / f"{song_name}.mp4"

    combine_audio_and_video(
        video_path=silent_video_path,
        audio_path=wav_path,
        output_path=final_video_path,
    )

    return {
        "raw_row": raw_row,
        "p0_row": material.p0_row,
        "pitch_events": pitch_events,
        "population_events": population_events,
        "pitch_df": pitch_events_to_dataframe(pitch_events),
        "population_df": pop_df,
        "midi_path": midi_path,
        "wav_path": wav_path,
        "video_path": final_video_path,
        "voice_count": process.next_voice_id,
    }