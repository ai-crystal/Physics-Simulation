import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


# ---------------------------------------------------------------- 图 8-1
# 悬臂梁大变形平衡形状：EI*theta'' = -P*cos(theta)，theta(0)=0，theta'(L)=0
def elastica(P, EI=1.0, L=1.0, n=1600):
    def rhs(s, y):
        th, w = y
        return [w, -P / EI * np.cos(th)]

    def integrate(slope0, t_eval=None):
        return solve_ivp(rhs, [0.0, L], [0.0, slope0], t_eval=t_eval,
                         rtol=1e-11, atol=1e-13)

    slope0 = brentq(lambda a: integrate(a).y[1, -1], 0.05, 12.0, xtol=1e-12)
    s = np.linspace(0.0, L, n)
    sol = integrate(slope0, s)
    th = sol.y[0]
    ds = np.diff(s)
    x = np.concatenate([[0.0], np.cumsum(np.cos(th)[1:] * ds)])
    y = np.concatenate([[0.0], np.cumsum(np.sin(th)[1:] * ds)])
    res = abs(integrate(slope0).y[1, -1])
    return s, th, x, y, res


def fig01():
    EI, L, P = 1.0, 1.0, 1.8
    s, th, x, y, res = elastica(P, EI, L)
    y_lin = P * s ** 2 * (3 * L - s) / (6 * EI)   # 线性解按弧长坐标作图

    fig, ax = plt.subplots(figsize=(6.2, 4.05))
    ax.plot(x, y, color=ACCENT, lw=2.6, solid_capstyle="round", zorder=4,
            label="非线性解")
    ax.plot(s, y_lin, color=BLUE, lw=1.5, ls=(0, (5, 2)), zorder=3,
            label="线性解")

    # 固定端
    ax.plot([0, 0], [-0.020, 0.055], color=INK, lw=2.2, zorder=5)
    for yy in np.arange(-0.016, 0.055, 0.022):
        ax.plot([-0.026, 0.0], [yy, yy + 0.022], color=MUTED, lw=0.8, zorder=5)

    # 两个端点的高度
    ax.plot([0, x[-1]], [y[-1], y[-1]], color=FAINT, lw=0.8, ls=(0, (3, 2)), zorder=2)
    ax.plot([0, L], [y_lin[-1], y_lin[-1]], color=FAINT, lw=0.8,
            ls=(0, (2, 2)), zorder=2)
    label(ax, 0.030, y[-1] - 0.026, "0.463 m", fs=8.6, color=ACCENT, ha="left",
          va="bottom")
    label(ax, 0.030, y_lin[-1] + 0.014, "0.600 m", fs=8.6, color=BLUE, ha="left",
          va="bottom")

    # 端部载荷（从右下方指向变形后的端点）
    xt, yt = x[-1], y[-1]
    arrow(ax, (0.700, 0.700), (xt - 0.012, yt + 0.024), color=INK, lw=1.2, ms=9, z=6)
    label(ax, 0.690, 0.705, r"$P$", fs=10, color=INK, ha="right", va="bottom")

    # 水平缩短
    ax.annotate("", xy=(0.0, 0.760), xytext=(0.860, 0.760),
                arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.8,
                                mutation_scale=7))
    ax.plot([0.860, 0.860], [0.760, 0.500], color=FAINT, lw=0.7, ls=(0, (2, 2)))
    ax.plot([1.000, 1.000], [0.760, y_lin[-1] + 0.02], color=FAINT, lw=0.7,
            ls=(0, (2, 2)))
    label(ax, 0.43, 0.805, "水平投影 0.860 m", fs=8.4, color=MUTED)

    ax.set_xlabel("$x$  (m)")
    ax.set_ylabel("$y$  (m，向下为正)")
    ax.set_xlim(-0.05, 1.12)
    ax.set_ylim(0.84, -0.16)
    ax.set_aspect("equal")
    clean(ax, grid=True)
    ax.legend(loc="upper left", fontsize=8.6, handlelength=2.4, borderaxespad=0.5)
    ax.text(1.11, 0.22, "$L=1$ m\n$EI=1$ N·m²\n$P=1.8$ N", fontsize=8.0,
            color=MUTED, ha="right", va="top", linespacing=1.7)
    print("  末端弯矩残差", res)
    save(fig, "08", "fig08-01")


# ---------------------------------------------------------------- 图 8-2
def fig02():
    fig, ax = canvas(6.8, 3.6, (0, 1), (0, 1))

    pts = [(0.10, 0.46), (0.30, 0.67), (0.53, 0.75), (0.76, 0.66), (0.92, 0.49)]
    P = np.array(pts)
    ax.plot(P[:, 0], P[:, 1], color=INK, lw=2.1, zorder=3, solid_capstyle="round")
    for i, p in enumerate(P):
        ax.scatter([p[0]], [p[1]], s=46, facecolor="white", edgecolor=INK,
                   linewidth=1.2, zorder=5)
        label(ax, p[0], p[1] - 0.072, rf"$\mathbf{{x}}_{i}$".replace("i", str(i)),
              fs=8.8, color=INK)

    # 转角：节点 x_2 处，入射边的延长线与出射边之间
    i = 2
    d1 = P[i] - P[i - 1]; d1 /= np.linalg.norm(d1)
    d2 = P[i + 1] - P[i]; d2 /= np.linalg.norm(d2)
    ax.plot([P[i][0], P[i][0] + 0.115 * d1[0]], [P[i][1], P[i][1] + 0.115 * d1[1]],
            color=FAINT, lw=1.0, ls=(0, (3, 2)), zorder=2)
    a1 = np.degrees(np.arctan2(d1[1], d1[0]))
    a2 = np.degrees(np.arctan2(d2[1], d2[0]))
    ax.add_patch(Arc(P[i], 0.155, 0.155, theta1=a2, theta2=a1,
                     color=PURPLE, lw=1.0, zorder=4))
    label(ax, P[i][0] + 0.105, P[i][1] + 0.010, r"$\theta_i$", fs=9.4, color=PURPLE,
          ha="left")

    # 材料坐标轴：m1 在纸面内，m2 垂直纸面
    for i, col, dx in ((1, BLUE, -0.018), (3, ACCENT, 0.018)):
        p = P[i]
        tng = (P[i] - P[i - 1]) / np.linalg.norm(P[i] - P[i - 1])
        nrm = np.array([-tng[1], tng[0]])
        if nrm[1] < 0:
            nrm = -nrm
        arrow(ax, p, p + 0.105 * nrm, color=col, lw=1.0, ms=6, z=6)
        label(ax, p[0] + 0.128 * nrm[0] + dx, p[1] + 0.128 * nrm[1], r"$\mathbf{m}_1$",
              fs=8.6, color=col)
        # 垂直纸面的轴：圆圈加叉
        c2 = p + 0.055 * nrm + 0.055 * tng
        ax.add_patch(Circle(c2, 0.016, facecolor="white", edgecolor=col, lw=0.9, zorder=6))
        ax.plot([c2[0] - 0.011, c2[0] + 0.011], [c2[1] - 0.011, c2[1] + 0.011],
                color=col, lw=0.8, zorder=7)
        ax.plot([c2[0] - 0.011, c2[0] + 0.011], [c2[1] + 0.011, c2[1] - 0.011],
                color=col, lw=0.8, zorder=7)
        label(ax, c2[0] + 0.030, c2[1] + 0.004, r"$\mathbf{m}_2$", fs=8.6, color=col,
              ha="left")

    # 边标号
    label(ax, 0.152, 0.420, r"$\mathbf{e}_i$", fs=8.4, color=MUTED)

    # 能量式
    box(ax, 0.025, 0.015, 0.545, 0.285, "", fc="#FBF7F0", ec=GRID, lw=0.8)
    label(ax, 0.045, 0.225,
          r"$E=\dfrac{1}{2}\sum_i\dfrac{EI}{l_i}(\theta_i-\bar\theta_i)^2"
          r"+\dfrac{1}{2}\sum_i\dfrac{GJ}{l_i}(\tau_i-\bar\tau_i)^2$",
          fs=8.6, color=INK, ha="left", va="center")
    label(ax, 0.045, 0.105,
          r"$\tau_i=(\varphi_{i+1}-\varphi_i)/l_i$，材料轴沿边平行传输",
          fs=8.2, color=MUTED, ha="left", va="center")
    label(ax, 0.045, 0.048, "$l_i$ 为第 $i$ 段长度，$EI$ 与 $GJ$ 分别为弯、扭刚度", fs=8.0,
          color=FAINT, ha="left", va="center")

    # 右下：截面绕切向转动
    cx, cy, r = 0.775, 0.245, 0.078
    ax.add_patch(Circle((cx, cy), r, facecolor="white", edgecolor=INK, lw=1.0, zorder=4))
    ax.add_patch(Circle((cx, cy), 0.0055, facecolor=INK, edgecolor="none", zorder=6))
    arrow(ax, (cx, cy), (cx + r * 0.90, cy + r * 0.28), color=BLUE, lw=1.0, ms=6, z=7)
    arrow(ax, (cx, cy), (cx + r * 0.26, cy + r * 0.90), color=ACCENT, lw=1.0, ms=6, z=7)
    label(ax, cx + r * 1.05, cy + r * 0.26, r"$\mathbf{m}_1$", fs=8.4, color=BLUE,
          ha="left")
    label(ax, cx + r * 0.28, cy + r * 1.12, r"$\mathbf{m}_2$", fs=8.4, color=ACCENT)
    ax.add_patch(Arc((cx, cy), 2 * r * 0.52, 2 * r * 0.52, theta1=17, theta2=74,
                     color=MUTED, lw=0.9))
    label(ax, cx - 0.014, cy + r * 0.40, r"$\varphi_i$", fs=8.6, color=MUTED,
          ha="right")
    label(ax, cx, 0.128, "沿边看截面，转过的角", fs=8.2, color=MUTED)

    save(fig, "08", "fig08-02")


fig01()
fig02()
