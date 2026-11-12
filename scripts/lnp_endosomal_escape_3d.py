"""
3D simulation: a lipid nanoparticle (LNP) entering a muscle cell and
escaping the endosome to release its mRNA.
"""

import math
import random
import time
import tkinter as tk
from tkinter import ttk

# --------------------------------------------------------------------------
# here's math so far
# --------------------------------------------------------------------------

#min and max values for x, lo, hi
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x

# i found this to be a linear interpolation function, which calculates a value between a and b based on the parameter t
def lerp(a, b, t):
    return a + (b - a) * t

# based on reddit discussions this is meant make the motion smoother- starts slow accelerates and then slow again
def ease(t):
    """smooth 0->1 curve (slow start, slow end)."""
    t = clamp(t)
    return t * t * (3 - 2 * t)

#adds 2 3D points a and b 
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

#subtracts a 3D point from another 3D point b
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

#multiplies a 3D point a by a scalar s
def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)

#dot product of two 3D points a and b, which is a measure of how much they point in the same direction

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

#cross product gives direction at a right angle
def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

# length 1
def norm(a):
    length = math.sqrt(dot(a, a)) or 1.0
    return mul(a, 1.0 / length)

# i believe this is a vector linear interpolation function, which calculates a point between two 3D points a and b based on the parameter t
def vlerp(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))

#here it blends the two colors so like blue to orange
def mix(c1, c2, t):
    t = clamp(t)
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

#tkinter color formatting
def hexc(c):
    return "#%02x%02x%02x" % tuple(int(clamp(v, 0, 255)) for v in c)

#spreads the n points evenly over a sphere of 1 unite using the Fibonacci sphere algorithm,for distributing points on a sphere in a way that minimizes clustering and maximizes uniformity.
def fib_sphere(n):
    """n points spread evenly over a unit sphere."""
    pts = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        th = golden * i
        pts.append((math.cos(th) * r, y, math.sin(th) * r))
    return pts


# --------------------------------------------------------------------------
# colors -- R, G, B
# --------------------------------------------------------------------------

BG = (10, 14, 26)
MEMB = (222, 184, 135)       # sarcolemma lipid heads
ION_N = (110, 140, 230)      # ionizable lipid, neutral
ION_P = (255, 140, 50)       # ionizable lipid, protonated (+)
DSPC = (235, 235, 245)
CHOL = (150, 150, 165)
PEG = (90, 220, 120)
APOE = (255, 215, 70)
LDLR = (180, 100, 230)
ENDO_EARLY = (110, 215, 150)
ENDO_LATE = (240, 95, 95)
PUMP = (70, 215, 230)
HPLUS = (255, 255, 255)
MRNA = (240, 70, 130)
RIBO_L = (80, 140, 255)
RIBO_S = (150, 190, 255)
PROT = (200, 255, 120)

# --------------------------------------------------------------------------
# the process, tuple (name, duration, color, description)
# --------------------------------------------------------------------------

STAGES = [
    ("1. Approach & protein corona", 6, (120, 170, 255),
     "After intramuscular injection the LNP drifts through the fluid "
     "between muscle fibres. PEG-lipids (green) shed from its surface and "
     "apolipoprotein E (ApoE, yellow) from the tissue fluid coats the "
     "particle."),

    ("2. Receptor binding", 5, (180, 100, 230),
     "ApoE on the LNP is recognised by receptors such as the LDL receptor "
     "(purple) on the sarcolemma (the muscle cell membrane). Receptors "
     "cluster underneath the particle."),

    ("3. Endocytosis", 7, (222, 184, 135),
     "The membrane bends inward and wraps around the LNP, then pinches "
     "off. The particle is now trapped inside a membrane bubble: an early "
     "endosome."),

    ("4. Early endosome (pH ~6.5)", 5, (110, 215, 150),
     "The endosome moves deeper into the cell. V-ATPase proton pumps (cyan) "
     "pump H+ ions (white) inside, so the endosome starts to turn acidic."),

    ("5. Acidification (pH 6.5 -> 5.0)", 6, (240, 140, 90),
     "As pH drops below the ionizable lipid's pKa (~6.4), the lipids pick up "
     "protons and become positively charged (blue -> orange). Receptors "
     "are recycled back to the surface."),

    ("6. Endosomal escape", 8, (255, 140, 50),
     "Positive ionizable lipids pair with negative lipids in the endosome "
     "membrane. The lipids mix and form non-bilayer (hexagonal HII) "
     "structures, which destabilise the membrane. A hole opens and the mRNA "
     "slips out into the cytosol. In reality only ~1-2% of LNPs manage this!"),

    ("7. Translation", 9, (80, 140, 255),
     "Ribosomes (blue) in the muscle cell's cytosol read the mRNA and build "
     "the encoded protein (lime chains), e.g. a vaccine antigen."),
]
#shows empty list to hold the start times of each stage and calculates the total duration of all stages combined
STARTS = []

#accumulated duration of stages, starts at 0.0 and adds the duration of each stage to it, appending the accumulated value to STARTS
_acc = 0.0
for _s in STAGES:
    STARTS.append(_acc)
    _acc += _s[1]
TOTAL = _acc

PKA = 6.4            # apparent pKa of the ionizable lipid
ENDO_R = 1.75        # endosome radius
FUNNEL_W2 = 1.8 ** 2  # width of the membrane invagination
N_MRNA = 48

# direction in which the endosome ruptures, and two perpendicular axes
P = norm((0.5, -0.25, -1.0))
Q = norm(cross(P, (0, 1, 0)))
Q2 = cross(P, Q)

# returns which stage and how har through them
def stage_at(t):
    t = clamp(t, 0, TOTAL - 1e-6)
    for i in range(len(STAGES) - 1, -1, -1):
        if t >= STARTS[i]:
            return i, (t - STARTS[i]) / STAGES[i][1]
    return 0, 0.0


# --------------------------------------------------------------------------
# computed from the time t
# --------------------------------------------------------------------------

class Scene:
    #interesting and also hard part of creating the memrane grid, myofibrils, LNP lipids, ApoE proteins, LDL receptors, endosome membrane and V-ATPase pumps, protons, and mRNA coiled up inside the LNP
    def __init__(self):
        rng = random.Random(7)

        # muscle cell membrane (sarcolemma): a grid of lipid heads at y = 0
        n = 20
        span = 7.0
        self.grid = [(lerp(-span, span, i / (n - 1)), lerp(-span, span, j / (n - 1)))
                     for i in range(n) for j in range(n)]

        # myofibrils deep in the cell, with striped sarcomere bands
        self.myo = []
        for z in (-4.0, -1.5, 1.0, 3.5):
            x = -9.0
            while x <= 9.0:
                d = abs(((x + 9.0) % 2.2) - 1.1)
                col = (240, 225, 225) if d > 0.95 else (225, 130, 145) if d > 0.5 else (140, 35, 55)
                self.myo.append(((x, -9.5, z), col))
                x += 0.55

        # LNP surface lipids
        self.lnp = []
        for d in fib_sphere(90):
            r = rng.random()
            typ = "ion" if r < 0.5 else "dspc" if r < 0.6 else "chol" if r < 0.92 else "peg"
            self.lnp.append((d, typ))

        # ApoE proteins: final direction on LNP, starting offset, arrival delay
        self.apoe = []
        for d in fib_sphere(11):
            off = mul(norm((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))),
                      rng.uniform(4, 6))
            self.apoe.append((d, off, rng.uniform(0.05, 0.6)))

        # LDL receptors on the membrane
        self.ldlr = []
        for i in range(12):
            a = 2 * math.pi * i / 12
            r0 = rng.uniform(2.0, 6.0)
            ang0 = rng.uniform(0, 2 * math.pi)
            self.ldlr.append((r0 * math.cos(ang0), r0 * math.sin(ang0), a))

        # endosome membrane and V-ATPase pumps (kept away from the rupture side)
        self.endo = fib_sphere(170)
        self.pumps = [d for d in fib_sphere(14) if dot(d, P) < 0.3][:6]

        # protons: which pump they come through, and when
        a, b = STARTS[3], STARTS[5]
        self.protons = [(i % len(self.pumps), lerp(a, b, i / 70)) for i in range(70)]

        # mRNA coiled up inside the LNP
        self.coil = []
        for i in range(N_MRNA):
            s = 2 * math.pi * i / (N_MRNA - 1)
            self.coil.append((0.4 * math.sin(2 * s + 0.3),
                              0.4 * math.sin(3 * s),
                              0.4 * math.cos(2 * s) * math.cos(s)))

    # ---- motion ------------------------------------------
# location of where the membrane is pushed in during endocytosis
    def lnp_center(self, t):
        s, u = stage_at(t)
        if s == 0:
            e = ease(u)
            p = vlerp((3.0, 9.0, -2.0), (0.0, 2.6, 0.0), e)
            return add(p, (0.4 * math.sin(u * 7) * (1 - e), 0, 0.3 * math.cos(u * 5) * (1 - e)))
        if s == 1:
            return vlerp((0, 2.6, 0), (0, 1.25, 0), ease(u))
        if s == 2:
            if u < 0.7:
                return (0, 1.25 - self.depth(t), 0)
            return vlerp((0, -1.95, 0), (0, -3.0, 0), ease((u - 0.7) / 0.3))
        if s == 3:
            return vlerp((0, -3.0, 0), (0.8, -5.0, 0.4), ease(u))
        if s == 4:
            return vlerp((0.8, -5.0, 0.4), (1.2, -5.6, 0.6), ease(u))
        return (1.2, -5.6, 0.6)

    def depth(self, t):
        """how deep the membrane is pushed in under the LNP."""
        s, u = stage_at(t)
        if s != 2:
            return 0.0
        if u < 0.7:
            return 3.2 * ease(u / 0.7)
        return 3.2 * (1 - ease((u - 0.7) / 0.3))
    
# ph at time t, 7.4 to 6.5 to 5.0, based on the stage of the process
    def ph(self, t):
        s, u = stage_at(t)
        if s <= 2:
            return 7.4
        if s == 3:
            return lerp(7.4, 6.5, ease(u))
        if s == 4:
            return lerp(6.5, 5.0, ease(u))
        return 5.0
    
# where the camera should look at
    def camera_target(self, t):
        s, u = stage_at(t)
        c = self.lnp_center(t)
        tgt = (c[0] * 0.6, clamp(c[1], -5.6, 3.0), c[2] * 0.6)
        if s == 5:
            tgt = add(tgt, mul(P, 1.5 * ease(u)))
        elif s == 6:
            tgt = add(tgt, mul(P, 1.5 + 1.5 * ease(u)))
        return tgt

    # how do i build a sphere for this moment?
