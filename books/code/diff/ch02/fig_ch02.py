import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 2-1
# 计算图的前向与反向（结构示意，数值按 x1=1.2, x2=0.8 计算）。
def fig01():
    x1v, x2v = 1.2, 0.8
    u = x1v * x2v
    v = np.sin(u)
    y = v * x1v
    yb = 1.0
    vb = yb * x1v
    ub = vb * np.cos(u)
    x1b = yb * v + ub * x2v
    x2b = ub * x1v

    fig, ax = canvas(6.8, 3.45)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.plot([0.0, 1.0], [0.0, 1.0], alpha=0.01, lw=0.1)

    R = 0.055
    W, H = 0.070, 0.132
    P = {"x1": (0.078, 0.630), "x2": (0.078, 0.262), "u": (0.322, 0.436),
         "v": (0.548, 0.436), "y": (0.780, 0.630)}
    edges = [("x1", "u", 0.0), ("x2", "u", 0.0), ("u", "v", 0.0),
             ("v", "y", 0.0), ("x1", "y", -0.15)]
    for a, b, rad in edges:
        p0, p1 = np.array(P[a]), np.array(P[b])
        d = p1 - p0
        d = d / np.linalg.norm(d)
        arrow(ax, tuple(p0 + d * R), tuple(p1 - d * R), color=INK, lw=1.0,
              rad=rad, ms=7, shrinkA=0, shrinkB=0)

    def node(key, sym, fs=9.4):
        x, yy = P[key]
        box(ax, x - W / 2, yy - H / 2, W, H, sym, fc="white", ec=INK, fs=fs,
            lw=1.1, rounded=0.028)

    node("x1", r"$x_1$")
    node("x2", r"$x_2$")
    node("u", r"$\times$", 11.5)
    node("v", r"$\sin$", 8.8)
    node("y", r"$\times$", 11.5)

    fv = {"x1": "%.3f" % x1v, "x2": "%.3f" % x2v, "u": "%.3f" % u,
          "v": "%.3f" % v, "y": "%.3f" % y}
    bv = {"x1": "%.3f" % x1b, "x2": "%.3f" % x2b, "u": "%.3f" % ub,
          "v": "%.3f" % vb, "y": "%.1f" % yb}
    for k in fv:
        x, yy = P[k]
        label(ax, x, yy + H / 2 + 0.046, fv[k], fs=8.4, color=INK)
    for k in bv:
        x, yy = P[k]
        label(ax, x, yy - H / 2 - 0.046, bv[k], fs=8.4, color=PURPLE)

    label(ax, 0.780, 0.805, "输出", fs=8.0, color=FAINT)
    label(ax, 0.078, 0.805, "输入", fs=8.0, color=FAINT)

    ax.scatter([0.185], [0.130], s=26, facecolor="white", edgecolor=INK, lw=1.0)
    label(ax, 0.208, 0.130, "前向：节点上方的值", fs=8.2, color=INK, ha="left")
    ax.scatter([0.185], [0.055], s=26, facecolor="white", edgecolor=PURPLE, lw=1.0)
    label(ax, 0.208, 0.055, "反向：节点下方的梯度", fs=8.2, color=PURPLE, ha="left")

    save(fig, "02", "fig02-01")


# ---------------------------------------------------------------- 图 2-2
# 有限差分的误差随步长（真实计算），以及求梯度所需的求值次数。
def fig02():
    f = lambda z: np.exp(np.sin(z ** 3))
    df = lambda z: np.exp(np.sin(z ** 3)) * np.cos(z ** 3) * 3 * z ** 2
    X = np.linspace(0.35, 0.65, 15)
    REF = df(X)

    hs = np.logspace(-16, -2.4, 400)[:, None]
    e_fd = np.mean(np.abs((f(X + hs) - f(X)) / hs - REF) / np.abs(REF), axis=1)
    e_cd = np.mean(np.abs((f(X + hs) - f(X - hs)) / (2 * hs) - REF)
                     / np.abs(REF), axis=1)
    e_cs = np.mean(np.abs(np.imag(f(X + 1j * hs)) / hs - REF) / np.abs(REF),
                     axis=1)
    hs = hs[:, 0]

    fig = plt.figure(figsize=(6.8, 3.35))
    ax = fig.add_axes([0.093, 0.175, 0.495, 0.775])
    ax.loglog(hs, e_fd, color=ACCENT, lw=1.5, label="前向差分")
    ax.loglog(hs, e_cd, color=BLUE, lw=1.5, label="中心差分")
    ax.loglog(hs, e_cs, color=GREEN, lw=1.5, label="复数步长")
    ax.axhline(2.2e-16, color=PURPLE, lw=1.4, ls=(0, (5, 2)),
               label="反向自动微分")
    i1, i2 = np.argmin(e_fd), np.argmin(e_cd)
    ax.plot([hs[i1]], [e_fd[i1]], "o", ms=4.4, mfc="white", mec=ACCENT,
            mew=1.3, zorder=6)
    ax.plot([hs[i2]], [e_cd[i2]], "o", ms=4.4, mfc="white", mec=BLUE,
            mew=1.3, zorder=6)
    ax.set_xlabel("步长 $h$", labelpad=2)
    ax.set_ylabel("平均相对误差", labelpad=2)
    ax.set_xlim(1e-16, 6e-3)
    ax.set_ylim(1e-17, 2e1)
    ax.tick_params(labelsize=8.6, length=2.6, pad=2)
    clean(ax, grid=True)
    ax.legend(loc="upper center", fontsize=7.8, handlelength=1.7,
              labelspacing=0.3, borderaxespad=0.3, ncol=2,
              bbox_to_anchor=(0.52, 1.01))

    ax2 = fig.add_axes([0.685, 0.175, 0.300, 0.775])
    n = np.logspace(0, 4, 200)
    ax2.loglog(n, n + 1, color=ACCENT, lw=1.5, label="$n+1$（前向差分）")
    ax2.loglog(n, 2 * n, color=BLUE, lw=1.5, ls=(0, (5, 2)),
               label="$2n$（中心差分）")
    ax2.loglog(n, 3 * np.ones_like(n), color=PURPLE, lw=1.4,
               label="约 3（自动微分）")
    ax2.set_xlabel("参数个数 $n$", labelpad=2)
    ax2.set_ylabel("求一次全梯度的求值次数", labelpad=2)
    ax2.set_xlim(1, 1e4)
    ax2.set_ylim(1, 3e4)
    ax2.tick_params(labelsize=8.6, length=2.6, pad=2)
    clean(ax2, grid=True)
    ax2.legend(loc="upper left", fontsize=7.4, handlelength=1.6,
               labelspacing=0.3, borderaxespad=0.3)

    save(fig, "02", "fig02-02")
    print("h_fd=%.2e e=%.2e | h_cd=%.2e e=%.2e"
          % (hs[i1], e_fd[i1], hs[i2], e_cd[i2]))


if __name__ == "__main__":
    fig01()
    fig02()
