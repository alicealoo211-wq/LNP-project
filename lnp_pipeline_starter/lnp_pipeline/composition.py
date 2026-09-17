"""
composition.py
==============

The simplest module -- a good place to start reading.

These functions describe a lipid "recipe" using plain numbers. They do NOT
need a simulation file; they just do arithmetic on the composition.
"""


def np_ratio(n_ionizable_amines, n_mrna_phosphates):
    """
    Compute the N/P ratio.

    "N" = the number of positively-chargeable nitrogen (amine) groups on the
          ionizable lipids.
    "P" = the number of negatively-charged phosphate groups on the mRNA.

    The N/P ratio is just N divided by P. It tells you the charge balance of
    the formulation -- a number formulation scientists care about a lot.

    Example:
        >>> np_ratio(600, 100)
        6.0
    """
    if n_mrna_phosphates <= 0:
        raise ValueError("Number of phosphates must be greater than zero.")
    return n_ionizable_amines / n_mrna_phosphates


def molar_fractions(component_counts):
    """
    Turn a count of each lipid type into fractions that add up to 1.0.

    `component_counts` is a dictionary like:
        {"ionizable": 50, "cholesterol": 38, "helper": 10, "peg": 2}

    Returns a dictionary of the same keys, but each value is that component's
    share of the total.

    Example:
        >>> molar_fractions({"a": 1, "b": 3})
        {'a': 0.25, 'b': 0.75}
    """
    total = sum(component_counts.values())
    if total <= 0:
        raise ValueError("Total lipid count must be greater than zero.")
    return {name: count / total for name, count in component_counts.items()}
