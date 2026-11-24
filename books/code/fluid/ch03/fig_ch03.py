import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 3-1  三种泊松求解器的残差收敛（真实计算）
#   64x64 网格，Dirichlet 边界，五点拉普拉斯
#   右端项：两个高斯源之差，模拟平流后残留的散度
# ============================================================
N = 64
h = 1.0 / (N + 1)
x = np.linspace(h, 1 - h, N)
X, Y = np.meshgrid(x, x, indexing="ij")
b = -(np.exp(-((X - 0.35) ** 2 + (Y - 0.40) ** 2) / 0.012)
      - np.exp(-((X - 0.70) ** 2 + (Y - 0.65) ** 2) / 0.020))
b /= np.abs(b).max()
nb = np.linalg.norm(b)


def lap(p):
    q = np.zeros((N + 2, N + 2))
    q[1:-1, 1:-1] = p
    return (q[2:, 1:-1] + q[:-2, 1:-1] + q[1:-1, 2:] + q[1:-1, :-2] - 4 * p) / h ** 2


def resid(p):
    return np.linalg.norm((b - lap(p)).ravel()) / nb


# --- Jacobi ---
p = np.zeros((N, N))
hist_j = [resid(p)]
for _ in range(800):
    q = np.zeros((N + 2, N + 2))
    q[1:-1, 1:-1] = p
    p = 0.25 * (q[2:, 1:-1] + q[:-2, 1:-1] + q[1:-1, 2:] + q[1:-1, :-2] - h * h * b)
    hist_j.append(resid(p))

# --- Gauss-Seidel（红黑排序） ---
q = np.zeros((N + 2, N + 2))
ii, jj = np.indices((N, N))
red = ((ii + jj) % 2 == 0)
hist_g = [resid(q[1:-1, 1:-1])]
for _ in range(800):
    for color in (True, False):
        nb4 = 0.25 * (q[0:N, 1:N + 1] + q[2:N + 2, 1:N + 1]
                      + q[1:N + 1, 0:N] + q[1:N + 1, 2:N + 2])
        q[1:-1, 1:-1] = np.where(red == color, nb4 - 0.25 * h * h * b, q[1:-1, 1:-1])
    hist_g.append(resid(q[1:-1, 1:-1]))

# --- 共轭梯度：解 -A p = -b，M = -A 对称正定 ---
def M(v):
    return (-lap(v.reshape(N, N))).ravel()


rhs = -b.ravel()
p = np.zeros(N * N)
r = rhs - M(p)
d = r.copy()
rs = r @ r
hist_c = [np.linalg.norm(M(p) - rhs) / nb]
for _ in range(250):
    Md = M(d)
    al = rs / (d @ Md)
    p = p + al * d
    r = r - al * Md
    rs2 = r @ r
    hist_c.append(np.sqrt(rs2) / nb)
    d = r + (rs2 / rs) * d
    rs = rs2

hist_j = np.array(hist_j); hist_g = np.array(hist_g); hist_c = np.array(hist_c)
print("Jacobi  800 步残差 %.4f" % hist_j[-1])
print("GS      800 步残差 %.4f" % hist_g[-1])
print("CG      200 步残差 %.2e，%d 步残差 %.2e" % (hist_c[200], len(hist_c) - 1, hist_c[-1]))

fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.semilogy(np.arange(len(hist_j)), hist_j, color=ACCENT, lw=1.5,
            label="Jacobi（800 步，$0.08$）")
ax.semilogy(np.arange(len(hist_g)), hist_g, color=BLUE, lw=1.5,
            label="Gauss–Seidel（800 步，$0.023$）")
ax.semilogy(np.arange(201), hist_c[:201], color=GREEN, lw=1.7,
            label="共轭梯度（200 步，$2\\times10^{-9}$）")
ax.axhline(1e-3, color=FAINT, lw=0.8, ls=(0, (5, 4)), zorder=1)
ax.text(575, 4.0e-3, "常用容差 $10\^{-3}$", fontsize=8.2, color=MUTED,
        ha="left", va="bottom")

ax.set_xlim(0, 830)
ax.set_ylim(1e-10, 1.6)
ax.set_xlabel("迭代次数")
ax.set_ylabel("相对残差")
ax.set_xticks([0, 200, 400, 600, 800])
clean(ax, grid=True)
ax.legend(loc="center right", bbox_to_anchor=(0.995, 0.30), handlelength=2.0,
          borderaxespad=0.0, labelspacing=0.55)
ax.text(0.995, 0.02, "64×64 网格 · Dirichlet 边界 · 高斯源", fontsize=7.6, color=FAINT,
        ha="right", va="bottom", transform=ax.transAxes)
save(fig, "03", "fig03-01")

# ============================================================
# 图 3-2  MAC 网格：压力在格心，速度在面上（示意图）
# ============================================================
fig, ax = plt.subplots(figsize=(6.6, 3.5))
ax.set_xlim(0, 1)
ax.set_ylim(0, 0.465)
ax.axis("off")

nx, ny = 4, 3
cw, chh = 0.082, 0.082
x0, y0 = 0.062, 0.082
gw, gh = nx * cw, ny * chh
hc = (1, 1)                      # 被放大的格子

ax.add_patch(Rectangle((x0, y0), gw, gh, facecolor="#F6F8FB", edgecolor="none", zorder=0))
for i in range(nx + 1):
    ax.plot([x0 + i * cw, x0 + i * cw], [y0, y0 + gh], color="#D5DAE2", lw=0.8, zorder=1)
for j in range(ny + 1):
    ax.plot([x0, x0 + gw], [y0 + j * chh, y0 + j * chh], color="#D5DAE2", lw=0.8, zorder=1)

ax.add_patch(Rectangle((x0 + hc[0] * cw, y0 + hc[1] * chh), cw, chh,
                       facecolor="#FDF2E9", edgecolor=ACCENT, lw=1.0, zorder=2))

for i in range(nx + 1):
    for j in range(ny):
        xf, yf = x0 + i * cw, y0 + (j + 0.5) * chh
        ax.annotate("", xy=(xf + 0.023, yf), xytext=(xf, yf),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.9,
                                    shrinkA=0, shrinkB=0, mutation_scale=6), zorder=3)
for i in range(nx):
    for j in range(ny + 1):
        xf, yf = x0 + (i + 0.5) * cw, y0 + j * chh
        ax.annotate("", xy=(xf, yf + 0.021), xytext=(xf, yf),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9,
                                    shrinkA=0, shrinkB=0, mutation_scale=6), zorder=3)

for i in range(nx):
    for j in range(ny):
        ax.scatter([x0 + (i + 0.5) * cw], [y0 + (j + 0.5) * chh], s=13, color=INK,
                   zorder=4, linewidths=0)

label(ax, x0 - 0.010, 0.435, "(a) 网格上的存放位置", fs=8.8, color=MUTED,
      ha="left", va="center")

# 图例
lg_y = 0.030
ax.scatter([x0 + 0.004], [lg_y], s=16, color=INK, zorder=4, linewidths=0)
label(ax, x0 + 0.016, lg_y, "压力 $p$", fs=8.4, color=INK, ha="left", va="center")
ax.annotate("", xy=(x0 + 0.118, lg_y), xytext=(x0 + 0.094, lg_y),
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=7,
                            shrinkA=0, shrinkB=0))
label(ax, x0 + 0.128, lg_y, "水平速度 $u$", fs=8.4, color=INK, ha="left", va="center")
ax.annotate("", xy=(x0 + 0.335, lg_y + 0.013), xytext=(x0 + 0.335, lg_y - 0.013),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.0, mutation_scale=7,
                            shrinkA=0, shrinkB=0))
label(ax, x0 + 0.347, lg_y, "竖直速度 $v$", fs=8.4, color=INK, ha="left", va="center")

# ---- 右半：放大一个格子 ----
zx0, zy0, zs = 0.615, 0.098, 0.235
label(ax, zx0 - 0.020, 0.435, "(b) 一个格子与它的四个面", fs=8.8, color=MUTED,
      ha="left", va="center")

ax.add_patch(Rectangle((zx0, zy0), zs, zs, facecolor="#FDF2E9", edgecolor=INK,
                       lw=1.1, zorder=2))
ax.scatter([zx0 + zs / 2], [zy0 + zs / 2], s=26, color=INK, zorder=4, linewidths=0)
label(ax, zx0 + zs / 2 + 0.004, zy0 + zs / 2 + 0.032, "$p_{i,j}$", fs=9.0, color=INK)

ax.annotate("", xy=(zx0 - 0.028, zy0 + zs / 2), xytext=(zx0, zy0 + zs / 2),
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1, mutation_scale=8,
                            shrinkA=0, shrinkB=0))
label(ax, zx0 - 0.036, zy0 + zs / 2, "$u_{i-1/2,j}$", fs=8.6, color=BLUE,
      ha="right", va="center")
ax.annotate("", xy=(zx0 + zs + 0.028, zy0 + zs / 2), xytext=(zx0 + zs, zy0 + zs / 2),
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1, mutation_scale=8,
                            shrinkA=0, shrinkB=0))
label(ax, zx0 + zs + 0.036, zy0 + zs / 2, "$u_{i+1/2,j}$", fs=8.6, color=BLUE,
      ha="left", va="center")

ax.annotate("", xy=(zx0 + zs / 2, zy0 + zs + 0.026), xytext=(zx0 + zs / 2, zy0 + zs),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.1, mutation_scale=8,
                            shrinkA=0, shrinkB=0))
label(ax, zx0 + zs / 2, zy0 + zs + 0.030, "$v_{i,j+1/2}$", fs=8.6, color=GREEN,
      ha="center", va="bottom")
ax.annotate("", xy=(zx0 + zs / 2, zy0 - 0.026), xytext=(zx0 + zs / 2, zy0),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.1, mutation_scale=8,
                            shrinkA=0, shrinkB=0))
label(ax, zx0 + zs / 2, zy0 - 0.030, "$v_{i,j-1/2}$", fs=8.6, color=GREEN,
      ha="center", va="top")

save(fig, "03", "fig03-02")
