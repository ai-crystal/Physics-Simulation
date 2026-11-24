import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 4-1  支撑函数与闵可夫斯基差（示意）
#   只画关系，坐标不是计算结果：差集在 d 方向的支撑点等于
#   A、B 各自支撑点之差，投影长度等于 h_A(d) + h_B(-d)。
# ============================================================
fig, ax = canvas(6.7, 3.55, (0, 1), (0.08, 0.90))

d = np.array([np.cos(np.deg2rad(24.0)), np.sin(np.deg2rad(24.0))])
n = np.array([-d[1], d[0]])

# ---------- 左：A 与 B ----------
A = np.array([[0.070, 0.400], [0.125, 0.318], [0.215, 0.322],
              [0.262, 0.400], [0.215, 0.480], [0.125, 0.478]])
B = np.array([[0.372, 0.640], [0.470, 0.700], [0.452, 0.598]])
ax.add_patch(Polygon(A, closed=True, facecolor="#EFF4FF", edgecolor=BLUE, lw=1.3, zorder=3))
ax.add_patch(Polygon(B, closed=True, facecolor="#FDF2E9", edgecolor=ACCENT, lw=1.3, zorder=3))
label(ax, 0.132, 0.428, "A", fs=9.6, color=BLUE)
label(ax, 0.484, 0.664, "B", fs=9.6, color=ACCENT, ha="left")

iA = int(np.argmax(A @ d))
iB = int(np.argmax(B @ -d))
sA, sB = A[iA], B[iB]

# 方向罗盘：一条双向线段，两端标 d 与 -d
c = np.array([0.105, 0.800])
ax.plot([c[0] - 0.090 * d[0], c[0] + 0.090 * d[0]],
        [c[1] - 0.090 * d[1], c[1] + 0.090 * d[1]], color=NAVY, lw=1.3, zorder=6)
arrow(ax, (c[0] + 0.020 * d[0], c[1] + 0.020 * d[1]),
      (c[0] + 0.090 * d[0], c[1] + 0.090 * d[1]), color=NAVY, lw=1.3, ms=8, z=7)
arrow(ax, (c[0] - 0.020 * d[0], c[1] - 0.020 * d[1]),
      (c[0] - 0.090 * d[0], c[1] - 0.090 * d[1]), color=NAVY, lw=1.3, ms=8, z=7)
label(ax, c[0] + 0.112 * d[0], c[1] + 0.112 * d[1], r"$\mathbf{d}$", fs=9.6, color=NAVY)
label(ax, c[0] - 0.112 * d[0] - 0.010, c[1] - 0.112 * d[1] - 0.004, r"$-\mathbf{d}$",
      fs=9.6, color=NAVY)

ax.add_patch(Circle(sA, 0.009, facecolor=BLUE, edgecolor="white", lw=1.0, zorder=8))
ax.add_patch(Circle(sB, 0.009, facecolor=ACCENT, edgecolor="white", lw=1.0, zorder=8))
for p0, col in ((sA, BLUE), (sB, ACCENT)):
    q0 = p0 - 0.048 * n
    q1 = p0 + 0.048 * n
    ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=col, lw=0.9, ls=(0, (3, 2)),
            zorder=5, alpha=0.85)

label(ax, 0.286, 0.336, r"$s_A(\mathbf{d})$", fs=8.6, color=BLUE, ha="left")
ax.plot([0.286, 0.268], [0.352, 0.386], color=BLUE, lw=0.8, zorder=6)

label(ax, 0.318, 0.700, r"$s_B(-\mathbf{d})$", fs=8.6, color=ACCENT, ha="right")
ax.plot([0.330, 0.340], [0.648, 0.664], color=ACCENT, lw=0.8, zorder=6)

label(ax, 0.165, 0.205, "(a) 两个凸形，各自求支撑点", fs=9.0, color=INK, weight="bold")
label(ax, 0.165, 0.150, r"沿 $\mathbf{d}$ 与 $-\mathbf{d}$ 各取最远点", fs=8.4, color=MUTED)

# ---------- 右：差集 ----------
D = np.array([[0.640, 0.470], [0.700, 0.385], [0.790, 0.378],
              [0.865, 0.455], [0.882, 0.560], [0.822, 0.640],
              [0.720, 0.632], [0.652, 0.560]])
ax.add_patch(Polygon(D, closed=True, facecolor="#F5F3FF", edgecolor=PURPLE, lw=1.3, zorder=3))
label(ax, 0.888, 0.660, r"$A\ominus B$", fs=9.6, color=PURPLE)

o = np.array([0.772, 0.505])
p = np.array([0.866, 0.462])
ax.add_patch(Circle(o, 0.0075, facecolor="white", edgecolor=INK, lw=1.2, zorder=8))
label(ax, o[0] - 0.014, o[1] - 0.004, "原点", fs=8.4, color=INK, ha="right")
ax.add_patch(Circle(p, 0.009, facecolor=PURPLE, edgecolor="white", lw=1.0, zorder=8))
label(ax, p[0] + 0.012, p[1] - 0.022, r"$s_A(\mathbf{d})-s_B(-\mathbf{d})$", fs=8.4,
      color=PURPLE, ha="left", va="top")

arrow(ax, (0.640, 0.775), (0.640 + 0.105 * d[0], 0.775 + 0.105 * d[1]),
      color=NAVY, lw=1.3, ms=8, z=7)
label(ax, 0.640 + 0.128 * d[0], 0.775 + 0.128 * d[1], r"$\mathbf{d}$", fs=9.6, color=NAVY)

proj = (p - o) @ d
q0 = p - 0.048 * n
q1 = p + 0.048 * n
ax.plot([q0[0], q1[0]], [q0[1], q1[1]], color=PURPLE, lw=0.9, ls=(0, (3, 2)), zorder=5)
mid = (o + p) / 2
label(ax, 0.856, mid[1] + 0.046, r"$h(\mathbf{d})=%.2f$" % proj, fs=8.2,
      color=PURPLE, ha="right", va="bottom")
ax.plot([o[0], p[0]], [o[1], p[1]], color=PURPLE, lw=1.0, alpha=0.55, zorder=4)

label(ax, 0.762, 0.205, "(b) 差集与它在该方向的支撑点", fs=9.0, color=INK, weight="bold")
label(ax, 0.762, 0.150, r"$h_{A\ominus B}(\mathbf{d})=h_A(\mathbf{d})+h_B(-\mathbf{d})$",
      fs=8.6, color=MUTED)

save(fig, "04", "fig04-01")


# ============================================================
# 图 4-2  二维 GJK 的三次迭代（真实计算）
#   A：矩形 x∈[-0.90,0.05]，y∈[-0.275,0.275]
#   B：三角形 (0.3247,-0.0404) (0.2939,0.3953) (0.0359,0.1098)
#   支撑点 s(d) = argmax x·d；差集支撑 = s_A(d) - s_B(-d)
# ============================================================
A = np.array([[-0.90, -0.275], [0.05, -0.275], [0.05, 0.275], [-0.90, 0.275]])
B = np.array([[0.3247, -0.0404], [0.2939, 0.3953], [0.0359, 0.1098]])


def sup(P, d):
    i = int(np.argmax(P @ np.asarray(d, float)))
    return P[i], i


def msup(d):
    pa, ia = sup(A, d)
    pb, ib = sup(B, -np.asarray(d, float))
    return pa - pb, ia, ib


def reduce(pts):
    """返回 (新单纯形, 新方向或 None 表示原点在单纯形内)。"""
    if len(pts) == 1:
        return pts, -pts[0]
    if len(pts) == 2:
        a, b = pts[1], pts[0]
        ab, ao = b - a, -a
        if ab @ ao > 0:
            nn = np.array([-ab[1], ab[0]])
            if nn @ ao < 0:
                nn = -nn
            return pts, nn
        return [a], ao
    a, b, c = pts[2], pts[1], pts[0]
    ab, ac, ao = b - a, c - a, -a
    nab = np.array([-ab[1], ab[0]])
    if nab @ (c - a) > 0:
        nab = -nab
    nac = np.array([-ac[1], ac[0]])
    if nac @ (b - a) > 0:
        nac = -nac
    if nab @ ao > 0:
        return [a, b], nab
    if nac @ ao > 0:
        return [a, c], nac
    return pts, None


def seg_closest(p, q):
    """线段 pq 上离原点最近的点。"""
    pq = q - p
    t = -(p @ pq) / (pq @ pq)
    t = min(1.0, max(0.0, t))
    return p + t * pq


d = np.array([1.0, 0.0])
pts, steps = [], []
hit = False
for it in range(12):
    p_, ia, ib = msup(d)
    print("迭代 %d：d=(%.4f, %.4f)  差集支撑点=(%.4f, %.4f)  投影=%.4f "
          " A支撑顶点 %d  B支撑顶点 %d" % (it + 1, d[0], d[1], p_[0], p_[1], p_ @ d, ia, ib))
    steps.append(dict(d=d.copy(), p=p_.copy(), ia=ia, ib=ib, simplex=[q.copy() for q in pts]))
    if p_ @ d <= 1e-12:
        print("分离")
        break
    pts.append(p_)
    pts, d2 = reduce(pts)
    if d2 is None:
        hit = True
        break
    d = d2 / np.linalg.norm(d2)
print("相交" if hit else "未相交", "，最终单纯形：", np.round(np.array(pts), 4))

# ---- 闵可夫斯基差的凸包 ----
diff = np.array([a - b for a in A for b in B])


def hull(P):
    P = P[np.lexsort((P[:, 1], P[:, 0]))]

    def half(points):
        out = []
        for q in points:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (q[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (q[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(q)
        return out

    lower = half(P)
    upper = half(P[::-1])
    return np.array(lower[:-1] + upper[:-1])


H = hull(diff)
print("差集顶点数：", len(H))

fig, (fa, fb) = plt.subplots(1, 2, figsize=(6.9, 3.4))

# ---------- (a) 两个多边形与支撑点对 ----------
fa.add_patch(Polygon(A, closed=True, facecolor="#EFF4FF", edgecolor=BLUE, lw=1.3, zorder=3))
fa.add_patch(Polygon(B, closed=True, facecolor="#FDF2E9", edgecolor=ACCENT, lw=1.3, zorder=3))
fa.axhline(0, color=GRID, lw=0.8, zorder=1)
fa.axvline(0, color=GRID, lw=0.8, zorder=1)
label(fa, -0.60, -0.02, "A", fs=9.6, color=BLUE)
label(fa, 0.30, 0.44, "B", fs=9.6, color=ACCENT)

marks = ["\u2460", "\u2461", "\u2462"]
# 第二、三次迭代在 B 上取到同一个顶点，标记做一点错位以免重叠
bfix = {0: (0.020, 0.036), 2: (-0.026, -0.030)}
for k, st in enumerate(steps):
    pa, pb = A[st["ia"]], B[st["ib"]]
    fa.plot([pa[0], pb[0]], [pa[1], pb[1]], color=FAINT, lw=0.9, ls=(0, (2, 2)), zorder=2)
    dxb, dyb = bfix.get(k, (0.0, 0.0))
    fa.add_patch(Circle(pa, 0.030, facecolor="white", edgecolor=BLUE, lw=1.0, zorder=7))
    fa.add_patch(Circle((pb[0] + dxb, pb[1] + dyb), 0.030, facecolor="white",
                        edgecolor=ACCENT, lw=1.0, zorder=7))
    label(fa, pa[0], pa[1], str(k + 1), fs=7.8, color=BLUE, z=8)
    label(fa, pb[0] + dxb, pb[1] + dyb, str(k + 1), fs=7.8, color=ACCENT, z=8)

fa.set_xlim(-1.06, 0.40)
fa.set_ylim(-0.56, 0.56)
fa.set_aspect("equal")
fa.set_xlabel("x  (m)")
fa.set_ylabel("y  (m)")
fa.set_xticks([-1.0, -0.5, 0.0])
fa.set_yticks([-0.5, 0.0, 0.5])
clean(fa, grid=False)
fa.text(0.02, 1.045, "(a) 三次迭代取到的支撑点对", transform=fa.transAxes,
        fontsize=9.0, color=INK, weight="bold", ha="left", va="bottom")

# ---------- (b) 差集与单纯形 ----------
fb.add_patch(Polygon(H, closed=True, facecolor="#F5F3FF", edgecolor=PURPLE, lw=1.2,
                     alpha=0.85, zorder=2))
P0, P1, P2 = steps[0]["p"], steps[1]["p"], steps[2]["p"]
tri = np.array([P0, P1, P2])
fb.add_patch(Polygon(tri, closed=True, facecolor=GOLD, edgecolor=GOLD, lw=1.0,
                     alpha=0.16, zorder=3))
fb.plot([P0[0], P1[0]], [P0[1], P1[1]], color=MUTED, lw=1.0, ls=(0, (3, 2)), zorder=4)

# 搜索方向：从上一个单纯形上离原点最近的点出发
c0 = P0
c1 = seg_closest(P0, P1)
arrow(fb, tuple(c1), tuple(c1 + 0.32 * steps[1]["d"]), color=NAVY, lw=1.3, ms=8, z=8)
label(fb, c1[0] + 0.355 * steps[1]["d"][0] + 0.030, c1[1] + 0.355 * steps[1]["d"][1],
      r"$\mathbf{d}$", fs=9.0, color=NAVY)

for q, nm, dx, dy in ((P0, r"$\mathbf{p}_1$", 0.045, -0.075),
                      (P1, r"$\mathbf{p}_2$", 0.050, 0.045),
                      (P2, r"$\mathbf{p}_3$", 0.030, 0.075)):
    fb.add_patch(Circle(q, 0.026, facecolor="white", edgecolor=PURPLE, lw=1.1, zorder=9))
    label(fb, q[0], q[1], "", fs=7)
    label(fb, q[0] + dx, q[1] + dy, nm, fs=8.4, color=PURPLE)

fb.add_patch(Circle((0, 0), 0.024, facecolor="white", edgecolor=INK, lw=1.2, zorder=10))
fb.annotate("原点", xy=(0.016, -0.012), xytext=(0.115, -0.20), fontsize=8.2, color=INK,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="->", color=INK, lw=0.8,
                            connectionstyle="arc3,rad=0.20"))

fb.set_xlim(-1.30, 0.48)
fb.set_ylim(-0.72, 0.52)
fb.set_aspect("equal")
fb.set_xlabel("x  (m)")
fb.set_ylabel("y  (m)")
fb.set_xticks([-1.0, -0.5, 0.0])
fb.set_yticks([-0.5, 0.0, 0.5])
clean(fb, grid=False)
fb.text(0.02, 1.045, "(b) 差集里的单纯形：点、线、三角形", transform=fb.transAxes,
        fontsize=9.0, color=INK, weight="bold", ha="left", va="bottom")

fig.subplots_adjust(wspace=0.34)
save(fig, "04", "fig04-02")
