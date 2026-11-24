import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 10-1
# 前向与反向两条时间线，以及反向所需的存储量（复杂度模型）。
def fig01():
    fig = plt.figure(figsize=(7.0, 3.8))

    ax = fig.add_axes([0.035, 0.10, 0.585, 0.83])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    xs = [0.115, 0.295, 0.475, 0.655, 0.815]
    yf, yb = 0.74, 0.24
    lab_f = [r"$\mathbf{x}_0$", r"$\mathbf{x}_1$", r"$\mathbf{x}_2$",
             r"$\mathbf{x}_3$", r"$\mathbf{x}_T$"]
    lab_b = [r"$\lambda_0$", r"$\lambda_1$", r"$\lambda_2$",
             r"$\lambda_3$", r"$\lambda_T$"]

    for i in range(len(xs) - 1):
        arrow(ax, (xs[i] + 0.045, yf), (xs[i + 1] - 0.045, yf), color=MUTED,
              lw=1.1, shrinkA=0, shrinkB=0)
        arrow(ax, (xs[i + 1] - 0.045, yb), (xs[i] + 0.045, yb), color=PURPLE,
              lw=1.1, shrinkA=0, shrinkB=0)
    for i, x in enumerate(xs):
        ax.scatter([x], [yf], s=430, facecolor="white", edgecolor=INK,
                   linewidth=1.0, zorder=4)
        ax.scatter([x], [yb], s=430, facecolor="white", edgecolor=PURPLE,
                   linewidth=1.0, zorder=4)
        label(ax, x, yf, lab_f[i], fs=8.6, color=INK)
        label(ax, x, yb, lab_b[i], fs=8.6, color=PURPLE)
        label(ax, x, yf - 0.105, "存", fs=8.0, color=FAINT)

    for i in range(len(xs) - 1):
        mx = (xs[i] + xs[i + 1]) / 2.0
        label(ax, mx, yf + 0.085, r"$f$", fs=9.0, color=MUTED)
        label(ax, mx, yb - 0.085, r"$\partial f/\partial \mathbf{x}$", fs=8.2,
              color=PURPLE)

    ax.plot([xs[-1], xs[-1]], [yf - 0.07, yb + 0.07], color=FAINT, lw=0.8,
            ls=(0, (2, 2)), zorder=2)
    label(ax, xs[-1] + 0.02, (yf + yb) / 2, "同一时刻\n梯度接上", fs=7.6,
          color=FAINT, ha="left")

    ax.annotate("", xy=(xs[-1] + 0.02, 0.955), xytext=(xs[0] - 0.02, 0.955),
                arrowprops=dict(arrowstyle="<->", color=FAINT, lw=0.8))
    label(ax, (xs[0] + xs[-1]) / 2, 0.90, "T 份状态全部留在内存里", fs=8.0,
          color=MUTED)

    label(ax, 0.035, yf, "前向", fs=8.4, color=INK, rot=90)
    label(ax, 0.035, yb, "反向", fs=8.4, color=PURPLE, rot=90)

    # ---- 右：存储量
    ax2 = fig.add_axes([0.655, 0.225, 0.315, 0.545])
    T = np.array([8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192],
                 dtype=float)
    ax2.loglog(T, T, "-o", color=ACCENT, lw=1.5, ms=3.0, mfc="white", mew=1.0,
               label="全部保存　$O(T)$")
    ax2.loglog(T, 2 * np.sqrt(T), "-s", color=GREEN, lw=1.5, ms=3.0,
               mfc="white", mew=1.0, label="checkpoint　$O(\\sqrt{T})$")
    ax2.set_xlabel("时间步数 T", fontsize=8.6, labelpad=1.5)
    ax2.set_ylabel("需保存的状态份数", fontsize=8.6, labelpad=1.5)
    ax2.tick_params(labelsize=8.0, length=2.5, pad=1.5)
    clean(ax2, grid=True, spines=("left", "bottom"))
    ax2.legend(loc="upper left", fontsize=8.0, handlelength=1.6,
               labelspacing=0.4, borderaxespad=0.5)
    ax2.set_ylim(1, 3e4)

    save(fig, "10", "fig10-01")


# ---------------------------------------------------------------- 图 10-2
# 伴随法的一步：前向算状态，反向把梯度回传并顺手累加参数梯度。
def fig02():
    fig, ax = canvas(6.6, 3.5)

    box(ax, 0.02, 0.68, 0.15, 0.16, r"$\mathbf{x}_t$", fc="#F8FAFC", fs=9.2)
    box(ax, 0.30, 0.68, 0.21, 0.16, r"$f(\mathbf{x}_t,\theta)$", fc="#F8FAFC",
        fs=9.2)
    box(ax, 0.62, 0.68, 0.15, 0.16, r"$\mathbf{x}_{t+1}$", fc="#F8FAFC", fs=9.2)
    arrow(ax, (0.175, 0.76), (0.295, 0.76), color=MUTED, lw=1.1, shrinkA=0,
          shrinkB=0)
    arrow(ax, (0.515, 0.76), (0.615, 0.76), color=MUTED, lw=1.1, shrinkA=0,
          shrinkB=0)

    box(ax, 0.352, 0.900, 0.120, 0.092, r"$\theta$", fc="white", ec=ACCENT,
        tc=ACCENT, fs=9.0, lw=1.0, rounded=0.010)
    arrow(ax, (0.4125, 0.895), (0.4125, 0.845), color=ACCENT, lw=1.0,
          shrinkA=0, shrinkB=0)

    # 反向
    box(ax, 0.62, 0.26, 0.15, 0.16, r"$\lambda_{t+1}$", fc="#F5F3FF",
        ec=PURPLE, tc=PURPLE, fs=9.2)
    box(ax, 0.28, 0.26, 0.25, 0.16, "左乘\n$(\\partial f/\\partial\\mathbf{x})^{\\top}$",
        fc="#F5F3FF", ec=PURPLE, tc=PURPLE, fs=8.2)
    box(ax, 0.02, 0.26, 0.15, 0.16, r"$\lambda_t$", fc="#F5F3FF", ec=PURPLE,
        tc=PURPLE, fs=9.2)
    arrow(ax, (0.615, 0.34), (0.535, 0.34), color=PURPLE, lw=1.1, shrinkA=0,
          shrinkB=0)
    arrow(ax, (0.275, 0.34), (0.175, 0.34), color=PURPLE, lw=1.1, shrinkA=0,
          shrinkB=0)

    # 同一时刻的接续
    ax.plot([0.695, 0.695], [0.675, 0.425], color=FAINT, lw=0.8,
            ls=(0, (2, 2)), zorder=1)
    label(ax, 0.71, 0.55, "同一时刻\n$\\lambda$ 由上一层传来", fs=8.0,
          color=FAINT, ha="left")

    # 参数梯度累加
    box(ax, 0.185, 0.015, 0.470, 0.145,
        "逐时刻累加　$\\partial L/\\partial\\theta\\;{+}{=}\\,"
        "\\lambda_{t+1}^{\\top}(\\partial f/\\partial\\theta)$",
        fc="white", ec=ACCENT, fs=8.0)
    curve_arrow(ax, [(0.695, 0.25), (0.695, 0.088), (0.660, 0.088)],
                color=ACCENT, lw=1.0)

    label(ax, 0.02, 0.90, "前向", fs=8.4, color=INK, ha="left")
    label(ax, 0.02, 0.50, "反向", fs=8.4, color=PURPLE, ha="left")

    save(fig, "10", "fig10-02")


# ---------------------------------------------------------------- 图 10-3
# 可微模拟的闭环：参数 → 仿真 → 损失 → 梯度 → 更新。
def fig03():
    fig, ax = canvas(6.6, 3.4)

    box(ax, 0.045, 0.60, 0.30, 0.20,
        "参数 $\\theta$\n材料、形状、控制", fc="#FDF7EC", ec=ACCENT, fs=8.6)
    box(ax, 0.635, 0.60, 0.33, 0.20, "可微仿真器\n前向上万步", fc="#EFF4FF",
        ec=BLUE, fs=8.6)
    box(ax, 0.635, 0.16, 0.33, 0.20, "观测量与损失\n$L(\\mathbf{x}(T))$",
        fc="#EFF4FF", ec=BLUE, fs=8.6)
    box(ax, 0.045, 0.16, 0.30, 0.20, "梯度\n$\\partial L/\\partial\\theta$",
        fc="#F5F3FF", ec=PURPLE, fs=8.6)

    arrow(ax, (0.35, 0.70), (0.625, 0.70), color=MUTED, lw=1.2)
    arrow(ax, (0.80, 0.595), (0.80, 0.375), color=MUTED, lw=1.2)
    arrow(ax, (0.625, 0.26), (0.355, 0.26), color=MUTED, lw=1.2)
    arrow(ax, (0.19, 0.155), (0.19, 0.585), color=MUTED, lw=1.2)

    label(ax, 0.49, 0.745, "① 给定参数", fs=8.0, color=MUTED)
    label(ax, 0.815, 0.485, "② 得到轨迹", fs=8.0, color=MUTED, ha="left")
    label(ax, 0.49, 0.205, "③ 与观测比较", fs=8.0, color=MUTED)
    label(ax, 0.175, 0.50, "④ 更新参数\n前向 + 反向各一次", fs=8.0, color=MUTED,
          ha="right")

    ax.add_patch(Rectangle((0.02, 0.005), 0.96, 0.075, facecolor="#F9FAFB",
                           edgecolor="#E5E7EB", lw=0.8, zorder=1))
    label(ax, 0.50, 0.0425, "参数辨识　·　形状优化　·　控制序列　·　sim-to-real",
          fs=8.2, color=MUTED, z=3)

    save(fig, "10", "fig10-03")


fig01()
fig02()
fig03()
