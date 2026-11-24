import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 4-1  三种离散方式：拉格朗日、欧拉、混合（示意图）
# ============================================================
fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.45))
for ax in axs:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

# ---- (a) 拉格朗日：粒子带着物质走 ----
ax = axs[0]
th = np.linspace(0, 2 * np.pi, 200)
ax.plot(0.5 + 0.32 * np.cos(th), 0.52 + 0.25 * np.sin(th), color=FAINT, lw=0.9,
        ls=(0, (3, 3)), zorder=1)
rng = np.random.default_rng(7)
pts = []
while len(pts) < 120:
    p = rng.uniform(-1, 1, 2)
    if p[0] ** 2 + p[1] ** 2 < 1:
        pts.append(p)
pts = np.array(pts)
X = 0.5 + 0.26 * pts[:, 0] * (1.0 + 0.16 * pts[:, 1])
Y = 0.52 + 0.205 * pts[:, 1] * (1.0 - 0.10 * pts[:, 0])
ax.scatter(X, Y, s=6.5, color=PURPLE, alpha=0.85, linewidths=0, zorder=3)
for i in (12, 47, 88):
    ax.annotate("", xy=(X[i] + 0.10, Y[i] + 0.045), xytext=(X[i], Y[i]),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=0.9, alpha=0.9,
                                shrinkA=1.5, shrinkB=1.5, mutation_scale=8))
label(ax, 0.03, 0.95, "(a)", fs=9.2, color=INK, weight="bold", ha="left", va="top")
label(ax, 0.5, 0.05, "每个粒子带一份质量", fs=8.4, color=MUTED, va="center")

# ---- (b) 欧拉：固定网格上存场 ----
ax = axs[1]
nx, ny = 8, 7
g0, gw, gh = 0.14, 0.72, 0.62
xs = g0 + gw * np.arange(nx + 1) / nx
ys = 0.22 + gh * np.arange(ny + 1) / ny
U = np.zeros((ny + 1, nx + 1))
V = np.zeros((ny + 1, nx + 1))
for j, yy in enumerate(ys):
    for i, xx in enumerate(xs):
        dx, dy = xx - 0.46, yy - 0.52
        r2 = (dx / 0.30) ** 2 + (dy / 0.34) ** 2
        wgt = np.exp(-1.4 * r2)
        U[j, i] = -dy * wgt
        V[j, i] = dx * wgt
ax.add_patch(Rectangle((g0, 0.22), gw, gh, facecolor="#F3F6FB", edgecolor="none", zorder=0))
for i, xx in enumerate(xs):
    ax.plot([xx, xx], [0.22, 0.22 + gh], color=GRID, lw=0.8, zorder=1)
for j, yy in enumerate(ys):
    ax.plot([g0, g0 + gw], [yy, yy], color=GRID, lw=0.8, zorder=1)
ax.quiver(xs[1:-1], ys[1:-1], U[1:-1, 1:-1] * 0.42, V[1:-1, 1:-1] * 0.42, color=BLUE,
          angles="xy", scale_units="xy", scale=1.0, width=0.005, zorder=3)
label(ax, 0.03, 0.95, "(b)", fs=9.2, color=INK, weight="bold", ha="left", va="top")
label(ax, 0.5, 0.05, "每个格子存一份场", fs=8.4, color=MUTED, va="center")

# ---- (c) 混合：粒子与网格来回传 ----
ax = axs[2]
nx, ny = 5, 4
xs = g0 + gw * np.arange(nx + 1) / nx
ys = 0.22 + gh * np.arange(ny + 1) / ny
ax.add_patch(Rectangle((g0, 0.22), gw, gh, facecolor="#F8FAFC", edgecolor="none", zorder=0))
for i, xx in enumerate(xs):
    ax.plot([xx, xx], [0.22, 0.22 + gh], color=GRID, lw=0.8, zorder=1)
for j, yy in enumerate(ys):
    ax.plot([g0, g0 + gw], [yy, yy], color=GRID, lw=0.8, zorder=1)
rng3 = np.random.default_rng(21)
sel = rng3.uniform(-1, 1, (95, 2))
sel = sel[sel[:, 0] ** 2 + sel[:, 1] ** 2 < 1]
sel = sel[np.hypot(sel[:, 0], sel[:, 1]) < 0.94]
px = 0.50 + 0.25 * sel[:, 0]
py = 0.53 + 0.21 * sel[:, 1]
ax.scatter(px, py, s=6.5, color=PURPLE, alpha=0.85, linewidths=0, zorder=4)
qx, qy = px[7], py[7]
cx = g0 + gw * np.round((qx - g0) / gw * nx) / nx
cy = 0.22 + gh * np.round((qy - 0.22) / gh * ny) / ny
for ex in (cx - gw / nx, cx):
    for ey in (cy - gh / ny, cy):
        ax.plot([qx, ex], [qy, ey], color=TEAL, lw=1.0, alpha=0.9, zorder=3)
        ax.scatter([ex], [ey], s=8, color=TEAL, zorder=5)
ax.scatter([qx], [qy], s=22, color=PURPLE, edgecolor="white", linewidth=0.8, zorder=6)
label(ax, 0.03, 0.95, "(c)", fs=9.2, color=INK, weight="bold", ha="left", va="top")
label(ax, 0.5, 0.05, "粒子带细节，网格解方程", fs=8.4, color=MUTED, va="center")

save(fig, "04", "fig04-01")

# ============================================================
# 图 4-2  同一个圆：体积分数、粒子、水平集（由解析圆计算）
# ============================================================
R = 0.30
CX, CY = 0.5, 0.5
fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.45))
for ax in axs:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(FAINT)
        s.set_linewidth(0.8)

# ---- (a) 体积分数 ----
ax = axs[0]
N = 10
sub = 24
frac = np.zeros((N, N))
for j in range(N):
    for i in range(N):
        xs_ = (np.arange(sub) + 0.5) / sub
        Xg, Yg = np.meshgrid((i + xs_) / N, (j + xs_) / N)
        frac[j, i] = np.mean((Xg - CX) ** 2 + (Yg - CY) ** 2 < R ** 2)
ax.imshow(frac, extent=[0, 1, 0, 1], origin="lower", cmap="Blues", vmin=0, vmax=1.25,
          zorder=1, interpolation="nearest")
for k in range(N + 1):
    ax.plot([k / N, k / N], [0, 1], color="white", lw=0.8, alpha=0.9, zorder=2)
    ax.plot([0, 1], [k / N, k / N], color="white", lw=0.8, alpha=0.9, zorder=2)
th = np.linspace(0, 2 * np.pi, 200)
ax.plot(CX + R * np.cos(th), CY + R * np.sin(th), color=ACCENT, lw=1.0, ls=(0, (3, 2)),
        zorder=4)
ax.text(0.55, 0.55, "%.2f" % frac[5, 5], color=INK, fontsize=8.0, zorder=5, ha="center",
        va="center")
ax.text(0.06, 0.94, "(a)", color=INK, fontsize=9.2, weight="bold", va="top", zorder=6)
ax.text(0.5, -0.09, "格子里的体积分数", color=MUTED, fontsize=8.4, ha="center", va="top")

# ---- (b) 粒子 ----
ax = axs[1]
h = 0.042
pts = []
yy = -1.0
row = 0
while yy < 1.05:
    off = 0.5 * h if row % 2 else 0.0
    xx = -1.05 + off
    while xx < 1.1:
        pts.append((xx, yy))
        xx += h
    yy += h * 0.866
    row += 1
pts = np.array(pts)
rng2 = np.random.default_rng(11)
pts = pts + rng2.normal(0, h * 0.16, pts.shape)
ins = ((pts[:, 0] - CX) ** 2 + (pts[:, 1] - CY) ** 2) < R ** 2
ax.scatter(pts[ins, 0], pts[ins, 1], s=8.0, color=PURPLE, alpha=0.9, linewidths=0, zorder=3)
ax.scatter(pts[~ins, 0], pts[~ins, 1], s=8.0, color=MUTED, alpha=0.20, linewidths=0, zorder=2)
ax.plot(CX + R * np.cos(th), CY + R * np.sin(th), color=ACCENT, lw=1.0, ls=(0, (3, 2)),
        zorder=4)
ax.text(0.06, 0.94, "(b)", color=INK, fontsize=9.2, weight="bold", va="top", zorder=6)
ax.text(0.5, -0.09, "粒子的位置就是形状", color=MUTED, fontsize=8.4, ha="center", va="top")

# ---- (c) 水平集 ----
ax = axs[2]
n = 240
gx = np.linspace(0, 1, n)
GX, GY = np.meshgrid(gx, gx)
phi = np.sqrt((GX - CX) ** 2 + (GY - CY) ** 2) - R
ax.contourf(GX, GY, phi, levels=np.linspace(-0.32, 0.32, 17), cmap="RdBu_r", alpha=0.85,
            zorder=1)
ax.contour(GX, GY, phi, levels=[0.0], colors=[INK], linewidths=1.2, zorder=4)
ax.contour(GX, GY, phi, levels=[-0.15, 0.15], colors=[INK], linewidths=0.6,
           linestyles="dashed", alpha=0.55, zorder=3)
ax.text(0.06, 0.94, "(c)", color=INK, fontsize=9.2, weight="bold", va="top", zorder=6,
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none",
                  alpha=0.85))
ax.text(0.5, -0.09, "零等值面就是界面", color=MUTED, fontsize=8.4, ha="center", va="top")
ax.annotate("$\\phi = 0$", xy=(0.5, 0.5 + R), xytext=(0.62, 0.90), color=INK, fontsize=8.4,
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8,
                            connectionstyle="arc3,rad=0.2"), zorder=7)

save(fig, "04", "fig04-02")

# ============================================================
# 图 4-3  选型决策树（方框与箭头不重叠，脚本内自检）
# ============================================================
fig, ax = canvas(6.9, 3.95)
boxes = []


def tnode(x, y, w, h, text, fc="white", ec=INK, fs=8.6, lw=1.0):
    box(ax, x, y, w, h, text, fc=fc, ec=ec, fs=fs, lw=lw)
    boxes.append((x, y, x + w, y + h))


# 根
tnode(0.315, 0.845, 0.37, 0.085, "物质的状态跟着什么走？", fc=PAPER, fs=9.2)
# 第二层
tnode(0.020, 0.605, 0.290, 0.080, "跟着物质：粒子", ec=PURPLE)
tnode(0.355, 0.605, 0.290, 0.080, "固定在空间：网格", ec=BLUE)
tnode(0.690, 0.605, 0.290, 0.080, "两者都用：粒子 + 网格", ec=TEAL)
# 第三层
tnode(0.020, 0.360, 0.290, 0.110, "SPH：水花、泡沫、飞溅\nPBD：布料、软体、实时", ec=PURPLE, fs=8.1)
tnode(0.355, 0.360, 0.290, 0.110, "半拉格朗日 + 投影：烟、火\n有限体积：严格守恒的场", ec=BLUE, fs=8.1)
tnode(0.690, 0.360, 0.290, 0.110, "FLIP / APIC：大水、白水\nMPM：雪、沙、相变、粘弹", ec=TEAL, fs=8.1)
# 第四层：共同判据
tnode(0.020, 0.150, 0.290, 0.090, "要精确界面？\n要，就加粒子或水平集", ec=FAINT, fs=8.1)
tnode(0.355, 0.150, 0.290, 0.090, "要拓扑变化？\n要，就别焊死在网格上", ec=FAINT, fs=8.1)
tnode(0.690, 0.150, 0.290, 0.090, "预算够吗？\n紧，就降分辨率或自适应", ec=FAINT, fs=8.1)

segs = []


def poly(points, color=FAINT, lw=1.0):
    for a, b in zip(points[:-1], points[1:]):
        segs.append((a, b))
    for a, b in zip(points[:-2], points[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, zorder=2,
                solid_capstyle="round")
    arrow(ax, points[-2], points[-1], color=color, lw=lw, ms=8)


# 根 -> 三个分支
poly([(0.50, 0.845), (0.50, 0.795), (0.165, 0.795), (0.165, 0.687)])
poly([(0.50, 0.845), (0.50, 0.687)])
poly([(0.50, 0.845), (0.50, 0.795), (0.835, 0.795), (0.835, 0.687)])
# 第二层 -> 第三层
poly([(0.165, 0.605), (0.165, 0.472)])
poly([(0.50, 0.605), (0.50, 0.472)])
poly([(0.835, 0.605), (0.835, 0.472)])
# 第三层 -> 第四层
poly([(0.165, 0.360), (0.165, 0.242)], color=GRID, lw=0.9)
poly([(0.50, 0.360), (0.50, 0.242)], color=GRID, lw=0.9)
poly([(0.835, 0.360), (0.835, 0.242)], color=GRID, lw=0.9)



# ---- 自检：箭头线段不得穿过方框内部 ----
bad = []
for a, b in segs:
    for t in np.linspace(0, 1, 60):
        p = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        for (x0, y0, x1, y1) in boxes:
            inside = (x0 + 0.004 < p[0] < x1 - 0.004) and (y0 + 0.004 < p[1] < y1 - 0.004)
            if inside:
                bad.append((tuple(np.round(p, 3)), (x0, y0, x1, y1)))
print("方框数 %d，箭头线段 %d，穿框点 %d" % (len(boxes), len(segs), len(bad)))
if bad:
    for b in bad[:6]:
        print("  穿框:", b)

save(fig, "04", "fig04-03")
