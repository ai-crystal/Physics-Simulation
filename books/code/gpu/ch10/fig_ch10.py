import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 10-1  区域分解与幽灵层（二维示意，无数值含义）
# ============================================================
fig, ax = canvas(6.8, 3.7)

# ---- 左：2x2 块分解 ----
X0, Y0, W, H = 0.075, 0.235, 0.245, 0.555
NC = 8
cw, ch = W / NC, H / NC
bands = [SOFT[1], SOFT[2], SOFT[4], SOFT[3]]
names = ["块 A", "块 B", "块 C", "块 D"]
for bi in range(4):
    bx = X0 + (bi % 2) * W / 2
    by = Y0 + (1 - bi // 2) * H / 2
    ax.add_patch(Rectangle((bx, by), W / 2, H / 2, facecolor=bands[bi],
                           edgecolor="none", zorder=1))
    label(ax, bx + W / 4, by + H / 4, names[bi], fs=8.8, color=INK, weight="bold")

# 幽灵层：紧贴分解线两侧各一列
ghost = "#E8D5C2"
for i, x in enumerate([X0 + (NC / 2 - 1) * cw, X0 + (NC / 2) * cw]):
    ax.add_patch(Rectangle((x, Y0), cw, H, facecolor=ghost, edgecolor="none",
                           alpha=0.9, zorder=2))
for y in [Y0 + (NC / 2 - 1) * ch, Y0 + (NC / 2) * ch]:
    ax.add_patch(Rectangle((X0, y), W, ch, facecolor=ghost, edgecolor="none",
                           alpha=0.9, zorder=2))

grid(ax, X0, Y0, W, H, NC, NC, color="#FFFFFF", lw=0.9)
ax.add_patch(Rectangle((X0, Y0), W, H, facecolor="none", edgecolor=INK, lw=1.1, zorder=6))
ax.plot([X0 + W / 2, X0 + W / 2], [Y0, Y0 + H], color=INK, lw=1.6, zorder=7)
ax.plot([X0, X0 + W], [Y0 + H / 2, Y0 + H / 2], color=INK, lw=1.6, zorder=7)

# 幽灵层标注
label(ax, X0 + W + 0.012, Y0 + H - 0.045, "斜纹格：\n幽灵层", fs=7.6, color=ACCENT,
      ha="left", va="center")
arrow(ax, (X0 + W + 0.010, Y0 + H - 0.045), (X0 + W - 0.5 * cw, Y0 + H - 0.02),
      color=ACCENT, lw=0.8, ms=7)
label(ax, X0 + W / 2, Y0 - 0.075, "分解线（数据在这里被切开）", fs=7.6, color=MUTED)
label(ax, 0.012, 0.955, "(a) 二维域切成四块，每块各留一层", fs=8.6, color=INK, ha="left")

# ---- 右：一次交换的放大图 ----
c = 0.062
ay, by = 0.645, 0.335
ax_cells = [0.585, 0.647, 0.709, 0.771]
bx_cells = [0.709, 0.771, 0.833, 0.895]
for i, x in enumerate(ax_cells):
    is_ghost = (i == 3)
    ax.add_patch(Rectangle((x, ay), c, 0.085, facecolor=ghost if is_ghost else SOFT[1],
                           edgecolor=INK, lw=0.8, zorder=3))
for i, x in enumerate(bx_cells):
    is_ghost = (i == 0)
    ax.add_patch(Rectangle((x, by), c, 0.085, facecolor=ghost if is_ghost else SOFT[2],
                           edgecolor=INK, lw=0.8, zorder=3))
label(ax, ax_cells[0], ay + 0.115, "进程 A 的局部数组", fs=7.8, color=MUTED, ha="left")
label(ax, bx_cells[-1] + c, by - 0.045, "进程 B 的局部数组", fs=7.8, color=MUTED,
      ha="right")

# 两条交换箭头
arrow(ax, (0.709 + c / 2, ay - 0.004), (0.709 + c / 2, by + 0.089), color=BLUE,
      lw=1.1, ms=9)
arrow(ax, (0.771 + c / 2, by + 0.089), (0.771 + c / 2, ay - 0.004), color=ACCENT,
      lw=1.1, ms=9)
label(ax, 0.709 - 0.014, 0.505, "A 的边界列\n发给 B 的幽灵格", fs=7.4, color=BLUE,
      ha="right", va="center")
label(ax, 0.833 + 0.014, 0.505, "B 的边界列\n发给 A 的幽灵格", fs=7.4, color=ACCENT,
      ha="left", va="center")
label(ax, 0.575, 0.20, "同一列数据在两边各存一份：\n交换之后两边都能算出与邻居相接的那一层",
      fs=7.6, color=MUTED, ha="left")
label(ax, 0.575, 0.955, "(b) 一个界面上一对边界列的交换", fs=8.6, color=INK, ha="left")

save(fig, "10", "fig10-01")


# ============================================================
# 图 10-2  强/弱扩展效率（按模型计算，非实测）
#   强：T = 100/P + 20*P^(-2/3) + 0.5
#   弱：T = 100 + 6 + 0.6*P^(1/3) + 100*P/2048
# ============================================================
P = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], dtype=float)

T_strong = 100.0 / P + 20.0 * P ** (-2.0 / 3.0) + 0.5
T_strong[0] = 100.0                      # P=1 时没有交换
E_strong = T_strong[0] / (P * T_strong)

T_weak = 100.0 + 6.0 + 0.6 * P ** (1.0 / 3.0) + 100.0 * P / 2048.0
T_weak[0] = 100.0
E_weak = T_weak[0] / T_weak

fig, ax = plt.subplots(figsize=(6.5, 3.5))
clean(ax, grid=True)
ax.set_xscale("log", base=2)
ax.set_xticks([1, 4, 16, 64, 256, 1024])
ax.set_xticklabels(["1", "4", "16", "64", "256", "1024"])
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)

ax.plot(P, E_strong, color=ACCENT, marker="o", ms=4.2, lw=1.5, mfc="white", mew=1.1,
        label="强扩展（总量固定）", zorder=4)
ax.plot(P, E_weak, color=BLUE, marker="s", ms=4.0, lw=1.5, mfc="white", mew=1.1,
        label="弱扩展（每进程工作量固定）", zorder=4)

ax.set_xlabel("进程数 $P$")
ax.set_ylabel("并行效率 $E$")
ax.set_ylim(0.08, 1.07)
ax.set_xlim(0.85, 1200)
leg = ax.legend(loc="lower left", fontsize=8.4, handlelength=2.4, borderaxespad=0.8)
for t in leg.get_texts():
    t.set_color(INK)

# 关键点的数值标注
ann = [("0.47", 64, E_strong[6], (12, 7), ACCENT, "left"),
       ("0.28", 256, E_strong[8], (14, 5), ACCENT, "left"),
       ("0.82", 256, E_weak[8], (0, 11), BLUE, "center"),
       ("0.62", 1024, E_weak[10], (-8, -13), BLUE, "right")]
for s, p, e, off, col, ha in ann:
    ax.annotate(s, xy=(p, e), xytext=off, textcoords="offset points", fontsize=8.0,
                color=col, ha=ha, va="center")

fig.subplots_adjust(left=0.105, right=0.975, top=0.965, bottom=0.155)
save(fig, "10", "fig10-02")

print("P      E_strong  E_weak")
for p, es, ew in zip(P, E_strong, E_weak):
    print(f"{int(p):5d}  {es:8.3f}  {ew:7.3f}")
