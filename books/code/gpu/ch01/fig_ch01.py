import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 1-1  Amdahl 定律（真实计算）
#   S(P) = 1 / (s + (1-s)/P)，s 为串行比例
# ============================================================
def amdahl(P, s):
    return 1.0 / (s + (1.0 - s) / P)


fig, ax = plt.subplots(figsize=(6.7, 3.75))
clean(ax, grid=True)

P = np.logspace(0, np.log10(1024), 600)
SS = [0.01, 0.05, 0.10, 0.20]
COLS = [BLUE, ACCENT, GREEN, PURPLE]
NAMES = ["s = 0.01", "s = 0.05", "s = 0.10", "s = 0.20"]

for s, c, nm in zip(SS, COLS, NAMES):
    ax.plot(P, amdahl(P, s), color=c, lw=1.7, zorder=4, label=nm)
    ax.plot(P, np.full_like(P, 1.0 / s), color=c, lw=0.8, ls=(0, (4, 4)),
            alpha=0.5, zorder=2)

# 两条参考竖线：8 核与 64 核
for pv, tx in [(8, "8 核"), (64, "64 核")]:
    ax.axvline(pv, color=FAINT, lw=0.7, ls=(0, (2, 3)), zorder=1)
    ax.text(pv, 103, tx, fontsize=8.4, color=MUTED, ha="center", va="bottom")

# s=0.05 上的两个取值点
for pv in (8, 64):
    y = amdahl(pv, 0.05)
    ax.plot([pv], [y], marker="o", ms=5.2, mfc="white", mec=ACCENT, mew=1.5, zorder=6)
ax.annotate("15.42", (64, amdahl(64, 0.05)), textcoords="offset points", xytext=(9, 6),
            fontsize=8.6, color=ACCENT, ha="left", va="bottom")

ax.annotate("上限 1/s", (830, 100), textcoords="offset points", xytext=(0, 5),
            fontsize=8.2, color=BLUE, ha="center", va="bottom")

ax.set_xscale("log", base=2)
ax.set_xlim(1, 1024)
ax.set_ylim(0, 112)
ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
ax.set_xticklabels(["1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"])
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_xlabel("处理器数 $P$")
ax.set_ylabel("加速比 $S$")
ax.legend(loc="upper left", bbox_to_anchor=(0.015, 0.985), handlelength=1.7,
          labelspacing=0.30, borderpad=0.15, fontsize=8.8)

save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  带宽受限与算力受限（屋顶线示意）
#   归一化屋顶：y = min(1, x / ridge)，ridge 为折点处的算术强度
# ============================================================
fig, ax = plt.subplots(figsize=(6.7, 3.9))
clean(ax, grid=False)

RIDGE = 20.0
AI_MIN, AI_MAX = 0.1, 3000.0
Y_MIN, Y_MAX = 0.002, 2.4

xs = np.logspace(np.log10(AI_MIN), np.log10(AI_MAX), 800)
ys = np.minimum(1.0, xs / RIDGE)
ax.plot(xs, ys, color=NAVY, lw=2.0, zorder=4, solid_capstyle="round")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(AI_MIN, AI_MAX)
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xticks([0.1, 1, 10, 100, 1000])
ax.set_xticklabels(["0.1", "1", "10", "100", "1000"])
ax.set_yticks([0.01, 0.1, 1.0])
ax.set_yticklabels(["1%", "10%", "100%"])
ax.set_xlabel("算术强度（浮点运算次数 / 字节）")
ax.set_ylabel("相对峰值性能")

# 两个区域：斜面上受带宽限制，平顶上受算力限制
ax.annotate("带宽受限区", xy=(0.85, 0.042), xytext=(0.52, 0.42),
            fontsize=9.0, color=TEAL, ha="center", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=0.9,
                            shrinkA=3, shrinkB=2, mutation_scale=8))
ax.annotate("算力受限区", xy=(160.0, 1.0), xytext=(165.0, 1.55),
            fontsize=9.0, color=GOLD, ha="center", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.9,
                            shrinkA=3, shrinkB=3, mutation_scale=8))
ax.plot([RIDGE], [1.0], marker="o", ms=4.6, mfc="white", mec=NAVY, mew=1.5, zorder=6)
ax.annotate("折点", (RIDGE, 1.0), textcoords="offset points", xytext=(-2, 11),
            fontsize=8.2, color=MUTED, ha="center")

# 三个工作点（横坐标由运算数与字节数数出来）
PTS = [(0.40, ("七点模板", "0.2–0.8 次/字节"), (0.30, 0.0045), "left"),
       (3.30, ("粒子对循环", "约 3.3 次/字节"), (5.5, 0.026), "left"),
       (300.0, ("稠密矩阵乘", "随规模增长"), (300.0, 0.20), "center")]

for ai, name, (tx, ty), ha in PTS:
    name = "\n".join([s for s in name if s])
    y = min(1.0, ai / RIDGE)
    ax.plot([ai], [y], marker="s", ms=5.0, mfc=ACCENT, mec="white", mew=0.9, zorder=7)
    ax.annotate(name, xy=(ai, y), xytext=(tx, ty), fontsize=8.5, color=INK,
                ha=ha, va="bottom", linespacing=1.5,
                arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7,
                                shrinkA=4, shrinkB=4))

save(fig, "01", "fig01-02")
