import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
from matplotlib.patches import Rectangle, Arc

# ============================================================
# 图 2-1  同一个旋转的三种表示（示意图）
#   绕 z 轴转 90°，R = [[0,-1,0],[1,0,0],[0,0,1]]
#   q = (cos45°, 0, 0, sin45°) = (0.707, 0, 0, 0.707)
# ============================================================
fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.75),
                        gridspec_kw=dict(wspace=0.16))
for ax in axs:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

# ---- (a) 旋转矩阵 ----
ax = axs[0]
vals = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
cell, mx, my = 0.185, 0.275, 0.745
for i in range(3):
    for j in range(3):
        x = mx + j * cell
        y = my - (i + 1) * cell
        ax.add_patch(Rectangle((x, y), cell, cell, facecolor=SOFT[1] if vals[i][j] else "white",
                               edgecolor=GRID, lw=0.8, zorder=2))
        label(ax, x + cell / 2, y + cell / 2, str(vals[i][j]), fs=9.6, color=INK)
# 方括号
for xb in (mx - 0.012, mx + 3 * cell + 0.012):
    ax.plot([xb, xb], [my, my - 3 * cell], color=INK, lw=1.2)
    s = 0.02 * (1 if xb < mx else -1)
    ax.plot([xb, xb - s], [my, my], color=INK, lw=1.2)
    ax.plot([xb, xb - s], [my - 3 * cell, my - 3 * cell], color=INK, lw=1.2)
label(ax, 0.5, 0.885, "旋转矩阵", fs=9.2, weight="bold")
label(ax, 0.5, 0.150, "9 个数，6 个正交约束", fs=8.2, color=SLATE)
label(ax, 0.5, 0.075, "只剩 3 个自由度", fs=8.2, color=SLATE)

# ---- (b) 轴角 ----
ax = axs[1]
cx, cy = 0.50, 0.400
ax.add_patch(Ellipse((cx, cy), 0.60, 0.28, angle=0, fill=False, edgecolor=FAINT,
                     lw=1.0, ls=(0, (3, 2.5)), zorder=2))
arrow(ax, (cx, cy), (cx, cy + 0.335), color=INK, lw=1.3, ms=9)
label(ax, cx + 0.022, cy + 0.352, "轴 $\\mathbf{n}$", fs=8.6, color=INK, ha="left", va="center")
rx_, ry_ = 0.30, 0.14
a0, a1 = np.radians(-24), np.radians(44)
p0 = np.array([cx + rx_ * np.cos(a0), cy + ry_ * np.sin(a0)])
p1 = np.array([cx + rx_ * np.cos(a1), cy + ry_ * np.sin(a1)])
ax.plot([cx, p0[0]], [cy, p0[1]], color=SLATE, lw=0.9, zorder=3)
ax.plot([cx, p1[0]], [cy, p1[1]], color=ACCENT, lw=0.9, zorder=3)
ax.scatter([p0[0]], [p0[1]], s=16, color=SLATE, zorder=5)
ax.scatter([p1[0]], [p1[1]], s=16, color=ACCENT, zorder=5)
ax.add_patch(Arc((cx, cy), 0.40, 0.187, angle=0, theta1=-24, theta2=44,
                 color=ACCENT, lw=1.0, zorder=4))
label(ax, cx + 0.136, cy + 0.020, "$\\theta$", fs=9.6, color=ACCENT)
label(ax, p0[0] + 0.018, p0[1] - 0.020, "p", fs=8.4, color=SLATE, ha="left", va="top")
label(ax, p1[0] + 0.020, p1[1] + 0.024, "p'", fs=8.4, color=ACCENT, ha="left")
label(ax, 0.5, 0.885, "轴角", fs=9.2, weight="bold")
label(ax, 0.5, 0.150, "3 个轴分量 + 1 个角", fs=8.2, color=SLATE)
label(ax, 0.5, 0.075, "轴长要归一化，角取 0 到 π", fs=8.2, color=SLATE)

# ---- (c) 四元数 ----
ax = axs[2]
box(ax, 0.215, 0.245, 0.57, 0.42, "", fc=SOFT[3], ec=PURPLE, lw=1.1)
parts = [("w", "0.707"), ("x", "0"), ("y", "0"), ("z", "0.707")]
for i, (k, v) in enumerate(parts):
    y = 0.615 - i * 0.098
    label(ax, 0.280, y, k, fs=9.0, color=PURPLE, ha="left")
    label(ax, 0.390, y, "=", fs=8.6, color=SLATE, ha="left")
    label(ax, 0.470, y, v, fs=9.0, color=INK, ha="left")
label(ax, 0.5, 0.885, "单位四元数", fs=9.2, weight="bold")
label(ax, 0.5, 0.150, "4 个数，模长为 1", fs=8.2, color=SLATE)
label(ax, 0.5, 0.075, "$\\mathbf{q}$ 与 $-\\mathbf{q}$ 是同一个旋转", fs=8.2, color=SLATE)
save(fig, "02", "fig02-01")

# ============================================================
# 图 2-2  SVD：单位圆被 A 映射成椭圆
#   A = [[1.5, 0.8], [0.4, 1.1]]，网格步长 0.3，范围 [-1.2, 1.2]
# ============================================================
A = np.array([[1.5, 0.8], [0.4, 1.1]])
U, S, Vt = np.linalg.svd(A)

fig, ax = plt.subplots(figsize=(6.5, 3.95))
ax.axis("off")
ax.set_aspect("equal")

gv = np.arange(-1.2, 1.2001, 0.3)
tt = np.linspace(0, 2 * np.pi, 500)
circ = np.array([np.cos(tt), np.sin(tt)])


def grid_segments():
    for g in gv:
        yield np.array([[g, g], [-1.2, 1.2]])
        yield np.array([[-1.2, 1.2], [g, g]])


# 原像网格：极淡的虚线
for seg in grid_segments():
    ax.plot(seg[0], seg[1], color="#E7E9ED", lw=0.7, ls=(0, (2, 2.5)), zorder=1)
# 像网格
for seg in grid_segments():
    p = A @ seg
    ax.plot(p[0], p[1], color="#CFD4DB", lw=0.8, zorder=2)

ax.plot([-2.05, 2.05], [0, 0], color=FAINT, lw=0.8, zorder=1)
ax.plot([0, 0], [-1.70, 1.70], color=FAINT, lw=0.8, zorder=1)

# 原像单位圆
ax.plot(circ[0], circ[1], color=BLUE, lw=1.3, ls=(0, (4, 3)), zorder=3)
# 像：椭圆
im = A @ circ
ax.plot(im[0], im[1], color=ACCENT, lw=1.9, zorder=4)

# 主轴
u1 = -U[:, 0]
u2 = -U[:, 1]
v1 = S[0] * u1
v2 = S[1] * u2
arrow(ax, (0, 0), (v1[0], v1[1]), color=PURPLE, lw=1.3, ms=9, shrinkA=0, z=6)
arrow(ax, (0, 0), (v2[0], v2[1]), color=PURPLE, lw=1.3, ms=9, shrinkA=0, z=6)
label(ax, v1[0] + 0.10, v1[1] + 0.10, "$\\sigma_1 = %.2f$" % S[0], fs=8.6, color=PURPLE,
      ha="left", va="bottom")
label(ax, v2[0] + 0.16, v2[1] - 0.34, "$\\sigma_2 = %.2f$" % S[1], fs=8.6, color=PURPLE,
      ha="left", va="top")

label(ax, -2.20, 1.74, "原像：单位圆 + 网格", fs=8.4, color=BLUE, ha="left", va="top")
label(ax, 0.28, 1.74, "像：椭圆 + 剪切后的网格", fs=8.4, color=ACCENT, ha="left", va="top")
label(ax, -2.20, -1.86, "A = [[1.5, 0.8], [0.4, 1.1]]，网格步长 0.3，面积比 |det A| = %.2f" % abs(np.linalg.det(A)),
      fs=8.8, color=INK, ha="left", va="bottom")
ax.set_xlim(-2.35, 2.62)
ax.set_ylim(-2.00, 1.80)
save(fig, "02", "fig02-02")

# ============================================================
# 图 2-3  欧拉角线性插值与四元数 slerp 的轨迹对比
#   起止姿态：单位阵 → 绕 z 转 150°、再绕 y 转 85°（ZYX 顺序）
#   采样 201 个插值参数 t
# ============================================================
def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                     w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])


def qaxis(ax_, ang):
    ax_ = np.asarray(ax_, float)
    ax_ = ax_ / np.linalg.norm(ax_)
    return np.concatenate([[np.cos(ang / 2)], np.sin(ang / 2) * ax_])


def qeuler(yaw, pitch, roll):
    return qmul(qmul(qaxis([0, 0, 1], yaw), qaxis([0, 1, 0], pitch)), qaxis([1, 0, 0], roll))


def R_from_q(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def slerp(q0, q1, t):
    q0 = q0 / np.linalg.norm(q0)
    q1 = q1 / np.linalg.norm(q1)
    d = float(np.dot(q0, q1))
    if d < 0:
        q1 = -q1
        d = -d
    d = min(1.0, d)
    th = np.arccos(d)
    if th < 1e-9:
        return q0.copy()
    return (np.sin((1 - t) * th) * q0 + np.sin(t * th) * q1) / np.sin(th)


def ang_between(Ra, Rb):
    return np.degrees(np.arccos(np.clip((np.trace(Ra.T @ Rb) - 1) / 2, -1, 1)))


YAW, PITCH = np.radians(150), np.radians(85)
q0 = np.array([1.0, 0, 0, 0])
q1 = qeuler(YAW, PITCH, 0.0)
ts = np.linspace(0, 1, 201)
Rv = np.array([1.0, 0, 0])

P_e, P_s, dev = [], [], []
for t in ts:
    Re = R_from_q(qeuler(t * YAW, t * PITCH, 0.0))
    Rs = R_from_q(slerp(q0, q1, t))
    P_e.append(Re @ Rv)
    P_s.append(Rs @ Rv)
    dev.append(ang_between(Re, Rs))
P_e, P_s, dev = np.array(P_e), np.array(P_s), np.array(dev)

fig = plt.figure(figsize=(6.9, 3.3))
ax3 = fig.add_subplot(1, 2, 1, projection="3d")
ax2 = fig.add_subplot(1, 2, 2)
fig.subplots_adjust(wspace=0.20)

ph = np.linspace(0, 2 * np.pi, 240)
circles = [np.c_[np.cos(ph), np.sin(ph), 0 * ph],
           np.c_[np.cos(ph), 0 * ph, np.sin(ph)],
           np.c_[0 * ph, np.cos(ph), np.sin(ph)]]
for c in circles:
    ax3.plot(c[:, 0], c[:, 1], c[:, 2], color="#D6DAE0", lw=0.7, zorder=1)
ax3.plot(P_e[:, 0], P_e[:, 1], P_e[:, 2], color=ACCENT, lw=2.0, zorder=6)
ax3.plot(P_s[:, 0], P_s[:, 1], P_s[:, 2], color=BLUE, lw=2.0, zorder=7)
ax3.scatter([P_e[0, 0]], [P_e[0, 1]], [P_e[0, 2]], s=26, color=INK, zorder=9, depthshade=False)
ax3.scatter([P_e[-1, 0]], [P_e[-1, 1]], [P_e[-1, 2]], s=26, color=GREEN, zorder=9,
            depthshade=False)
ax3.text(P_e[0, 0] + 0.10, P_e[0, 1] - 0.06, P_e[0, 2] + 0.16, "$t=0$", fontsize=8.2, color=INK)
ax3.text(P_e[-1, 0] + 0.06, P_e[-1, 1] + 0.12, P_e[-1, 2] - 0.16, "$t=1$", fontsize=8.2, color=GREEN)
ax3.set_box_aspect((1, 1, 1))
ax3.set_xlim(-1.05, 1.05)
ax3.set_ylim(-1.05, 1.05)
ax3.set_zlim(-1.05, 1.05)
ax3.set_axis_off()
ax3.view_init(elev=9, azim=52)
ax3.text2D(0.02, 0.97, "单位向量 $\\mathbf{r}$ 末端的轨迹", transform=ax3.transAxes,
           fontsize=8.6, color=INK, va="top")
ax3.text2D(0.02, 0.905, "欧拉角线性插值", transform=ax3.transAxes, fontsize=8.4,
           color=ACCENT, va="top")
ax3.text2D(0.02, 0.850, "四元数 slerp", transform=ax3.transAxes, fontsize=8.4,
           color=BLUE, va="top")

clean(ax2, grid=True, spines=("left", "bottom"))
ax2.plot(ts, dev, color=PURPLE, lw=1.6)
imax = int(np.argmax(dev))
ax2.plot([ts[imax]], [dev[imax]], marker="o", ms=4.2, color=PURPLE, mfc="white", mew=1.0)
ax2.annotate("最大 %.1f°\n$t=%.2f$" % (dev[imax], ts[imax]),
             xy=(ts[imax], dev[imax]), xytext=(ts[imax] + 0.10, 7.5),
             fontsize=8.4, color=PURPLE, va="center",
             arrowprops=dict(arrowstyle="-", color=PURPLE, lw=0.8))
ax2.set_xlim(0, 1.0)
ax2.set_ylim(0, 38)
ax2.set_xlabel("插值参数 $t$")
ax2.set_ylabel("两种姿态的夹角（度）")
ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
save(fig, "02", "fig02-03")
