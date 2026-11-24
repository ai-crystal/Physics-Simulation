import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import numpy.linalg as la

# ============================================================
# 与第 5 章同一块布：1 m 见方，13x13 顶点，对角两顶点固定
# 结构 / 剪切 / 弯曲刚度 2000 / 600 / 60 N/m，总质量 50 g
# ============================================================
N = 13
LL = 1.0
TOTAL_M = 0.05
K_S, K_SH, K_B = 2000.0, 600.0, 60.0
GRAV = 9.81


def build_cloth():
    xs = np.linspace(0, LL, N)
    X = np.zeros((N * N, 3))
    idx = lambda i, j: i * N + j
    for i in range(N):
        for j in range(N):
            X[idx(i, j)] = (xs[j], xs[i], 0.0)
    h = LL / (N - 1)
    sp = []
    for i in range(N):
        for j in range(N):
            if j + 1 < N:
                sp.append((idx(i, j), idx(i, j + 1), h, K_S))
            if i + 1 < N:
                sp.append((idx(i, j), idx(i + 1, j), h, K_S))
            if i + 1 < N and j + 1 < N:
                sp.append((idx(i, j), idx(i + 1, j + 1), h * np.sqrt(2), K_SH))
                sp.append((idx(i, j + 1), idx(i + 1, j), h * np.sqrt(2), K_SH))
            if j + 2 < N:
                sp.append((idx(i, j), idx(i, j + 2), 2 * h, K_B))
            if i + 2 < N:
                sp.append((idx(i, j), idx(i + 2, j), 2 * h, K_B))
    return X, np.array(sp, float), idx


def spring_energy(x, sp, need_hess):
    n = x.size
    E = 0.0
    g = np.zeros(n)
    H = np.zeros((n, n)) if need_hess else None
    for (a, b, Lr, k) in sp:
        a = int(a); b = int(b)
        ia = slice(3 * a, 3 * a + 3)
        ib = slice(3 * b, 3 * b + 3)
        d = x[ia] - x[ib]
        l = np.sqrt(d @ d) + 1e-12
        E += 0.5 * k * (l - Lr) ** 2
        gd = k * (l - Lr) * d / l
        g[ia] += gd
        g[ib] -= gd
        if need_hess:
            Hk = k * ((Lr / l) * np.outer(d, d) / l ** 2 + (1.0 - Lr / l) * np.eye(3))
            H[ia, ia] += Hk
            H[ib, ib] += Hk
            H[ia, ib] -= Hk
            H[ib, ia] -= Hk
    return E, g, H


def setup(dt=1 / 60):
    X, sp, idx = build_cloth()
    n = N * N
    dof = 3 * n
    isfree = np.ones(dof, bool)
    for (i, j) in [(0, 0), (0, N - 1)]:
        k = idx(i, j)
        isfree[3 * k:3 * k + 3] = False
    x = X.reshape(-1).copy()
    v = np.zeros(dof)
    v[1::3] -= GRAV * dt
    yhat = x + dt * v
    yhat[~isfree] = x[~isfree]
    m = TOTAL_M / n
    M = np.repeat(np.full(n, m), 3) * isfree
    return x, yhat, sp, M, isfree, dt, dof


# ============================================================
# 图 6-2  投影动力学与牛顿法的收敛对比（真实计算）
# ============================================================
def run_both(iters_pd=90):
    x, yhat, sp, M, isfree, dt, dof = setup()
    f = np.where(isfree)[0]
    pn = np.where(~isfree)[0]

    # 常数全局矩阵：G = sum k A^T A
    G = np.zeros((dof, dof))
    for (a, b, Lr, k) in sp:
        a = int(a); b = int(b)
        ia = slice(3 * a, 3 * a + 3)
        ib = slice(3 * b, 3 * b + 3)
        G[ia, ia] += k * np.eye(3)
        G[ib, ib] += k * np.eye(3)
        G[ia, ib] -= k * np.eye(3)
        G[ib, ia] -= k * np.eye(3)
    Amat = G + np.diag(M) / dt ** 2
    As = Amat[np.ix_(f, f)]
    Afp = Amat[np.ix_(f, pn)]
    xpin = x[pn].copy()

    # ---- 投影动力学：局部投影 + 全局线性求解 ----
    xk = yhat.copy()
    pd_res = []
    for _ in range(iters_pd + 1):
        E, g, _ = spring_energy(xk, sp, False)
        r = M * (xk - yhat) / dt ** 2 + g
        pd_res.append(la.norm(r[f]))
        b = M * yhat / dt ** 2
        for (a, b2, Lr, k) in sp:
            a = int(a); b2 = int(b2)
            ia = slice(3 * a, 3 * a + 3)
            ib = slice(3 * b2, 3 * b2 + 3)
            d = xk[ia] - xk[ib]
            p = Lr * d / (np.sqrt(d @ d) + 1e-12)
            b[ia] += k * p
            b[ib] -= k * p
        xn = xk.copy()
        xn[f] = la.solve(As, b[f] - Afp @ xpin)
        xk = xn

    # ---- 牛顿法：每次重新装配、重新分解 ----
    xk = yhat.copy()
    nt_res = []
    for _ in range(5):
        E, g, H = spring_energy(xk, sp, True)
        r = M * (xk - yhat) / dt ** 2 + g
        nt_res.append(la.norm(r[f]))
        K = H + np.diag(M) / dt ** 2
        dx = np.zeros(dof)
        dx[f] = -la.solve(K[np.ix_(f, f)], r[f])
        slope = g @ dx
        Phi = 0.5 * np.sum(M * (xk - yhat) ** 2) / dt ** 2 + E
        alpha = 1.0
        for _ in range(20):
            xn = xk + alpha * dx
            En, _, _ = spring_energy(xn, sp, False)
            Pn = 0.5 * np.sum(M * (xn - yhat) ** 2) / dt ** 2 + En
            if Pn <= Phi + 1e-4 * alpha * slope:
                break
            alpha *= 0.5
        xk = xn
    return np.array(pd_res), np.array(nt_res)


pd_res, nt_res = run_both()
print("PD :", " ".join(f"{v:.3e}" for v in pd_res[[0, 5, 20, 41, 56, 75, 89]]))
print("NT :", " ".join(f"{v:.3e}" for v in nt_res))
print("rho:", f"{(pd_res[89] / pd_res[20]) ** (1 / 69):.4f}")

fig, ax = plt.subplots(figsize=(6.5, 3.9))
fig.subplots_adjust(left=0.118, right=0.974, bottom=0.145, top=0.955)
ax.set_xlim(-2, 92)
ax.set_ylim(1e-13, 2e1)
ax.set_yscale("log")
clean(ax, spines=("left", "bottom"))
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)

ax.semilogy(np.arange(pd_res.size), pd_res, color=BLUE, lw=1.5, zorder=3,
            label="投影动力学（局部投影 + 预分解的全局解）")
ax.semilogy(np.arange(nt_res.size), nt_res, color=ACCENT, lw=1.0, zorder=4)
ax.semilogy(np.arange(nt_res.size), nt_res, "o", ms=6.5, mfc="white", mec=ACCENT,
            mew=1.7, zorder=5, label="牛顿法（每次重新装配与分解）")

ax.axhline(1e-4, color=FAINT, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.text(89, 1.35e-4, "常用容差 1e-4", fontsize=8.2, color=MUTED, ha="right", va="bottom")

ax.annotate("牛顿：3 次到 2.9e-12", xy=(3.1, 3.0e-12), xytext=(7.0, 6.0e-10),
            fontsize=8.6, color=ACCENT, ha="left", va="center", zorder=8,
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9,
                            connectionstyle="arc3,rad=0.20", shrinkB=6))
ax.annotate("56 次到 1e-4，75 次到 1e-5", xy=(56.2, 7.0e-5), xytext=(31, 3.6e-8),
            fontsize=8.6, color=BLUE, ha="left", va="center", zorder=8,
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.9,
                            connectionstyle="arc3,rad=-0.18", shrinkB=6))
ax.text(26, 4.0e-2, "每步乘 0.87", fontsize=8.4, color=BLUE, ha="left", va="bottom")

ax.set_xlabel("迭代次数", fontsize=9.8)
ax.set_ylabel("残差范数 $\\|\\nabla\\Phi\\|$（N）", fontsize=9.8)
ax.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1e0])
ax.legend(loc="upper right", bbox_to_anchor=(1.005, 1.02), handlelength=2.4,
          labelspacing=0.4, borderpad=0.25)

save(fig, "06", "fig06-02")


# ============================================================
# 图 6-1  局部步与全局步的交替（示意）
# 三角形中只有一根弹簧被拉长，局部投影只改动它两端的顶点，
# 全局步按质量加权平均这些互相矛盾的目标
# ============================================================
P = np.array([[0.00, 0.00], [1.00, 0.14], [0.30, 0.82]])
EDGES = [(0, 1), (1, 2), (2, 0)]
CUR = [la.norm(P[i] - P[j]) for (i, j) in EDGES]
REST = [0.60 * CUR[0], CUR[1], CUR[2]]          # 只有第一条边被拉长

cand = [[], [], []]
for (i, j), Lr in zip(EDGES, REST):
    m = 0.5 * (P[i] + P[j])
    u = (P[j] - P[i]) / la.norm(P[j] - P[i])
    cand[i].append(m - 0.5 * Lr * u)          # u 由 i 指向 j
    cand[j].append(m + 0.5 * Lr * u)
Pnew = np.array([np.mean(c, axis=0) for c in cand])

fig, ax = canvas(6.7, 4.4)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

panels = [(0.015, 0.300), (0.357, 0.643), (0.700, 0.985)]
BG0, BG1 = 0.378, 0.940


def to_axes(pt, x0, x1, y0=BG0 + 0.015, h=BG1 - BG0 - 0.03, pad=0.032):
    sx = (x1 - x0 - 2 * pad)
    sy = h - 0.02
    return (x0 + pad + sx * pt[0], y0 + 0.01 + sy * pt[1])


for (x0, x1) in panels:
    ax.add_patch(Rectangle((x0, BG0), x1 - x0, BG1 - BG0, facecolor=SOFT[0],
                           edgecolor="none", zorder=0))

TITLES = ["① 当前位形 $x^k$", "② 局部步：各自投影", "③ 全局步：一次线性求解"]
NOTES = ["红边被拉到静止长度的 1.7 倍\n另两根正好",
         "红边拉回静止长度\n它的两个端点各得一个新目标",
         "两个目标取质量加权平均\n得到自洽的 $x^{k+1}$"]
for (x0, x1), tt, note in zip(panels, TITLES, NOTES):
    label(ax, (x0 + x1) / 2, 0.952, tt, fs=9.2, color=INK, va="bottom")
    label(ax, (x0 + x1) / 2, 0.352, note, fs=8.2, color=MUTED, va="top")

# --- 面板一：当前位形 ---
x0, x1 = panels[0]
qa = [to_axes(p, x0, x1) for p in P]
for (i, j) in EDGES:
    c = ACCENT if (i, j) == (0, 1) else SLATE
    ax.plot([qa[i][0], qa[j][0]], [qa[i][1], qa[j][1]], color=c,
            lw=2.4 if (i, j) == (0, 1) else 1.6, zorder=3)
for q in qa:
    ax.add_patch(Circle(q, 0.0140, facecolor=INK, edgecolor="white", lw=1.1, zorder=4))

# --- 面板二：每根弹簧各自投影 ---
x0, x1 = panels[1]
qb = [to_axes(p, x0, x1) for p in P]
for (i, j), Lr in zip(EDGES, REST):
    m = 0.5 * (P[i] + P[j])
    u = (P[j] - P[i]) / la.norm(P[j] - P[i])
    a = to_axes(m - 0.5 * Lr * u, x0, x1)
    b = to_axes(m + 0.5 * Lr * u, x0, x1)
    if (i, j) == (0, 1):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=ACCENT, lw=1.6, zorder=3,
                ls=(0, (4, 3)))
    else:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=SLATE, lw=1.3, zorder=3)
for k in range(3):
    for c in cand[k]:
        cc = to_axes(c, x0, x1)
        if la.norm(c - P[k]) > 1e-9:
            arrow(ax, qb[k], cc, color=ACCENT, lw=1.0, ms=7,
                  style="-|>", shrinkA=8, shrinkB=7, z=4)
            ax.add_patch(Circle(cc, 0.0112, facecolor="white", edgecolor=ACCENT,
                                lw=1.4, zorder=5))
for q in qb:
    ax.add_patch(Circle(q, 0.0140, facecolor="none", edgecolor=INK, lw=1.0, zorder=6))

# --- 面板三：全局步 ---
x0, x1 = panels[2]
for (i, j) in EDGES:                       # 旧位形做淡底
    a = to_axes(P[i], x0, x1)
    b = to_axes(P[j], x0, x1)
    ax.plot([a[0], b[0]], [a[1], b[1]], color="#D1D5DB", lw=1.2, zorder=2,
            ls=(0, (3, 3)))
qn = [to_axes(p, x0, x1) for p in Pnew]
for k in range(3):
    for c in cand[k]:
        cc = to_axes(c, x0, x1)
        if la.norm(c - P[k]) > 1e-9:
            ax.plot([cc[0], qn[k][0]], [cc[1], qn[k][1]], color=FAINT, lw=0.8,
                    ls=(0, (2, 2)), zorder=4)
            ax.add_patch(Circle(cc, 0.0098, facecolor="white", edgecolor=FAINT,
                                lw=1.1, zorder=4))
for (i, j) in EDGES:
    ax.plot([qn[i][0], qn[j][0]], [qn[i][1], qn[j][1]], color=GREEN, lw=2.2, zorder=5)
for q in qn:
    ax.add_patch(Circle(q, 0.0140, facecolor=GREEN, edgecolor="white", lw=1.1, zorder=6))

# 流程箭头
arrow(ax, (0.307, 0.660), (0.350, 0.660), color=MUTED, lw=1.3, ms=10)
arrow(ax, (0.650, 0.660), (0.693, 0.660), color=MUTED, lw=1.3, ms=10)
curve_arrow(ax, [(0.988, 0.372), (0.988, 0.232), (0.008, 0.232), (0.008, 0.500),
                 (0.020, 0.500)], color=BLUE, lw=1.2, ms=10, ls=(0, (5, 4)))
label(ax, 0.500, 0.180, "残差还没降到阈值就再来一轮；矩阵不变，只换右端",
      fs=8.8, color=BLUE)
frame_note(ax, "示意图：几何按比例缩放，颜色与步骤对应真实算法", x=0.985, y=0.015, fs=7.6)

save(fig, "06", "fig06-01")
