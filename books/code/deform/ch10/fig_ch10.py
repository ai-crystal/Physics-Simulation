import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from scipy.spatial import cKDTree

# ============================================================
# 图 10-1  断裂方法谱系（分类示意）
# ============================================================
fig, ax = canvas(6.9, 3.7)

# ---- 两条分类轴 ----
arrow(ax, (0.045, 0.500), (0.968, 0.500), color=INK, lw=1.1, ms=10)
arrow(ax, (0.500, 0.052), (0.500, 0.948), color=INK, lw=1.1, ms=10)

label(ax, 0.045, 0.512, "破坏路径在运行时决定", fs=8.2, color=MUTED, ha="left", va="bottom")
label(ax, 0.955, 0.512, "路径提前给定", fs=8.2, color=MUTED, ha="right", va="bottom")
label(ax, 0.500, 0.030, "求解对象：体网格", fs=8.2, color=MUTED, ha="center", va="center")
label(ax, 0.500, 0.972, "求解对象：裂纹面", fs=8.2, color=MUTED, ha="center", va="center")

# ---- 四个象限 ----
cells = [
    # (x0, y0, w, h, 边框色, 底色, 成本, 方法行, 说明)
    (0.045, 0.062, 0.417, 0.348, BLUE, "#EFF4FF", "成本 低",
     ["单元删除", "虚拟节点", "内聚力界面"],
     "改网格或界面，裂纹受单元约束"),
    (0.045, 0.590, 0.417, 0.348, GREEN, "#ECFDF5", "成本 高",
     ["边界元 BEM", "扩展有限元"],
     "只离散裂纹面，形状自由但最贵"),
    (0.538, 0.062, 0.417, 0.348, ACCENT, "#FDF6EC", "成本 低",
     ["Voronoi 预碎片"],
     "碎片当刚体，连接断了就分开"),
    (0.538, 0.590, 0.417, 0.348, PURPLE, "#F5F3FF", "成本 很低",
     ["预制裂纹面"],
     "几何阶段切好，模拟只断连接"),
]

for x0, y0, w, h, ec, fc, cost, rows, note in cells:
    box(ax, x0, y0, w, h, "", fc=fc, ec=ec, lw=1.0, rounded=0.014)
    label(ax, x0 + 0.016, y0 + h - 0.016, cost, fs=7.5, color=ec, ha="left", va="top")
    ytop = y0 + h - 0.086
    for k, s in enumerate(rows):
        label(ax, x0 + w / 2, ytop - k * 0.068, s, fs=8.6, color=INK, ha="center", va="center")
    label(ax, x0 + 0.016, y0 + 0.022, note, fs=7.3, color=MUTED, ha="left", va="bottom")

save(fig, "10", "fig10-01")


# ============================================================
# 图 10-2  Voronoi 预碎片的尺寸分布（真实计算）
# ============================================================
rng = np.random.default_rng(7)
N = 200
S = rng.random((N, 2))                     # 1 m x 1 m 内的种子

# ---- 面积：细网格最近邻归属 ----
M = 1100
g = (np.arange(M) + 0.5) / M
GX, GY = np.meshgrid(g, g, indexing="ij")
P = np.column_stack([GX.ravel(), GY.ravel()])
tree = cKDTree(S)
lab = tree.query(P, k=1)[1]
lab2 = lab.reshape(M, M)
cnt = np.bincount(lab, minlength=N).astype(float)
area = cnt / M ** 2                        # 单位 m^2
d = np.sqrt(4.0 * area / np.pi)            # 等效直径，单位 m

# ---- 边：最近与次近距离差为零的等值线 ----
Mc = 600
gc = (np.arange(Mc) + 0.5) / Mc
CX, CY = np.meshgrid(gc, gc, indexing="ij")
dist = tree.query(np.column_stack([CX.ravel(), CY.ravel()]), k=2)[0]
diff = (dist[:, 1] - dist[:, 0]).reshape(Mc, Mc)

fig, axes = new(6.9, 3.15, ncols=2, gridspec_kw={"width_ratios": [1.0, 1.22], "wspace": 0.30})
axa, axb = axes

# ---- 左：胞结构 ----
axa.contour(g, g, lab2, levels=np.arange(0.5, N, 1.0), colors=[SLATE],
            linewidths=0.4, antialiased=True, zorder=2)
axa.plot(S[:, 0], S[:, 1], ".", ms=1.3, color=ACCENT, alpha=0.85, zorder=4)
axa.set_xlim(0, 1)
axa.set_ylim(0, 1)
axa.set_aspect("equal")
axa.set_xticks([])
axa.set_yticks([])
for s in ("top", "right", "left", "bottom"):
    axa.spines[s].set_visible(True)
    axa.spines[s].set_color("#9CA3AF")
    axa.spines[s].set_linewidth(0.8)

# 比例尺
axa.plot([-0.005, 0.195], [-0.072, -0.072], color=INK, lw=1.8,
         solid_capstyle="butt", zorder=6, clip_on=False)
axa.plot([-0.005, -0.005], [-0.078, -0.066], color=INK, lw=1.0, clip_on=False)
axa.plot([0.195, 0.195], [-0.078, -0.066], color=INK, lw=1.0, clip_on=False)
axa.text(0.095, -0.094, "20 cm", fontsize=7.6, color=MUTED, ha="center", va="top",
         clip_on=False)

# ---- 右：尺寸分布 ----
dc = d * 100.0                             # cm
bw = 0.7
bins = np.arange(dc.min() - bw / 2, dc.max() + bw, bw)
axb.hist(dc, bins=bins, color=ACCENT, alpha=0.28, edgecolor=ACCENT, lw=0.8,
         zorder=2, label="胞的实测分布")

mu = np.mean(np.log(dc))
sig = np.std(np.log(dc), ddof=1)
xs = np.linspace(dc.min() * 0.85, dc.max() * 1.10, 400)
from math import exp
pdf = np.exp(-(np.log(xs) - mu) ** 2 / (2 * sig ** 2)) / (xs * sig * np.sqrt(2 * np.pi))
axb.plot(xs, pdf * N * bw, color=BLUE, lw=1.7, zorder=3,
         label="对数正态拟合")

med = exp(mu)
axb.axvline(med, color=GREEN, lw=1.0, ls=(0, (4, 3)), zorder=3)
axb.text(med + 0.5, 39.4, "中位数 %.1f cm" % med,
         fontsize=7.8, color=GREEN, ha="left", va="center")

axb.set_xlabel("等效直径 $d=\\sqrt{4A/\\pi}$（cm）")
axb.set_ylabel("胞数")
axb.set_xlim(2.0, 13.4)
axb.set_ylim(0, 44)
clean(axb, grid=True)
axb.legend(loc="upper left", fontsize=8.0, handlelength=1.4, borderpad=0.25)

save(fig, "10", "fig10-02")
