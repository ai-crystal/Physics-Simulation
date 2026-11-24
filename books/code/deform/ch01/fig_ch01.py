import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 1-1  三角网上的三类弹簧（示意图）
#   上排：同一张 4x3 网格，分别只画出一类弹簧（其余边淡灰）
#   下排：这一类弹簧抵抗的变形（灰虚线为变形前，实线为变形后）
# ============================================================
W, H = 6.9, 4.15
fig, ax = canvas(W, H)

COLS = [0.165, 0.500, 0.835]
SY = 0.048          # 网格纵向格距
SX = 0.050          # 网格横向格距
GY = 0.760          # 上排网格中心
NX, NY = 4, 3


def mesh(cx, cy):
    return [[(cx + (i - (NX - 1) / 2) * SX, cy + (j - (NY - 1) / 2) * SY)
             for i in range(NX)] for j in range(NY)]


def faint_edges(P):
    for j in range(NY):
        for i in range(NX):
            if i + 1 < NX:
                ax.plot([P[j][i][0], P[j][i + 1][0]], [P[j][i][1], P[j][i + 1][1]],
                        color="#D8D8D8", lw=0.9, zorder=1)
            if j + 1 < NY:
                ax.plot([P[j][i][0], P[j + 1][i][0]], [P[j][i][1], P[j + 1][i][1]],
                        color="#D8D8D8", lw=0.9, zorder=1)


def nodes(P, r=0.0072):
    for j in range(NY):
        for i in range(NX):
            ax.add_patch(Ellipse(P[j][i], 2 * r, 2 * r * W / H, facecolor="white",
                                 edgecolor=INK, lw=0.9, zorder=6))


def hop(A, C, vert, color=ACCENT, r=0.0092):
    B = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
    if not vert:
        ax.plot([A[0], B[0] - r], [A[1], B[1]], color=color, lw=1.6,
                ls=(0, (1.4, 1.6)), zorder=6)
        ax.plot([B[0] + r, C[0]], [B[1], C[1]], color=color, lw=1.6,
                ls=(0, (1.4, 1.6)), zorder=6)
        ax.add_patch(Arc(B, 2 * r, 2 * r * W / H, theta1=0, theta2=180,
                         edgecolor=color, lw=1.3, zorder=7))
    else:
        ax.plot([A[0], B[0]], [A[1], B[1] - r], color=color, lw=1.6,
                ls=(0, (1.4, 1.6)), zorder=6)
        ax.plot([B[0], C[0]], [B[1] + r, C[1]], color=color, lw=1.6,
                ls=(0, (1.4, 1.6)), zorder=6)
        ax.add_patch(Arc(B, 2 * r * W / H, 2 * r, theta1=270, theta2=90,
                         edgecolor=color, lw=1.3, zorder=7))


# ---------- 上排：三类弹簧 ----------
for n, (cx, kind, name, color) in enumerate([
        (COLS[0], "s", "结构弹簧", INK),
        (COLS[1], "h", "剪切弹簧", BLUE),
        (COLS[2], "b", "弯曲弹簧", ACCENT)]):
    P = mesh(cx, GY)
    faint_edges(P)
    if kind == "s":
        for j in range(NY):
            for i in range(NX):
                if i + 1 < NX:
                    ax.plot([P[j][i][0], P[j][i + 1][0]], [P[j][i][1], P[j][i + 1][1]],
                            color=color, lw=2.0, zorder=4, solid_capstyle="round")
                if j + 1 < NY:
                    ax.plot([P[j][i][0], P[j + 1][i][0]], [P[j][i][1], P[j + 1][i][1]],
                            color=color, lw=2.0, zorder=4, solid_capstyle="round")
    elif kind == "h":
        for j in range(NY - 1):
            for i in range(NX - 1):
                ax.plot([P[j][i][0], P[j + 1][i + 1][0]], [P[j][i][1], P[j + 1][i + 1][1]],
                        color=color, lw=1.4, ls=(0, (5, 3)), zorder=4)
                ax.plot([P[j][i + 1][0], P[j + 1][i][0]], [P[j][i + 1][1], P[j + 1][i][1]],
                        color=color, lw=1.4, ls=(0, (5, 3)), zorder=4)
    else:
        for j in range(NY):
            for i in range(NX - 2):
                hop(P[j][i], P[j][i + 2], vert=False, color=color)
    nodes(P)
    label(ax, cx, 0.890, name, fs=9.0, color=color, weight="bold")

# ---------- 下排：对应的变形 ----------
def ghost(pts, color=FAINT):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=0.9,
            ls=(0, (3.5, 2.8)), zorder=2)


def solid(pts, color, close=True):
    q = pts + [pts[0]] if close else pts
    ax.plot([p[0] for p in q], [p[1] for p in q], color=color, lw=1.6, zorder=4,
            solid_capstyle="round")
    ax.scatter([p[0] for p in q], [p[1] for p in q], s=13, color=color, zorder=5,
               edgecolor="white", linewidth=0.7)


DY = 0.455
# 拉伸
cx = COLS[0]
ghost([(cx - 0.050, DY - 0.086), (cx + 0.050, DY - 0.086), (cx + 0.050, DY - 0.056),
       (cx - 0.050, DY - 0.056), (cx - 0.050, DY - 0.086)])
solid([(cx - 0.050, DY - 0.032), (cx + 0.075, DY - 0.032), (cx + 0.075, DY + 0.028),
       (cx - 0.050, DY + 0.028)], INK)
arrow(ax, (cx + 0.022, DY - 0.002), (cx + 0.062, DY - 0.002), color=INK, lw=0.9,
      style="-|>", z=6, ms=6)
label(ax, cx, 0.272, "抵抗拉伸", fs=8.6, color=MUTED)

# 剪切
cx = COLS[1]
ghost([(cx - 0.052, DY - 0.086), (cx + 0.048, DY - 0.086), (cx + 0.048, DY - 0.056),
       (cx - 0.052, DY - 0.056), (cx - 0.052, DY - 0.086)])
solid([(cx - 0.052, DY - 0.032), (cx + 0.048, DY - 0.032), (cx + 0.088, DY + 0.028),
       (cx - 0.012, DY + 0.028)], BLUE)
arrow(ax, (cx + 0.036, DY + 0.028), (cx + 0.084, DY + 0.028), color=BLUE, lw=0.9,
      style="-|>", z=6, ms=6)
label(ax, cx, 0.272, "抵抗剪切", fs=8.6, color=MUTED)

# 折叠
cx = COLS[2]
ghost([(cx - 0.078, DY - 0.040), (cx + 0.078, DY - 0.040)])
solid([(cx - 0.078, DY - 0.040), (cx, DY + 0.052), (cx + 0.078, DY - 0.040)],
      ACCENT, close=False)
label(ax, cx, 0.272, "抵抗折叠", fs=8.6, color=MUTED)

ax.plot([0.022, 0.978], [0.625, 0.625], color=GRID, lw=0.9, zorder=0)
ax.set_ylim(0.190, 0.935)
save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  显式积分的临界步长（真实计算）
#   左：单体弹簧 dt = 2*sqrt(m/k)，m = 1/4/16 g
#   右：5x5 三角网，dt = 2/omega_max，omega_max 由 M^-1 K 最大特征值算出
# ============================================================
def grid_points(nx, ny, h):
    return np.array([(i * h, j * h) for j in range(ny) for i in range(nx)], float)


def grid_springs(nx, ny):
    idx = lambda i, j: j * nx + i
    out = []
    for j in range(ny):
        for i in range(nx):
            if i + 1 < nx:
                out.append((idx(i, j), idx(i + 1, j), "s"))
            if j + 1 < ny:
                out.append((idx(i, j), idx(i, j + 1), "s"))
            if i + 1 < nx and j + 1 < ny:
                out.append((idx(i, j), idx(i + 1, j + 1), "h"))
                out.append((idx(i + 1, j), idx(i, j + 1), "h"))
            if i + 2 < nx:
                out.append((idx(i, j), idx(i + 2, j), "b"))
            if j + 2 < ny:
                out.append((idx(i, j), idx(i, j + 2), "b"))
    return out


def stiffness_matrix(pts, conn, kdict):
    n = len(pts)
    K = np.zeros((2 * n, 2 * n))
    for a, b, t in conn:
        d = pts[b] - pts[a]
        nv = d / np.linalg.norm(d)
        blk = kdict[t] * np.outer(nv, nv)        # 静止构型下的 Hessian = k n n^T
        ia = [2 * a, 2 * a + 1]
        ib = [2 * b, 2 * b + 1]
        K[np.ix_(ia, ia)] += blk
        K[np.ix_(ib, ib)] += blk
        K[np.ix_(ia, ib)] -= blk
        K[np.ix_(ib, ia)] -= blk
    return K


def critical_dt(ks, mass=1e-3, h=0.05, nx=5, ny=5):
    pts = grid_points(nx, ny, h)
    conn = grid_springs(nx, ny)
    K = stiffness_matrix(pts, conn, {"s": ks, "h": ks / 2.0, "b": ks / 10.0})
    M = np.eye(2 * len(pts)) * mass
    w2 = np.sort(np.linalg.eigvalsh(np.linalg.solve(M, K)))
    w2 = w2[w2 > 1e-6]                            # 去掉三个刚体模态
    return 2.0 / np.sqrt(w2[-1])


print("网格临界步长：", [(k, round(critical_dt(k) * 1e3, 4)) for k in (1e3, 1e4, 1e5)])

fig, (fa, fb) = plt.subplots(1, 2, figsize=(6.9, 3.25))

kk = np.logspace(2, 6, 400)
for m, c, lab in [(1e-3, BLUE, "$m=1$ g"), (4e-3, GREEN, "$m=4$ g"),
                  (16e-3, ACCENT, "$m=16$ g")]:
    fa.plot(kk, 2 * np.sqrt(m / kk), color=c, lw=1.7, label=lab)
fa.axhline(1 / 60, color=MUTED, lw=1.0, ls=(0, (5, 3)))
fa.axhline(1 / 240, color=MUTED, lw=1.0, ls=(0, (1.5, 2.5)))
fa.set_xscale("log")
fa.set_yscale("log")
fa.set_xlim(1e2, 1.2e6)
fa.set_ylim(2e-5, 4e-2)
fa.set_xlabel("弹簧刚度 $k$  (N/m)")
fa.set_ylabel("临界步长  $\\Delta t$  (s)")
label(fa, 1.9e5, 1 / 60 * 2.05, "60 帧  1/60 s", fs=8.2, color=MUTED, ha="left")
label(fa, 1.9e5, 1 / 240 * 1.85, "240 帧", fs=8.2, color=MUTED, ha="left")
fa.legend(loc="lower left", handlelength=1.5, labelspacing=0.3)
clean(fa)
fa.tick_params(which="minor", length=2, color=GRID)

ks_list = np.logspace(2, 5, 26)
fb.plot(ks_list, [critical_dt(k) for k in ks_list], color=INK, lw=1.7, zorder=3)

for k, txt, off, ha, va in [(1e3, "0.87 ms", (8, 6), "left", "bottom"),
                            (1e4, "0.27 ms", (8, 6), "left", "bottom"),
                            (1e5, "0.087 ms", (-8, -12), "right", "top")]:
    dt = critical_dt(k)
    fb.plot([k], [dt], marker="^", ms=7.5, mfc="white", mec=ACCENT, mew=1.3, zorder=5)
    fb.annotate(txt, xy=(k, dt), xytext=off, textcoords="offset points",
                fontsize=8.2, color=ACCENT, ha=ha, va=va)

fb.set_xscale("log")
fb.set_yscale("log")
fb.set_xlim(8e1, 1.8e5)
fb.set_ylim(4e-5, 9e-3)
fb.set_xlabel("结构弹簧刚度 $k_s$  (N/m)")
fb.set_ylabel("临界步长  $\\Delta t$  (s)")
clean(fb)
fb.tick_params(which="minor", length=2, color=GRID)

lo, hi = 4e-5, 9e-3
fb2 = fb.twinx()
fb2.set_yscale("log")
fb2.set_ylim((1 / 60) / hi, (1 / 60) / lo)
fb2.set_ylabel("一帧（1/60 s）所需子步数", color=SLATE)
fb2.tick_params(colors=SLATE, labelsize=8.2)
fb2.spines["top"].set_visible(False)
fb2.spines["right"].set_color("#9CA3AF")

fig.subplots_adjust(wspace=0.52)
save(fig, "01", "fig01-02")
