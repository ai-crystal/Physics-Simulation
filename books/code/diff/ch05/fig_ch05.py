"""第 5 章配图。

图 5-1  前向与伴随的时间线（示意）
图 5-2  检查点个数与峰值显存、总时间（真实计算模型）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# --------------------------------------------------- 真实计算用的参数
N_STEP = 600              # 步数
S_MB   = 41.9             # 单步状态：5 个 128^3 单精度场
CARD   = 24.0             # 显存档位（GB）
C_FWD, C_BWD = 1.0, 1.8   # 反向一步相对前向一步的成本


def peak_mem_gb(K, N=N_STEP, S=S_MB):
    """峰值显存：检查点 K 个 + 正在重算那一段的 N/K 个状态。"""
    return (K + N / K) * S / 1000.0


def total_time(K, N=N_STEP):
    """总时间（以一次前向为 1）：前向 + 重算 + 反向。"""
    recompute = 1.0 if K < N else 0.0
    return C_FWD + recompute + C_BWD


# --------------------------------------------------- 图 5-1 时间线
def fig_timeline():
    fig, ax = canvas(6.8, 3.4)
    X0, DX, W = 0.170, 0.127, 0.091
    YF, YA, YC, YB = 0.850, 0.660, 0.480, 0.290
    NC = 6
    xs = [X0 + i * DX for i in range(NC)]

    # 虚线：前向状态 -> 保存 -> 反向
    for x in xs:
        ax.plot([x + W / 2, x + W / 2], [YF - 0.043, YB + 0.043],
                color=GRID, lw=0.8, ls=(0, (1.2, 2.0)), zorder=0.6)

    # 前向
    for i, x in enumerate(xs):
        box(ax, x, YF - 0.0425, W, 0.085, rf"$x^{{{i}}}$", fc=SOFT[1], ec=BLUE,
            tc=INK, fs=8.8, lw=0.9)
        if i:
            arrow(ax, (x - 0.032, YF), (x - 0.008, YF), color=BLUE, lw=1.0, ms=6)

    # 全部保存
    for x in xs:
        box(ax, x, YA - 0.0425, W, 0.085, "", fc="#DCE7FF", ec="#B9CBF2", lw=0.8)

    # 检查点：只存 0 与 3，其余由重算得到
    KEEP = {0, 3}
    for i, x in enumerate(xs):
        if i in KEEP:
            box(ax, x, YC - 0.0425, W, 0.085, "", fc="#F7D9BC", ec=ACCENT, lw=0.9)
        else:
            box(ax, x, YC - 0.0425, W, 0.085, "", fc="#FCEFE3", ec="#E7B98F",
                lw=0.7, ls=(0, (2.2, 1.6)))

    # 反向：箭头朝左
    for i, x in enumerate(xs):
        box(ax, x, YB - 0.0425, W, 0.085, rf"$\lambda^{{{i}}}$", fc="#FDECE3",
            ec=ACCENT, tc=INK, fs=8.8, lw=0.9)
        if i:
            arrow(ax, (x - 0.008, YB), (x - 0.032, YB), color=ACCENT, lw=1.0, ms=6)

    # 左侧行标签
    label(ax, 0.018, YF, "前向", fs=9.2, color=BLUE, ha="left", weight="bold")
    label(ax, 0.018, YA, "全部保存", fs=8.6, color=MUTED, ha="left")
    label(ax, 0.018, YC, "检查点", fs=8.6, color=ACCENT, ha="left")
    label(ax, 0.018, YB, "反向", fs=9.2, color=ACCENT, ha="left", weight="bold")

    # 时间方向
    label(ax, xs[0] + W / 2, 0.935, r"$t_{0}$", fs=8.2, color=BLUE, va="center")
    label(ax, xs[-1] + W / 2, 0.935, r"$t_{N}$", fs=8.2, color=BLUE, va="center")
    arrow(ax, (xs[0] + W / 2 + 0.020, 0.935), (xs[-1] + W / 2 - 0.020, 0.935),
          color="#BFD3F7", lw=0.8, ms=6, style="-|>")

    # 底部说明与图例
    label(ax, 0.018, 0.150,
          "反向第 n 步需要第 n 帧的状态与该步算子的转置；",
          fs=8.0, color=MUTED, ha="left")
    label(ax, 0.018, 0.096,
          "检查点策略下，未常驻的那几帧要先按段重算再回放。",
          fs=8.0, color=MUTED, ha="left")

    ax.add_patch(Rectangle((0.560, 0.138), 0.030, 0.022, facecolor="#DCE7FF",
                           edgecolor="#B9CBF2", lw=0.7, zorder=4))
    label(ax, 0.598, 0.149, "常驻显存", fs=8.0, color=INK, ha="left")
    ax.add_patch(Rectangle((0.560, 0.074), 0.030, 0.022, facecolor="#F7D9BC",
                           edgecolor=ACCENT, lw=0.7, zorder=4))
    label(ax, 0.598, 0.085, "检查点", fs=8.0, color=INK, ha="left")
    ax.add_patch(Rectangle((0.706, 0.074), 0.030, 0.022, facecolor="#FCEFE3",
                           edgecolor="#E7B98F", lw=0.7, ls=(0, (2.2, 1.6)), zorder=4))
    label(ax, 0.744, 0.085, "重算得到", fs=8.0, color=INK, ha="left")

    save(fig, "05", "fig05-01")


# --------------------------------------------------- 图 5-2 显存与时间
def fig_memory():
    fig, (ax1, ax2) = new(6.9, 3.2, ncols=2,
                          gridspec_kw={"wspace": 0.70, "left": 0.08,
                                       "right": 0.965, "bottom": 0.16, "top": 0.94})

    # ---- (a) 随检查点个数
    Ks = np.unique(np.round(np.logspace(0, np.log10(N_STEP), 400)).astype(int))
    Ks = np.append(Ks, N_STEP)
    mem = peak_mem_gb(Ks)
    tim = np.array([total_time(k) for k in Ks])

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.plot(Ks, mem, color=BLUE, lw=1.6, zorder=3)
    ax1.axhline(CARD, color=MUTED, lw=0.9, ls=(0, (4, 2.4)), zorder=2)

    kopt = np.sqrt(N_STEP)
    mopt = peak_mem_gb(kopt)
    ax1.plot([kopt], [mopt], "o", ms=6.0, color=BLUE, mec="white", mew=1.1, zorder=6)
    ax1.annotate("最低点 " + f"{mopt:.2f} GB" + "\n" + r"$K=\sqrt{N}\approx 24$",
                 xy=(kopt, mopt * 1.06), xytext=(1.15, 52),
                 fontsize=8.0, color=BLUE, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8,
                                 shrinkA=4, shrinkB=6))

    ax1.set_xlabel("检查点个数 K", fontsize=9.4, labelpad=3)
    ax1.set_ylabel("峰值显存（GB）", fontsize=9.4, color=BLUE, labelpad=2)
    ax1.tick_params(labelsize=8.4)
    ax1.set_xlim(1, 1500)
    ax1.set_ylim(0.95, 90)
    ax1.spines["top"].set_visible(False)
    ax1.grid(True, which="major", color=GRID, lw=0.6)
    ax1.set_axisbelow(True)


    # 全存那一点
    ax1.annotate(f"全存 {mem[-1]:.1f} GB\n越过 24 GB 档位", xy=(N_STEP, mem[-1]), xytext=(78, 52),
                 fontsize=8.0, color=MUTED, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8,
                                 shrinkA=3, shrinkB=3))

    ax1b = ax1.twinx()
    ax1b.step(Ks, tim, where="post", color=ACCENT, lw=1.3, zorder=4)
    ax1b.plot([N_STEP], [2.8], "o", ms=5.0, color=ACCENT, mec="white", mew=1.0, zorder=6)
    ax1b.set_ylabel("总时间（倍前向）", fontsize=9.4, color=ACCENT, labelpad=2)
    ax1b.set_ylim(2.2, 4.5)
    ax1b.tick_params(labelsize=8.4, colors=ACCENT)
    ax1b.spines["top"].set_visible(False)
    ax1b.annotate("省掉一次重算", xy=(N_STEP, 2.8), xytext=(60, 2.44),
                  fontsize=8.0, color=ACCENT, ha="left", va="center",
                  arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                                  shrinkA=2, shrinkB=4))

    # ---- (b) 随步数
    Ns = np.logspace(2, np.log10(2000), 200)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.plot(Ns, Ns * S_MB / 1000, color=BLUE, lw=1.6)
    ax2.plot(Ns, 2 * np.sqrt(Ns) * S_MB / 1000, color=ACCENT, lw=1.6)
    ax2.plot(Ns, np.log2(Ns) * S_MB / 1000, color=GREEN, lw=1.6)
    ax2.axhline(CARD, color=MUTED, lw=0.9, ls=(0, (4, 2.4)), zorder=2)

    lab = [(84, "全部保存"), (3.76, "均匀检查点"), (0.46, "二项式")]
    for yv, tx in lab:
        ax2.text(2100, yv, tx, fontsize=8.2, color=INK, ha="left", va="center")

    ax2.set_xlabel("步数 N", fontsize=9.4, labelpad=3)
    ax2.set_ylabel("峰值显存（GB）", fontsize=9.4, labelpad=2)
    ax2.tick_params(labelsize=8.4)
    ax2.set_xlim(100, 9000)
    ax2.set_ylim(0.18, 300)
    ax2.grid(True, which="major", color=GRID, lw=0.6)
    ax2.set_axisbelow(True)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    ax2.text(112, CARD * 1.10, "24 GB", fontsize=8.0, color=MUTED,
             ha="left", va="bottom")

    save(fig, "05", "fig05-02")


if __name__ == "__main__":
    fig_timeline()
    fig_memory()
    print("K_opt =", round(np.sqrt(N_STEP), 2), "peak =", round(peak_mem_gb(np.sqrt(N_STEP)), 3), "GB")
    print("full  =", round(peak_mem_gb(N_STEP), 2), "GB")
    print("binomial N=600:", round(np.log2(600) * S_MB / 1000, 3), "GB")
