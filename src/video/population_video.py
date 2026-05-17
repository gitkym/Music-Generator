from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, FFMpegWriter


def build_population_frame_df(
    pop_df: pd.DataFrame,
    song_length: float,
    fps: int = 15,
) -> pd.DataFrame:
    step_seconds = 1 / fps
    frame_times = np.arange(0, song_length + step_seconds, step_seconds)

    population_at_frame = []

    for t in frame_times:
        past_events = pop_df[pop_df["time"] <= t]

        if past_events.empty:
            population_at_frame.append(0)
        else:
            population_at_frame.append(int(past_events["population_size"].iloc[-1]))

    return pd.DataFrame(
        {
            "time": frame_times,
            "population_size": population_at_frame,
        }
    )


def render_population_video(
    pop_df: pd.DataFrame,
    output_path: str | Path,
    song_length: float,
    fps: int = 15,
    width: int = 1280,
    height: int = 720,
    title: str = "Birth-death active voices over time",
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    anim_df = build_population_frame_df(
        pop_df=pop_df,
        song_length=song_length,
        fps=fps,
    )

    dpi = 100
    figsize = (width / dpi, height / dpi)

    max_population = max(1, int(anim_df["population_size"].max()) + 1)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    ax.set_xlim(0, song_length)
    ax.set_ylim(0, max_population)
    ax.set_title(title)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Active voices")
    ax.grid(True, alpha=0.3)

    line, = ax.step([], [], where="post", linewidth=2)
    point, = ax.plot([], [], marker="o", markersize=8)
    time_text = ax.text(
        0.02,
        0.92,
        "",
        transform=ax.transAxes,
        fontsize=12,
    )

    def init():
        line.set_data([], [])
        point.set_data([], [])
        time_text.set_text("")
        return line, point, time_text

    def update(frame_idx: int):
        frame_data = anim_df.iloc[: frame_idx + 1]

        x = frame_data["time"]
        y = frame_data["population_size"]

        line.set_data(x, y)
        point.set_data([x.iloc[-1]], [y.iloc[-1]])
        time_text.set_text(f"t = {x.iloc[-1]:.2f}s | voices = {y.iloc[-1]}")

        return line, point, time_text

    animation = FuncAnimation(
        fig,
        update,
        frames=len(anim_df),
        init_func=init,
        interval=1000 / fps,
        blit=True,
    )

    writer = FFMpegWriter(
        fps=fps,
        metadata={"artist": "stochastic_music"},
        bitrate=1800,
    )

    animation.save(str(output_path), writer=writer)
    plt.close(fig)

    return output_path