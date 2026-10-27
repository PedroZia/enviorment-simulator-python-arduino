# -*- coding: utf-8 -*-
"""Gera os visuais da apresentacao no estilo editorial do deck."""
import os, sys, csv, re, math, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
ASSETS = os.path.join(BASE, "assets")
os.makedirs(ASSETS, exist_ok=True)

PAPER = "#F4F1EA"
INK = "#171512"
MUTED = "#6E6960"
RULE = "#D9D2C5"
TERRA = "#C24E2E"
SAND = "#E7DCCB"
SOFT = "#B9AC97"

plt.rcParams.update({
    "font.family": "Bahnschrift",
    "font.size": 9,
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": RULE,
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "axes.unicode_minus": False,
})

def save(fig, name, transparent=True, tight=True):
    path = os.path.join(ASSETS, name)
    if tight:
        fig.savefig(path, dpi=300, transparent=transparent, bbox_inches="tight", pad_inches=0.02)
    else:
        fig.savefig(path, dpi=300, transparent=transparent)
    plt.close(fig)
    print("ok", path)

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

def clean_axes(ax, dark=False, grid=True):
    ax.set_facecolor("none")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#4A453D" if dark else RULE)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(length=0, labelsize=8.5, colors=("#B9B2A5" if dark else MUTED))
    if grid:
        ax.yaxis.grid(True, color=("#3A352E" if dark else RULE), linewidth=0.6, alpha=0.55)
        ax.xaxis.grid(False)
        ax.set_axisbelow(True)

# ---------------------------------------------------------------- hero
def hero():
    fig, ax = plt.subplots(figsize=(13.4, 5.2))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot(TRACK[:, 0], TRACK[:, 1], color=INK, lw=1.5, alpha=0.9, solid_capstyle="round")
    x, y = 0.0, -20.0
    for ang in (-0.61, 0.0, 0.61):
        ax.plot([x, x + 6.2 * math.cos(ang)], [y, y + 6.2 * math.sin(ang)],
                color=TERRA, lw=1.0, alpha=0.55, solid_capstyle="round")
    ax.add_patch(Circle((x, y), 2.2, facecolor=TERRA, edgecolor="none", zorder=5))
    ax.add_patch(Circle((x, y), 3.6, facecolor="none", edgecolor=TERRA, lw=0.9, alpha=0.45, zorder=5))
    ax.set_xlim(-62, 62)
    ax.set_ylim(-26, 26)
    save(fig, "hero_track.png")

# ---------------------------------------------------------------- robo
def robot():
    fig, ax = plt.subplots(figsize=(9.2, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-4.8, 4.8)
    ax.set_ylim(-3.6, 4.3)

    ax.add_patch(FancyBboxPatch((-1.85, -1.35), 3.7, 2.7,
                                boxstyle="round,pad=0.02,rounding_size=0.22",
                                linewidth=1.6, edgecolor=INK, facecolor=SAND, zorder=3))
    for sx in (-1, 1):
        ax.add_patch(FancyBboxPatch((sx * 2.08 - 0.26, -1.18), 0.52, 2.36,
                                    boxstyle="round,pad=0.01,rounding_size=0.12",
                                    linewidth=1.2, edgecolor=INK, facecolor=INK, zorder=4))
        ax.plot([sx * 2.08 - 0.16, sx * 2.08 - 0.16], [-0.75, 0.75], color=PAPER, lw=1.0, alpha=0.5, zorder=5)
    ax.add_patch(Circle((0, -1.75), 0.30, facecolor=PAPER, edgecolor=INK, lw=1.2, zorder=5))

    ax.add_patch(FancyBboxPatch((-0.92, 1.12), 1.84, 0.34,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.1, edgecolor=INK, facecolor=INK, zorder=6))
    for sx in (-0.55, 0.0, 0.55):
        ax.add_patch(Circle((sx, 1.29), 0.13, facecolor=TERRA, edgecolor="none", zorder=7))
        ax.plot([sx * 1.0, sx * 1.75], [1.48, 3.25], color=TERRA, lw=0.9, alpha=0.5, zorder=5)

    ax.add_patch(FancyBboxPatch((-0.72, -0.18), 1.44, 0.92,
                                boxstyle="round,pad=0.02,rounding_size=0.05",
                                linewidth=1.0, edgecolor=INK, facecolor=PAPER, zorder=6))
    ax.add_patch(Rectangle((-0.55, 0.40), 0.44, 0.20, facecolor=INK, edgecolor="none", zorder=7))
    for i, yy in enumerate((0.18, 0.10)):
        for xx in (-0.52, -0.36, -0.20, -0.04, 0.12, 0.28, 0.44):
            ax.add_patch(Circle((xx, yy), 0.022, facecolor=MUTED, edgecolor="none", zorder=7))

    ax.add_patch(FancyBboxPatch((-0.58, -1.02), 1.16, 0.54,
                                boxstyle="round,pad=0.02,rounding_size=0.04",
                                linewidth=1.0, edgecolor=INK, facecolor=PAPER, zorder=6))
    ax.add_patch(Rectangle((-0.43, -0.90), 0.34, 0.30, facecolor=INK, edgecolor="none", zorder=7))
    for xx in (0.10, 0.27, 0.44):
        ax.plot([xx, xx], [-0.86, -0.68], color=MUTED, lw=1.4, zorder=7)

    def note(text, xy, ha="center", size=8.4, color=MUTED, rotation=0):
        ax.text(xy[0], xy[1], text, ha=ha, va="center", fontsize=size,
                color=color, rotation=rotation, zorder=10)

    note("3 SENSORES IR", (1.55, 2.55), ha="left", size=9.2, color=INK)
    ax.plot([1.5, 0.95], [2.48, 1.48], color=MUTED, lw=0.8, zorder=9)

    note("ARDUINO", (1.02, 0.32), ha="left", size=7.3)
    note("PONTE H", (1.02, -0.76), ha="left", size=7.3)
    note("MOTOR", (-2.45, 0.0), ha="center", size=7.8, rotation=90)
    note("MOTOR", (2.45, 0.0), ha="center", size=7.8, rotation=90)
    note("RODIZIO", (0.0, -2.42), ha="center", size=8.4)
    note("CHASSI", (-1.15, -1.12), ha="center", size=7.3)

    save(fig, "robot_top.png")

# ---------------------------------------------------------------- pista
def sim_track():
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot(TRACK[:, 0], TRACK[:, 1], color=SAND, lw=11, solid_capstyle="round", zorder=1)
    ax.plot(TRACK[:, 0], TRACK[:, 1], color=INK, lw=1.0, alpha=0.55, zorder=2)

    for k in range(8):
        idx = int(k * (len(TRACK) - 1) / 8)
        x, y = TRACK[idx]
        if math.hypot(x, y + 20) < 12:
            continue
        ax.add_patch(Circle((x, y), 0.85, facecolor=PAPER, edgecolor=INK, lw=0.8, alpha=0.9, zorder=3))

    x, y = 0.0, -20.0
    for ang in (-0.61, 0.0, 0.61):
        ax.plot([x, x + 6.0 * math.cos(ang)], [y, y + 6.0 * math.sin(ang)],
                color=TERRA, lw=1.0, alpha=0.7, zorder=4)
    ax.add_patch(Polygon([[x - 1.8, y - 1.2], [x + 2.0, y], [x - 1.8, y + 1.2]],
                         closed=True, facecolor=TERRA, edgecolor="none", zorder=5))
    ax.set_xlim(-64, 64)
    ax.set_ylim(-26, 26)
    save(fig, "sim_track.png")

# ---------------------------------------------------------------- paths
def parse_q():
    qt = [[0.0] * 3 for _ in range(8)]
    for line in open(os.path.join(ROOT, "snapshots", "qtable_ep_0200.txt")):
        m = re.match(r"\s*\[([01]{3})\]\s*->\s*([+\-\d.]+)\s+([+\-\d.]+)\s+([+\-\d.]+)", line)
        if m:
            qt[int(m.group(1), 2)] = [float(m.group(2)), float(m.group(3)), float(m.group(4))]
    return qt

QT = parse_q()

def _dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def run(policy, idx=0, max_steps=650, seed=None):
    rnd = random.Random(seed)
    x, y = TRACK[idx]
    th = math.atan2(TRACK[idx + 1][1] - TRACK[idx][1], TRACK[idx + 1][0] - TRACK[idx][0])
    path = [(x, y)]
    lost = 0
    for _ in range(max_steps):
        r = []
        for off in (-0.61, 0.0, 0.61):
            px, py = x + 2 * math.cos(th + off), y + 2 * math.sin(th + off)
            d = min(_dist_seg(px, py, TRACK[i], TRACK[i + 1]) for i in range(len(TRACK) - 1))
            r.append(1 if d < 0.8 else 0)
        s = (r[0] << 2) | (r[1] << 1) | r[2]
        if policy == "greedy":
            a = max(range(3), key=lambda k: QT[s][k])
        else:
            a = rnd.randrange(3)
        th += (a - 1) * math.radians(15)
        x += 0.8 * math.cos(th)
        y += 0.8 * math.sin(th)
        path.append((x, y))
        d = min(_dist_seg(x, y, TRACK[i], TRACK[i + 1]) for i in range(len(TRACK) - 1))
        if d > 0.8:
            lost += 1
        else:
            lost = 0
        if lost >= 15:
            break
    return np.array(path), lost >= 15

def path_panel(name, paths, lost_flags, highlight=0):
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot(TRACK[:, 0], TRACK[:, 1], color=SAND, lw=9.0, solid_capstyle="round", zorder=1)
    ax.plot(TRACK[:, 0], TRACK[:, 1], color=INK, lw=0.8, alpha=0.35, zorder=2)
    for i, p in enumerate(paths):
        c = TERRA if i == highlight else SOFT
        lw = 2.4 if i == highlight else 1.2
        al = 1.0 if i == highlight else 0.55
        ax.plot(p[:, 0], p[:, 1], color=c, lw=lw, alpha=al, solid_capstyle="round", zorder=4)
        ax.add_patch(Circle(p[0], 1.25, facecolor=PAPER, edgecolor=INK, lw=0.9, zorder=6))
        if lost_flags[i]:
            ex, ey = p[-1]
            ax.plot([ex - 1.3, ex + 1.3], [ey - 1.3, ey + 1.3], color=TERRA, lw=1.8, zorder=7)
            ax.plot([ex - 1.3, ex + 1.3], [ey + 1.3, ey - 1.3], color=TERRA, lw=1.8, zorder=7)
        else:
            ax.add_patch(Circle(p[-1], 1.1, facecolor=TERRA, edgecolor="none", zorder=7))
    ax.set_xlim(-70, 70)
    ax.set_ylim(-30, 30)
    save(fig, name, tight=False)

def paths():
    random_paths, lost = [], []
    for seed in (7, 19, 31):
        p, l = run("random", idx=0, max_steps=200, seed=seed)
        random_paths.append(p); lost.append(l)
    path_panel("path_before.png", random_paths, lost)

    good, good_lost = [], []
    for idx in (0, 250, 480):
        p, l = run("greedy", idx=idx, max_steps=650, seed=1)
        good.append(p); good_lost.append(l)
    path_panel("path_after.png", good, good_lost)
    print("before lens", [len(p) for p in random_paths], "lost", lost)
    print("after lens", [len(p) for p in good], "lost", good_lost)

# ---------------------------------------------------------------- epsilon
def epsilon_curve():
    ep = np.arange(0, 200)
    eps = np.maximum(0.02, 1.0 * (0.99 ** ep))
    fig, ax = plt.subplots(figsize=(6.4, 3.1))
    clean_axes(ax)
    ax.fill_between(ep, 0, eps, color=SAND, alpha=0.65, linewidth=0)
    ax.plot(ep, eps, color=TERRA, lw=2.2, solid_capstyle="round")
    ax.set_xlim(0, 199)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("episódios", labelpad=6, fontsize=9)
    ax.set_ylabel("chance de explorar", labelpad=8, fontsize=9)
    ax.annotate("começa curioso", xy=(3, 0.99), xytext=(34, 0.84),
                fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("termina mais experiente", xy=(195, 0.132), xytext=(92, 0.055),
                fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    save(fig, "epsilon.png")

# ---------------------------------------------------------------- learning curve
def learning():
    rewards = [float(r["reward"]) for r in csv.DictReader(open(os.path.join(ROOT, "history.csv")))]
    r = np.array(rewards)
    ma = np.convolve(r, np.ones(10) / 10, mode="valid")
    ep = np.arange(len(r))

    def chart(name, dark=False):
        fig, ax = plt.subplots(figsize=(10.6, 3.75))
        clean_axes(ax, dark=dark)
        ink = PAPER if dark else INK
        ter = "#D96A45" if dark else TERRA
        ax.axhline(0, color=("#5A544A" if dark else RULE), lw=0.7, zorder=1)
        ax.plot(ep, r, color=ter, lw=0.7, alpha=0.28, zorder=2)
        ax.plot(np.arange(9, len(r)), ma, color=ink, lw=2.2, solid_capstyle="round", zorder=4)
        ax.plot(len(r) - 1, ma[-1], "o", color=ter, ms=5.5, zorder=5)
        ax.set_xlim(0, 199)
        ax.set_ylim(-150, 880)
        ax.set_xlabel("episódios de treinamento", labelpad=7, fontsize=9)
        ax.set_ylabel("recompensa", labelpad=8, fontsize=9)
        ax.annotate("média móvel (10 episódios)", xy=(152, 350), xytext=(112, 735),
                    fontsize=9, color=ink,
                    arrowprops=dict(arrowstyle="-", color=("#8A8274" if dark else MUTED), lw=0.8))
        save(fig, name)

    chart("learning_curve.png")
    chart("learning_curve_dark.png", dark=True)

def sparkline():
    rewards = [float(r["reward"]) for r in csv.DictReader(open(os.path.join(ROOT, "history.csv")))]
    r = np.array(rewards)
    ma = np.convolve(r, np.ones(10) / 10, mode="valid")
    fig, ax = plt.subplots(figsize=(9.0, 2.2))
    ax.set_facecolor("none")
    ax.axis("off")
    ax.plot(np.arange(9, len(r)), ma, color=TERRA, lw=2.8, solid_capstyle="round")
    ax.set_xlim(0, 199)
    ax.set_ylim(-120, 850)
    save(fig, "sparkline_dark.png")

if __name__ == "__main__":
    hero()
    robot()
    sim_track()
    paths()
    epsilon_curve()
    learning()
    sparkline()
