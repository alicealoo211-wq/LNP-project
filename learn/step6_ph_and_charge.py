"""
STEP 6 - Acidification and lipid charge (the science behind endosomal escape).

The key equation (Henderson-Hasselbalch, rearranged for a base):

    fraction protonated (charged) = 1 / (1 + 10^(pH - pKa))

  * pKa of a typical ionizable lipid (e.g. in mRNA vaccines) is ~6.4.
  * In blood (pH 7.4):  1 / (1 + 10^(1.0))  = 1/11  ~ 9%   -> mostly NEUTRAL (safe, less toxic)
  * At pH = pKa (6.4):  1 / (1 + 10^0)      = 1/2   = 50%
  * Late endosome (5.0): 1 / (1 + 10^(-1.4)) ~ 96%  -> mostly POSITIVE

Positively charged lipids attract the negatively charged lipids of the
endosome membrane, which disrupts it -> the mRNA can escape.

In this step the endosome's pH falls from 7.4 to 5.0 over 10 seconds.
Each ionizable lipid's colour is blended from blue (neutral) to orange (+)
by the charged fraction, and the endosome itself goes green -> red.
The program also prints a table of the equation when it starts.

Use the slider to set the pH yourself.

Run:  python learn/step6_ph_and_charge.py
"""

import math
import tkinter as tk

PKA = 6.4


def fraction_charged(pH, pKa=PKA):
    return 1.0 / (1.0 + 10 ** (pH - pKa))


print(" pH   fraction of ionizable lipids charged")
for pH in (7.4, 7.0, 6.5, 6.4, 6.0, 5.5, 5.0):
    print(f" {pH:.1f}   {fraction_charged(pH) * 100:5.1f} %")


def mix(c1, c2, u):
    u = max(0.0, min(1.0, u))
    return tuple(int(a + (b - a) * u) for a, b in zip(c1, c2))


def fib_sphere(n):
    pts, g = [], math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - y * y)
        pts.append((math.cos(g * i) * r, y, math.sin(g * i) * r))
    return pts


NEUTRAL, CHARGED = (110, 140, 230), (255, 140, 50)
EARLY, LATE = (110, 215, 150), (240, 95, 95)
LNP_DIRS = fib_sphere(90)
IONIZABLE = [i % 2 == 0 for i in range(90)]        # half of the LNP lipids are ionizable
ENDO_DIRS = fib_sphere(170)

W, H = 900, 650
root = tk.Tk()
root.title("Step 6 - pH and lipid charge")
canvas = tk.Canvas(root, width=W, height=H, bg="#0a0e1a")
canvas.pack()
ph_var = tk.DoubleVar(value=7.4)
auto = tk.BooleanVar(value=True)
bar = tk.Frame(root)
bar.pack(fill="x")
tk.Label(bar, text="pH").pack(side="left")
slider = tk.Scale(bar, from_=7.4, to=4.5, resolution=0.05, orient="horizontal", length=400,
                  variable=ph_var)
slider.pack(side="left")
slider.bind("<ButtonPress-1>", lambda _e: auto.set(False))   # touching the slider stops auto mode
tk.Checkbutton(bar, text="auto-acidify", variable=auto).pack(side="left")

yaw, pitch, DIST, FOCAL = 0.0, 0.3, 8.0, 520


def project(p):
    x, y, z = p
    x1 = x * math.cos(yaw) - z * math.sin(yaw)
    z1 = x * math.sin(yaw) + z * math.cos(yaw)
    y2 = y * math.cos(pitch) + z1 * math.sin(pitch)
    z2 = -y * math.sin(pitch) + z1 * math.cos(pitch)
    d = z2 + DIST
    s = FOCAL / d
    return W / 2 + x1 * s, H / 2 - y2 * s, d, s


def tick():
    global yaw
    yaw += 0.006
    if auto.get():
        new = ph_var.get() - 0.004
        ph_var.set(7.4 if new < 5.0 else new)       # loop back to 7.4 at the end
    pH = ph_var.get()
    f = fraction_charged(pH)

    balls = []
    endo_color = mix(EARLY, LATE, (7.4 - pH) / 2.4)
    for d in ENDO_DIRS:
        balls.append((tuple(1.75 * v for v in d), 0.13, endo_color))
    for d, ion in zip(LNP_DIRS, IONIZABLE):
        balls.append((d, 0.2, mix(NEUTRAL, CHARGED, f) if ion else (150, 150, 165)))

    canvas.delete("all")
    items = sorted((project(p) + (r, c) for p, r, c in balls), key=lambda it: -it[2])
    for sx, sy, d, s, r, c in items:
        rr = r * s
        canvas.create_oval(sx - rr, sy - rr, sx + rr, sy + rr, fill="#%02x%02x%02x" % c, outline="")

    canvas.create_text(20, 25, anchor="w", fill="white", font=("Helvetica", 18, "bold"),
                       text=f"pH {pH:.2f}   ->   {f * 100:.0f}% of ionizable lipids charged (+)")
    canvas.create_text(20, 55, anchor="w", fill="#8a96b0", font=("Helvetica", 13),
                       text=f"fraction = 1 / (1 + 10^(pH - pKa)) = 1 / (1 + 10^({pH:.2f} - {PKA})) = {f:.2f}")
    root.after(16, tick)


tick()
root.mainloop()
