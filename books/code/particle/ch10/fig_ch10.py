import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np

# fig10-01 -------------------------------------------------------------
fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.9, 3.2),
                               gridspec_kw={"width_ratios": [1.0, 1.12], "wspace": 0.08})
axL.set_xlim(0, 1); axL.set_ylim(0, 1); axL.set_aspect("equal"); axL.axis("off")
axR.set_xlim(0, 1); axR.set_ylim(0, 1); axR.axis("off")

n = 8
x0, y0, W = 0.06, 0.10, 0.88
h = W / n
ci, cj = 3, 3           # 中心格（列、行，从 0 计）
R = 0.055

# 27（二维 9）格邻域填色
for i in range(ci - 1, ci + 2):
    for j in range(cj - 1, cj + 2):
        axL.add_patch(Rectangle((x0 + i * h, y0 + j * h), h, h,
                                fc="#F6EBD7" if (i, j) != (ci, cj) else "#E8C88C",
                                ec="none", zorder=1))
grid(axL, x0, y0, W, W, n, n, color="#D8D3C8", lw=0.7)
axL.add_patch(Rectangle((x0, y0), W, W, fill=False, ec=MUTED, lw=0.9, zorder=4))

rng = np.random.default_rng(4)
pts = []
for i in range(n):
    for j in range(n):
        k = rng.integers(0, 3)
        for _ in range(k):
            pts.append((x0 + (i + rng.uniform(0.18, 0.82)) * h,
                        y0 + (j + rng.uniform(0.18, 0.82)) * h))
pts = np.array(pts)
mc = np.array([x0 + (ci + 0.5) * h, y0 + (cj + 0.5) * h])
pts = pts[np.hypot(pts[:, 0] - mc[0], pts[:, 1] - mc[1]) > 1.6 * R]

cx = x0 + (ci + 0.5) * h
cy = y0 + (cj + 0.5) * h
axL.add_patch(Circle((cx, cy), 2 * R, fill=False, ec=BLUE, lw=1.1, ls=(0, (3, 2)), zorder=5))
for p in pts:
    inside = abs(p[0] - cx) < 2 * R and abs(p[1] - cy) < 2 * R
    axL.add_patch(Circle(p, R * 0.52, fc="white", ec=FAINT, lw=0.6, zorder=2))
for p in pts:
    if np.hypot(p[0] - cx, p[1] - cy) < 2 * R:
        axL.plot([cx, p[0]], [cy, p[1]], color=ACCENT, lw=0.7, alpha=0.85, zorder=6)
axL.add_patch(Circle((cx, cy), R * 0.62, fc=BLUE, ec="white", lw=0.6, zorder=7))
label(axL, cx, cy - 2 * R - 0.055, r"$2r$", fs=8.6, color=BLUE)

# 右侧：计数排序的三条数组
cells = [2, 0, 3, 1, 5, 0, 4, 2, 0, 1, 3, 2]
nc = len(cells)
bx0, bw, gap = 0.16, 0.055, 0.006
rows_y = [0.74, 0.50, 0.22]
label(axR, bx0, rows_y[0] + 0.135, "每格颗数", fs=8.6, color=MUTED, ha="left")
label(axR, bx0, rows_y[1] + 0.135, "前缀和得到的起始下标", fs=8.6, color=MUTED, ha="left")
label(axR, bx0, rows_y[2] + 0.135, "按格排好的编号", fs=8.6, color=MUTED, ha="left")

offs = np.concatenate([[0], np.cumsum(cells)[:-1]])
for k in range(nc):
    axR.add_patch(Rectangle((bx0 + k * (bw + gap), rows_y[0]), bw, 0.085,
                            fc="#FCFCFB", ec=FAINT, lw=0.7, zorder=3))
    label(axR, bx0 + k * (bw + gap) + bw / 2, rows_y[0] + 0.042, str(cells[k]), fs=8.4, color=INK)
    axR.add_patch(Rectangle((bx0 + k * (bw + gap), rows_y[1]), bw, 0.085,
                            fc="#FCFCFB", ec=FAINT, lw=0.7, zorder=3))
    label(axR, bx0 + k * (bw + gap) + bw / 2, rows_y[1] + 0.042, str(offs[k]), fs=8.4, color=MUTED)

# 排序后的编号条：按格分组着色
group_edges = np.concatenate([[0], np.cumsum(cells)])
tw = (0.78) / group_edges[-1]
cols = ["#E7CFA4", "#CFE0F3"]
for k in range(nc):
    a, b = group_edges[k], group_edges[k + 1]
    for t in range(a, b):
        axR.add_patch(Rectangle((bx0 + t * tw, rows_y[2]), tw * 0.94, 0.075,
                                fc=cols[k % 2], ec="white", lw=0.6, zorder=3))
label(axR, bx0, rows_y[2] - 0.075, "同一格的编号连续存放，邻居可以一次读完",
      fs=8.2, color=MUTED, ha="left")
arrow(axR, (bx0 + 0.60, rows_y[0] - 0.005), (bx0 + 0.60, rows_y[1] + 0.095),
      color=FAINT, lw=0.8, ms=7)
save(fig, "10", "fig10-01")

# fig10-02 -------------------------------------------------------------
N = np.logspace(5, 8, 400)
s, fps, k = 4, 60.0, 32
b_naive = 48 + k * 24          # 816 B
b_tile = 48 + k * 3            # 144 B
B1 = s * fps * N * b_naive / 1e9      # GB/s
B2 = s * fps * N * b_tile / 1e9

fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.loglog(N, B1, color=ACCENT, lw=1.9, zorder=4)
ax.loglog(N, B2, color=BLUE, lw=1.9, zorder=4)
ax.axhline(1000, color=MUTED, lw=1.0, ls=(0, (5, 3)), zorder=2)
ax.axhline(3000, color=INK, lw=1.0, ls=(0, (1, 2)), zorder=2)
ax.set_xlim(1e5, 1e8)
ax.set_ylim(3, 6e4)
ax.set_xlabel("颗粒数 N")
ax.set_ylabel("所需显存带宽 (GB/s)")
clean(ax, grid=True)

label(ax, 1.15e5, 1080, "1 TB/s", fs=8.2, color=MUTED, ha="left", va="bottom")
label(ax, 1.15e5, 3250, "3 TB/s", fs=8.2, color=INK, ha="left", va="bottom")

n1 = 1e12 / (s * fps * b_naive)
n2 = 1e12 / (s * fps * b_tile)
ax.plot([n1], [1000], "o", ms=5.4, mfc="white", mec=ACCENT, mew=1.4, zorder=6)
ax.plot([n2], [1000], "o", ms=5.4, mfc="white", mec=BLUE, mew=1.4, zorder=6)
ax.annotate("500 万颗", xy=(n1, 1000), xytext=(1.2e6, 3900),
            fontsize=8.4, color=ACCENT, ha="left", va="bottom",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7, shrinkA=2, shrinkB=4))
ax.annotate("2900 万颗", xy=(n2, 1000), xytext=(1.1e7, 150),
            fontsize=8.4, color=BLUE, ha="left", va="top",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7, shrinkA=2, shrinkB=4))

label(ax, 1.15e5, 4.4e4, "每对接触直接读显存\n816 B/颗/子步", fs=8.4,
      color=ACCENT, ha="left", va="top")
label(ax, 1.3e6, 13.5, "分块到共享内存\n144 B/颗/子步", fs=8.4,
      color=BLUE, ha="left", va="top")
save(fig, "10", "fig10-02")
