import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 2-1  AoS 与 SoA 的访存（示意，字节数由记录大小与缓存行算出）
#   记录 36 B（位置 12、速度 12、其余 12），缓存行 64 B
#   64 B 行装 64/36 = 1.78 条记录，其中位置 1.78*12 = 21.3 B
# ============================================================
REC, LINE = 36, 64
S = 0.0030                     # 每字节对应的画布宽度

C_POS, C_VEL, C_OTH = "#CFE0FF", "#CFEFDC", "#FBE7C6"

fig, ax = canvas(6.9, 4.4)


def bar(x0, y, n, fields):
    x = x0
    for i in range(n):
        for nb, c in zip(fields, (C_POS, C_VEL, C_OTH)):
            ax.add_patch(Rectangle((x, y), nb * S, 0.055, facecolor=c,
                                   edgecolor=INK, lw=0.45, zorder=3))
            x += nb * S


def clines(x0, y0, y1, n):
    for k in range(1, n):
        ax.plot([x0 + k * LINE * S] * 2, [y0, y1], color=FAINT, lw=0.8,
                ls=(0, (3, 3)), zorder=4)


# ---------- 上：AoS ----------
x0, yA = 0.085, 0.792
bar(x0, yA, 6, (12, 12, 12))
clines(x0, yA - 0.017, yA + 0.072, 4)
label(ax, x0, 0.943, "AoS：位置、速度、其余字段交错在一条记录里", fs=9.4,
      ha="left", weight="bold")

dim_arrow(ax, (x0, 0.882), (x0 + LINE * S, 0.882), "64 B", fs=8.0, off=0.015)
ax.annotate("", xy=(x0, yA - 0.017), xytext=(x0 + REC * S, yA - 0.017),
            arrowprops=dict(arrowstyle="<|-|>", color=ACCENT, lw=0.9, mutation_scale=7))
label(ax, x0 + REC * S / 2, yA - 0.044, "36 B", fs=8.2, color=ACCENT)

label(ax, 0.748, yA + 0.044, "一行装 1.78 条记录", fs=8.3, ha="left")
label(ax, 0.748, yA + 0.008, "只取位置时", fs=8.3, ha="left", color=MUTED)
label(ax, 0.748, yA - 0.024, "21 / 64 字节有用", fs=8.3, ha="left", color=MUTED)

# ---------- 下：SoA ----------
xB = 0.130
label(ax, 0.085, 0.668, "SoA：每个字段一个数组", fs=9.4, ha="left", weight="bold")

rows = [(0.518, "位置", 12, C_POS), (0.433, "速度", 12, C_VEL), (0.348, "其余", 12, C_OTH)]
for y, name, nb, col in rows:
    ax.add_patch(Rectangle((xB, y), 6 * nb * S, 0.052, facecolor=col,
                           edgecolor=INK, lw=0.45, zorder=3))
    for k in range(1, 6):
        ax.plot([xB + k * nb * S] * 2, [y, y + 0.052], color=MUTED, lw=0.35, zorder=4)
    label(ax, xB - 0.012, y + 0.026, name, fs=8.3, ha="right")

clines(xB, 0.518 - 0.016, 0.518 + 0.068, 2)
dim_arrow(ax, (xB, 0.615), (xB + LINE * S, 0.615), "64 B", fs=8.0, off=0.015)
label(ax, xB + LINE * S + 0.028, 0.601, "16 个浮点 = 5.33 个粒子的坐标",
      fs=8.3, ha="left", color=MUTED)

# ---------- 底部说明 ----------
label(ax, 0.085, 0.248, "同样取 6 个粒子的位置：AoS 取回 4 行 256 B，SoA 取回 2 行 128 B",
      fs=8.5, ha="left", color=INK)
label(ax, 0.085, 0.212, "色块宽度按字节数画，深色边框是记录内部字段的分界",
      fs=8.0, ha="left", color=FAINT)
legend_row(ax, [(C_POS, "位置 12 B"), (C_VEL, "速度 12 B"), (C_OTH, "密度压力编号 12 B")],
           x=0.470, y=0.300, dy=0.055, fs=8.2, sw=0.020, sh=0.020)

save(fig, "02", "fig02-01")


# ============================================================
# 图 2-2  同一操作在两种布局下的访存（真实计算：按缓存行取整计数）
#   N = 10^6 个粒子，记录 36 B：位置 12、速度 12、密度 4、压力 4、编号 4
# ============================================================
N = 1000000
LINE_B = 64
REC_B = 36


def fetch(nbytes):
    """按整条缓存行取回，返回字节数。"""
    return -(-nbytes // LINE_B) * LINE_B


ops = [
    ("邻域搜索\n只读位置", N * 12, N * REC_B),
    ("积分\n读写位置与速度", 4 * N * 12, 2 * N * REC_B),
    ("统计\n只读密度与压力", N * 8, N * REC_B),
    ("归档\n读写全部字段", N * REC_B, N * REC_B),
]

soa_vals = [fetch(a) / 1e6 for _, a, _ in ops]
aos_vals = [fetch(b) / 1e6 for _, _, b in ops]

fig, ax = plt.subplots(figsize=(6.7, 3.9))
clean(ax, grid=True, spines=("left", "bottom"))
ax.grid(axis="y")

x = np.arange(len(ops))
w = 0.32
ax.bar(x - w / 2, aos_vals, w, color=ACCENT, edgecolor="white", lw=0.8,
       zorder=3, label="AoS（36 B 记录交错）")
ax.bar(x + w / 2, soa_vals, w, color=TEAL, edgecolor="white", lw=0.8,
       zorder=3, label="SoA（每字段一个数组）")

for xi, v in zip(x - w / 2, aos_vals):
    ax.text(xi, v + 1.8, f"{v:.0f}", ha="center", va="bottom", fontsize=8.3, color=ACCENT)
for xi, v in zip(x + w / 2, soa_vals):
    ax.text(xi, v + 1.8, f"{v:.0f}", ha="center", va="bottom", fontsize=8.3, color=TEAL)

for xi, a, s in zip(x, aos_vals, soa_vals):
    ax.text(xi, max(a, s) + 9.0, f"{a / s:.1f}×", ha="center", va="bottom",
            fontsize=9.0, color=INK)

ax.set_xticks(x)
ax.set_xticklabels([o[0] for o in ops], fontsize=8.6, linespacing=1.6)
ax.set_ylabel("取回字节数（MB）")
ax.set_ylim(0, 96)
ax.set_yticks([0, 20, 40, 60, 80])
ax.set_xlim(-0.6, len(ops) - 0.4)
ax.legend(loc="upper right", bbox_to_anchor=(0.995, 0.995), fontsize=8.4,
          handlelength=1.4, labelspacing=0.35)

save(fig, "02", "fig02-02")
print("AoS MB:", [f"{v:.1f}" for v in aos_vals])
print("SoA MB:", [f"{v:.1f}" for v in soa_vals])
print("ratio:", [f"{a/s:.2f}" for a, s in zip(aos_vals, soa_vals)])
