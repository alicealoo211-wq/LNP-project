"""
STEP 5 - A timeline of stages, and endocytosis.

New ideas in this step:
  * TIME DRIVES EVERYTHING. We keep one number, t (seconds). A function
    stage_at(t) says which stage we are in and how far through it we are (u,
    from 0.0 to 1.0). Every position is then calculated from t.
    -> Because nothing depends on the previous frame, you can jump to any time.
  * lerp(a, b, u): "linear interpolation" = slide from a to b as u goes 0 -> 1.
  * ease(u): makes the slide start and stop gently instead of jerking.
  * Endocytosis: the membrane is pushed down by a bell-shaped (Gaussian) dip
        y = -depth * exp(-(x^2 + z^2) / w^2)
    which is deepest right under the LNP and flat far away.
  * Then the endosome (a bigger sphere around the LNP) appears and the
    membrane springs back flat: the vesicle has pinched off.

Space = pause, Right arrow = next stage.

Run:  python learn/step5_timeline_endocytosis.py
"""

import math
import tkinter as tk

W, H = 900, 650
root = tk.Tk()
root.title("Step 5 - timeline + endocytosis")
canvas = tk.Canvas(root, width=W, height=H, bg="#0a0e1a")
canvas.pack()

# (name, duration in seconds)
STAGES = [("1. Approach", 4), ("2. Membrane wraps around LNP", 5),
          ("3. Pinch off -> endosome", 3), ("4. Endosome moves inward", 4)]
STARTS = [sum(d for _, d in STAGES[:i]) for i in range(len(STAGES))]   # [0, 4, 9, 12]
TOTAL = sum(d for _, d in STAGES)


def stage_at(t):
    """Return (stage index, progress u from 0 to 1)."""
    for i in range(len(STAGES) - 1, -1, -1):
        if t >= STARTS[i]:
            return i, min(1.0, (t - STARTS[i]) / STAGES[i][1])
    return 0, 0.0


def lerp(a, b, u):
    return a + (b - a) * u


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)          # "smoothstep" curve


def fib_sphere(n):
    pts, g = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        pts.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return pts


LNP_DIRS = fib_sphere(90)
ENDO_DIRS = fib_sphere(170)
GRID = [(-7 + 14 * i / 19, -7 + 14 * j / 19) for i in range(20) for j in range(20)]
MAX_DEPTH = 3.2


def world(t):
    """Everything in the scene at time t, as (position, radius, colour)."""
    s, u = stage_at(t)
    # --- where is the LNP and how deep is the dip? ---
    depth, endo = 0.0, 0.0
    if s == 0:
        lnp_y = lerp(7.0, 1.25, ease(u))               # falls onto the membrane
    elif s == 1:
        depth = MAX_DEPTH * ease(u)                    # membrane bends in
        lnp_y = 1.25 - depth                           # LNP sinks with it
    elif s == 2:
        depth = MAX_DEPTH * (1 - ease(u))              # membrane springs back...
        endo = ease(u)                                 # ...and the endosome appears
        lnp_y = lerp(1.25 - MAX_DEPTH, -3.0, ease(u))
    else:
        endo = 1.0
        lnp_y = lerp(-3.0, -5.0, ease(u))              # moves deeper into the cell

    balls = []
    for x, z in GRID:
        y = -depth * math.exp(-(x * x + z * z) / 1.8 ** 2)   # the Gaussian dip
        balls.append(((x, y, z), 0.3, (222, 184, 135)))
    for d in LNP_DIRS:
        balls.append(((d[0], lnp_y + d[1], d[2]), 0.21, (110, 140, 230)))
    if endo > 0:
        for d in ENDO_DIRS:
            balls.append(((1.75 * d[0], lnp_y + 1.75 * d[1], 1.75 * d[2]), 0.15 * endo, (110, 215, 150)))
    return balls, lnp_y


# ---- 3D engine --------------------------------------------------------------
yaw, pitch, DIST, FOCAL = 0.6, 0.35, 16.0, 600
cam_y = 2.0


def project(p):
    x, y, z = p[0], p[1] - cam_y, p[2]
    x1 = x * math.cos(yaw) - z * math.sin(yaw)
    z1 = x * math.sin(yaw) + z * math.cos(yaw)
    y2 = y * math.cos(pitch) + z1 * math.sin(pitch)
    z2 = -y * math.sin(pitch) + z1 * math.cos(pitch)
    d = z2 + DIST
    s = FOCAL / d
    return W / 2 + x1 * s, H / 2 - y2 * s, d, s


t = 0.0
playing = True


def tick():
    global t, yaw, cam_y
    if playing:
        t = (t + 0.016) % TOTAL
    yaw += 0.002
    balls, lnp_y = world(t)
    cam_y += (max(lnp_y, -4) - cam_y) * 0.05     # camera slowly follows the LNP

    canvas.delete("all")
    items = sorted((project(p) + (r, c) for p, r, c in balls), key=lambda it: -it[2])
    for sx, sy, d, s, r, (cr, cg, cb) in items:
        rr = r * s
        canvas.create_oval(sx - rr, sy - rr, sx + rr, sy + rr, fill="#%02x%02x%02x" % (cr, cg, cb), outline="")

    s, u = stage_at(t)
    canvas.create_text(20, 25, anchor="w", fill="white", font=("Helvetica", 18, "bold"), text=STAGES[s][0])
    canvas.create_text(20, 52, anchor="w", fill="#8a96b0", text=f"t = {t:.1f} s    stage progress u = {u:.2f}")
    root.after(16, tick)


def toggle(_e):
    global playing
    playing = not playing


def next_stage(_e):
    global t
    s, _ = stage_at(t)
    t = STARTS[(s + 1) % len(STAGES)]


root.bind("<space>", toggle)
root.bind("<Right>", next_stage)
tick()
root.mainloop()
