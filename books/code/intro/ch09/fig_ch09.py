import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 9-1
# 上：60/30 fps 一帧内的时间怎么被分掉（比例取自量级经验，示意图）
# 下：把三种预算放到同一根对数时间尺上。
def fig01():
    fig = plt.figure(figsize=(6.7, 4.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.62,
                          left=0.115, right=0.965, top=0.945, bottom=0.11)

    ax = fig.add_subplot(gs[0])
    rows = [
        (1.0, "30 fps", [15.6, 4.2, 7.2, 6.3], "33.3 ms"),
        (0.0, "60 fps", [8.2, 2.1, 3.4, 2.9], "16.7 ms"),
    ]
    cols = ["#DCE6FA", "#DBEDE3", ACCENT, "#E5E7EB"]
    names = ["渲染与后处理", "动画与脚本", "物理", "其他与留白"]
    for y, nm, parts, tot in rows:
        left = 0.0
        for c, p in zip(cols, parts):
            ax.barh(y, p, left=left, height=0.40, color=c, edgecolor="white",
                    linewidth=1.2, zorder=3)
            left += p
        ax.text(left + 0.8, y, tot, va="center", ha="left", fontsize=8.4,
                color=MUTED)
        cx = parts[0] + parts[1] + parts[2] / 2.0
        yt = y - 0.26
        ax.plot([cx, cx], [y - 0.20, yt - 0.02], color=ACCENT, lw=0.7, zorder=4)
        ax.text(cx, yt - 0.04, "物理 %s ms" % ("%.1f" % parts[2]),
                ha="center", va="top", fontsize=8.2, color=ACCENT)

    ax.set_xlim(-10.0, 38.0)
    ax.set_ylim(-0.62, 1.42)
    ax.set_yticks([1.0, 0.0])
    ax.set_yticklabels(["30 fps", "60 fps"], fontsize=9)
    ax.set_xticks([0, 10, 20, 30])
    ax.set_xlabel("一帧内的时间分配（ms）", fontsize=9)
    clean(ax, spines=("bottom",))
    ax.tick_params(axis="x", length=2.5, pad=2)
    ax.tick_params(axis="y", length=0, pad=7)

    handles = [Rectangle((0, 0), 1, 1, facecolor=c, edgecolor="none")
               for c in cols]
    ax.legend(handles, names, loc="upper left", bbox_to_anchor=(-0.02, 1.30),
              ncol=4, fontsize=8.2, handlelength=1.1, handleheight=0.7,
              columnspacing=1.0, handletextpad=0.42, borderaxespad=0.0)

    ax2 = fig.add_subplot(gs[1])
    ax2.set_xscale("log")
    ax2.set_xlim(0.6, 2.5e7)
    ax2.set_ylim(0, 1)
    ax2.axis("off")
    ax2.plot([0.8, 2e7], [0.5, 0.5], color=MUTED, lw=1.1, zorder=2,
             solid_capstyle="butt")
    dec = [(1e0, "1 ms"), (1e1, "10"), (1e2, "100"), (1e3, "1 s"),
           (1e4, "10"), (1e5, "100"), (1e6, "1000"), (1e7, "$10^4$ s")]
    for v, t in dec:
        ax2.plot([v, v], [0.445, 0.555], color=MUTED, lw=0.8, zorder=2)
        ax2.text(v, 0.40, t, ha="center", va="top", fontsize=8.0, color=MUTED)

    marks = [(16.7, "60 fps 的 16.7 ms", "up", ACCENT),
             (33.3, "30 fps 的 33.3 ms", "down", ACCENT),
             (1.8e6, "离线一帧 30 min", "up", BLUE)]
    for v, t, side, c in marks:
        ax2.plot([v, v], [0.5, 0.76 if side == "up" else 0.24], color=c, lw=0.8,
                 ls=(0, (2, 2)), zorder=2)
        ax2.scatter([v], [0.5], s=26, color=c, zorder=4, edgecolor="white",
                    linewidth=0.8)
        ax2.text(v, 0.80 if side == "up" else 0.18, t, ha="center",
                 va="bottom" if side == "up" else "top", fontsize=8.2, color=c)

    ax2.annotate("", xy=(1.55e5, 0.12), xytext=(9.0e5, 0.12),
                 arrowprops=dict(arrowstyle="<->", color=BLUE, lw=0.8))
    ax2.text(3.7e5, 0.06, "离线常见区间", ha="center", va="top", fontsize=8.0,
             color=BLUE)

    save(fig, "09", "fig09-01")


# ---------------------------------------------------------------- 图 9-2
# 二维五点拉普拉斯在 12x12 网格上的真实稀疏结构。
def fig02():
    N = 12
    n = N * N
    A = np.zeros((n, n))
    for j in range(N):
        for i in range(N):
            p = j * N + i
            A[p, p] = 4.0
            if i > 0:
                A[p, p - 1] = -1.0
            if i < N - 1:
                A[p, p + 1] = -1.0
            if j > 0:
                A[p, p - N] = -1.0
            if j < N - 1:
                A[p, p + N] = -1.0

    fig = plt.figure(figsize=(6.8, 3.6))

    fig.text(0.045, 0.935, "(a) 网格与五点模板", fontsize=9.2, color=INK)
    fig.text(0.395, 0.935, "(b) 对应的矩阵非零元分布", fontsize=9.2, color=INK)

    # --- (a) 网格
    axa = fig.add_axes([0.045, 0.20, 0.30, 0.66])
    axa.set_xlim(-0.25, N + 0.25)
    axa.set_ylim(-0.25, N + 0.25)
    axa.set_aspect("equal")
    axa.axis("off")
    for k in range(N + 1):
        axa.plot([0, N], [k, k], color=GRID, lw=0.6, zorder=1)
        axa.plot([k, k], [0, N], color=GRID, lw=0.6, zorder=1)
    j0, i0 = 4, 3
    axa.add_patch(Rectangle((0, j0), N, 1, facecolor="#DCE6FA", edgecolor="none",
                            zorder=2))
    axa.add_patch(Rectangle((i0, j0), 1, 1, facecolor=ACCENT, edgecolor="none",
                            zorder=4))
    for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        axa.add_patch(Rectangle((i0 + di, j0 + dj), 1, 1, facecolor=ACCENT,
                                alpha=0.20, edgecolor="none", zorder=3))
    fig.text(0.045, 0.105, "网格 12×12，未知量 n = 144", fontsize=8.2,
             color=MUTED)
    fig.text(0.045, 0.045, "中心格与上下左右四个邻居，构成五点模板", fontsize=8.2,
             color=MUTED)

    # --- (b) 矩阵
    axb = fig.add_axes([0.415, 0.175, 0.335, 0.705])
    rows, cols = np.nonzero(A)
    axb.scatter(cols, rows, s=1.4, marker="s", c=ACCENT, linewidths=0, zorder=3)
    for k in range(0, n + 1, N):
        axb.plot([-0.5, n - 0.5], [k - 0.5, k - 0.5], color=FAINT, lw=0.5,
                 ls=(0, (3, 2)), zorder=2)
        axb.plot([k - 0.5, k - 0.5], [-0.5, n - 0.5], color=FAINT, lw=0.5,
                 ls=(0, (3, 2)), zorder=2)
    axb.plot([-0.5, n - 0.5], [-0.5, n - 0.5], color=BLUE, lw=0.7,
             ls=(0, (4, 3)), zorder=2)
    axb.set_xlim(-4, n + 6)
    axb.set_ylim(n + 6, -10)
    axb.set_aspect("equal")
    axb.axis("off")

    nnz = int(np.count_nonzero(A))
    fig.text(0.770, 0.885, "非零元 %d 个\n占全部元素的 %.1f%%"
             % (nnz, 100.0 * nnz / n / n), ha="left", va="top", fontsize=8.2,
             color=MUTED, linespacing=1.5)

    fig.text(0.415, 0.105, "中间粗线：主对角与左右邻居叠加", fontsize=8.2,
             color=MUTED)
    fig.text(0.415, 0.045, "外侧斜线：上下邻居，偏移 N = 12", fontsize=8.2,
             color=MUTED)

    fig.text(0.770, 0.545, "蓝虚线：主对角\n方块：非零元\n虚线框：一行网格\n对应一个 12×12 块",
             ha="left", va="top", fontsize=8.0, color=MUTED, linespacing=1.7)

    save(fig, "09", "fig09-02")


# ---------------------------------------------------------------- 图 9-3
# 三种求解器计算量随分辨率增长（复杂度模型，非实测）。
def fig03():
    N = np.array([16, 32, 64, 128, 256, 512], dtype=float)
    base = 32.0
    dense = (N / base) ** 6.0
    cg = (N / base) ** 3.0
    mg = (N / base) ** 2.0

    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    fig.subplots_adjust(left=0.115, right=0.965, top=0.955, bottom=0.155)

    ax.loglog(N, dense, "-o", color=ACCENT, lw=1.6, ms=4.0, mfc="white",
              mew=1.2, label="稠密直接法　$O(n^3)=O(N^6)$")
    ax.loglog(N, cg, "-s", color=BLUE, lw=1.6, ms=4.0, mfc="white", mew=1.2,
              label="共轭梯度　$O(n^{1.5})=O(N^3)$")
    ax.loglog(N, mg, "-^", color=GREEN, lw=1.6, ms=4.0, mfc="white", mew=1.2,
              label="多重网格　$O(n)=O(N^2)$")

    ax.set_xticks(N)
    ax.set_xticklabels([str(int(v)) for v in N])
    ax.minorticks_off()
    ax.set_xlabel("每个方向的网格数 N（未知量 n = N²）", fontsize=9.4)
    ax.set_ylabel("相对计算量（N = 32 归一）", fontsize=9.4)
    ax.set_xlim(14, 640)
    ax.set_ylim(1e-2, 3e8)
    clean(ax, grid=True, spines=("left", "bottom"))
    ax.legend(loc="upper left", fontsize=8.2, handlelength=1.9,
              labelspacing=0.45, borderaxespad=0.7)

    # 沿曲线写斜率，角度按屏幕坐标算
    def slope_label(x0, m, text, color, dy=1.75):
        y0 = (x0 / base) ** m
        p0 = ax.transData.transform((x0, y0))
        p1 = ax.transData.transform((x0 * 1.35, (x0 * 1.35 / base) ** m))
        ang = np.degrees(np.arctan2(p1[1] - p0[1], p1[0] - p0[0]))
        ax.text(x0, y0 * dy, text, color=color, fontsize=8.2, rotation=ang,
                rotation_mode="anchor", ha="left", va="bottom",
                bbox=dict(fc="white", ec="none", pad=1.0), zorder=6)

    slope_label(78, 6.0, "斜率 6", ACCENT)
    slope_label(90, 3.0, "斜率 3", BLUE)
    slope_label(185, 2.0, "斜率 2", GREEN)

    ax.annotate("N = 512 时相差约 6.6 万倍",
                xy=(512, 1.7e7), xytext=(140, 7.0e7), fontsize=8.4,
                color=MUTED, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7,
                                connectionstyle="arc3,rad=0.25"))

    save(fig, "09", "fig09-03")


fig01()
fig02()
fig03()
