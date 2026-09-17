"""
visualize.py
============

Makes graphs from your results using Matplotlib, a Python plotting toolbox.

Later, molecular 3D images and animations come from VMD (separate software).
This module handles the quantitative graphs -- e.g. a curve showing curvature
rising over time, with the detected transition marked.
"""

import matplotlib
matplotlib.use("Agg")  # "Agg" saves images to files without needing a screen
import matplotlib.pyplot as plt


def plot_metric_over_time(times, values, output_path,
                          ylabel="Measurement", onset_frame=None):
    """
    Draw a metric (like curvature) against time and save it as an image.

    `times`   : list of frame/time numbers (the x-axis)
    `values`  : the measurement at each time (the y-axis)
    `output_path` : where to save the picture, e.g. "curvature.png"
    `onset_frame` : optional -- if given, draws a vertical line marking where
                    the transition was detected.
    """
    plt.figure(figsize=(7, 4))
    plt.plot(times, values, marker="o", linewidth=2, label=ylabel)

    if onset_frame is not None:
        plt.axvline(times[onset_frame], color="red", linestyle="--",
                    label="Transition detected")

    plt.xlabel("Time (frame)")
    plt.ylabel(ylabel)
    plt.title(ylabel + " over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    return output_path
