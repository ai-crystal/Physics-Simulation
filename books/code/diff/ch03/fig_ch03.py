import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 3-1  三条路线的数据流（示意图）
# ============================================================
fig, ax = canvas(6.9, 4.35)

yc = [0.845, 0.555, 0.265]

names = ["录进计算图", "伴随", "手工解析"]
times = ["时间  前向的 2–3 倍", "时间  前向的 2–3 倍", "时间  前向的 1.2–2 倍"]
mems = ["显存  正比于步数", "显存  正比于步数", "显存  只留当前步"]

bx0, bw, gap = 0.268, 0.086, 0.031
nb = 5
xs = [bx0 + i * (bw + gap) for i in range(nb)]
labels = ["1", "2", "· · ·", "N−1", "N"]

for k, y in enumerate(yc):
    # 左侧标签
    label(ax, 0.020, y + 0.045, names[k], fs=9.4, ha="left", weight="bold")
    label(ax, 0.020, y - 0.004, times[k], fs=7.9, ha="left", color=MUTED)
    label(ax, 0.020, y - 0.048, mems[k], fs=7.9, ha="left", color=MUTED)

    # 前向
    label(ax, 0.268 + (nb * (bw + gap) - gap) / 2, y + 0.088, "前向", fs=7.9,
          color=BLUE, weight="bold")
    arrow(ax, (xs[0], y + 0.073), (xs[-1] + bw, y + 0.073), color=BLUE, lw=1.0, ms=7)

    # 步的方框
    for i, x in enumerate(xs):
        dashed = (i == 2)
        box(ax, x, y - 0.043, bw, 0.086, labels[i],
            fc="white" if not dashed else "#F6F7F9",
            ec=FAINT if dashed else INK, fs=8.4,
            lw=0.9, ls=(0, (3, 2)) if dashed else "-")

    # 反向
    arrow(ax, (xs[-1] + bw, y - 0.072), (xs[0], y - 0.072), color=ACCENT, lw=1.0, ms=7)

# ---- 每行反向那一步在做什么 ----
label(ax, 0.862, yc[0] - 0.072, "逐算子反传", fs=8.6, color=ACCENT, ha="left", weight="bold")
label(ax, 0.862, yc[1] - 0.072, "解 $\\mathbf{A}^{\\top}\\mathbf{z}=\\boldsymbol{\\lambda}$", fs=8.8,
      color=ACCENT, ha="left", weight="bold")
label(ax, 0.862, yc[2] - 0.072, "代入闭式公式", fs=8.6, color=ACCENT, ha="left", weight="bold")

# ---- 保存的东西 ----
# 第一行：每步的中间量，厚块
for x in xs:
    ax.add_patch(Rectangle((x, yc[0] - 0.150), bw, 0.042, facecolor="#FBE7D2",
                           edgecolor=ACCENT, lw=0.8, zorder=3))
label(ax, 0.862, yc[0] - 0.129, "每步中间量", fs=8.0, color=ACCENT, ha="left")

# 第二行：每步的状态，薄条
for x in xs:
    ax.add_patch(Rectangle((x, yc[1] - 0.150), bw, 0.016, facecolor="#DCE6FA",
                           edgecolor=BLUE, lw=0.8, zorder=3))
label(ax, 0.862, yc[1] - 0.142, "每步状态", fs=8.0, color=BLUE, ha="left")

# 第三行：什么也不存
label(ax, xs[0] + (nb * (bw + gap) - gap) / 2, yc[2] - 0.118,
      "不保存，只留当前步", fs=7.9, color=FAINT, ha="center")

# ---- 分隔 ----
for y in (0.670, 0.380):
    ax.plot([0.020, 0.985], [y, y], color=GRID, lw=0.8, zorder=1)
ax.plot([0.248, 0.248], [0.030, 0.955], color=GRID, lw=0.8, zorder=1)

# ---- 顶部说明 ----
label(ax, 0.020, 0.985, "一步 = 一个时间步的映射 $S$，橙箭头是反向", fs=8.2,
      color=MUTED, ha="left", va="top")
label(ax, 0.985, 0.985, "色块厚度示意每步要留的量", fs=8.2, color=MUTED,
      ha="right", va="top")

save(fig, "03", "fig03-01")

# ============================================================
# 图 3-2  显存随步数（按模型真实计算）
#   模型：5 万顶点，每顶点 6 个 float32 = 24 B，一份状态 1.2 MB
#        录图每步存 4 倍中间量 = 4.2 MB/步
#        检查点按 sqrt 分段，段内重算
#        GB 按 1024 MB 计
# ============================================================
S_MB = 50000 * 24 / 2**20          # 1.14 MB，取 1.2
S_MB = 1.2
T_MB = 4.0 * S_MB                  # 4.8 MB/步（录图）
P = 12                             # 有限差分参数个数

N = np.unique(np.round(np.logspace(np.log10(50), np.log10(10000), 260))).astype(int)

tape = N * T_MB
state = N * S_MB + 2 * S_MB
fd = (P + 1) * S_MB * np.ones_like(N, float)

ckpt = np.empty_like(N, float)
best_s = np.empty_like(N, int)
for i, n in enumerate(N):
    ss = np.arange(1, n + 1)
    mem = np.ceil(n / ss) * S_MB + ss * T_MB
    j = np.argmin(mem)
    ckpt[i] = mem[j]
    best_s[i] = ss[j]

fig, ax = plt.subplots(figsize=(6.8, 4.05))
clean(ax, grid=True, spines=("left", "bottom"))

ax.axhline(24 * 1024, color=PINK, lw=1.0, ls=(0, (5, 3)), zorder=2)
label(ax, 62, 24 * 1024 * 1.12, "单张 24 GB 显卡", fs=8.4, color=PINK, ha="left", va="bottom")

ax.loglog(N, tape, color=ACCENT, lw=1.7, label="录进计算图（4.0 倍中间量）")
ax.loglog(N, state, color=BLUE, lw=1.7, label="伴随：每步存状态")
ax.loglog(N, ckpt, color=GREEN, lw=1.7, ls=(0, (5, 2.4)),
          label="伴随 + 检查点（段长取最优）")
ax.loglog(N, fd, color=MUTED, lw=1.5, ls=(0, (2, 2)), label="有限差分（12 个参数）")

# 交点
n_cross = 24 * 1024 / T_MB
ax.plot([n_cross], [24 * 1024], "o", ms=4.4, color=ACCENT, mec="white", mew=0.8, zorder=6)
ax.annotate("约 %d 步出卡" % int(n_cross),
            xy=(n_cross, 24 * 1024), xytext=(900, 5.6e4),
            fontsize=8.4, color=ACCENT, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, shrinkA=5, shrinkB=4))

# 1000 步时的两个读数
for yv, c in ((1000 * T_MB, ACCENT), (1000 * S_MB, BLUE)):
    ax.plot([1000], [yv], "o", ms=3.8, color=c, mec="white", mew=0.7, zorder=6)
label(ax, 1055, 1000 * T_MB * 1.42, "%.1f GB" % (1000 * T_MB / 1024), fs=8.4,
      color=ACCENT, ha="left", va="bottom")
label(ax, 1055, 1000 * S_MB * 1.45, "%.1f GB" % (1000 * S_MB / 1024), fs=8.4,
      color=BLUE, ha="left", va="bottom")

ax.set_xlim(50, 1.0e4)
ax.set_ylim(8, 1.1e5)
ax.set_xlabel("时间步数 $N$")
ax.set_ylabel("显存占用 (MB)")
ax.set_xticks([50, 100, 300, 1000, 3000, 10000])
ax.set_xticklabels(["50", "100", "300", "1000", "3000", "10000"])
ax.set_yticks([10, 100, 1000, 1e4, 1e5])
ax.set_yticklabels(["10", "100", "1000", "10⁴", "10⁵"])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.255), ncol=2, fontsize=8.4,
          labelspacing=0.55, handlelength=2.2, columnspacing=1.6)
save(fig, "03", "fig03-02")
