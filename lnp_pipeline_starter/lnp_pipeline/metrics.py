"""
metrics.py
==========

The measurement routines -- the heart of the project.

Each function takes particle positions (as arrays of numbers) and returns a
single number describing one structural feature. These are the "science
signals" that change when the nanoparticle is about to break open.

We use NumPy, a Python toolbox for doing math on lots of numbers at once.
"""

import numpy as np


def membrane_curvature(surface_heights):
    """
    A simple measure of how bumpy / curved the membrane surface is.

    `surface_heights` is a list of the height (z-position) of many points on
    the membrane surface. A perfectly flat sheet has all the same height, so
    the spread is 0. As the membrane bends, the heights spread out, so a
    LARGER number means MORE curvature.

    (This is a simplified proxy. Real analyses fit a curved surface; the idea
    is the same: measure how far the surface departs from flat.)
    """
    heights = np.asarray(surface_heights, dtype=float)
    return float(np.std(heights))


def tail_splay_angle(tail_vector_a, tail_vector_b):
    """
    The angle (in degrees) between two lipid-tail directions.

    Each tail can be described by an arrow (a vector) pointing along its
    length. When lipids pack neatly the tails are nearly parallel (small
    angle). When the structure reorganizes, the tails splay apart (bigger
    angle).
    """
    a = np.asarray(tail_vector_a, dtype=float)
    b = np.asarray(tail_vector_b, dtype=float)
    cosine = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    cosine = np.clip(cosine, -1.0, 1.0)  # guard against tiny rounding errors
    return float(np.degrees(np.arccos(cosine)))


def water_penetration_depth(water_z_positions, membrane_surface_z):
    """
    How far the deepest water molecule has pushed past the membrane surface.

    `water_z_positions` are the heights of water beads. `membrane_surface_z`
    is the height of the outer membrane surface. If water sits below the
    surface, it has penetrated. A bigger number means water is getting deeper
    inside -- a sign the structure is destabilizing.

    Returns 0 if no water has crossed the surface.
    """
    water = np.asarray(water_z_positions, dtype=float)
    depth = membrane_surface_z - water.min()
    return float(max(depth, 0.0))
