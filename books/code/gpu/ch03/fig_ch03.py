# -*- coding: utf-8 -*-
"""第 3 章插图：warp 分支发散示意、占用率阶梯。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ---------------------------------------------------------------- 图 3-1
# 8x4 的块 = 32 lane = 一个 warp。液体格点占 11 个，形成台阶状界面。
FLUID = [(0, 0), (1, 0), (2, 0), (3, 0),
         (0, 1), (1, 1), (2, 1), (3, 1),
         (0, 2), (1, 2),
         (0, 3)]
NCOL, NROW = 8, 4


def fig_divergence():
    fig = plt.figure(figsize=(6.55, 2.95))
    axs = fig.add_axes([0.02, 0.05, 0.40, 0.86])
    axt = fig.add_axes([0.555, 0.20, 0.425, 0.70])

    # ---- 左：warp 的 32 个 lane
    ax = axs
    ax.set_xlim(0, NCOL)
    ax.set_ylim(-0.95, NROW + 0.62)
    ax.set_aspect("equal")
    ax.axis("off")
    for c in range(NCOL):
        for r in range(NROW):
            if (c, r) in FLUID:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor=ACCENT, alpha=0.28,
                                       edgecolor=ACCENT, lw=1.1, zorder=3))
            else:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="white",
                                       edgecolor="#CBD5E1", lw=1.0, zorder=3))
    ax.text(NCOL / 2, -0.48, "一个 warp = 32 个 lane = 8×4 的块",
            fontsize=8.8, color=INK, ha="center", va="center")
    ax.text(NCOL / 2, NROW + 0.30, "填色 11 个为液体，留白 21 个为空气",
            fontsize=8.2, color=MUTED, ha="center", va="center")

    # ---- 右：时间轴
    ax = axt
    T_A, T_B = 20, 5
    ax.barh(2.05, T_A, height=0.52, color=ACCENT, alpha=0.85, edgecolor="none", zorder=3)
    ax.barh(1.20, T_B, left=T_A, height=0.52, color=BLUE, alpha=0.80,
            edgecolor="none", zorder=3)
    ax.barh(0.32, T_A, height=0.44, facecolor="white", edgecolor=MUTED,
            lw=1.0, ls=(0, (3.5, 2.0)), zorder=3)

    ax.text(T_A / 2, 2.05, "路径 A（11 lane）%d 周期" % T_A, fontsize=8.2, color="white",
            ha="center", va="center", zorder=5, weight="bold")
    ax.text(T_A + T_B + 0.8, 1.20, "路径 B（21 lane）%d 周期" % T_B, fontsize=8.0,
            color=BLUE, ha="left", va="center")
    ax.text(T_A + 0.8, 0.32, "无分支  %d 周期" % T_A, fontsize=8.0, color=MUTED,
            ha="left", va="center")

    ax.axvline(T_A, color=MUTED, lw=0.8, ls=(0, (2, 2)), zorder=2)
    ax.set_xlim(0, 37)
    ax.set_ylim(-0.05, 2.60)
    ax.set_yticks([2.05, 1.20, 0.32])
    ax.set_yticklabels(["实际 A", "实际 B", "理想"], fontsize=8.4)
    ax.set_xticks([0, 5, 10, 15, 20, 25])
    ax.set_xlabel("warp 被占用的周期", fontsize=9.0)
    clean(ax, spines=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.text(0.0, 2.48, "合计 25 周期，理想 20 周期", fontsize=8.0, color=MUTED,
            ha="left", va="bottom")

    save(fig, "03", "fig03-01")


# ---------------------------------------------------------------- 图 3-2
REGS_SM = 65536
MAX_T = 2048
MAX_B = 32
SMEM_SM = 96 * 1024


def occ(r, B, S_blk=0):
    ra = ((r + 7) // 8) * 8          # 寄存器按 8 的倍数整块分配
    b = REGS_SM // (ra * B)
    if S_blk:
        b = min(b, SMEM_SM // S_blk)
    b = max(0, min(b, MAX_B, MAX_T // B))
    return b * B / MAX_T, b


def fig_occupancy():
    fig, axs = plt.subplots(1, 2, figsize=(6.9, 2.90),
                            gridspec_kw=dict(wspace=0.30,
                                             left=0.09, right=0.975,
                                             top=0.965, bottom=0.165))

    # 左：占用率随每线程寄存器数
    ax = axs[0]
    rs = np.arange(16, 97)
    for B, col, lab in ((128, BLUE, "块 128 线程"),
                        (256, ACCENT, "块 256 线程"),
                        (512, GREEN, "块 512 线程")):
        ys = np.array([occ(int(r), B)[0] for r in rs]) * 100
        ax.plot(rs, ys, color=col, lw=1.35, drawstyle="steps-post", label=lab)
    ax.set_xlim(16, 96)
    ax.set_ylim(0, 106)
    ax.set_xticks([16, 32, 48, 64, 80, 96])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("每线程寄存器数 $r$", fontsize=9.0)
    ax.set_ylabel("占用率 / %", fontsize=9.0)
    clean(ax, grid=True)
    ax.legend(loc="lower left", fontsize=8.0, handlelength=1.9,
              borderaxespad=0.15, ncol=1)
    o40 = occ(40, 256)[0] * 100
    ax.plot([40], [o40], marker="o", ms=4.2, color=ACCENT, mec="white", mew=0.9, zorder=6)
    ax.annotate("$r=40$：6 个块，75%",
                xy=(40.6, o40), xytext=(47, 88), fontsize=8.0, color=ACCENT,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                                shrinkA=1, shrinkB=3))

    # 右：占用率随每块共享内存
    ax = axs[1]
    ks = np.arange(1, 49)
    for r, col, lab in ((32, BLUE, "$r=32$"), (40, ACCENT, "$r=40$")):
        ys = np.array([occ(r, 256, int(k * 1024))[0] for k in ks]) * 100
        ax.plot(ks, ys, color=col, lw=1.35, drawstyle="steps-post", label=lab)
    ax.axhline(occ(40, 256)[0] * 100, color=ACCENT, lw=0.9, ls=(0, (4, 2)))
    ax.axhline(occ(32, 256)[0] * 100, color=BLUE, lw=0.9, ls=(0, (4, 2)))
    ax.set_xlim(1, 48)
    ax.set_ylim(0, 106)
    ax.set_xticks([1, 8, 16, 24, 32, 40, 48])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("每块共享内存 / KB", fontsize=9.0)
    ax.set_ylabel("占用率 / %", fontsize=9.0)
    clean(ax, grid=True)
    ax.legend(loc="lower left", fontsize=8.0, handlelength=1.9, borderaxespad=0.15)
    ax.plot([16], [75], marker="o", ms=4.0, color=ACCENT, mec="white", mew=0.9, zorder=6)
    ax.plot([20], [50], marker="o", ms=4.0, color=ACCENT, mec="white", mew=0.9, zorder=6)
    ax.text(24.0, 60, "16 KB：6 个块，75%\n20 KB：4 个块，50%", fontsize=7.9,
            color=MUTED, ha="left", va="center", linespacing=1.8)

    save(fig, "03", "fig03-02")


if __name__ == "__main__":
    fig_divergence()
    fig_occupancy()
    print("r=40,B=256:", occ(40, 256), "r=32,B=256:", occ(32, 256))
    for k in (4, 8, 12, 16, 20, 24, 32):
        print("S=%dKB" % k, occ(40, 256, k * 1024), occ(32, 256, k * 1024))
    for r in (24, 32, 33, 40, 41, 48, 96):
        print("r=%d B=256" % r, occ(r, 256))
