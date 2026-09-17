"""
lnp_pipeline
============

A small, beginner-friendly toolkit for analyzing lipid nanoparticle (LNP)
molecular dynamics simulations.

The package is split into small files ("modules"), each with ONE job:

    io.py           -> open simulation files
    metrics.py      -> measure structural features (curvature, tail angle, water)
    transition.py   -> detect WHEN the shape change happens
    composition.py  -> compute recipe numbers like the N/P ratio
    visualize.py    -> make graphs

Nothing here is magic. Each function takes some numbers in and gives numbers
(or a picture) out. Start by reading composition.py -- it's the simplest.
"""

__version__ = "0.1.0"
