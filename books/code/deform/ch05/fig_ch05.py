import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import numpy.linalg as la

# ============================================================
# 布料模型：1 m 见方，13x13 顶点，对角两顶点固定
# 结构 / 剪切 / 弯曲弹簧刚度 2000 / 600 / 60 N/m，总质量 50 g
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
            # 轴向刚度 k，横向刚度 k(1 - L/l)
            Hk = k * ((Lr / l) * np.outer(d, d) / l ** 2 + (1.0 - Lr / l) * np.eye(3))
            H[ia, ia] += Hk
            H[ib, ib] += Hk
            H[ia, ib] -= Hk
            H[ib, ia] -= Hk
    return E, g, H


def setup(dt, v0):
    X, sp, idx = build_cloth()
    n = N * N
    dof = 3 * n
    isfree = np.ones(dof, bool)
    for (i, j) in [(0, 0), (0, N - 1)]:
        k = idx(i, j)
        isfree[3 * k:3 * k + 3] = False
    x = X.reshape(-1).copy()
    v = np.zeros(dof)
    for c in range(3):
        v[c::3] = v0[c]
    v[1::3] -= GRAV * dt
    yhat = x + dt * v
    yhat[~isfree] = x[~isfree]
    m = TOTAL_M / n
    M = np.repeat(np.full(n, m), 3) * isfree
    return x, yhat, sp, M, isfree, dt, dof


# ============================================================
# 图 5-1  牛顿迭代的残差（真实计算）
# 重力下落一帧，dt = 1/60 s，每次迭代做 Armijo 回溯线搜索
# ============================================================
def newton_residuals(dt=1 / 60, v0=(0, 0, 0), itmax=5):
    x, yhat, sp, M, isfree, dt, dof = setup(dt, v0)
    f = np.where(isfree)[0]
    xk = yhat.copy()
    res = []
    for _ in range(itmax):
        E, g, H = spring_energy(xk, sp, True)
        r = M * (xk - yhat) / dt ** 2 + g
        res.append(la.norm(r[f]))
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
    return np.array(res)


res = newton_residuals()
print("newton residuals:", " ".join(f"{r:.3e}" for r in res))

fig, ax = plt.subplots(figsize=(6.5, 3.85))
fig.subplots_adjust(left=0.115, right=0.975, bottom=0.145, top=0.955)
ax.set_xlim(-0.15, 4.3)
ax.set_ylim(1e-13, 6e1)
ax.set_yscale("log")
clean(ax, spines=("left", "bottom"))

ax.semilogy(np.arange(res.size), res, color=ACCENT, lw=1.6, zorder=4)
ax.semilogy(np.arange(res.size), res, "o", ms=6.5, mfc="white", mec=ACCENT,
            mew=1.7, zorder=5)
ax.axhline(2.5e-12, color=FAINT, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.text(0.03, 3.3e-12, "浮点下限 2.5e-12", fontsize=8.2, color=MUTED,
        ha="left", va="bottom")

ax.text(2.40, 9.0e0, "相邻残差之比", fontsize=8.4, color=SLATE, ha="left", va="bottom")
ax.text(2.40, 2.4e0, "5.6e-3  →  3.8e-5  →  4.8e-7", fontsize=8.6, color=SLATE,
        ha="left", va="bottom")

ax.annotate("每迭代一次，\n误差自己平方一次", xy=(2.52, 2.2e-9), xytext=(2.66, 4.0e-7),
            fontsize=8.6, color=INK, ha="left", va="center", zorder=6,
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9,
                            connectionstyle="arc3,rad=-0.28"))

ax.set_xlabel("牛顿迭代次数", fontsize=9.8)
ax.set_ylabel("残差范数 $\\|\\nabla\\Phi\\|$（N）", fontsize=9.8)
ax.set_xticks(range(5))
ax.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1e0])
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)

save(fig, "05", "fig05-01")


# ============================================================
# 图 5-2  回溯线搜索（真实函数）
# 同一块布沿平面外甩出 20 m/s，dt = 1/30 s，首步牛顿方向上的切片
# ============================================================
def line_search_slice(dt=1 / 30, v0=(0, 0, 20)):
    x, yhat, sp, M, isfree, dt, dof = setup(dt, v0)
    f = np.where(isfree)[0]
    xk = yhat.copy()
    E, g, H = spring_energy(xk, sp, True)
    r = M * (xk - yhat) / dt ** 2 + g
    K = H + np.diag(M) / dt ** 2
    dx = np.zeros(dof)
    dx[f] = -la.solve(K[np.ix_(f, f)], r[f])
    Phi0 = 0.5 * np.sum(M * (xk - yhat) ** 2) / dt ** 2 + E
    slope = g @ dx
    Kdx = M * dx / dt ** 2 + H @ dx

    aa = np.linspace(0.0, 1.4, 281)
    true = np.empty_like(aa)
    for i, a in enumerate(aa):
        xn = xk + a * dx
        En, _, _ = spring_energy(xn, sp, False)
        true[i] = 0.5 * np.sum(M * (xn - yhat) ** 2) / dt ** 2 + En
    quad = Phi0 + aa * slope + 0.5 * aa ** 2 * (dx @ Kdx)
    return aa, true / Phi0, quad / Phi0, Phi0, slope, np.abs(dx).max()


aa, true_n, quad_n, Phi0, slope, dxmax = line_search_slice()
i1 = int(np.argmin(np.abs(aa - 1.0)))
imin = int(np.argmin(true_n))
j05 = int(np.argmin(np.abs(aa - 0.5)))

alpha, rejected = 1.0, []
for _ in range(20):
    j = int(np.argmin(np.abs(aa - alpha)))
    if true_n[j] <= 1.0 + 1e-4 * alpha * (slope / Phi0):
        break
    rejected.append(alpha)
    alpha *= 0.5
print(f"Phi0={Phi0:.4f} true(1)={true_n[i1]:.4f} min={aa[imin]:.3f}->{true_n[imin]:.4f} "
      f"model(1)={quad_n[i1]:.5f} dxmax={dxmax:.3f} accepted={alpha} rejected={rejected}")

fig, ax = plt.subplots(figsize=(6.6, 4.0))
fig.subplots_adjust(left=0.115, right=0.965, bottom=0.145, top=0.955)
ax.set_xlim(-0.03, 1.22)
ax.set_ylim(0.0, 2.30)
clean(ax, spines=("left", "bottom"))
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)

ax.axhline(1.0, color=FAINT, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.text(0.30, 1.045, "$\\Phi(0)$", fontsize=8.8, color=MUTED, ha="left", va="bottom")

ax.plot(aa, quad_n, color=BLUE, lw=1.4, ls=(0, (6, 4)), zorder=3,
        label="二次模型（牛顿法用的近似）")
ax.plot(aa, true_n, color=ACCENT, lw=1.9, zorder=4,
        label="真实增量势 $\\Phi(\\alpha)$")

ax.axvline(1.0, color=FAINT, lw=0.8, ls=":", zorder=1)
ax.plot([1.0], [true_n[i1]], "o", ms=7.2, mfc="white", mec=ACCENT, mew=1.8, zorder=6)
ax.plot([0.5], [true_n[j05]], "o", ms=7.0, mfc=ACCENT, mec=ACCENT, zorder=6)
ax.plot([aa[imin]], [true_n[imin]], "|", ms=12, color=GREEN, mew=2.0, zorder=7)

ax.annotate("全步 $\\alpha=1$：1.93\n比出发点还高，拒绝",
            xy=(1.0, true_n[i1]), xytext=(0.47, 1.90), fontsize=8.6, color=ACCENT,
            ha="left", va="center", zorder=8,
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, shrinkB=7))
ax.annotate("$\\alpha=0.5$：0.60\nArmijo 条件满足，接受",
            xy=(0.5, true_n[j05]), xytext=(0.56, 0.36), fontsize=8.6, color=GREEN,
            ha="left", va="center", zorder=8,
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9,
                            connectionstyle="arc3,rad=0.24", shrinkB=7))
ax.text(0.385, 0.645, "极小 0.55", fontsize=8.2, color=GREEN,
        ha="center", va="bottom")

ax.legend(loc="upper left", bbox_to_anchor=(0.005, 1.01), handlelength=2.2,
          labelspacing=0.45, borderpad=0.2)

ax.set_xlabel("步长比例 $\\alpha$", fontsize=9.8)
ax.set_ylabel("$\\Phi(\\alpha)\\,/\\,\\Phi(0)$", fontsize=9.8)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])

save(fig, "05", "fig05-02")
