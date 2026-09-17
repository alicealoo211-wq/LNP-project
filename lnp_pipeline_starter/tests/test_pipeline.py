"""
test_pipeline.py
================

Unit tests -- small checks that prove each function gives the right answer on
an example we already know by hand. This is how you show your code works.

Run them from the starter folder with:
    python -m pytest        (if you've installed pytest)
or simply:
    python tests/test_pipeline.py
"""

import os
import sys

# make the package importable when running this file directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lnp_pipeline import composition, metrics, transition


def test_np_ratio():
    assert composition.np_ratio(600, 100) == 6.0


def test_molar_fractions_sum_to_one():
    fr = composition.molar_fractions({"a": 1, "b": 3})
    assert abs(sum(fr.values()) - 1.0) < 1e-9
    assert fr["a"] == 0.25


def test_flat_membrane_has_zero_curvature():
    assert metrics.membrane_curvature([5, 5, 5, 5]) == 0.0


def test_parallel_tails_have_zero_angle():
    assert metrics.tail_splay_angle([0, 0, 1], [0, 0, 2]) == 0.0


def test_detect_transition_finds_crossing():
    assert transition.detect_transition([0.1, 0.2, 0.9, 1.0], 0.8) == 2


def test_detect_transition_returns_none_when_never_crosses():
    assert transition.detect_transition([0.1, 0.2, 0.3], 0.8) is None


if __name__ == "__main__":
    # a tiny test runner so you don't need pytest installed
    passed = 0
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print("PASS:", name)
            passed += 1
    print(f"\nAll {passed} tests passed.")
