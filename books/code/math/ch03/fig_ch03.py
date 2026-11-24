import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np
from matplotlib.patches import Polygon, Circle


# ---------------------------------------------------------------- 图 3-1
# 参考构型 -> 当前构型。映射 phi 取一个带二次项的小变形场：
#   phi(X,Y) = (1.30 X + 0.20 Y + 0.18 XY,  0.90 Y + 0.25 XY)
# 变形梯度 F = dphi/dX（解析求导），在 P=(0.55,0.45) 处取值。


def phi(X, Y):
    return 1.30 * X + 0.20 * Y + 0.18 * X * Y, 0.90 * Y + 0.25 * X * Y


def Fmat(X, Y):
    return np.array([[1.30 + 0.18 * Y, 0.20 + 0.18 * X],
                     [0.25 * Y, 0.90 + 0.25 * X]])


fig, ax = canvas(6.8, 3.35, xlim=(0, 6.8), ylim=(0, 3.35))
ax.set_aspect("equal")

S = 1.42                       # 物理单位 -> 英寸
REF_X0, REF_Y0 = 1.00, 1.15    # 参考构型左下角

# 当前构型：先算 phi 的值域，等比塞进右侧的框
_g = np.linspace(0, 1, 41)
_gX, _gY = np.meshgrid(_g, _g)
_px, _py = phi(_gX, _gY)
cur_x = (_px.min(), _px.max())
cur_y = (_py.min(), _py.max())
BOX = (3.95, 1.20, 2.50, 1.85)
sc = min(BOX[2] / (cur_x[1] - cur_x[0]), BOX[3] / (cur_y[1] - cur_y[0]))


def m2s(X, Y):
    """当前构型：物质坐标 -> 屏幕英寸"""
    x, y = phi(X, Y)
    return BOX[0] + (x - cur_x[0]) * sc, BOX[1] + (y - cur_y[0]) * sc


def r2s(X, Y):
    """参考构型：物质坐标 -> 屏幕英寸"""
    return REF_X0 + X * S, REF_Y0 + Y * S


n = 8
for k in range(n + 1):
    t = k / n
    ax.plot(*zip(r2s(t, 0), r2s(t, 1)), color=GRID, lw=0.6, zorder=1)
    ax.plot(*zip(r2s(0, t), r2s(1, t)), color=GRID, lw=0.6, zorder=1)

    ss = np.linspace(0, 1, 80)
    Xs, Ys = phi(ss, np.full_like(ss, t))
    ax.plot(BOX[0] + (Xs - cur_x[0]) * sc, BOX[1] + (Ys - cur_y[0]) * sc,
            color=GRID, lw=0.6, zorder=1)
    Xs, Ys = phi(np.full_like(ss, t), ss)
    ax.plot(BOX[0] + (Xs - cur_x[0]) * sc, BOX[1] + (Ys - cur_y[0]) * sc,
            color=GRID, lw=0.6, zorder=1)

# 参考构型外框
b0 = r2s(0, 0)
ax.add_patch(Rectangle(b0, S, S, fill=False, ec=INK, lw=1.1, zorder=3))

# 当前构型外框
ed = np.linspace(0, 1, 80)
pts = [m2s(ed, np.zeros_like(ed)), m2s(np.ones_like(ed), ed),
       m2s(ed[::-1], np.ones_like(ed)), m2s(np.zeros_like(ed), ed[::-1])]
pl = np.concatenate([np.column_stack(p) for p in pts])
ax.plot(np.append(pl[:, 0], pl[0, 0]), np.append(pl[:, 1], pl[0, 1]),
        color=INK, lw=1.1, zorder=3)

# 高亮一个物质单元并画基向量
P = np.array([0.55, 0.45])
h = 0.10
cell = np.array([[P[0] - h, P[1] - h], [P[0] + h, P[1] - h],
                 [P[0] + h, P[1] + h], [P[0] - h, P[1] + h]])
ax.add_patch(Polygon([r2s(*c) for c in cell], closed=True, fc=ACCENT, alpha=0.16,
                     ec=ACCENT, lw=0.9, zorder=4))

F = Fmat(*P)
dX1 = np.array([2 * h, 0.0])
dX2 = np.array([0.0, 2 * h])
dx1, dx2 = F @ dX1, F @ dX2
qx, qy = m2s(*P)
ax.add_patch(Polygon([m2s(*c) for c in cell], closed=True, fc=ACCENT, alpha=0.16,
                     ec=ACCENT, lw=0.9, zorder=4))

# 参考构型的基向量
p0 = r2s(*P)
ax.add_patch(Circle(p0, 0.035, color=INK, zorder=6))
for dv, lab, col, off, ha in ((dX1, r"$d\mathbf{X}_1$", BLUE, (0.05, -0.03), "left"),
                              (dX2, r"$d\mathbf{X}_2$", GREEN, (0.04, 0.03), "left")):
    e = r2s(P[0] + dv[0], P[1] + dv[1])
    arrow(ax, p0, e, color=col, lw=1.5, z=5, ms=9)
    label(ax, e[0] + off[0], e[1] + off[1], lab, fs=8.8, color=col, ha=ha)

# 当前构型的基向量 dx = F dX
ax.add_patch(Circle((qx, qy), 0.035, color=INK, zorder=6))
for dv, lab, col, off in ((dx1, r"$d\mathbf{x}_1$", BLUE, (0.05, -0.04)),
                          (dx2, r"$d\mathbf{x}_2$", GREEN, (0.05, 0.01))):
    e = (qx + dv[0] * sc, qy + dv[1] * sc)
    arrow(ax, (qx, qy), e, color=col, lw=1.5, z=5, ms=9)
    label(ax, e[0] + off[0], e[1] + off[1], lab, fs=9, color=col, ha="left")

label(ax, p0[0] - 0.12, p0[1] - 0.30, r"$\mathbf{X}$", fs=10, color=INK)
label(ax, qx - 0.10, qy - 0.34, r"$\mathbf{x}=\boldsymbol{\varphi}(\mathbf{X})$", fs=9.4, color=INK,
      bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.2))
label(ax, 5.22, 2.88, r"$d\mathbf{x}=\mathbf{F}\,d\mathbf{X}$", fs=9.4, color=INK)

# 映射箭头
arrow(ax, (3.05, 1.90), (3.72, 1.90), color=ACCENT, lw=1.7, ms=14)
label(ax, 3.38, 2.10, r"$\boldsymbol{\varphi}$", fs=12, color=ACCENT)
label(ax, 3.38, 1.66, "运动映射", fs=8.6, color=ACCENT)

label(ax, 1.71, 2.90, "参考构型", fs=10, color=INK)
label(ax, 1.71, 0.80, r"物质坐标 $\mathbf{X}$", fs=8.6, color=MUTED)
label(ax, 5.20, 3.10, "当前构型", fs=10, color=INK)
label(ax, 5.20, 0.88, r"空间坐标 $\mathbf{x}$", fs=8.6, color=MUTED)

label(ax, 0.30, 0.40,
      r"$\mathbf{F}=\partial\boldsymbol{\varphi}/\partial\mathbf{X}$，在 $\mathbf{X}=(0.55,0.45)$ 处："
      r"$F_{11}=%.2f$，$F_{12}=%.2f$，$F_{21}=%.2f$，$F_{22}=%.2f$"
      % (F[0, 0], F[0, 1], F[1, 0], F[1, 1]),
      fs=8.6, color=MUTED, ha="left")

save(fig, "03", "fig03-01")


# ---------------------------------------------------------------- 图 3-2
# 单轴拉伸 lam = 1 + 伸长率，小应变 eps = lam - 1，
# Green-Lagrange 应变 E = (lam^2 - 1)/2，Hencky 应变 ln(lam)。
lam = np.linspace(1.0, 1.5, 400)
eps = lam - 1.0
Egr = 0.5 * (lam ** 2 - 1.0)
eHe = np.log(lam)
x = (lam - 1) * 100

fig, ax = plt.subplots(figsize=(6.7, 3.9))
ax.set_xlim(-1.5, 54)
ax.set_ylim(0.0, 0.72)
clean(ax, grid=True)

ax.fill_between(x, eps, Egr, color=ACCENT, alpha=0.08, zorder=1)
ax.plot(x, Egr, color=ACCENT, lw=1.9, zorder=4,
        label=r"Green 应变 $E_{11}=(\lambda^2-1)/2$")
ax.plot(x, eps, color=BLUE, lw=1.9, zorder=4,
        label=r"小应变 $\varepsilon_{11}=\lambda-1$")
ax.plot(x, eHe, color=GREEN, lw=1.4, ls="--", zorder=3,
        label=r"对数应变 $e_{11}=\ln\lambda$")

for yy, cc in ((Egr[-1], ACCENT), (eps[-1], BLUE), (eHe[-1], GREEN)):
    ax.plot([50], [yy], "o", ms=5, color=cc, zorder=6)

# 50% 处的差值
ax.annotate("", xy=(45.0, Egr[-1]), xytext=(45.0, eps[-1]),
            arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.9))
ax.plot([45.0, 49.7], [Egr[-1], Egr[-1]], color=FAINT, lw=0.6, ls=":")
ax.plot([45.0, 49.7], [eps[-1], eps[-1]], color=FAINT, lw=0.6, ls=":")
label(ax, 45.0, 0.672, "差 0.125", fs=8.4, color=MUTED)

ax.set_xlabel(r"伸出量 $(\lambda-1)\times 100\%$")
ax.set_ylabel("轴向应变")
ax.legend(loc="upper left", frameon=False, fontsize=8.8,
          bbox_to_anchor=(0.02, 0.99), handlelength=2.3, labelspacing=0.45)
label(ax, 20.0, 0.042, "小变形区：三条曲线几乎重合", fs=8.2, color=MUTED, ha="center")
arrow(ax, (13.0, 0.072), (4.5, 0.028), color=FAINT, lw=0.7, ms=6)
ax.set_xticks([0, 10, 20, 30, 40, 50])
ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

save(fig, "03", "fig03-02")


# ---------------------------------------------------------------- 图 3-3
# 一点上应力分量的示意立方体（轴测投影，英寸坐标，等比）。
fig, ax = canvas(6.9, 4.3, xlim=(0, 6.9), ylim=(0, 4.3))
ax.set_aspect("equal")

O = np.array([3.55, 0.72])
ex = np.array([1.35, 0.00])
ey = np.array([0.55, 0.45])
ez = np.array([0.00, 1.45])
A = O + ex
B = O + ey
C = O + ey + ex

faces = [("front", [O, A, A + ez, O + ez], "#F4F5F7"),
         ("right", [A, C, C + ez, A + ez], "#E7EBF0"),
         ("top", [O + ez, A + ez, C + ez, B + ez], "#FBF7F0")]
for name, poly, fc in faces:
    ax.add_patch(Polygon(np.array(poly), closed=True, fc=fc, ec=INK, lw=1.0, zorder=2))

# 前表面（法向 +x）上的三个分量
Fc = O + ex / 2 + ez / 2
arrow(ax, (3.78, 1.22), (4.66, 1.22), color=ACCENT, lw=1.8, ms=11, z=6)
label(ax, 4.22, 1.05, r"$\sigma_{xx}$", fs=9.8, color=ACCENT)

arrow(ax, (3.80, 1.52), (4.15, 1.80), color=GREEN, lw=1.6, ms=10, z=6)
label(ax, 3.95, 1.94, r"$\tau_{xy}$", fs=9.4, color=GREEN)

arrow(ax, (4.50, 1.38), (4.50, 1.88), color=PURPLE, lw=1.6, ms=10, z=6)
label(ax, 4.60, 1.63, r"$\tau_{xz}$", fs=9.4, color=PURPLE, ha="left")

# 右表面（法向 +y）与上表面（法向 +z）只画法向分量
Rc = (A + C) / 2 + ez / 2
arrow(ax, (5.12, 1.62), (5.46, 1.90), color=ACCENT, lw=1.8, ms=11, z=6)
label(ax, 5.56, 2.02, r"$\sigma_{yy}$", fs=9.8, color=ACCENT, ha="left")

Tc = (O + ez + C + ez) / 2
arrow(ax, (4.52, 2.42), (4.52, 2.86), color=ACCENT, lw=1.8, ms=11, z=6)
label(ax, 4.62, 3.00, r"$\sigma_{zz}$", fs=9.8, color=ACCENT, ha="left")

# 面名（法向）
label(ax, 3.60, 0.46, r"$\mathbf{n}=+\mathbf{e}_x$", fs=8.8, color=MUTED, ha="left")
label(ax, 5.56, 1.28, r"$\mathbf{n}=+\mathbf{e}_y$", fs=8.8, color=MUTED, ha="left")
label(ax, 3.78, 2.82, r"$\mathbf{n}=+\mathbf{e}_z$", fs=8.8, color=MUTED, ha="left")

label(ax, 0.30, 3.96,
      r"牵引向量 $\mathbf{t}=\boldsymbol{\sigma}\mathbf{n}$ 随面法向 $\mathbf{n}$ 变化",
      fs=8.8, color=MUTED, ha="left")

# 3x3 分量表（手工排版）
label(ax, 0.30, 3.24, "九个分量写成一张表", fs=9.4, color=INK, ha="left")
label(ax, 0.30, 2.98, "行号 = 面法向，列号 = 力的方向", fs=8.2, color=MUTED, ha="left")

cols = [1.06, 2.00, 2.94]
rows_y = [2.48, 2.08, 1.68]
ent = [[r"$\sigma_{xx}$", r"$\tau_{xy}$", r"$\tau_{xz}$"],
       [r"$\tau_{yx}$", r"$\sigma_{yy}$", r"$\tau_{yz}$"],
       [r"$\tau_{zx}$", r"$\tau_{zy}$", r"$\sigma_{zz}$"]]
for j, yy in enumerate(rows_y):
    for i, xx in enumerate(cols):
        label(ax, xx, yy, ent[j][i], fs=9.4, color=INK)

for xb, sgn in ((0.90, 1), (3.28, -1)):
    ax.plot([xb + 0.05 * sgn, xb, xb, xb + 0.05 * sgn],
            [2.66, 2.66, 1.50, 1.50], color=INK, lw=1.0, zorder=6)
label(ax, 0.40, 2.08, r"$\boldsymbol{\sigma}$", fs=11, color=INK, ha="left")

label(ax, 0.30, 1.02, r"对称：$\sigma_{ij}=\sigma_{ji}$，九个分量只剩六个独立值",
      fs=8.2, color=MUTED, ha="left")
label(ax, 0.30, 0.70, "前表面画出完整分解，另两面只画法向分量，",
      fs=8.0, color=FAINT, ha="left")
label(ax, 0.30, 0.44, "切向分量按同一规则轮换（示意图）", fs=8.0, color=FAINT, ha="left")

save(fig, "03", "fig03-03")
