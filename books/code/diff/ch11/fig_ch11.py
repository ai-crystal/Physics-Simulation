import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 11-1  学习模块插入求解器的三个位置（示意）
# ============================================================
fig, ax = canvas(6.7, 4.3)

ROWS = [
    # (行顶 y, 标题, c2 文本, c3 文本, c4 文本, 说明)
    (0.950,
     "（a）修正项：插在状态上",
     "物理推进 $F(\\mathbf{x}_n)$",
     "$+\\;\\alpha\\,\\mathbf{g}_\\phi(\\mathbf{x}_n)$",
     "$\\mathbf{x}_{n+1}$",
     "网络吃状态、吐一个残差；物理负责全部推进，去掉网络（$\\alpha=0$）即退回纯物理。"),
    (0.655,
     "（b）本构：插在力的规则里",
     "学习本构 $\\boldsymbol{\\sigma}=\\mathcal{C}_\\phi(\\boldsymbol{\\varepsilon},\\dot{\\boldsymbol{\\varepsilon}})$",
     "平衡与时间积分",
     "$\\mathbf{x}_{n+1}$",
     "网络吃应变与应变率、吐应力；守恒与积分仍在求解器手里，网络须满足旋转不变与正耗散。"),
    (0.360,
     "（c）子网格：插在未解析尺度",
     "粗网格求解（可解析尺度）",
     "$\\mathcal{S}_\\phi$ 补未解析尺度",
     "$\\mathbf{x}_{n+1}$",
     "网络只看局部邻域、补小尺度对大尺度的贡献；离散格式仍守恒，长积分不发散。"),
]

CW = [(0.045, 0.100), (0.175, 0.340), (0.545, 0.280), (0.855, 0.100)]
H = 0.098


def node_colors(kind, label_text):
    """按插入位置给四个节点上色：橙为学习模块，白为物理。"""
    if kind == "a":
        return [(ACCENT, "#FDF2E9") if i == 2 else (INK, "white") for i in range(4)]
    if kind == "b":
        return [(ACCENT, "#FDF2E9") if i == 1 else (INK, "white") for i in range(4)]
    return [(ACCENT, "#FDF2E9") if i == 2 else (INK, "white") for i in range(4)]


for (ytop, head, t2, t3, t4, note), kind in zip(ROWS, "abc"):
    y = ytop - 0.135
    texts = ["$\\mathbf{x}_n$", t2, t3, t4]
    cols = node_colors(kind, None)
    for (x, w), tx, (ec, fc) in zip(CW, texts, cols):
        box(ax, x, y - H / 2, w, H, tx, fc=fc, ec=ec, fs=8.3,
            lw=(1.5 if ec == ACCENT else 1.0))
    for i in range(3):
        xa = CW[i][0] + CW[i][1]
        xb = CW[i + 1][0]
        arrow(ax, (xa + 0.004, y), (xb - 0.004, y), color=MUTED, lw=1.1, ms=8)

    label(ax, 0.045, ytop - 0.010, head, fs=9.0, ha="left", va="center",
          weight="bold", color=ACCENT)
    label(ax, 0.045, ytop - 0.238, note, fs=8.2, ha="left", va="center", color=INK)
    if ytop > 0.40:
        ax.plot([0.045, 0.985], [ytop - 0.293, ytop - 0.293], color=GRID, lw=0.9)

# 图例（右上）
box(ax, 0.620, 0.936, 0.034, 0.028, "", fc="#FDF2E9", ec=ACCENT, lw=1.4, rounded=0.009)
label(ax, 0.664, 0.950, "学习模块", fs=8.4, ha="left")
box(ax, 0.790, 0.936, 0.034, 0.028, "", fc="white", ec=INK, lw=1.0, rounded=0.009)
label(ax, 0.834, 0.950, "物理", fs=8.4, ha="left")

save(fig, "11", "fig11-01")


# ============================================================
# 图 11-2  辨识与随机化在参数空间里的接力（示意）
# ============================================================
fig, axs = new(6.7, 3.5, ncols=2, gridspec_kw=dict(width_ratios=[1.05, 1.0], wspace=0.34))
ax1, ax2 = axs

# ---------- 左：参数平面 ----------
ax1.set_xlim(0.15, 1.15)
ax1.set_ylim(-2, 62)
clean(ax1, grid=True)
ax1.set_xlabel("摩擦系数 $\\mu$")
ax1.set_ylabel("执行器延迟 (ms)")

ax1.add_patch(Rectangle((0.28, 0.0), 0.72, 45.0, facecolor="#FDF2E9",
                        edgecolor=ACCENT, lw=1.0, ls=(0, (4, 3)), alpha=0.75, zorder=1))
label(ax1, 0.29, 48.0, "随机化范围", fs=8.4, color=ACCENT, ha="left")

ax1.add_patch(Ellipse((0.46, 25.0), 0.20, 13.0, fill=False, edgecolor=BLUE,
                      lw=1.2, ls=(0, (3, 2)), zorder=4))
label(ax1, 0.455, 14.0, "辨识区间", fs=8.2, color=BLUE, ha="center")

ax1.plot([0.42], [28.0], "o", ms=5.2, color=INK, zorder=6)
ax1.annotate("真值", xy=(0.42, 28.0), xytext=(0.55, 36.0), fontsize=8.4, color=INK,
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8,
                             connectionstyle="arc3,rad=-0.2"), zorder=7)
arrow(ax1, (0.575, 25.0), (0.90, 25.0), color=ACCENT, lw=1.0, ms=8)
label(ax1, 0.735, 27.5, "放大到覆盖", fs=8.0, color=ACCENT, ha="center")

# ---------- 右：宽度与成功率 ----------
w = np.linspace(0, 1, 200)
succ = 0.90 * np.exp(-((w - 0.45) / 0.31) ** 2)
ax2.fill_between(w, 0, succ, color="#EFF4FF", alpha=0.9, zorder=1)
ax2.plot(w, succ, color=INK, lw=1.5, zorder=3)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.0)
clean(ax2, grid=False)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xlabel("随机化宽度（相对）")
ax2.set_ylabel("真机成功率（相对）")

ax2.plot([0.45, 0.45], [0, 0.90], color=ACCENT, lw=0.9, ls=(0, (3, 3)), zorder=2)
ax2.plot([0.45], [0.90], "o", ms=4.0, color=ACCENT, zorder=4)
label(ax2, 0.47, 0.935, "最优点", fs=8.2, color=ACCENT, ha="left")
label(ax2, 0.05, 0.26, "过拟合\n训练分布", fs=8.0, color=MUTED, ha="left")
label(ax2, 0.98, 0.26, "为最坏情况\n付保守代价", fs=8.0, color=MUTED, ha="right")

save(fig, "11", "fig11-02")
