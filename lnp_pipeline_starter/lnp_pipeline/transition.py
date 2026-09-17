"""
transition.py
=============

Finds WHEN the shape change (the Lalpha -> HII phase transition) happens.

A simulation is a series of frames over time. If we measure curvature at every
frame, we get a list of numbers that starts low and rises as the particle
changes shape. This module finds the first frame where the measurement crosses
a chosen threshold -- that is the "onset" of the change.
"""

import numpy as np


def detect_transition(time_series, threshold):
    """
    Find the first frame where a measurement crosses `threshold`.

    `time_series` is a list of measurements, one per frame (e.g. curvature at
    each moment in time). Returns the index (frame number) of the first value
    that reaches or exceeds the threshold, or None if it never does.

    Example:
        >>> detect_transition([0.1, 0.2, 0.9, 1.0], threshold=0.8)
        2
    """
    series = np.asarray(time_series, dtype=float)
    crossed = np.where(series >= threshold)[0]
    if len(crossed) == 0:
        return None
    return int(crossed[0])


def in_target_window(onset_frame, window_start, window_end):
    """
    Check whether the transition happened at the right time.

    We want the nanoparticle to break open inside the "late endosome" window,
    not too early and not too late. Given the frame where the change started,
    this returns True if it falls between window_start and window_end.
    """
    if onset_frame is None:
        return False
    return window_start <= onset_frame <= window_end
