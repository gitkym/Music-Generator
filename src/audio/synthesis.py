from __future__ import annotations

from pathlib import Path

import numpy as np
import pretty_midi
from scipy.io import wavfile


def synthesize_midi_to_wav(
    midi_path: str | Path,
    wav_path: str | Path,
    sample_rate: int = 44100,
    normalize: bool = True,
) -> Path:
    midi_path = Path(midi_path)
    wav_path = Path(wav_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)

    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    audio = midi_data.synthesize(fs=sample_rate)

    if normalize:
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio / peak

    audio_int16 = np.int16(audio * 32767)
    wavfile.write(wav_path, sample_rate, audio_int16)

    return wav_path