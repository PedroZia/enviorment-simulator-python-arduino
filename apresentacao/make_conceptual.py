# -*- coding: utf-8 -*-
"""Visuais conceituais: evolucao da Q-table e comportamento ao longo do tempo."""
import os, re, math, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
ASSETS = os.path.join(BASE, "assets")

PAPER = "#F4F1EA"
INK = "#171512"
MUTED = "#6E6960"
RULE = "#D9D2C5"
TERRA = "#C24E2E"
SAND = "#E7DCCB"
SAGE = "#7D8577"

plt.rcParams.update({
    "font.family": "Bahnschrift",
    "font.size": 9,
    "text.color": INK,
    "axes.unicode_minus": False,
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
})

def save(fig, name, transparent=True):
    path = os.path.join(ASSETS, name)
    fig.savefig(path, dpi=300, transparent=transparent, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("ok", path)

def parse_q(path):
    qt = np.zeros((8, 3))
    for line in open(path):
        m = re.match(r"\s*\[([01]{3})\]\s*->\s*([+\-\d.]+)\s+([+\-\d.]+)\s+([+\-\d.]+)", line)
        if m:
            qt[int(m.group(1), 2)] = [float(m.group(2)), float(m.group(3)), float(m.group(4))]
    return qt

def qtable_evolution():
    eps = [10, 50, 100, 200]
    qts = [parse_q(os.path.join(ROOT, "snapshots", f"qtable_ep_{e:04d}.txt")) for e in eps]
    cmap = LinearSegmentedColormap.from_list("q", [SAGE, PAPER, TERRA], N=256)
    fig, axes = plt.subplots(1, 4, figsize=(11.4, 2.95))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.12, wspace=0.16)
    for ax, e, q in zip(axes, eps, qts):
        ax.imshow(q, cmap=cmap, vmin=-12, vmax=10, aspect="auto", interpolation="nearest")
        for i in range(8):
            for j in range(3):
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                       edgecolor=PAPER, lw=2.2))
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(RULE); s.set_linewidth(0.8)
        ax.set_title(f"ep. {e}", fontsize=10, color=INK, pad=8, fontfamily="Consolas")
    save(fig, "qtable_evolution.png")

# ------------------------------------------------- comportamento
def stadium(n=720, L=40.0, R=20.0):
    pts = []
    for i in range(n):
        a = -math.pi / 2 + (i / n) * math.pi
        pts.append((L + R * math.cos(a), R * math.sin(a)))
    for i in range(n):
        t = i / n
        pts.append((L - 2 * L * t, R))
    for i in range(n):
        a = math.pi / 2 + (i / n) * math.pi
        pts.append((-L + R * math.cos(a), R * math.sin(a)))
    for i in range(n):
        t = i / n
        pts.append((-L + 2 * L * t, -R))
    pts.append(pts[0])
    return np.array(pts)

TRACK = stadium()
QT = parse_q(os.path.join(ROOT, "snapshots", "qtable_ep_0200.txt"))

def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def on_line(x, y):
    return min(dist_seg(x, y, TRACK[i], TRACK[i + 1]) for i in range(len(TRACK) - 1)) < 0.95

def run(policy, steps=120, seed=7):
    rnd = random.Random(seed)
    idx = 0
    x, y = TRACK[idx]
    th = math.atan2(TRACK[idx + 1][1] - TRACK[idx][1], TRACK[idx + 1][0] - TRACK[idx][0])
    out = []
    for _ in range(steps):
        out.append(on_line(x, y))
        r = []
        for off in (-0.61, 0.0, 0.61):
            px, py = x + 2 * math.cos(th + off), y + 2 * math.sin(th + off)
            d = min(dist_seg(px, py, TRACK[i], TRACK[i + 1]) for i in range(len(TRACK) - 1))
            r.append(1 if d < 0.8 else 0)
        s = (r[0] << 2) | (r[1] << 1) | r[2]
        if policy == "greedy":
            a = int(np.argmax(QT[s]))
        else:
            a = rnd.randrange(3)
        th += (a - 1) * math.radians(15)
        x += 0.8 * math.cos(th)
        y += 0.8 * math.sin(th)
    return np.array(out)

def online_strip():
    before = run("random", steps=120, seed=7)
    after = run("greedy", steps=120, seed=7)
    print("on-line before", int(before.sum()), "after", int(after.sum()))
    fig, ax = plt.subplots(figsize=(11.2, 1.45))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 2)
    ax.axis("off")
    for row, data, base in ((1, before, 1.12), (0, after, 0.12)):
        for i, v in enumerate(data):
            ax.add_patch(Rectangle((i + 0.06, base), 0.88, 0.62,
                                   facecolor=TERRA if v else RULE, edgecolor="none"))
    save(fig, "online_strip.png")

if __name__ == "__main__":
    qtable_evolution()
    online_strip()
