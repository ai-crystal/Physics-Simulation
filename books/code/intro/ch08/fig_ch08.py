import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 图 8-1
def fig01():
    fig, ax = canvas(6.7, 3.7, (0, 1), (0, 1))
    ax.add_patch(Rectangle((0.16, 0.14), 0.78, 0.70, fc="#FCFCFB", ec=GRID, lw=0.9, zorder=0))
    for i in range(1, 4):
        ax.plot([0.16 + i * 0.195] * 2, [0.14, 0.84], color="#F1F3F5", lw=0.7, zorder=1)
        ax.plot([0.16, 0.94], [0.14 + i * 0.175] * 2, color="#F1F3F5", lw=0.7, zorder=1)

    arrow(ax, (0.16, 0.115), (0.96, 0.115), color=MUTED, lw=1.0, ms=8)
    arrow(ax, (0.14, 0.14), (0.14, 0.88), color=MUTED, lw=1.0, ms=8)
    label(ax, 0.55, 0.075, "裂纹何时确定", fs=9.0, color=INK)
    label(ax, 0.16, 0.035, "预先切好", fs=8.0, color=MUTED, ha="left")
    label(ax, 0.94, 0.035, "运行时生成", fs=8.0, color=MUTED, ha="right")
    label(ax, 0.055, 0.49, "裂纹能分辨到多细", fs=9.0, color=INK, rot=90)
    label(ax, 0.60, 0.165, "网格尺度", fs=8.0, color=MUTED, ha="left")
    label(ax, 0.175, 0.815, "裂纹尺度", fs=8.0, color=MUTED, ha="left")

    items = [
        (0.21, 0.22, 0.24, 0.13, "Voronoi 预碎片", BLUE, SOFT[1]),
        (0.45, 0.36, 0.21, 0.13, "单元删除", ACCENT, SOFT[0]),
        (0.55, 0.56, 0.26, 0.13, "虚拟节点 / 内聚单元", ACCENT, SOFT[0]),
        (0.68, 0.72, 0.21, 0.11, "边界元 BEM", GREEN, SOFT[2]),
    ]
    for x, y, w, h, txt, ec, fc in items:
        box(ax, x, y, w, h, txt, fc=fc, ec=ec, fs=8.6, lw=1.1)
    save(fig, "08", "fig08-01")


# ---------------------------------------------------------------- 图 8-2
def fig02():
    fig = plt.figure(figsize=(6.7, 3.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.3, 1.0], height_ratios=[2.4, 1.0],
                          wspace=0.22, hspace=0.30)

    # 左上：接触点放大
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(-1.55, 1.60)
    ax.set_ylim(-1.15, 1.10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Circle((-0.82, 0.0), 0.98, fc=SOFT[1], ec=BLUE, lw=1.3, zorder=1))
    ax.add_patch(Circle((0.86, 0.0), 0.98, fc=SOFT[0], ec=ACCENT, lw=1.3, zorder=2))
    ax.plot([0.02, 0.02], [-0.95, 0.92], color=MUTED, lw=0.7, ls=":", zorder=4)

    arrow(ax, (0.02, 0.0), (-0.66, 0.0), color=BLUE, lw=1.4, ms=8, z=5)
    arrow(ax, (0.02, 0.0), (0.70, 0.0), color=ACCENT, lw=1.4, ms=8, z=5)
    label(ax, -0.44, 0.13, "$F_n$", fs=9.0, color=BLUE, z=6)
    label(ax, 0.47, 0.13, "$F_n$", fs=9.0, color=ACCENT, z=6)

    arrow(ax, (0.02, 0.06), (0.02, 0.66), color=GREEN, lw=1.4, ms=8, z=6)
    label(ax, 0.15, 0.46, "$F_t$", fs=9.0, color=GREEN, ha="left", z=6)
    arrow(ax, (0.02, -0.06), (0.02, -0.58), color=GREEN, lw=1.2, ms=8, ls=(0, (4, 2)), z=6)
    label(ax, 0.15, -0.34, r"上限 $\mu F_n$", fs=8.2, color=GREEN, ha="left", z=6)

    ax.annotate("", xy=(-0.10, -0.86), xytext=(0.16, -0.86),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9,
                                mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.plot([-0.10, -0.10], [-0.92, -0.80], color=INK, lw=0.8)
    ax.plot([0.16, 0.16], [-0.92, -0.80], color=INK, lw=0.8)
    label(ax, 0.03, -1.05, r"$\delta$", fs=9.0, color=INK)
    label(ax, -1.40, 0.66, "颗粒 $i$", fs=8.4, color=BLUE, ha="left")
    label(ax, 0.98, 0.62, "颗粒 $j$", fs=8.4, color=ACCENT, ha="left")

    # 左下：弹簧与阻尼器
    ax = fig.add_subplot(gs[1, 0])
    ax.set_xlim(0, 3.2)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    y0 = 0.62
    xs = np.linspace(0.30, 1.05, 9)
    zig = np.array([0.0, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, 0.0])
    ax.plot(xs, y0 + 0.13 * zig, color=INK, lw=1.0)
    ax.plot([0.12, 0.30], [y0, y0], color=INK, lw=1.0)
    ax.plot([1.05, 1.20], [y0, y0], color=INK, lw=1.0)
    label(ax, 0.66, 0.20, "法向弹簧 $k_n$", fs=8.2, color=INK)

    ax.add_patch(Rectangle((1.62, y0 - 0.13), 0.46, 0.26, fc="white", ec=INK, lw=1.0))
    ax.plot([1.45, 1.62], [y0, y0], color=INK, lw=1.0)
    ax.plot([2.08, 2.28], [y0, y0], color=INK, lw=1.0)
    ax.plot([1.98, 1.98], [y0 - 0.13, y0 + 0.13], color=INK, lw=1.6)
    ax.plot([1.86, 1.98], [y0, y0], color=INK, lw=1.2)
    label(ax, 1.86, 0.20, "阻尼 $c_n$", fs=8.2, color=INK)
    label(ax, 0.02, 0.92, "法向：", fs=8.2, color=MUTED, ha="left")

    # 右：恢复系数
    ax = fig.add_subplot(gs[:, 1])
    z = np.linspace(0.001, 0.9, 400)
    e = np.exp(-z * np.pi / np.sqrt(1 - z**2))
    ax.plot(z, e, color=BLUE, lw=1.7)
    for zz, lab, dy in [(0.1, "0.73", 0.12), (0.5, "0.16", 0.10)]:
        ee = np.exp(-zz * np.pi / np.sqrt(1 - zz**2))
        ax.plot([zz], [ee], "o", ms=5.0, mfc=ACCENT, mec="white", mew=0.8, zorder=4)
        ax.plot([zz, zz], [0, ee], color=ACCENT, lw=0.7, ls=(0, (3, 2)))
        label(ax, zz + 0.05, ee + dy, "$e=%s$" % lab, fs=8.2, color=ACCENT, ha="left")
    clean(ax, grid=True)
    ax.set_xlim(0, 0.95)
    ax.set_ylim(-0.02, 1.06)
    ax.set_xlabel(r"阻尼比 $\zeta$")
    ax.set_ylabel("恢复系数 $e$")
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    save(fig, "08", "fig08-02")


# ---------------------------------------------------------------- 图 8-3
def fig03():
    fig, ax = canvas(6.7, 3.3, (0, 1), (0, 1))
    bw, bh = 0.30, 0.21
    xl, xr = 0.03, 0.63
    yt, yb = 0.66, 0.10

    def node(x, y, title, sub, ec, fc):
        box(ax, x, y, bw, bh, "", fc=fc, ec=ec, lw=1.2)
        label(ax, x + bw / 2, y + bh / 2 + 0.036, title, fs=9.4, color=INK)
        label(ax, x + bw / 2, y + bh / 2 - 0.042, sub, fs=8.0, color=MUTED)

    node(xl, yt, "粒子", r"质量、速度、形变梯度 $\mathbf{F}$", BLUE, SOFT[1])
    node(xr, yt, "网格节点", "质量、动量", ACCENT, SOFT[0])
    node(xr, yb, "网格求解", "应力散度、节点速度", ACCENT, "white")
    node(xl, yb, "粒子更新", r"移动，更新 $\mathbf{F}$", BLUE, "white")

    ay = yt + bh / 2
    arrow(ax, (xl + bw + 0.015, ay), (xr - 0.015, ay), color=BLUE, lw=1.4, ms=10)
    label(ax, (xl + bw + xr) / 2, ay + 0.055, "P2G：散射动量", fs=8.2, color=BLUE)
    arrow(ax, (xr + bw / 2, yt - 0.012), (xr + bw / 2, yb + bh + 0.012), color=ACCENT, lw=1.4, ms=10)
    label(ax, xr + bw / 2 + 0.02, (yt + yb + bh) / 2 + 0.04, "求解", fs=8.2, color=ACCENT, ha="left")
    arrow(ax, (xr - 0.015, yb + bh / 2), (xl + bw + 0.015, yb + bh / 2), color=GREEN, lw=1.4, ms=10)
    label(ax, (xl + bw + xr) / 2, yb + bh / 2 - 0.06, "G2P：插回速度", fs=8.2, color=GREEN)
    arrow(ax, (xl + bw / 2, yb + bh + 0.012), (xl + bw / 2, yt - 0.012), color=MUTED, lw=1.2, ms=10,
          ls=(0, (4, 2)))
    label(ax, xl + bw / 2 + 0.025, (yt + yb + bh) / 2 - 0.05, "下一帧", fs=8.2, color=MUTED, ha="left")

    for i, txt in enumerate(["网格每步重建，", "不保存历史。", "历史在粒子的", r"$\mathbf{F}$ 里。"]):
        label(ax, 0.395, 0.545 - i * 0.065, txt, fs=8.0, color=MUTED, ha="left")
    save(fig, "08", "fig08-03")


fig01()
fig02()
fig03()
