import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 6-1 网格、哈希与邻域
def fig01():
    fig, ax = canvas(6.6, 3.6)

    # 均匀网格：8 x 6 格，格距等于截断半径
    x0, y0, c = 0.035, 0.30, 0.062
    nx, ny = 8, 6
    w, hgt = nx * c, ny * c
    ci, cj = 4, 3                                   # 查询粒子所在格

    patch_cells(ax, x0, y0, w, hgt, nx, ny,
                [(ci + di, cj + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)],
                color=BLUE, alpha=0.10, z=1)
    patch_cells(ax, x0, y0, w, hgt, nx, ny, [(ci, cj)], color=ACCENT, alpha=0.22, z=1)
    grid(ax, x0, y0, w, hgt, nx, ny, color="#D8DCE3", lw=0.7)

    rng = np.random.default_rng(11)
    for i in range(nx):
        for j in range(ny):
            k = 2 + int(rng.integers(0, 2))
            px = x0 + (i + rng.uniform(0.15, 0.85, k)) * c
            py = y0 + (j + rng.uniform(0.15, 0.85, k)) * c
            if (i, j) == (ci, cj):
                col, s, z = ACCENT, 14, 4
            elif abs(i - ci) <= 1 and abs(j - cj) <= 1:
                col, s, z = BLUE, 12, 4
            else:
                col, s, z = SLATE, 8, 3
            ax.scatter(px, py, s=s, color=col, alpha=0.9, linewidths=0, zorder=z)

    # 截断半径
    qx, qy = x0 + (ci + 0.5) * c, y0 + (cj + 0.5) * c
    ax.add_patch(Circle((qx, qy), c, fill=False, ec=ACCENT, lw=1.1,
                        ls=(0, (3, 2)), zorder=5))
    ax.annotate("", xy=(qx + c * 0.98, qy), xytext=(qx, qy),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.8,
                                shrinkA=0, shrinkB=0), zorder=6)
    label(ax, qx + c * 0.42, qy + 0.026, "$h$", fs=8.4, color=ACCENT)
    label(ax, x0, y0 - 0.05, "格距取 $h$：二维 9 格、三维 27 格必然覆盖半径 $h$ 的球",
          fs=8.2, color=MUTED, va="top", ha="left")

    # 桶数组
    tx, tw = 0.655, 0.315
    label(ax, tx, 0.90, r"桶号 = ( $i\,a_{1}$ XOR $j\,a_{2}$ XOR $k\,a_{3}$ ) mod $M$",
          fs=8.2, color=INK, ha="left")
    rows = [("3", "格子 (4,3)　3 个粒子", 0),
            ("7", "格子 (5,4)　2 个粒子", 0),
            ("8", "格子 (4,4)　4 个粒子", 0),
            ("11", "格子 (2,5)　1 个粒子", 1),
            ("11", "格子 (6,1)　2 个粒子", 1),
            ("13", "格子 (3,2)　3 个粒子", 0)]
    yy, rh, stp = 0.795, 0.085, 0.105
    for num, txt, collide in rows:
        ec = ACCENT if collide else "#D8DCE3"
        ax.add_patch(Rectangle((tx, yy), 0.055, rh, facecolor=LIGHT, edgecolor=ec,
                               lw=0.9, zorder=3))
        label(ax, tx + 0.0275, yy + rh / 2, num, fs=8.2, color=INK)
        ax.add_patch(Rectangle((tx + 0.055, yy), tw - 0.055, rh, facecolor="white",
                               edgecolor=ec, lw=0.9, zorder=3))
        label(ax, tx + 0.055 + 0.012, yy + rh / 2, txt, fs=8.2, ha="left",
              color=ACCENT if collide else INK)
        yy -= stp
    # 冲突两格之间的链式连接
    ax.plot([tx - 0.012, tx - 0.012], [0.795 - 3 * stp + rh / 2, 0.795 - 4 * stp + rh / 2],
            color=ACCENT, lw=1.0, zorder=6)
    label(ax, tx, 0.115, "同一桶可容纳两个格子，桶内另存坐标",
          fs=8.0, color=FAINT, ha="left")

    arrow(ax, (x0 + w + 0.018, 0.47), (tx - 0.018, 0.55), color=FAINT, lw=1.0, ms=8,
          rad=-0.15)
    label(ax, (x0 + w + tx) / 2, 0.43, "哈希", fs=8.2, color=MUTED)
    save(fig, "06", "fig06-01")


# ---------------------------------------------------------------- 6-2 重排前后的局部性
def fig02():
    fig, ax = canvas(6.6, 3.3)
    n, per_line = 16, 4
    labels4 = ["A", "B", "C", "D"]
    cols = [ACCENT, BLUE, GREEN, PURPLE]
    before = [i % 4 for i in range(n)]
    after = [i // per_line for i in range(n)]

    x0, sw, gap = 0.14, 0.045, 0.006
    step = sw + gap
    total = n * step - gap

    def draw_row(order, ytop, tag, note):
        for s in range(n):
            ax.add_patch(Rectangle((x0 + s * step, ytop), sw, 0.13,
                                   facecolor=cols[order[s]], edgecolor="white",
                                   lw=0.7, alpha=0.82, zorder=3))
        for b in range(1, n // per_line):
            xb = x0 + b * per_line * step - gap / 2
            ax.plot([xb, xb], [ytop - 0.045, ytop + 0.175], color=SLATE, lw=0.8,
                    ls=(0, (2, 2)), zorder=4)
        label(ax, 0.02, ytop + 0.065, tag, fs=9.0, color=INK, ha="left")
        label(ax, x0, ytop - 0.075, note, fs=8.2, color=MUTED, ha="left", va="top")

    draw_row(before, 0.66, "重排前", "格子 A 的四个粒子散布在整条数组上，跨越 4 条缓存行")
    draw_row(after, 0.26, "重排后", "格子 A 的四个粒子连续存放，只占 1 条缓存行")

    # 标记格子 A 的位置
    for s in range(n):
        if before[s] == 0:
            ax.add_patch(Rectangle((x0 + s * step - 0.002, 0.658), sw + 0.004, 0.134,
                                   fill=False, ec=INK, lw=1.0, zorder=5))
        if after[s] == 0:
            ax.add_patch(Rectangle((x0 + s * step - 0.002, 0.258), sw + 0.004, 0.134,
                                   fill=False, ec=INK, lw=1.0, zorder=5))

    label(ax, x0, 0.905, "细竖线为缓存行边界（每行 4 个粒子），黑框标出格子 A 的四个粒子",
          fs=8.2, color=MUTED, ha="left")
    for i, lab in enumerate(labels4):
        xx = x0 + i * 0.135
        ax.add_patch(Rectangle((xx, 0.055), 0.022, 0.018, facecolor=cols[i],
                               edgecolor="none", alpha=0.85, zorder=5))
        label(ax, xx + 0.03, 0.064, "格子 " + lab, fs=8.2, color=INK, ha="left")
    save(fig, "06", "fig06-02")


if __name__ == "__main__":
    fig01()
    fig02()
