import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as csg


def laplace2d(n, h=1.0):
    """二维五点格式的负拉普拉斯，Dirichlet 边界的内部未知量，n×n 个点。"""
    T = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(n, n)) / h**2
    I = sp.identity(n)
    return (sp.kron(I, T) + sp.kron(T, I)).tocsc()


# ---------------------------------------------------------------- 图 6-1
# 五点格式的稀疏模式，自然序与 RCM 序下的 Cholesky 因子
def fig01():
    n = 16
    A = laplace2d(n)
    Ad = A.toarray()
    Ln = np.linalg.cholesky(Ad + 1e-12 * np.eye(n * n))
    Ln[np.abs(Ln) < 1e-10] = 0.0

    perm = csg.reverse_cuthill_mckee(A.tocsr(), symmetric_mode=True)
    Ap = A[perm][:, perm].toarray()
    Lp = np.linalg.cholesky(Ap)
    Lp[np.abs(Lp) < 1e-10] = 0.0

    fig, axes = plt.subplots(1, 3, figsize=(6.7, 2.85),
                             gridspec_kw=dict(wspace=0.30, width_ratios=[1, 1, 1]))

    def spy(ax, M, color, tag, sub):
        idx = np.nonzero(np.abs(M) > 0)
        ax.plot(idx[1], idx[0], "s", ms=1.1, color=color, markeredgewidth=0, alpha=0.9)
        ax.set_xlim(-1.5, M.shape[1] + 0.5)
        ax.set_ylim(M.shape[0] + 0.5, -1.5)
        ax.set_aspect("equal")
        for sp_ in ("top", "right"):
            ax.spines[sp_].set_visible(False)
        ax.tick_params(labelsize=6.8, length=2.0)
        ax.set_xticks([0, 128, 255])
        ax.set_yticks([0, 128, 255])
        ax.set_xlabel("列", fontsize=7.8, labelpad=1)
        ax.set_ylabel("行" if tag.startswith("A") else "", fontsize=7.8, labelpad=6)
        ax.text(0.0, 1.10, tag, transform=ax.transAxes, fontsize=8.2, color=INK,
                ha="left", va="bottom")
        ax.text(0.0, 1.015, sub, transform=ax.transAxes, fontsize=7.6, color=MUTED,
                ha="left", va="bottom")

    nz_a = int(np.count_nonzero(Ad))
    nz_n = int(np.count_nonzero(Ln))
    nz_p = int(np.count_nonzero(Lp))
    spy(axes[0], Ad, INK, "A：五点格式", "%d 个非零，带宽 %d" % (nz_a, n))
    spy(axes[1], Ln, BLUE, "chol(A)，自然序", "%d 个非零，填进来 %d" % (nz_n, nz_n - (nz_a + n * n) // 2))
    spy(axes[2], Lp, GREEN, "chol(PAP$^T$)，RCM 序", "%d 个非零，填进来 %d" % (nz_p, nz_p - (nz_a + n * n) // 2))

    save(fig, "06", "fig06-01")


# ---------------------------------------------------------------- 图 6-2
# 共轭梯度：两种条件数下的残差曲线，外加理论收敛界
def cg_run(A, Aop, b, x0, iters, xt):
    x = x0.copy()
    r = b - Aop(x)
    p = r.copy()
    rr = r @ r
    e = x - xt
    out = [np.sqrt(e @ Aop(e)) / np.sqrt((x0 - xt) @ Aop(x0 - xt))]
    for _ in range(iters):
        Ap = Aop(p)
        a = rr / (p @ Ap)
        x = x + a * p
        r = r - a * Ap
        rr_new = r @ r
        e = x - xt
        out.append(np.sqrt(e @ Aop(e)) / np.sqrt((x0 - xt) @ Aop(x0 - xt)))
        if out[-1] < 1e-11:
            break
        p = r + (rr_new / rr) * p
        rr = rr_new
    return np.array(out)


def fig02():
    fig, ax = plt.subplots(figsize=(6.3, 3.30))

    cases = [(32, BLUE), (96, ACCENT)]
    info = []
    for n, c in cases:
        A = laplace2d(n)
        N = n * n
        b = np.ones(N)
        xt = sp.linalg.spsolve(A.tocsc(), b)
        err = cg_run(A.toarray(), lambda v: A @ v, b, np.zeros(N), 900, xt)
        k = np.arange(len(err))
        ax.semilogy(k, err, color=c, lw=1.5)

        cth = np.cos(np.pi / (n + 1))
        kappa = (1.0 + cth) / (1.0 - cth)
        kk = np.arange(0, len(err) + 2)
        bound = 2.0 * ((np.sqrt(kappa) - 1.0) / (np.sqrt(kappa) + 1.0)) ** kk
        ax.semilogy(kk, np.maximum(bound, 1e-11), color=c, lw=0.9, ls=(0, (4, 3)))
        hit = int(np.argmax(err < 1e-6))
        info.append((n, kappa, hit, len(err) - 1))

    ax.set_ylim(1e-9, 3.0)
    ax.set_xlim(0, 215)
    clean(ax, grid=True)
    ax.set_xlabel("迭代次数 $k$")
    ax.set_ylabel("相对 $A$-范数误差")
    ax.legend([r"$n=32$，$\kappa\approx 441$", "$n=32$ 的理论界",
               r"$n=96$，$\kappa\approx 3813$", "$n=96$ 的理论界"],
              loc="upper right", fontsize=7.8, handlelength=1.7, labelspacing=0.30,
              ncol=2, columnspacing=1.1, bbox_to_anchor=(1.01, 1.00))
    print("info:", info)

    save(fig, "06", "fig06-02")


# ---------------------------------------------------------------- 图 6-3
# 多重网格 V 循环（示意）
def fig03():
    fig, ax = canvas(6.7, 3.45, (0, 1), (0, 1))

    levels = [(16, 256, "$h$"), (8, 64, "$2h$"), (4, 16, "$4h$"), (2, 4, "$8h$")]
    ys = [0.790, 0.600, 0.410, 0.220]
    xg, wg, hg = 0.185, 0.395, 0.070

    arrow(ax, (0.040, 0.955), (0.070, 0.910), color=BLUE, lw=1.2, ms=8)
    label(ax, 0.082, 0.932, "限制 $R$：残差搬到粗网格", fs=8.2, ha="left", color=BLUE)
    arrow(ax, (0.420, 0.910), (0.450, 0.955), color=ACCENT, lw=1.2, ms=8)
    label(ax, 0.462, 0.932, "延拓 $P$：修正搬回细网格", fs=8.2, ha="left", color=ACCENT)

    for k, ((n, nunk, tag), y) in enumerate(zip(levels, ys)):
        grid(ax, xg, y - hg / 2, wg, hg, n, 2, color="#C9CDD4", lw=0.75)
        if k == 0:
            ax.add_patch(Rectangle((xg, y - hg / 2), wg, hg, fill=False, ec=INK, lw=1.0,
                                   zorder=3))
        label(ax, xg, y - hg / 2 - 0.030, tag, fs=8.4, ha="left", color=INK)
        label(ax, xg + 0.055, y - hg / 2 - 0.030, "%d 个未知量" % nunk, fs=7.4,
              ha="left", color=MUTED)

        if k < 3:
            label(ax, xg + wg + 0.030, y, "光滑 $\\nu_1+\\nu_2$ 次", fs=7.8, ha="left",
                  color=GREEN)
        else:
            label(ax, xg + wg + 0.030, y, "直接求解", fs=7.8, ha="left", color=ACCENT)

    for k in range(3):
        y0 = ys[k] - hg / 2 - 0.012
        y1 = ys[k + 1] + hg / 2 + 0.012
        arrow(ax, (0.150, y0), (0.150, y1), color=BLUE, lw=1.2, ms=8)
        arrow(ax, (0.830, y1), (0.830, y0), color=ACCENT, lw=1.2, ms=8)

    label(ax, 0.150, 0.085, "往粗网格走", fs=7.6, ha="center", color=BLUE)
    label(ax, 0.830, 0.085, "往回走", fs=7.6, ha="center", color=ACCENT)

    save(fig, "06", "fig06-03")


fig01()
fig02()
fig03()
