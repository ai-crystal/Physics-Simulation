import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 5-1  force-gap 平面上的互补分区（示意）
# 横轴 = 法向冲量，纵轴 = 间隙
# ============================================================
fig, ax = plt.subplots(figsize=(6.6, 4.1))
fig.subplots_adjust(left=0.105, right=0.97, bottom=0.13, top=0.97)
ax.set_xlim(-1.05, 1.72)
ax.set_ylim(-0.60, 1.50)
clean(ax, spines=("left", "bottom"))

# 三个区域
ax.add_patch(Rectangle((0, 0), 1.72, 1.50, facecolor="#FDF2E9", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((-1.05, -0.60), 2.77, 0.60, facecolor="#EFF4FF", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((-1.05, 0), 1.05, 1.50, facecolor="#F3F4F6", edgecolor="none", zorder=0))

ax.text(1.64, 1.34, "λ 大于 0 且 g 大于 0：隔空发力", fontsize=8.4, color=ACCENT,
        ha="right", va="center", zorder=6)
ax.text(-0.55, -0.31, "g 小于 0：还在穿透\n（残差没消完）", fontsize=8.4, color=BLUE,
        ha="center", va="center", zorder=6)
ax.text(-0.60, 0.99, "λ 小于 0：接触不能拉", fontsize=8.4, color=MUTED,
        ha="center", va="center", zorder=6)

# 可行集：两条半轴
ax.plot([0, 1.72], [0, 0], color=INK, lw=3.2, solid_capstyle="round", zorder=4)
ax.plot([0, 0], [0, 1.50], color=INK, lw=3.2, solid_capstyle="round", zorder=4)
ax.annotate("", xy=(1.72, 0), xytext=(1.57, 0),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=3.2, mutation_scale=15), zorder=5)
ax.annotate("", xy=(0, 1.50), xytext=(0, 1.35),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=3.2, mutation_scale=15), zorder=5)

ax.text(1.60, 0.075, "贴住：g = 0，λ 大于 0", fontsize=8.8, color=INK, ha="right", va="bottom")
ax.text(-0.06, 1.33, "分离：λ = 0，g 大于 0", fontsize=8.8, color=INK, ha="right", va="center")

# 情形一：不加力时已经分开，g0 = 0.35，k = 0.5（g = g0 + k λ）
lam1 = np.linspace(-0.70, 1.20, 400)
g1 = 0.35 + 0.5 * lam1
m = lam1 >= 0
ax.plot(lam1[m], g1[m], color=GOLD, lw=1.9, zorder=5)
ax.plot(lam1[~m], g1[~m], color=GOLD, lw=1.2, ls=(0, (4, 3)), zorder=4)
ax.plot([0.0], [0.35], "o", ms=6.8, mfc="white", mec=GOLD, mew=1.8, zorder=7)
ax.annotate("无约束解落在负 λ 上：\n截到 0，解回到 g 轴",
            xy=(-0.36, 0.15), xytext=(-0.98, 0.56),
            fontsize=8.3, color=GOLD, ha="left", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.9, shrinkA=3, shrinkB=4,
                            connectionstyle="arc3,rad=-0.15"), zorder=8)

# 情形二：不加力时已经穿透，g0 = -0.2，解落在 λ 轴上的 0.4
lam2 = np.linspace(0.0, 1.45, 300)
g2 = -0.20 + 0.5 * lam2
ax.plot(lam2, g2, color=GREEN, lw=1.9, zorder=5)
ax.plot([0], [-0.20], "o", ms=5, mfc="white", mec=GREEN, mew=1.5, zorder=7)
ax.plot([0.40], [0], "o", ms=6.8, mfc="white", mec=GREEN, mew=1.8, zorder=7)
ax.annotate("约束线 $g = g_0 + k\\lambda$\n截距为负：解在 λ 轴上",
            xy=(0.43, -0.05), xytext=(0.52, -0.55),
            fontsize=8.3, color=GREEN, ha="left", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9, shrinkA=3, shrinkB=4),
            zorder=8)

ax.set_xlabel("法向冲量 $\\lambda$", fontsize=9.6, labelpad=6)
ax.set_ylabel("间隙 $g$（速度层中就是法向相对速度 $w$）", fontsize=9.6, labelpad=6)
ax.axhline(0, color=FAINT, lw=0.8, zorder=1)
ax.axvline(0, color=FAINT, lw=0.8, zorder=1)
ax.set_xticks([-1.0, -0.5, 0, 0.5, 1.0, 1.5])
ax.set_yticks([-0.4, 0, 0.4, 0.8, 1.2])
ax.text(1.70, -0.035, "$\\lambda$", fontsize=9.4, color=INK, ha="left", va="top")
ax.text(-0.05, 1.48, "$g$", fontsize=9.4, color=INK, ha="right", va="top")

save(fig, "05", "fig05-01")


# ============================================================
# 图 5-2  三层堆叠的 PGS 残差（真实计算）
# ============================================================
g = 9.81
dt = 1.0 / 60.0


def build(n, m=1.0):
    """n 个 m 公斤的箱子竖直摞在无穷质量的地面上；contact 0 是地面与底箱。"""
    A = np.zeros((n, n))
    b = np.zeros(n)
    inv = 1.0 / m
    for j in range(n):
        A[j, j] += inv
        if j >= 1:
            A[j, j] += inv
            A[j, j - 1] -= inv
        if j + 1 < n:
            A[j, j + 1] -= inv
    b[0] = -g * dt                       # 一步重力后的相对法向速度
    return A, b


def pgs(A, b, iters):
    n = len(b)
    lam = np.zeros(n)
    hist = []
    for _ in range(iters + 1):
        w = A @ lam + b
        hist.append(np.max(np.abs(np.minimum(lam, w))))
        for j in range(n):                                # 自下而上扫一遍
            s = b[j] + A[j] @ lam - A[j, j] * lam[j]
            lam[j] = max(0.0, -s / A[j, j])
    return np.array(hist)


NIT = 80
res = {n: pgs(*build(n), NIT) for n in (2, 3, 5, 10)}

fig, ax = plt.subplots(figsize=(6.6, 3.9))
fig.subplots_adjust(left=0.115, right=0.97, bottom=0.145, top=0.95)
style = {2: (BLUE, 1.5, "两层  ×0.5"), 3: (ACCENT, 2.4, "三层  ×0.75"),
         5: (GREEN, 1.5, "五层  ×0.88"), 10: (PURPLE, 1.5, "十层  ×0.94")}
for n in (10, 5, 2, 3):
    c, lw, lab = style[n]
    y = np.maximum(res[n], 1e-17)
    ax.semilogy(np.arange(NIT + 1), y, color=c, lw=lw, label=lab, zorder=4 if n == 3 else 3)

ax.axhline(1e-3, color=FAINT, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.text(57, 1.30e-3, "常用容差 1e-3 m/s", fontsize=8.2, color=MUTED, ha="left", va="bottom")

ax.set_xlim(0, NIT)
ax.set_ylim(1e-13, 4e-1)
ax.set_xlabel("迭代轮次", fontsize=9.6)
ax.set_ylabel("残差 $r=\\max_j|\\min(\\lambda_j,\\ w_j)|$（m/s）", fontsize=9.6)
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
clean(ax)

hs, ls_ = ax.get_legend_handles_labels()
order = ["两层", "三层", "五层", "十层"]
idx = [next(i for i, lab in enumerate(ls_) if lab.startswith(o)) for o in order]
ax.legend([hs[i] for i in idx], [ls_[i] for i in idx], loc="upper right", ncol=2,
          handlelength=1.5, columnspacing=1.2, labelspacing=0.45,
          bbox_to_anchor=(1.008, 1.04))

i17 = 17
ax.plot([i17], [res[3][i17]], "o", ms=5.5, mfc="white", mec=ACCENT, mew=1.6, zorder=6)
ax.text(i17 + 0.7, 3.2e-4, "17 轮", fontsize=8.2, color=ACCENT, ha="left", va="top")

save(fig, "05", "fig05-02")
