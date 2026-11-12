"""
STEP 4 - Build the biology out of balls: a membrane and a real LNP.

Same 3D engine as step 3, but now each ball has a SIZE and a COLOUR, and we
build two objects:

  * The muscle cell membrane (sarcolemma): a flat 20 x 20 grid of lipid heads
    at height y = 0.
  * The LNP: 90 dots on a sphere. Each dot is randomly given a lipid type in
    roughly real LNP proportions (e.g. the Moderna/Pfizer-style 4-lipid recipe):
        ~50% ionizable lipid, ~10% DSPC (helper), ~32% cholesterol, ~8% PEG-lipid
    plus mRNA beads coiled inside.

Each ball is stored as (position, radius, colour) -> the whole scene is just a list.

Run:  python learn/step4_build_objects.py
"""

import math
import random
import tkinter as tk

W, H = 900, 650
root = tk.Tk()
root.title("Step 4 - membrane + LNP made of lipids (drag to rotate)")
canvas = tk.Canvas(root, width=W, height=H, bg="#0a0e1a")
canvas.pack()

COLORS = {
    "ionizable": (110, 140, 230),
    "DSPC": (235, 235, 245),
    "cholesterol": (150, 150, 165),
    "PEG": (90, 220, 120),
    "membrane": (222, 184, 135),
    "mRNA": (240, 70, 130),
}


def fib_sphere(n):
    pts, g = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        pts.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return pts


# ---- build the scene: a list of (position, radius, colour) ------------------
balls = []

# Membrane: grid from -7 to +7 in x and z, at y = 0
N = 20
for i in range(N):
    for j in range(N):
        x = -7 + 14 * i / (N - 1)
        z = -7 + 14 * j / (N - 1)
        balls.append(((x, 0.0, z), 0.3, COLORS["membrane"]))

# LNP: centre 3 units above the membrane, radius 1
rng = random.Random(7)              # fixed seed = same "random" LNP every run
LNP_CENTER = (0.0, 3.0, 0.0)
counts = {}
for d in fib_sphere(90):
    r = rng.random()
    lipid = ("ionizable" if r < 0.50 else
             "DSPC" if r < 0.60 else
             "cholesterol" if r < 0.92 else
             "PEG")
    counts[lipid] = counts.get(lipid, 0) + 1
    pos = (LNP_CENTER[0] + d[0], LNP_CENTER[1] + d[1], LNP_CENTER[2] + d[2])
    balls.append((pos, 0.21, COLORS[lipid]))

# mRNA: a tangled loop of 48 beads inside the LNP (a 3D "Lissajous" curve)
for i in range(48):
    s = 2 * math.pi * i / 47
    p = (0.4 * math.sin(2 * s + 0.3), 0.4 * math.sin(3 * s), 0.4 * math.cos(2 * s) * math.cos(s))
    balls.append(((LNP_CENTER[0] + p[0], LNP_CENTER[1] + p[1], LNP_CENTER[2] + p[2]), 0.12, COLORS["mRNA"]))

print("LNP composition (counts out of 90):", counts)

# ---- 3D engine (same as step 3) ---------------------------------------------
yaw, pitch, DIST, FOCAL = 0.6, 0.35, 14.0, 600
TARGET = (0.0, 1.5, 0.0)    # the point the camera looks at


def project(p):
    x, y, z = p[0] - TARGET[0], p[1] - TARGET[1], p[2] - TARGET[2]
    x1 = x * math.cos(yaw) - z * math.sin(yaw)
    z1 = x * math.sin(yaw) + z * math.cos(yaw)
    y2 = y * math.cos(pitch) + z1 * math.sin(pitch)
    z2 = -y * math.sin(pitch) + z1 * math.cos(pitch)
    depth = z2 + DIST
    s = FOCAL / depth
    return W / 2 + x1 * s, H / 2 - y2 * s, depth, s


def draw():
    canvas.delete("all")
    items = []
    for pos, radius, color in balls:
        sx, sy, depth, s = project(pos)
        items.append((depth, sx, sy, radius * s, color))
    items.sort(key=lambda it: -it[0])
    for depth, sx, sy, r, (cr, cg, cb) in items:
        fog = max(0.0, min(0.6, (depth - DIST + 4) / 25))     # far = fade to background
        c = "#%02x%02x%02x" % (int(cr + (10 - cr) * fog), int(cg + (14 - cg) * fog), int(cb + (26 - cb) * fog))
        canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=c, outline="")
    y = 20
    for name, (cr, cg, cb) in COLORS.items():
        canvas.create_oval(15, y - 6, 27, y + 6, fill="#%02x%02x%02x" % (cr, cg, cb), outline="")
        canvas.create_text(35, y, text=name, anchor="w", fill="white")
        y += 22


last = [0, 0]
canvas.bind("<ButtonPress-1>", lambda e: last.__setitem__(slice(0, 2), [e.x, e.y]))


def on_drag(e):
    global yaw, pitch
    yaw += (e.x - last[0]) * 0.01
    pitch += (e.y - last[1]) * 0.01
    last[0], last[1] = e.x, e.y


canvas.bind("<B1-Motion>", on_drag)


def tick():
    global yaw
    yaw += 0.003
    draw()
    root.after(16, tick)


tick()
root.mainloop()
