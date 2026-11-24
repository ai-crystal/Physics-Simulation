import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# =====================================================================
# 一维隐式 MPM 单步：残差、切线刚度、牛顿迭代、共轭梯度
#   网格 ncell 个单元、ppc 个粒子每单元、二次 B 样条权重
#   本构 P(F) = E ln F（亨奇）；屈服用平滑截断 P = sy tanh(E ln F / sy)
#   后向欧拉：r = m (v - v_n)/dt - f_ext - f_int(v) = 0
# =====================================================================
DT = 1.0 / 120.0
VPISTON = -1.5                # 右端节点向左压
GRAV = -9.81
RHO = 350.0                   # 雪的密度 kg/m3


def build(ncell=32, ppc=7.5):
    """一维网格与粒子。域长 1 m，密度 RHO，总质量 RHO。"""
    N = ncell + 1
    H = 1.0 / ncell
    NP = int(round(ppc * ncell))
    VP = 1.0 / NP
    mp = RHO / NP

    t = np.linspace(0.0, 1.0, NP)
    xp = 1.5 * H + (1.0 - 3.0 * H) * t
    Fn = 0.98 - 0.35 * (xp - xp[0]) / (xp[-1] - xp[0])   # 0.98 -> 0.63

    i0 = np.floor(xp / H).astype(int)
    s = xp / H - i0
    idx = np.stack([i0 - 1, i0, i0 + 1], axis=1)
    w = np.stack([0.5 * (1 - s) ** 2,
                  0.75 - (s - 0.5) ** 2,
                  0.5 * s ** 2], axis=1)
    dw = np.stack([-(1 - s), 1 - 2 * s, s], axis=1) / H

    m = np.zeros(N)
    for p in range(NP):
        for a in range(3):
            m[idx[p, a]] += w[p, a] * mp

    return dict(N=N, H=H, NP=NP, VP=VP, Fn=Fn, idx=idx, w=w, dw=dw, m=m)


def material(F, E, sy):
    """应力 P 与切线模量 dP/dF。sy = inf 表示纯亨奇弹性。"""
    F = np.maximum(F, 1e-4)
    e = E * np.log(F)
    if not np.isfinite(sy):
        return e, E / F
    th = np.tanh(e / sy)
    return sy * th, (E / F) * (1.0 - th * th)


def residual(md, v, E, sy):
    """未知节点残差与雅可比（边界节点速度已给定）。"""
    idx, dw, Fn, VP, m, N = md["idx"], md["dw"], md["Fn"], md["VP"], md["m"], md["N"]
    dvdx = np.einsum("pa,pa->p", dw, v[idx])
    F = Fn * (1.0 + DT * dvdx)
    P, dPdF = material(F, E, sy)

    fint = np.zeros(N)
    for a in range(3):
        np.add.at(fint, idx[:, a], -VP * P * dw[:, a])

    r = m * v / DT - m * GRAV - fint

    K = np.zeros((N, N))
    coef = DT * VP * dPdF * Fn
    for a in range(3):
        for b in range(3):
            np.add.at(K, (idx[:, a], idx[:, b]), coef * dw[:, a] * dw[:, b])
    J = np.diag(m / DT) + K

    free = np.arange(1, N - 1)
    return r[free], J[np.ix_(free, free)]


def norm(r):
    return np.linalg.norm(r) / np.sqrt(len(r))


def newton(md, E, sy=np.inf, maxit=60, tol=1e-11):
    """从 v = 0 出发，返回每次迭代后的相对残差序列。"""
    N = md["N"]
    v = np.zeros(N)
    v[N - 1] = VPISTON
    r, _ = residual(md, v, E, sy)
    r0 = norm(r)
    hist = [1.0]
    for _ in range(maxit):
        r, J = residual(md, v, E, sy)
        delta = np.linalg.solve(J, -r)
        alpha, base = 1.0, norm(r)
        for _ in range(14):
            vt = v.copy()
            vt[1:N - 1] += alpha * delta
            rt, _ = residual(md, vt, E, sy)
            if norm(rt) <= base:
                break
            alpha *= 0.5
        v[1:N - 1] += alpha * delta
        r, _ = residual(md, v, E, sy)
        hist.append(norm(r) / r0)
        if hist[-1] < tol:
            break
    return np.array(hist)


def cg_count(A, b, maxit=5000, tol=1e-10):
    """雅可比预条件共轭梯度，返回达到 1e-10 相对残差的迭代次数。"""
    d = np.diag(A).copy()
    r = b.copy()
    z = r / d
    p = z.copy()
    rz = r @ z
    b0 = np.linalg.norm(r)
    for k in range(1, maxit + 1):
        Ap = A @ p
        alpha = rz / (p @ Ap)
        r -= alpha * Ap
        if np.linalg.norm(r) / b0 < tol:
            return k
        z = r / d
        rz_new = r @ z
        p = z + (rz_new / rz) * p
        rz = rz_new
    return maxit


def fig01():
    E0 = 1e7
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.0))
    md = build(32)

    # ---- 左：弹性，三个模量
    ax = axes[0]
    for E, c in zip([1e6, 1e7, 1e8], [BLUE, TEAL, ACCENT]):
        h = newton(md, E)
        ax.semilogy(np.arange(len(h)), np.maximum(h, 1e-16), "-o", color=c,
                    lw=1.3, ms=3.4, mfc="white", mew=1.0,
                    label=rf"$E=10^{{{int(np.log10(E))}}}$ Pa")
    ax.set_xlabel("牛顿迭代次数")
    ax.set_ylabel(r"相对残差 $\|\mathbf{r}\|/\|\mathbf{r}_0\|$")
    ax.set_xlim(-0.3, 9)
    ax.set_ylim(1e-16, 2)
    ax.set_yticks([1, 1e-4, 1e-8, 1e-12, 1e-16])
    clean(ax, grid=True)
    ax.legend(loc="upper right", handlelength=1.7, labelspacing=0.55)

    # ---- 右：屈服截断，屈服应力两个取值
    ax = axes[1]
    for sy, c, mk in [(5e5, PINK, "s"), (1e6, PURPLE, "^")]:
        h = newton(md, E0, sy=sy)
        ax.semilogy(np.arange(len(h)), np.maximum(h, 1e-16), "-" + mk, color=c,
                    lw=1.3, ms=3.2, mfc="white", mew=1.0,
                    label=rf"$\sigma_y={sy/1e6:g}$ MPa")
    ax.set_xlabel("牛顿迭代次数")
    ax.set_ylabel(r"相对残差 $\|\mathbf{r}\|/\|\mathbf{r}_0\|$")
    ax.set_xlim(-0.3, 18)
    ax.set_ylim(1e-16, 2)
    ax.set_yticks([1, 1e-4, 1e-8, 1e-12, 1e-16])
    clean(ax, grid=True)
    ax.legend(loc="lower left", handlelength=1.7, labelspacing=0.55)

    fig.subplots_adjust(wspace=0.33)
    save(fig, "07", "fig07-01")


def fig02():
    Es = np.logspace(4, 9, 11)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.0))

    # ---- 左：CG 迭代次数随 E，三种网格分辨率
    ax = axes[0]
    for ncell, c, mk in [(16, TEAL, "o"), (32, BLUE, "s"), (64, ACCENT, "^")]:
        md = build(ncell)
        its = []
        for E in Es:
            v = np.zeros(md["N"])
            v[-1] = VPISTON
            r, J = residual(md, v, E, np.inf)
            its.append(cg_count(J, -r))
        ax.semilogx(Es, its, "-" + mk, color=c, lw=1.3, ms=3.4, mfc="white",
                    mew=1.0)
        ax.text(1.5e9, its[-1], f"{ncell} 个单元", va="center", ha="left",
                fontsize=8.4, color=c)
    ax.set_xlabel(r"杨氏模量 $E$（Pa）")
    ax.set_ylabel("共轭梯度迭代次数")
    ax.set_ylim(0, 58)
    ax.set_xlim(8e3, 2e10)
    clean(ax, grid=True)

    # ---- 右：牛顿迭代次数随屈服应力
    ax = axes[1]
    md = build(32)
    sys_ = np.logspace(5, 7.3, 10)
    ns = [len(newton(md, 1e7, sy=s)) - 1 for s in sys_]
    ax.semilogx(sys_, ns, "-o", color=ACCENT, lw=1.5, ms=3.6, mfc="white", mew=1.0)
    ax.axhline(4, color=FAINT, lw=0.9, ls=":")
    ax.text(1.05e5, 6.1, "弹性极限：4 次", fontsize=8, color=MUTED)
    ax.set_xlabel(r"屈服应力 $\sigma_y$（Pa）")
    ax.set_ylabel("牛顿迭代次数")
    ax.set_ylim(0, 34)
    clean(ax, grid=True)

    fig.subplots_adjust(wspace=0.34)
    save(fig, "07", "fig07-02")


if __name__ == "__main__":
    fig01()
    fig02()
