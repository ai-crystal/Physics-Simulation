import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 3-1  线性三角形与线性四面体单元（示意图）
#   左：三节点三角形，面积坐标把单元分成三块，每块面积占比就是形函数
#   右：四节点四面体，高亮顶点 1 对面的三角形，箭头是 grad N1 的方向
#   坐标按英寸排布，set_aspect(1) 之后圆是圆的
# ============================================================
W, H = 6.9, 3.3
fig, ax = canvas(W, H, xlim=(0, W), ylim=(0, H))
ax.set_aspect("equal")

BOX = dict(boxstyle="round,pad=0.16", fc="white", ec="none")

# ---------- 左：三角形 ----------
P1 = np.array([0.55, 1.10])
P2 = np.array([2.85, 0.78])
P3 = np.array([2.25, 2.52])
G = (P1 + P2 + P3) / 3.0

ax.add_patch(Polygon([P1, P2, P3], closed=True, facecolor="#F3F6FF",
                     edgecolor=INK, lw=1.3, zorder=2))
for A in (P1, P2, P3):
    ax.plot([G[0], A[0]], [G[1], A[1]], color=FAINT, lw=0.8,
            ls=(0, (3, 3)), zorder=3)

for pts, tag in (((P2, P3, G), r"$\xi_1$"), ((P3, P1, G), r"$\xi_2$"),
                 ((P1, P2, G), r"$\xi_3$")):
    c = np.mean(np.array(pts), axis=0)
    label(ax, c[0], c[1], tag, fs=9.0, color=MUTED)

for P, s, dx, dy, ha in ((P1, "1", -0.22, -0.16, "right"),
                         (P2, "2", 0.22, -0.16, "left"),
                         (P3, "3", 0.0, 0.26, "center")):
    ax.add_patch(Circle(P, 0.085, facecolor="white", edgecolor=INK, lw=1.1, zorder=5))
    label(ax, P[0] + dx, P[1] + dy, s, fs=9.6, color=INK, weight="bold",
          ha=ha, bbox=BOX)

label(ax, 1.70, 0.36, "三节点三角形", fs=9.6, color=INK)
label(ax, 1.70, 0.14, "6 个自由度", fs=8.6, color=MUTED)

# ---------- 右：四面体 ----------
V1 = np.array([4.30, 1.00])
V2 = np.array([3.66, 1.96])
V3 = np.array([5.98, 1.62])
V4 = np.array([4.95, 2.60])

# 顶点 1 的对面是 (2,3,4)，在背后，填淡色
ax.add_patch(Polygon([V2, V3, V4], closed=True, facecolor="#F3F6FF",
                     edgecolor="none", zorder=1))
for A, B, ls, lw in ((V1, V2, "-", 1.5), (V1, V3, "-", 1.5), (V1, V4, "-", 1.5),
                     (V2, V4, "-", 1.3), (V3, V4, "-", 1.3),
                     (V2, V3, (0, (3, 2)), 1.0)):
    ax.plot([A[0], B[0]], [A[1], B[1]], color=INK, lw=lw, ls=ls, zorder=3,
            solid_capstyle="round")

for V, s_, dx, dy, ha, va in ((V1, "1", 0.0, -0.30, "center", "center"),
                              (V2, "2", -0.26, 0.0, "right", "center"),
                              (V3, "3", 0.26, 0.0, "left", "center"),
                              (V4, "4", 0.0, 0.28, "center", "bottom")):
    ax.add_patch(Circle(V, 0.085, facecolor="white", edgecolor=INK, lw=1.1, zorder=5))
    label(ax, V[0] + dx, V[1] + dy, s_, fs=9.6, color=INK, weight="bold",
          ha=ha, va=va, bbox=BOX)

label(ax, 4.90, 0.40, "四节点四面体", fs=9.6, color=INK)
label(ax, 4.90, 0.16, "12 个自由度；浅色面是顶点 1 的对面", fs=8.6, color=MUTED)

ax.plot([3.42, 3.42], [0.28, 3.02], color=GRID, lw=1.0, ls=(0, (5, 4)))
save(fig, "03", "fig03-01")


# ============================================================
# 图 3-2  全局刚度矩阵的稀疏结构（真实组装）
#   6x6 方格，每格切两个三角形：49 节点、72 单元、98 自由度
#   K = sum_e V_e B^T C B，平面应力，E=1e5 Pa，nu=0.3，厚度 1
# ============================================================
n = 6
m = n + 1
pts = np.array([[i / n, j / n] for j in range(m) for i in range(m)], float)


def nid(i, j):
    return j * m + i


tris = []
for j in range(n):
    for i in range(n):
        a, b, c, e = nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)
        tris.append((a, b, c))
        tris.append((a, c, e))

E, nu = 1e5, 0.3
C = E / (1 - nu ** 2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
nd = 2 * len(pts)
K = np.zeros((nd, nd))
for tri in tris:
    X = pts[list(tri)]
    A = 0.5 * abs((X[1, 0] - X[0, 0]) * (X[2, 1] - X[0, 1])
                  - (X[2, 0] - X[0, 0]) * (X[1, 1] - X[0, 1]))
    B = np.zeros((3, 6))
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        gx = (X[j, 1] - X[k, 1]) / (2 * A)
        gy = (X[k, 0] - X[j, 0]) / (2 * A)
        B[0, 2 * i] = gx
        B[1, 2 * i + 1] = gy
        B[2, 2 * i] = gy
        B[2, 2 * i + 1] = gx
    Ke = A * B.T @ C @ B
    dofs = []
    for t in tri:
        dofs += [2 * t, 2 * t + 1]
    K[np.ix_(dofs, dofs)] += Ke

nz = np.abs(K) > 1e-9
nnz = int(nz.sum())
ii, jj = np.nonzero(nz)
bw = int(np.max(np.abs(ii - jj)))
zero_eig = int((np.abs(np.linalg.eigvalsh(K)) < 1e-6).sum())
print("节点 %d  单元 %d  自由度 %d" % (len(pts), len(tris), nd))
print("非零元 %d / %d = %.4f" % (nnz, nd * nd, nnz / nd ** 2))
print("最大偏移 %d   零特征值 %d" % (bw, zero_eig))

fig, ax = plt.subplots(figsize=(5.3, 5.0))
ax.scatter(jj, ii, s=3.2, color=ACCENT, marker="s", linewidths=0, zorder=3)
ax.plot([0, nd], [0, nd], color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.plot([0, nd - bw], [bw, nd], color=GRID, lw=0.9, ls="-", zorder=1)
ax.plot([bw, nd], [0, nd - bw], color=GRID, lw=0.9, ls="-", zorder=1)
ax.set_xlim(-3, nd + 8)
ax.set_ylim(nd + 8, -3)
ax.set_aspect("equal")
ax.set_xlabel("列（自由度编号）")
ax.set_ylabel("行（自由度编号）")
ax.set_xticks([0, 32, 64, 97])
ax.set_yticks([0, 32, 64, 97])
clean(ax, grid=False, spines=("left", "bottom"))

label(ax, 40, 4, "棕色方块：非零元 %d 个，占 %.1f%%" % (nnz, 100 * nnz / nd ** 2),
      fs=8.6, color=MUTED, ha="left", va="top")
label(ax, 40, 14, r"细线：带宽 $\pm17$ 的边界", fs=8.6, color=MUTED,
      ha="left", va="top")
save(fig, "03", "fig03-02")
