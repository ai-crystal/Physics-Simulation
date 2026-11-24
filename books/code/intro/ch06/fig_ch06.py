import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 6-1  三角网上的三类弹簧
# ============================================================
fig, ax = canvas(6.7, 3.2, ylim=(0.04, 0.87))

nx, ny = 4, 3
gx = [0.075 + i * 0.152 for i in range(nx)]
gy = [0.185 + j * 0.235 for j in range(ny)]
V = {(i, j): np.array([gx[i], gy[j]]) for i in range(nx) for j in range(ny)}

for i in range(nx - 1):
    for j in range(ny - 1):
        a, b, c, d = V[(i, j)], V[(i + 1, j)], V[(i + 1, j + 1)], V[(i, j + 1)]
        ax.add_patch(Polygon([a, b, c], closed=True, facecolor="#EFF4FF",
                             edgecolor="none", zorder=0))
        ax.add_patch(Polygon([a, c, d], closed=True, facecolor="#F8FAFF",
                             edgecolor="none", zorder=0))

for i in range(nx):
    for j in range(ny - 1):
        ax.plot([gx[i], gx[i]], [gy[j], gy[j + 1]], color=GRID, lw=0.9, zorder=1)
for j in range(ny):
    for i in range(nx - 1):
        ax.plot([gx[i], gx[i + 1]], [gy[j], gy[j]], color=GRID, lw=0.9, zorder=1)
for i in range(nx - 1):
    for j in range(ny - 1):
        ax.plot([gx[i], gx[i + 1]], [gy[j], gy[j + 1]], color="#E8EDF5", lw=0.8,
                ls=(0, (2, 2)), zorder=1)

for p in V.values():
    ax.plot([p[0]], [p[1]], "o", ms=2.8, color=MUTED, zorder=3)

arrow(ax, V[(0, 1)], V[(1, 1)], color=BLUE, lw=2.6, style="-", z=5, shrinkA=0, shrinkB=0)
arrow(ax, V[(1, 1)], V[(2, 0)], color=GREEN, lw=2.6, style="-", z=5, shrinkA=0, shrinkB=0)
arrow(ax, V[(0, 2)], V[(2, 2)], color=ACCENT, lw=2.0, style="-", rad=-0.5, z=5,
      shrinkA=0, shrinkB=0)

label(ax, 0.151, 0.372, "结构", fs=8.2, color=BLUE,
      bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
label(ax, 0.372, 0.305, "剪切", fs=8.2, color=GREEN,
      bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
label(ax, 0.227, 0.733, "弯曲", fs=8.2, color=ACCENT,
      bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

label(ax, 0.075, 0.090, "灰线为三角网，每个顶点是一个质点", fs=8.0, color=MUTED, ha="left")

item = [(BLUE, "结构弹簧：沿网格边\n拉与压都抵抗"),
        (GREEN, "剪切弹簧：三角形对角线\n抵抗面内剪切"),
        (ACCENT, "弯曲弹簧：隔一格相连\n抵抗弯折")]
for k, (c, t) in enumerate(item):
    y = 0.720 - k * 0.190
    ax.plot([0.605, 0.650], [y, y], color=c, lw=2.4, solid_capstyle="round")
    label(ax, 0.662, y, t, fs=8.2, ha="left", va="center")

save(fig, "06", "fig06-01")


# ============================================================
# 图 6-2  PBD 距离约束的投影
# ============================================================
fig, ax = canvas(6.7, 3.2, ylim=(0, 0.46))
ax.set_aspect("equal")

d = 0.13
y0 = 0.265
ax.plot([0.455, 0.455], [0.030, 0.430], color=GRID, lw=0.9)

# ---- 左：两端质量相等 ----
p1 = np.array([0.115, y0])
p2 = np.array([0.305, y0])
n1 = np.array([0.145, y0])
n2 = np.array([0.275, y0])
ax.add_patch(Arc(n1, 2 * d, 2 * d, theta1=0, theta2=180, edgecolor=FAINT,
                 lw=0.9, ls=(0, (3, 3)), zorder=1))
ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INK, lw=1.1, zorder=3)
ax.plot([p1[0]], [p1[1]], "o", ms=6, mfc="white", mec=INK, mew=1.2, zorder=4)
ax.plot([p2[0]], [p2[1]], "o", ms=6, mfc="white", mec=INK, mew=1.2, zorder=4)
arrow(ax, p1, n1, color=BLUE, lw=1.4, z=5, ms=9, shrinkA=0, shrinkB=0)
arrow(ax, p2, n2, color=BLUE, lw=1.4, z=5, ms=9, shrinkA=0, shrinkB=0)
label(ax, 0.115, 0.208, r"$\mathbf{p}_1$", fs=9.2)
label(ax, 0.305, 0.208, r"$\mathbf{p}_2$", fs=9.2)
label(ax, 0.210, 0.352, r"$C=l-d$", fs=9.0, color=ACCENT)
label(ax, 0.210, 0.430, "两端质量相等：各退一半", fs=8.8, weight="bold")
label(ax, 0.210, 0.150, r"$\Delta\mathbf{x}_1=-\frac{1}{2}C\,\mathbf{n}$", fs=9.0, va="top")
label(ax, 0.210, 0.092, r"$\Delta\mathbf{x}_2=+\frac{1}{2}C\,\mathbf{n}$", fs=9.0, va="top")

# ---- 右：一端固定 ----
q1 = np.array([0.620, y0])
q2 = np.array([0.810, y0])
r2 = np.array([0.750, y0])
ax.add_patch(Arc(q1, 2 * d, 2 * d, theta1=0, theta2=180, edgecolor=FAINT,
                 lw=0.9, ls=(0, (3, 3)), zorder=1))
ax.plot([q1[0], q2[0]], [q1[1], q2[1]], color=INK, lw=1.1, zorder=3)
ax.plot([q1[0]], [q1[1]], "s", ms=5.4, mfc=INK, mec=INK, zorder=4)
ax.plot([q2[0]], [q2[1]], "o", ms=6, mfc="white", mec=INK, mew=1.2, zorder=4)
ax.plot([q1[0] - 0.042, q1[0] + 0.042], [y0 - 0.018, y0 - 0.018], color=MUTED,
        lw=0.9, zorder=2)
for k in range(3):
    xx = q1[0] - 0.034 + k * 0.018
    ax.plot([xx, xx + 0.018], [y0 - 0.018, y0 - 0.034], color=MUTED, lw=0.8, zorder=2)
arrow(ax, q2, r2, color=BLUE, lw=1.4, z=5, ms=9, shrinkA=0, shrinkB=0)
label(ax, 0.600, 0.208, r"$\mathbf{p}_1$ 固定", fs=8.6, ha="right")
label(ax, 0.810, 0.208, r"$\mathbf{p}_2$", fs=9.2)
label(ax, 0.735, 0.430, "一端钉住：修正全落在自由端", fs=8.8, weight="bold")
label(ax, 0.735, 0.150, r"$w_1=0,\quad \Delta\mathbf{x}_2=C\,\mathbf{n}$", fs=9.0, va="top")
label(ax, 0.735, 0.092, r"$w=1/m$ 为质量的倒数", fs=8.0, color=MUTED, va="top")

save(fig, "06", "fig06-02")


# ============================================================
# 图 6-3  弯曲能量随细分的变化（真实计算，双对数）
# ============================================================
L, A, EI = 1.0, 0.05, 5e-4
K_FIX = 2e-3


def sample(n):
    x = np.linspace(0.0, L, 200001)
    y = A * np.sin(np.pi * x / L)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    t = np.linspace(0.0, s[-1], n)
    return np.interp(t, s, x), np.interp(t, s, y)


def turning(n):
    px, py = sample(n)
    P = np.stack([px, py], axis=1)
    e = np.diff(P, axis=0)
    h = np.linalg.norm(e, axis=1)
    eh = e / h[:, None]
    ang = np.array([np.arccos(np.clip(np.dot(eh[i], eh[i + 1]), -1.0, 1.0))
                    for i in range(len(e) - 1)])
    return ang, h


def energy_curv(n):
    ang, h = turning(n)
    hm = 0.5 * (h[:-1] + h[1:])
    return 0.5 * EI * np.sum(ang ** 2 / hm)


def energy_fixed(n):
    ang, _ = turning(n)
    return 0.5 * K_FIX * np.sum(ang ** 2)


E_ref = energy_curv(20000)
ns = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024])
e_curv = np.array([energy_curv(n) for n in ns]) / E_ref
e_fix = np.array([energy_fixed(n) for n in ns]) / E_ref
e_err = np.abs(1.0 - e_curv)

fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.loglog(ns, e_fix, "o-", ms=3.6, lw=1.4, color=ACCENT,
          label=r"固定刚度 $k_b=2\times10^{-3}$ N·m")
ax.loglog(ns, e_curv, "o-", ms=3.6, lw=1.4, color=BLUE,
          label=r"$k_b=B/h$，随网格变")
ax.loglog(ns, e_err, "s--", ms=3.0, lw=1.1, color=GREEN,
          label="曲率型离散的误差")
ax.axhline(1.0, color=FAINT, lw=1.0, ls=(0, (4, 3)), label="连续极限")
ax.set_xlabel("沿布条的分段数 n")
ax.set_ylabel("离散弯曲能量 / 连续极限")
ax.set_ylim(1e-7, 6.0)
ax.set_xlim(3.2, 1400)
ax.legend(loc="lower left", handlelength=2.0, labelspacing=0.38)
clean(ax, grid=True)
fig.tight_layout()
save(fig, "06", "fig06-03")

print("E_ref = %.4e" % E_ref)
print("slope fixed k  =", np.polyfit(np.log(ns), np.log(e_fix), 1)[0])
print("slope rel error=", np.polyfit(np.log(ns), np.log(e_err), 1)[0])
