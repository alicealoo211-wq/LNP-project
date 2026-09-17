"""
demo.py
=======

A COMPLETE, RUNNABLE example -- run this first to see the whole pipeline work.

It does NOT need any real simulation files or MDAnalysis. Instead it makes up
some pretend data that behaves the way a real nanoparticle would (curvature
staying low, then rising as the membrane changes shape), then runs the real
measurement, detection, and plotting code on it.

Run it from the starter folder with:
    python demo.py
"""

import numpy as np

from lnp_pipeline import composition, metrics, transition, visualize


def main():
    print("=" * 55)
    print("  LNP pipeline demo (using pretend data)")
    print("=" * 55)

    # 1) COMPOSITION -- pure arithmetic, no simulation needed ---------------
    recipe = {"ionizable": 50, "cholesterol": 38, "helper": 10, "peg": 2}
    fractions = composition.molar_fractions(recipe)
    ratio = composition.np_ratio(n_ionizable_amines=600, n_mrna_phosphates=100)
    print("\n[1] Composition")
    print("    Molar fractions:", {k: round(v, 3) for k, v in fractions.items()})
    print("    N/P ratio:", ratio)

    # 2) MEASUREMENTS over time --------------------------------------------
    # Pretend we measured the membrane at 10 time points. Early on it's flat
    # (low curvature); partway through it starts to bend (curvature rises).
    rng = np.random.default_rng(seed=0)
    curvature_over_time = []
    for frame in range(10):
        base = 0.1 if frame < 5 else 0.9          # jumps up at frame 5
        heights = rng.normal(loc=0.0, scale=base, size=200)
        curvature_over_time.append(metrics.membrane_curvature(heights))

    print("\n[2] Curvature measured each frame")
    print("    ", [round(c, 2) for c in curvature_over_time])

    # A quick one-off measurement example: angle between two lipid tails
    angle = metrics.tail_splay_angle([0, 0, 1], [0, 1, 1])
    print("    Example tail-splay angle:", round(angle, 1), "degrees")

    # 3) DETECT the transition ---------------------------------------------
    onset = transition.detect_transition(curvature_over_time, threshold=0.5)
    in_window = transition.in_target_window(onset, window_start=4, window_end=8)
    print("\n[3] Transition detection")
    print("    Shape change first detected at frame:", onset)
    print("    Happened inside the target window?", in_window)

    # 4) VISUALIZE ---------------------------------------------------------
    times = list(range(10))
    out = visualize.plot_metric_over_time(
        times, curvature_over_time, "curvature_demo.png",
        ylabel="Membrane curvature", onset_frame=onset,
    )
    print("\n[4] Saved graph to:", out)
    print("\nDone. Open curvature_demo.png to see the result.\n")


if __name__ == "__main__":
    main()
