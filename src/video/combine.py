from __future__ import annotations

from pathlib import Path

try:
    from moviepy import AudioFileClip, VideoFileClip
except ImportError:
    from moviepy.editor import AudioFileClip, VideoFileClip


def combine_audio_and_video(
    video_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
) -> Path:
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_clip = VideoFileClip(str(video_path))
    audio_clip = AudioFileClip(str(audio_path))

    if hasattr(video_clip, "with_audio"):
        final_clip = video_clip.with_audio(audio_clip)
    else:
        final_clip = video_clip.set_audio(audio_clip)

    final_clip.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=video_clip.fps,
    )

    video_clip.close()
    audio_clip.close()
    final_clip.close()

    return output_path