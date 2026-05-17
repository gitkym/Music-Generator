from __future__ import annotations

from pathlib import Path
import subprocess

import mido
import numpy as np
import pretty_midi
import IPython.display as ipd

from processes.birth_death import PitchClassEvent


def seconds_to_ticks(
    time_seconds: float,
    bpm: float = 120,
    ticks_per_beat: int = 480,
) -> int:
    return int(round((time_seconds * bpm / 60) * ticks_per_beat))


def pitch_class_to_midi_note(
    pitch_class: int,
    base_octave: int = 4,
    octave_span: int = 3,
    voice_id: int = 0,
) -> int:
    octave = base_octave + (voice_id % octave_span)
    midi_note = int(pitch_class) + 12 * octave

    return int(max(0, min(127, midi_note)))


def pitch_events_to_midi(
    pitch_events: list[PitchClassEvent],
    output_path: str | Path,
    bpm: int = 120,
    ticks_per_beat: int = 480,
    base_octave: int = 4,
    octave_span: int = 3,
    track_name: str = "birth_death_12tone",
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    midi = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    midi.tracks.append(track)

    track.append(
        mido.MetaMessage(
            "set_tempo",
            tempo=mido.bpm2tempo(bpm),
            time=0,
        )
    )

    track.append(
        mido.MetaMessage(
            "track_name",
            name=track_name,
            time=0,
        )
    )

    midi_events = []

    for event in sorted(pitch_events, key=lambda e: e.time):
        note = pitch_class_to_midi_note(
            pitch_class=event.pitch_class,
            base_octave=base_octave,
            octave_span=octave_span,
            voice_id=event.voice_id,
        )

        start_tick = seconds_to_ticks(
            event.time,
            bpm=bpm,
            ticks_per_beat=ticks_per_beat,
        )

        end_tick = start_tick + seconds_to_ticks(
            event.duration,
            bpm=bpm,
            ticks_per_beat=ticks_per_beat,
        )

        midi_events.append(
            (
                start_tick,
                mido.Message(
                    "note_on",
                    note=note,
                    velocity=event.velocity,
                    time=0,
                ),
            )
        )

        midi_events.append(
            (
                end_tick,
                mido.Message(
                    "note_off",
                    note=note,
                    velocity=0,
                    time=0,
                ),
            )
        )

    midi_events.sort(key=lambda x: x[0])

    previous_tick = 0

    for absolute_tick, message in midi_events:
        message.time = max(0, absolute_tick - previous_tick)
        track.append(message)
        previous_tick = absolute_tick

    midi.save(output_path)

    return output_path


def play_midi_in_notebook(
    midi_path: str | Path,
    sample_rate: int = 44100,
    normalize: bool = True,
):
    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    audio = midi_data.synthesize(fs=sample_rate)

    if normalize:
        peak = np.max(np.abs(audio))

        if peak > 0:
            audio = audio / peak

    return ipd.Audio(audio, rate=sample_rate)


def open_in_reaper(midi_path: str | Path) -> None:
    midi_path = Path(midi_path)

    possible_paths = [
        r"C:\Program Files\REAPER (x64)\reaper.exe",
        r"C:\Program Files\REAPER\reaper.exe",
    ]

    for path in possible_paths:
        if Path(path).exists():
            subprocess.Popen([path, str(midi_path)])
            print(f"Opened in REAPER: {midi_path}")
            return

    print(f"REAPER not found automatically. MIDI saved here: {midi_path}")