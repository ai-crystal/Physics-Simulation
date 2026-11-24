import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 一维试验用的四个格式（周期边界，均匀速度 u = 1，h = 1）
# ============================================================
N = 256


def upwind(p, C):
    return p - C * (p - np.roll(p, 1))


def central_rk4(p, C, dt):
    def f(q):
        return -(np.roll(q, -1) - np.roll(q, 1)) / 2.0
    k1 = f(p)
    k2 = f(p + dt / 2 * k1)
    k3 = f(p + dt / 2 * k2)
    k4 = f(p + dt * k3)
    return p + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def catmull_rom(p, xq):
    i0 = np.floor(xq).astype(int)
    t = xq - i0
    p0 = p[(i0 - 1) % N]
    p1 = p[i0 % N]
    p2 = p[(i0 + 1) % N]
    p3 = p[(i0 + 2) % N]
    return 0.5 * (2 * p1 + (-p0 + p2) * t
                  + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def semi_lagrange_cubic(p, C):
    return catmull_rom(p, np.arange(N) - C)


def maccormack_lim(p, C):
    ph = p - C * (np.roll(p, -1) - p)
    pn = 0.5 * (p + ph - C * (ph - np.roll(ph, 1)))
    lo = np.minimum(np.minimum(np.roll(p, 1), p), np.roll(p, -1))
    hi = np.maximum(np.maximum(np.roll(p, 1), p), np.roll(p, -1))
    return np.clip(pn, lo, hi)


# ============================================================
# 图 4-1  方波平流 200 步后的形状（真实计算）
#   N=256, u=1, h=1, dt=0.5（C=0.5），宽 16 格的方波
# ============================================================
C = 0.5
STEPS = 200
p0 = np.zeros(N)
p0[100:116] = 1.0

runs = [
    ("迎风", ACCENT, lambda p: upwind(p, C)),
    ("中心差分 + RK4", BLUE, lambda p: central_rk4(p, C, 0.5)),
    ("半拉格朗日三次", PURPLE, lambda p: semi_lagrange_cubic(p, C)),
    ("MacCormack", GREEN, lambda p: maccormack_lim(p, C)),
]

fig, ax = plt.subplots(figsize=(6.6, 3.5))
idx = np.arange(N)
exact = np.roll(p0, 100)
ax.plot(idx, exact, color=FAINT, lw=1.2, ls=(0, (4, 3)), zorder=1,
        label="解析解")

for name, color, fn in runs:
    p = p0.copy()
    for _ in range(STEPS):
        p = fn(p)
    ax.plot(idx, p, color=color, lw=1.5, label=name, zorder=3)
    print("%-22s max %.3f  min %.3f" % (name, p.max(), p.min()))

ax.set_xlim(186, 240)
ax.set_ylim(-0.58, 1.45)
ax.set_xlabel("格子索引")
ax.set_ylabel("被平流的量 $\\phi$")
ax.set_yticks([0, 0.5, 1.0])
clean(ax, grid=True)
ax.legend(loc="upper right", handlelength=2.0, borderaxespad=0.6, labelspacing=0.42,
          fontsize=8.6)
save(fig, "04", "fig04-01")

# ============================================================
# 图 4-2  振幅随行程的衰减（真实计算 + 解析增益）
#   波长 32 格的正弦波，走过 100 格，C = 0.2 / 0.5 / 0.8
# ============================================================
k = 2 * np.pi / 32
xg = np.arange(N)

fig, ax = plt.subplots(figsize=(6.6, 3.5))

cfgs = [(0.2, ACCENT), (0.5, BLUE), (0.8, GREEN)]
for Cv, color in cfgs:
    steps = int(round(100 / Cv))
    p = np.sin(k * xg)
    amps = [(p.max() - p.min()) / 2]
    for _ in range(steps):
        p = upwind(p, Cv)
        amps.append((p.max() - p.min()) / 2)
    xs = np.arange(len(amps)) * Cv
    ax.plot(xs, amps, color=color, lw=1.6, zorder=3,
            label="迎风 $C=%.1f$（%d 步）" % (Cv, steps))
    G = np.sqrt(1 - 2 * Cv * (1 - Cv) * (1 - np.cos(k)))
    th = G ** np.arange(len(amps))
    ks = np.array([0, 25, 50, 75, 100]) / Cv
    ks = np.clip(np.round(ks).astype(int), 0, len(amps) - 1)
    ax.scatter(xs[ks], th[ks], s=26, facecolor="white", edgecolor=color,
               linewidths=1.1, zorder=5)
    ax.text(102.5, amps[-1], "%.2f" % amps[-1], color=color, fontsize=8.4,
            ha="left", va="center")
    print("C=%.1f 步数 %d 终值 %.4f 解析 %.4f" % (Cv, steps, amps[-1], th[-1]))

# 半拉格朗日三次插值作对照
p = np.sin(k * xg)
amps = [(p.max() - p.min()) / 2]
for _ in range(200):
    p = semi_lagrange_cubic(p, 0.5)
    amps.append((p.max() - p.min()) / 2)
ax.plot(np.arange(len(amps)) * 0.5, amps, color=PURPLE, lw=1.6, zorder=3,
        label="半拉格朗日三次插值 $C=0.5$（200 步）")
ax.text(102.5, amps[-1], "%.2f" % amps[-1], color=PURPLE, fontsize=8.4,
        ha="left", va="center")
print("SL三次 终值 %.4f" % amps[-1])

ax.set_xlim(0, 114)
ax.set_ylim(0, 1.07)
ax.set_xlabel("波走过的格数")
ax.set_ylabel("振幅（峰谷差的一半）")
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
clean(ax, grid=True)
h, l = ax.get_legend_handles_labels()
ax.legend(h, l, loc="lower left", handlelength=2.2, borderaxespad=0.7,
          labelspacing=0.42, fontsize=8.6)
ax.text(0.985, 0.02, "实线为实测，圆点为一阶迎风解析增益", fontsize=7.6, color=FAINT,
        ha="right", va="bottom", transform=ax.transAxes)
save(fig, "04", "fig04-02")
