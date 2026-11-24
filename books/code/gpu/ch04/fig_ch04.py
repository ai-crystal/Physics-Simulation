# -*- coding: utf-8 -*-
"""第 4 章插图：块稀疏网格示意、稠密与稀疏的存储随分辨率。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ---------------------------------------------------------------- 图 4-1
NBX, NBY = 12, 10         # 块的个数（每块 8x8x8 体素）


def fig_block_sparse():
    fig = plt.figure(figsize=(6.9, 3.45))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    x0, y0 = 0.035, 0.155
    w, h = 0.400, 0.700
    bw, bh = w / NBX, h / NBY

    cx_, cy_ = x0 + w * 0.47, y0 + h * 0.50
    r_in = 3.1 * bw
    ry_ratio = 6.9 / 3.45            # 让圆在纸面看上去是圆的
    band = 0.40 * bw                 # 窄带半厚（轴单位，x 方向）

    def blk_dist(bx, by):
        l, r = bx, bx + bw
        b, t = by, by + bh
        dx = max(l - cx_, 0.0, cx_ - r)
        dy = max(b - cy_, 0.0, cy_ - t) / ry_ratio
        dmin = np.hypot(dx, dy)
        dx2 = max(abs(cx_ - l), abs(cx_ - r))
        dy2 = max(abs(cy_ - b), abs(cy_ - t)) / ry_ratio
        return dmin, np.hypot(dx2, dy2)

    active = np.zeros((NBX, NBY), bool)
    for i in range(NBX):
        for j in range(NBY):
            dmin, dmax = blk_dist(x0 + i * bw, y0 + j * bh)
            active[i, j] = (dmin < r_in + band) and (dmax > r_in - band)

    for i in range(NBX):
        for j in range(NBY):
            bx, by = x0 + i * bw, y0 + j * bh
            if active[i, j]:
                ax.add_patch(Rectangle((bx, by), bw, bh, facecolor=ACCENT, alpha=0.26,
                                       edgecolor=ACCENT, lw=0.75, zorder=2))
            else:
                ax.add_patch(Rectangle((bx, by), bw, bh, facecolor="white",
                                       edgecolor="#DDE3EA", lw=0.45, zorder=2))

    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(cx_ + r_in * np.cos(th), cy_ + r_in * np.sin(th) * ry_ratio,
            color=BLUE, lw=1.30, zorder=6)
    for rr in (r_in - band, r_in + band):
        ax.plot(cx_ + rr * np.cos(th), cy_ + rr * np.sin(th) * ry_ratio,
                color=BLUE, lw=0.65, ls=(0, (3, 2)), alpha=0.75, zorder=5)

    label(ax, x0 + w / 2, y0 + h + 0.042, "填色的块被分配，其余取背景值", fs=8.4, color=MUTED)
    label(ax, x0 + w / 2, y0 - 0.058, "一个块 $8^{3}$ = 512 体素 = 2 KiB", fs=8.4, color=INK)

    # ---- 右侧：三层结构
    bx0, bw2 = 0.560, 0.390
    rows = [("根节点　哈希表\n键为 $4096^{3}$ 的块坐标", 0.740, "整块全空则不占条目"),
            ("内部节点　$16^{3}$ 个孩子\n全同值则记为常量瓦片", 0.460, "常量瓦片：一个值顶一块"),
            ("叶节点　$8^{3}$ 个值\n加 512 位活跃掩码", 0.180, "查不到 → 背景值")]
    for txt, yb, note in rows:
        box(ax, bx0, yb, bw2, 0.135, txt, fc="white", ec=INK, fs=8.2, lw=1.05)
        label(ax, bx0 + bw2 / 2 + 0.030, yb - 0.058, note, fs=7.7, color=MUTED)

    for yb in (0.740, 0.460):
        arrow(ax, (bx0 + 0.042, yb - 0.010), (bx0 + 0.042, yb - 0.150),
              color=FAINT, lw=1.0, ms=8)

    save(fig, "04", "fig04-01")


# ---------------------------------------------------------------- 图 4-2
B = 8
RF, BAND = 0.35, 3.0          # 球半径 0.35L，窄带每侧 3 格


def count_blocks(N):
    nb = N // B
    h = 1.0 / N
    c = (np.arange(nb) * B + B / 2) * h
    half = B * h / 2.0
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    d, e, f = np.abs(X - 0.5), np.abs(Y - 0.5), np.abs(Z - 0.5)
    dmin = np.sqrt(np.maximum(d - half, 0) ** 2 + np.maximum(e - half, 0) ** 2
                   + np.maximum(f - half, 0) ** 2)
    dmax = np.sqrt((d + half) ** 2 + (e + half) ** 2 + (f + half) ** 2)
    delta = BAND * h
    return int(((dmin < RF + delta) & (dmax > RF - delta)).sum())


def fig_memory():
    Ns = 2 ** np.arange(4, 11)
    dense, sparse, frac, nblk = [], [], [], []
    for N in Ns:
        nbk = count_blocks(int(N))
        nblk.append(nbk)
        dense.append(4.0 * N ** 3)
        sparse.append(4.0 * nbk * B ** 3)
        frac.append(nbk * B ** 3 / float(N) ** 3 * 100)
    dense, sparse, frac = map(np.array, (dense, sparse, frac))
    for N, nbk, d, s, f_ in zip(Ns, nblk, dense, sparse, frac):
        print("N=%4d blocks=%7d dense=%8.1f MiB sparse=%7.2f MiB frac=%6.2f%%"
              % (N, nbk, d / 2 ** 20, s / 2 ** 20, f_))

    fig, axs = plt.subplots(1, 2, figsize=(6.9, 2.95),
                            gridspec_kw=dict(wspace=0.30, left=0.085, right=0.975,
                                             top=0.955, bottom=0.175))
    ax = axs[0]
    ax.loglog(Ns, dense / 2 ** 20, color=INK, lw=1.5, marker="s", ms=3.4, mfc=INK,
              mew=0, label="稠密网格 $N^{3}$")
    ax.loglog(Ns, sparse / 2 ** 20, color=ACCENT, lw=1.5, marker="o", ms=3.6,
              mfc=ACCENT, mew=0, label="块稀疏窄带")
    n0 = 128.0
    y0 = 4.0 * n0 ** 3 / 2 ** 20
    nn = np.array([96.0, 1024.0])
    ax.loglog(nn, y0 * (nn / n0) ** 3, color=MUTED, lw=0.9, ls=(0, (4, 2)))
    ax.loglog(nn, y0 * (nn / n0) ** 2, color=GREEN, lw=0.9, ls=(0, (4, 2)))
    ax.text(1055, 470, "$N^{2}$", fontsize=8.4, color=GREEN, ha="left", va="bottom")
    ax.set_xlim(14, 1400)
    ax.set_ylim(1e-2, 3e4)
    ax.set_xticks([16, 64, 256, 1024])
    ax.set_xticklabels(["16", "64", "256", "1024"])
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_yticks([1e-1, 1e0, 1e1, 1e2, 1e3, 1e4])
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_xlabel("每方向格点数 $N$", fontsize=9.0)
    ax.set_ylabel("单个场的存储 / MiB", fontsize=9.0)
    clean(ax, grid=True)
    ax.legend(loc="upper left", fontsize=8.2, handlelength=2.0, borderaxespad=0.2)
    i = int(np.where(Ns == 512)[0][0])
    ax.annotate("512 MiB", xy=(512, dense[i] / 2 ** 20), xytext=(560, 1.9e3),
                fontsize=7.8, color=INK, ha="center", va="bottom",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7, shrinkA=1, shrinkB=2))
    ax.annotate("%.0f MiB" % (sparse[i] / 2 ** 20), xy=(512, sparse[i] / 2 ** 20),
                xytext=(560, 0.30), fontsize=7.8, color=ACCENT, ha="center", va="top",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7, shrinkA=1, shrinkB=2))

    ax = axs[1]
    ax.semilogx(Ns, frac, color=ACCENT, lw=1.5, marker="o", ms=3.6, mfc=ACCENT, mew=0)
    ax.set_xlim(14, 1300)
    ax.set_ylim(0, 108)
    ax.set_xticks([16, 64, 256, 1024])
    ax.set_xticklabels(["16", "64", "256", "1024"])
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("每方向格点数 $N$", fontsize=9.0)
    ax.set_ylabel("已分配体素占比 / %", fontsize=9.0)
    clean(ax, grid=True)
    for N, off in ((64, 6), (256, 8), (512, 7)):
        f_ = frac[int(np.where(Ns == N)[0][0])]
        ax.annotate("%.0f%%" % f_, xy=(N, f_), xytext=(N * 1.22, f_ + off),
                    fontsize=7.8, color=MUTED, ha="left", va="bottom")

    save(fig, "04", "fig04-02")
    return Ns, dense, sparse, frac


if __name__ == "__main__":
    fig_block_sparse()
    fig_memory()
