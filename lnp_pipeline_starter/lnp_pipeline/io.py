"""
io.py
=====

Opens real simulation files.

Simulation results come as two files: a "topology" (what the particles ARE)
and a "trajectory" (where they MOVE over time). The MDAnalysis library reads
both and hands you a single object -- called a "Universe" -- that you can ask
questions about.

NOTE: MDAnalysis is only imported when you actually call load_universe(), so
the rest of the toolkit (and the demo) runs even before you've installed it.
Install it later with:  pip install MDAnalysis
"""


def load_universe(topology_file, trajectory_file):
    """
    Load a simulation into an MDAnalysis Universe.

    Example (once you have real files and MDAnalysis installed):
        u = load_universe("system.gro", "trajectory.xtc")
        print(len(u.atoms), "particles")
        print(len(u.trajectory), "frames")

    Returns the Universe object, which the other modules can measure.
    """
    try:
        import MDAnalysis as mda
    except ImportError as err:
        raise ImportError(
            "MDAnalysis is not installed yet. Install it with:\n"
            "    pip install MDAnalysis"
        ) from err

    return mda.Universe(topology_file, trajectory_file)


def surface_heights_from_universe(universe, atom_selection="name PO4"):
    """
    Pull the height (z-position) of chosen atoms from the current frame.

    `atom_selection` is written in MDAnalysis' selection language. The default
    "name PO4" grabs the phosphate beads that sit on the membrane surface in
    coarse-grained models. The result can be fed straight into
    metrics.membrane_curvature().
    """
    selected = universe.select_atoms(atom_selection)
    return selected.positions[:, 2]  # column 2 is the z-axis (height)
