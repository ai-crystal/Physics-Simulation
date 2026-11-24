import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 5-1 三种求解器残差
def build_poisson(n):
    """二维五点差分 Poisson，返回稠密 A 与随机右端项（固定种子）。"""
    h = 1.0 / (n + 1)
    N = n * n
    A = np.zeros((N, N))

    def idx(i, j):
        return i * n + j

    for i in range(n):
        for j in range(n):
            k = idx(i, j)
            A[k, k] = 4.0 / h ** 2
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ii, jj = i + di, j + dj
                if 0 <= ii < n and 0 <= jj < n:
                    A[k, idx(ii, jj)] = -1.0 / h ** 2
    rng = np.random.default_rng(7)
    b = rng.standard_normal(N)
    b -= b.mean()
    return A, b, n


def residuals(A, b, n, iters=800):
    N = n * n
    x0 = np.zeros(N)
    r0 = np.linalg.norm(b)
    D = np.diag(A)

    res_j = []
    x = x0.copy()
    for _ in range(iters):
        x = x + (b - A @ x) / D
        res_j.append(np.linalg.norm(b - A @ x) / r0)

    res_g = []
    x = x0.copy()
    for _ in range(iters):
        for color in (0, 1):
            for i in range(n):
                for j in range(n):
                    if (i + j) % 2 == color:
                        k = i * n + j
                        s = b[k]
                        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ii, jj = i + di, j + dj
                            if 0 <= ii < n and 0 <= jj < n:
                                s -= A[k, ii * n + jj] * x[ii * n + jj]
                        x[k] = s / A[k, k]
        res_g.append(np.linalg.norm(b - A @ x) / r0)

    res_c = []
    x = x0.copy()
    r = b - A @ x
    p = r.copy()
    rs = r @ r
    for _ in range(iters):
        Ap = A @ p
        al = rs / (p @ Ap)
        x = x + al * p
        r = r - al * Ap
        rs2 = r @ r
        p = r + (rs2 / rs) * p
        rs = rs2
        res_c.append(np.sqrt(rs) / r0)

    return np.array(res_j), np.array(res_g), np.array(res_c)


def fig01():
    n = 32
    A, b, n = build_poisson(n)
    rj, rg, rc = residuals(A, b, n)
    it = np.arange(1, len(rj) + 1)

    fig, ax = plt.subplots(figsize=(6.5, 3.7))
    clean(ax, grid=True, spines=("left", "bottom"))

    floor = 1e-9
    mj = rj > floor
    mg = rg > floor
    mc = rc > floor
    ax.semilogy(it[mj], rj[mj], color=BLUE, lw=1.6, label="Jacobi")
    ax.semilogy(it[mg], rg[mg], color=GREEN, lw=1.6, label="红黑 Gauss-Seidel")
    ax.semilogy(it[mc], rc[mc], color=ACCENT, lw=1.7, label="共轭梯度")

    ax.set_xlim(0, 800)
    ax.set_ylim(1e-8, 2.0)
    ax.set_xlabel("迭代次数")
    ax.set_ylabel("相对残差  $\\Vert r^{k}\\Vert/\\Vert r^{0}\\Vert$")
    ax.axhline(1e-2, color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
    label(ax, 792, 1.25e-2, "百分之一", fs=8.2, color=MUTED, ha="right", va="bottom")

    def first(res, tol):
        idx = np.nonzero(res < tol)[0]
        return int(idx[0]) + 1 if len(idx) else None

    series = {1: rj, 2: rg, 3: rc}
    cols = {1: BLUE, 2: GREEN, 3: ACCENT}
    for key, col in cols.items():
        k = first(series[key], 1e-2)
        ax.plot([k], [1e-2], "o", ms=5.5, mfc="white", mec=col, mew=1.4, zorder=6)

    ax.text(0.30, 0.045, "空心点为残差降到 $10^{-2}$ 的位置：Jacobi 184 次，红黑 GS 96 次，CG 30 次",
            transform=ax.transAxes, fontsize=8.2, color=MUTED, ha="left", va="bottom")

    ax.legend(loc="upper right", bbox_to_anchor=(0.985, 0.985), handlelength=1.6,
              labelspacing=0.45)
    save(fig, "05", "fig05-01")


# ---------------------------------------------------------------- 5-2 V 循环
def fig02():
    fig, ax = canvas(6.5, 3.8)
    h = 0.13
    rows = [0.74, 0.45, 0.16]

    # 下行（限制）
    box(ax, 0.06, rows[0], 0.20, h, "平滑 ×2\n算残差 $r=b-Ax$", fc=LIGHT, ec=BLUE, fs=8.4)
    box(ax, 0.20, rows[1], 0.20, h, "平滑 ×2\n再限制残差", fc=LIGHT, ec=BLUE, fs=8.4)
    box(ax, 0.34, rows[2], 0.24, h, "最粗层　$64^{3}$\n直接解 / CG", fc="#FFF7ED", ec=ACCENT, fs=8.4)

    # 上行（延拓与修正）
    box(ax, 0.64, rows[1], 0.22, h, "延拓修正\n平滑 ×2", fc="#ECFDF5", ec=GREEN, fs=8.4)
    box(ax, 0.70, rows[0], 0.24, h, "延拓修正\n平滑 ×2", fc="#ECFDF5", ec=GREEN, fs=8.4)

    arrow(ax, (0.26, rows[0] + 0.035), (0.275, rows[1] + h + 0.008), color=BLUE, lw=1.1, ms=9)
    arrow(ax, (0.40, rows[1] + 0.035), (0.415, rows[2] + h + 0.008), color=BLUE, lw=1.1, ms=9)
    arrow(ax, (0.52, rows[2] + h - 0.02), (0.645, rows[1] + 0.035), color=GREEN, lw=1.1, ms=9)
    arrow(ax, (0.86, rows[1] + h - 0.03), (0.885, rows[0] + 0.012), color=GREEN, lw=1.1, ms=9)

    label(ax, 0.16, 0.955, "第 0 层　$256^{3}$", fs=8.6, color=MUTED)
    label(ax, 0.44, 0.635, "第 1 层　$128^{3}$", fs=8.6, color=MUTED, ha="left")
    label(ax, 0.34, 0.095, "粗化到一万个未知数左右即停", fs=8.0, color=FAINT, ha="left")
    label(ax, 0.50, 0.02, "蓝色为下行：限制算子 $R$　　绿色为上行：延拓算子 $P$ 与修正",
          fs=8.4, color=MUTED)
    save(fig, "05", "fig05-02")


if __name__ == "__main__":
    fig01()
    fig02()
