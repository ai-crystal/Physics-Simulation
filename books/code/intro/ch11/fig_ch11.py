import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 11-1
def fig01():
    fig, ax = canvas(6.6, 3.6)

    # 左：一次消息传递
    ci = (0.235, 0.50)
    nb = [(0.045, 0.78), (0.035, 0.20), (0.175, 0.90)]
    for p in nb:
        ax.plot([p[0], ci[0]], [p[1], ci[1]], color=FAINT, lw=1.0, zorder=1)
    ax.scatter([p[0] for p in nb], [p[1] for p in nb], s=62, color="white",
               edgecolor=INK, linewidth=1.0, zorder=3)
    ax.scatter([ci[0]], [ci[1]], s=78, color=SOFT[4], edgecolor=ACCENT,
               linewidth=1.2, zorder=4)
    label(ax, ci[0], ci[1] - 0.075, r"$i$", fs=10, color=ACCENT)
    label(ax, nb[0][0], nb[0][1] + 0.055, r"$j$", fs=9, color=MUTED)
    label(ax, nb[1][0], nb[1][1] - 0.055, r"$j$", fs=9, color=MUTED)
    label(ax, nb[2][0], nb[2][1] + 0.050, r"$j$", fs=9, color=MUTED)

    label(ax, 0.125, 0.665, r"$\phi_e$", fs=9, color=BLUE)
    label(ax, 0.118, 0.335, r"$\phi_e$", fs=9, color=BLUE)
    label(ax, 0.252, 0.735, r"$\phi_e$", fs=9, color=BLUE)

    box(ax, 0.325, 0.435, 0.075, 0.13, r"$\sum$", fc=SOFT[2], ec=GREEN, fs=12)
    arrow(ax, (0.285, 0.50), (0.323, 0.50), color=GREEN, lw=1.1)
    box(ax, 0.432, 0.435, 0.085, 0.13, r"$\phi_v$", fc=SOFT[3], ec=PURPLE, fs=10)
    arrow(ax, (0.402, 0.50), (0.430, 0.50), color=PURPLE, lw=1.1)
    ax.scatter([0.575], [0.50], s=86, color=SOFT[3], edgecolor=PURPLE,
               linewidth=1.2, zorder=4)
    arrow(ax, (0.519, 0.50), (0.560, 0.50), color=PURPLE, lw=1.1)
    label(ax, 0.575, 0.415, r"$i'$", fs=10, color=PURPLE)
    label(ax, 0.575, 0.565, r"$\mathbf{h}_i'$", fs=9, color=PURPLE)
    label(ax, 0.30, 0.055, "每条边算一次，每个节点求一次和", fs=8.2, color=MUTED)

    # 右：层数与覆盖范围（4 邻域，曼哈顿距离）
    ax.plot([0.655, 0.655], [0.10, 0.94], color=GRID, lw=0.8, ls=(0, (4, 3)))
    rows, cols = 9, 9
    x0, x1 = 0.715, 0.955
    y0, y1 = 0.16, 0.86
    xs = np.linspace(x0, x1, cols)
    ys = np.linspace(y0, y1, rows)
    gx, gy = np.meshgrid(xs, ys)
    ax.scatter(gx.ravel(), gy.ravel(), s=7, color=FAINT, zorder=2, linewidths=0)
    cx, cy = xs[cols // 2], ys[rows // 2]
    ax.scatter([cx], [cy], s=46, color=ACCENT, zorder=5, linewidths=0)
    sx = (x1 - x0) / (cols - 1)
    sy = (y1 - y0) / (rows - 1)
    for L, al in ((1, 0.95), (2, 0.6), (3, 0.35)):
        d = [(cx + L * sx, cy), (cx, cy + L * sy), (cx - L * sx, cy), (cx, cy - L * sy)]
        ax.add_patch(Polygon(d, closed=True, fill=False, edgecolor=BLUE, lw=1.1,
                             alpha=al, ls="--", zorder=3))
    label(ax, 0.835, 0.955, "由内到外：$L = 1, 2, 3$", fs=8.2, color=BLUE)
    label(ax, 0.835, 0.055, "4 邻域下，$L$ 层覆盖\n曼哈顿距离不超过 $L$ 的节点", fs=8.0,
          color=MUTED)
    save(fig, "11", "fig11-01")


# ---------------------------------------------------------------- 图 11-2
def fig02():
    fig, ax = canvas(6.7, 3.9)
    ax.plot([0.505, 0.505], [0.06, 0.94], color=GRID, lw=0.8, ls=(0, (4, 3)))
    label(ax, 0.240, 0.965, "数值求解器", fs=9.8, color=NAVY, weight="bold")
    label(ax, 0.775, 0.965, "学到的算子", fs=9.8, color=ACCENT, weight="bold")

    # 左列
    lx, lw_ = 0.055, 0.265
    steps = [("初值 $u_0$ 与边界", 0.775, "white", INK),
             ("平流：把量搬到新位置", 0.600, "white", INK),
             ("解压力 / 解隐式系统", 0.425, "white", INK),
             ("更新状态，$t+\\Delta t$", 0.250, "white", INK)]
    for txt, y, fc, ec in steps:
        box(ax, lx, y, lw_, 0.115, txt, fc=fc, ec=ec, fs=8.5)
    for i in range(len(steps) - 1):
        y_top = steps[i][1]
        y_bot = steps[i + 1][1] + 0.115
        arrow(ax, (lx + lw_ / 2, y_top), (lx + lw_ / 2, y_bot), color=FAINT, lw=1.0)
    # 回环走右侧，不穿框
    curve_arrow(ax, [(lx + lw_, 0.3075), (0.395, 0.3075), (0.395, 0.6575),
                     (lx + lw_ + 0.006, 0.6575)], color=BLUE, lw=1.1, ms=8)
    label(ax, 0.438, 0.482, "重复上千步", fs=8.2, color=BLUE, rot=90)
    box(ax, lx, 0.070, lw_, 0.10, "整段时空的解", fc=SOFT[1], ec=NAVY, fs=8.6)
    arrow(ax, (lx + lw_ / 2, 0.250), (lx + lw_ / 2, 0.172), color=FAINT, lw=1.0)

    # 右列
    rx = 0.620
    box(ax, rx, 0.720, 0.325, 0.140, "输入 $a$：初值、边界、\n材料参数", fc="white", ec=INK, fs=8.5)
    box(ax, rx, 0.440, 0.325, 0.160, "训练好的算子 $\\mathcal{G}_\\theta$\n一次前向", fc=SOFT[0], ec=ACCENT, fs=8.8)
    box(ax, rx, 0.140, 0.325, 0.130, "输出 $u(\\mathbf{x}, t)$", fc=SOFT[0], ec=ACCENT, fs=8.8)
    arrow(ax, (rx + 0.1625, 0.720), (rx + 0.1625, 0.602), color=FAINT, lw=1.0)
    arrow(ax, (rx + 0.1625, 0.440), (rx + 0.1625, 0.272), color=FAINT, lw=1.0)
    label(ax, rx + 0.1625, 0.378, "无迭代", fs=8.2, color=MUTED)

    label(ax, 0.240, 0.030, "成本在每一次查询", fs=8.4, color=NAVY)
    label(ax, 0.775, 0.030, "成本在训练时的一批样本", fs=8.4, color=ACCENT)
    save(fig, "11", "fig11-02")


# ---------------------------------------------------------------- 图 11-3
def fig03():
    fig, ax = canvas(6.4, 4.4)

    bw, bh, gap = 0.33, 0.090, 0.042
    bx = 0.235
    names = [r"状态 $\mathbf{s}_n$", "几何与离散", "内部力：应力与本构", "外力与修正项",
             "时间积分", "碰撞与约束", r"状态 $\mathbf{s}_{n+1}$"]
    ys = [0.850 - i * (bh + gap) for i in range(len(names))]
    for i, txt in enumerate(names):
        ec = MUTED if i in (0, len(names) - 1) else INK
        box(ax, bx, ys[i], bw, bh, txt, fc="white", ec=ec, fs=9.0)
        if i:
            arrow(ax, (bx + bw / 2, ys[i - 1]), (bx + bw / 2, ys[i] + bh),
                  color=FAINT, lw=1.0)

    inserts = [(3, "① 学修正项", SOFT[0], ACCENT),
               (2, "② 学本构", SOFT[2], GREEN),
               (5, "③ 学接触响应", SOFT[3], PURPLE)]
    for idx, txt, fc, ec in inserts:
        y = ys[idx] + bh / 2
        box(ax, 0.680, y - 0.044, 0.290, 0.088, txt, fc=fc, ec=ec, fs=9.0)
        arrow(ax, (0.678, y), (bx + bw + 0.005, y), color=ec, lw=1.1, ls=(0, (4, 2.5)),
              style="<|-", ms=7)
    label(ax, 0.825, 0.960, "网络插在这里", fs=8.6, color=MUTED)

    label(ax, 0.150, 0.940, "一帧", fs=9.0, color=MUTED)
    arrow(ax, (0.150, 0.905), (0.150, 0.075), color=FAINT, lw=0.9, ms=9)
    save(fig, "11", "fig11-03")


fig01()
fig02()
fig03()
