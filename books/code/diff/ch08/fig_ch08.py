# -*- coding: utf-8 -*-
"""第 8 章插图：参数辨识的收敛（真实计算）与形状优化的迭代（示意）。

图 8-1 左：四个初值下损失随迭代次数的下降（纵轴对数）；
图 8-1 右：损失在 (k, c) 平面上的等高线与四条 Adam 优化路径。
图 8-2   ：两维悬臂形状优化的四帧示意。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *          # noqa: E402,F401,F403

import numpy as np              # noqa: E402
from matplotlib.colors import LinearSegmentedColormap   # noqa: E402
from matplotlib.patches import Polygon                  # noqa: E402

# ---------------------------------------------------------------- 振子模型
DT = 1.0 / 120.0        # 采样间隔 1/120 s
NS = 360                # 采样点数（3 s × 120 Hz）
MASS = 1.0
K_TRUE, C_TRUE = 60.0, 1.2      # 真值 N/m, N·s/m
SEED = 3                        # 观测噪声的随机种子
INITS = [(18.0, 0.15), (120.0, 3.2), (45.0, 0.2), (230.0, 6.5)]
LR_K, LR_C = 0.5, 0.012         # Adam 对 k 与 c 的步长
STEPS = 400
COLORS = [ACCENT, BLUE, GREEN, PURPLE]


def rollout(k, c):
    """RK4 前向积分，同时带两个前向敏感度 ∂u/∂k、∂u/∂c。

    k、c 可以是同形状的数组（一次算一整张参数网格或一批初值）。
    返回位置序列 u 与敏感度 Su、Tu，形状均为 (NS+1,)+k.shape。
    """
    k = np.asarray(k, float)
    c = np.asarray(c, float)
    shape = np.broadcast(k, c).shape
    u, v = np.ones(shape), np.zeros(shape)          # 位置、速度
    su, sv = np.zeros(shape), np.zeros(shape)       # ∂/∂k
    tu, tv = np.zeros(shape), np.zeros(shape)       # ∂/∂c
    U = np.empty((NS + 1,) + shape)
    Su = np.empty((NS + 1,) + shape)
    Tu = np.empty((NS + 1,) + shape)
    U[0], Su[0], Tu[0] = u, su, tu
    h = DT
    m = MASS
    for i in range(NS):
        # 状态 + 两条切线一并 RK4：
        # u' = v,           v' = (-k u - c v)/m
        # ∂u' = sv,         ∂v' = (-k su - c sv - u)/m
        # t' = [tv, (-k tu - c tv - v)/m]
        a1u, a1v = v, (-k * u - c * v) / m
        b1u, b1v = sv, (-k * su - c * sv - u) / m
        c1u, c1v = tv, (-k * tu - c * tv - v) / m
        u2, v2 = u + 0.5 * h * a1u, v + 0.5 * h * a1v
        s2, q2 = su + 0.5 * h * b1u, sv + 0.5 * h * b1v
        t2, r2 = tu + 0.5 * h * c1u, tv + 0.5 * h * c1v
        a2u, a2v = v2, (-k * u2 - c * v2) / m
        b2u, b2v = q2, (-k * s2 - c * q2 - u2) / m
        c2u, c2v = r2, (-k * t2 - c * r2 - v2) / m
        u3, v3 = u + 0.5 * h * a2u, v + 0.5 * h * a2v
        s3, q3 = su + 0.5 * h * b2u, sv + 0.5 * h * b2v
        t3, r3 = tu + 0.5 * h * c2u, tv + 0.5 * h * c2v
        a3u, a3v = v3, (-k * u3 - c * v3) / m
        b3u, b3v = q3, (-k * s3 - c * q3 - u3) / m
        c3u, c3v = r3, (-k * t3 - c * r3 - v3) / m
        u4, v4 = u + h * a3u, v + h * a3v
        s4, q4 = su + h * b3u, sv + h * b3v
        t4, r4 = tu + h * c3u, tv + h * c3v
        a4u, a4v = v4, (-k * u4 - c * v4) / m
        b4u, b4v = q4, (-k * s4 - c * q4 - u4) / m
        c4u, c4v = r4, (-k * t4 - c * r4 - v4) / m
        u = u + h / 6.0 * (a1u + 2 * a2u + 2 * a3u + a4u)
        v = v + h / 6.0 * (a1v + 2 * a2v + 2 * a3v + a4v)
        su = su + h / 6.0 * (b1u + 2 * b2u + 2 * b3u + b4u)
        sv = sv + h / 6.0 * (b1v + 2 * b2v + 2 * b3v + b4v)
        tu = tu + h / 6.0 * (c1u + 2 * c2u + 2 * c3u + c4u)
        tv = tv + h / 6.0 * (c1v + 2 * c2v + 2 * c3v + c4v)
        U[i + 1], Su[i + 1], Tu[i + 1] = u, su, tu
    return U, Su, Tu


def loss_grad(k, c, obs):
    """L = ½ Σ (u_i - u_i^obs)²，返回 L 及其对 k、c 的梯度。"""
    U, Su, Tu = rollout(k, c)
    o = np.asarray(obs, float).reshape((NS,) + (1,) * (U.ndim - 1))
    r = U[1:] - o
    L = 0.5 * np.sum(r * r, axis=0)
    return L, np.sum(Su[1:] * r, axis=0), np.sum(Tu[1:] * r, axis=0)


def make_obs(seed=SEED, noise=0.01):
    """含噪观测：噪声标准差取峰值的 1%。"""
    clean = rollout(K_TRUE, C_TRUE)[0]
    sig = noise * np.max(np.abs(clean))
    rng = np.random.default_rng(seed)
    obs = clean + rng.normal(0.0, sig, clean.shape)
    obs[0] = clean[0]           # 初始位置按已知条件处理
    return obs[1:], sig


def adam_paths(obs, k0, c0, lrk=LR_K, lrc=LR_C, steps=STEPS):
    """并行跑一批初值，返回迭代轨迹 (steps+1, n)。"""
    k = np.array(k0, float)
    c = np.array(c0, float)
    m = np.zeros((2,) + k.shape)
    v = np.zeros((2,) + k.shape)
    b1, b2 = 0.9, 0.999
    K = np.empty((steps + 1,) + k.shape)
    C = np.empty((steps + 1,) + c.shape)
    L = np.empty((steps + 1,) + k.shape)
    for t in range(steps + 1):
        L[t], gk, gc = loss_grad(k, c, obs)
        K[t], C[t] = k, c
        if t == steps:
            break
        i = t + 1
        m[0] = b1 * m[0] + (1 - b1) * gk
        m[1] = b1 * m[1] + (1 - b1) * gc
        v[0] = b2 * v[0] + (1 - b2) * gk ** 2
        v[1] = b2 * v[1] + (1 - b2) * gc ** 2
        k = k - lrk * (m[0] / (1 - b1 ** i)) / (np.sqrt(v[0] / (1 - b2 ** i)) + 1e-8)
        c = c - lrc * (m[1] / (1 - b1 ** i)) / (np.sqrt(v[1] / (1 - b2 ** i)) + 1e-8)
    return K, C, L


def hessian(obs, k=K_TRUE, c=C_TRUE, h=1e-3):
    """真值处 ½Σr² 的 Hessian（有限差分），用于报告条件数。"""
    L0 = loss_grad(k, c, obs)[0]
    Lkk = (loss_grad(k + h, c, obs)[0] - 2 * L0 + loss_grad(k - h, c, obs)[0]) / h ** 2
    Lcc = (loss_grad(k, c + h, obs)[0] - 2 * L0 + loss_grad(k, c - h, obs)[0]) / h ** 2
    Lkc = (loss_grad(k + h, c + h, obs)[0] - loss_grad(k + h, c - h, obs)[0]
           - loss_grad(k - h, c + h, obs)[0] + loss_grad(k - h, c - h, obs)[0]) / (4 * h * h)
    return np.array([[Lkk, Lkc], [Lkc, Lcc]])


# ---------------------------------------------------------------- 图 8-1
def fig1():
    obs, sig = make_obs()
    K, C, L = adam_paths(obs, [p[0] for p in INITS], [p[1] for p in INITS])
    L_floor = loss_grad(K_TRUE, C_TRUE, obs)[0]
    H = hessian(obs)
    ev = np.linalg.eigvalsh(H)

    print("[8-1] 噪声 σ = %.4f，真值残差 L = %.4f" % (sig, L_floor))
    for i, p in enumerate(INITS):
        print("      初值 (%.0f, %.2f) → (%.2f, %.3f)，L = %.4f"
              % (p[0], p[1], K[-1, i], C[-1, i], L[-1, i]))
    print("      Hessian 特征值 %.3f / %.2f，条件数 %.0f" % (ev[0], ev[1], ev[1] / ev[0]))

    fig = plt.figure(figsize=(6.75, 3.12))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.06], wspace=0.30,
                          left=0.085, right=0.985, bottom=0.16, top=0.965)
    axa = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])

    # ---------------- 左：损失下降 ----------------
    it = np.arange(1, STEPS + 1)
    for i, p in enumerate(INITS):
        axa.loglog(it, L[1:, i], color=COLORS[i], lw=1.45,
                   label=r"$(%.0f,\ %.2g)$" % (p[0], p[1]))
    axa.axhline(L_floor, color=FAINT, lw=0.9, ls=(0, (5, 3)), zorder=1,
                label="噪声下限 $%.4f$" % L_floor)
    axa.set_xscale("log")
    axa.set_xlim(1.0, 420.0)
    axa.set_ylim(0.011, 3.2e2)
    axa.set_xlabel("迭代次数")
    axa.set_ylabel("损失 $L$")
    axa.set_xticks([1, 10, 100, 400])
    axa.set_xticklabels(["1", "10", "100", "400"])
    axa.set_xticks([], minor=True)
    axa.set_yticks([1e-2, 1e-1, 1e0, 1e1, 1e2])
    clean(axa, grid=True)
    label(axa, 405, 14.6, "残差 %.1f" % L[-1, 3], fs=8.0, color=PURPLE,
          ha="right", va="bottom")
    leg = axa.legend(loc="lower left", fontsize=8.0, handlelength=1.6, ncol=1,
                     borderaxespad=0.45, labelspacing=0.32, frameon=True,
                     facecolor="white", edgecolor="none", framealpha=0.92,
                     title="初值 $(k_0,\\ c_0)$", title_fontsize=8.0)
    leg.get_frame().set_linewidth(0.0)
    label(axa, 0.04, 0.955, "(a)", fs=9.6, color=MUTED, ha="left", va="top",
          transform=axa.transAxes)

    # ---------------- 右：损失景观与优化路径 ----------------
    kl = np.linspace(np.log10(13.0), np.log10(320.0), 240)
    cl = np.linspace(np.log10(0.13), np.log10(9.5), 240)
    Xg, Yg = np.meshgrid(10.0 ** kl, 10.0 ** cl)
    Zg = np.log10(loss_grad(Xg, Yg, obs)[0])

    cmap = LinearSegmentedColormap.from_list(
        "paper", ["#FFFDF9", "#FDF3E3", "#F9E7CB", "#F1D5AC", "#E3BC86"])
    levels = np.arange(-1.5, 1.75, 0.4)
    cf = axb.contourf(Xg, Yg, Zg, levels=levels, cmap=cmap, extend="both", zorder=1)
    axb.contour(Xg, Yg, Zg, levels=levels, colors="#B0813F", linewidths=0.55,
                alpha=0.8, zorder=2)

    for i in range(len(INITS)):
        axb.plot(K[:, i], C[:, i], color=COLORS[i], lw=1.15, zorder=5,
                 solid_capstyle="round")
        axb.plot(K[::20, i], C[::20, i], "o", ms=2.3, mfc="white", mec=COLORS[i],
                 mew=0.75, zorder=6)
    for i in range(len(INITS)):
        axb.plot([INITS[i][0]], [INITS[i][1]], "o", ms=4.4, mfc="white",
                 mec=COLORS[i], mew=1.1, zorder=7)
        axb.plot([K[-1, i]], [C[-1, i]], marker="x", ms=4.6, mew=1.15,
                 color=COLORS[i], zorder=8, ls="none")
    axb.plot([K_TRUE], [C_TRUE], marker="*", ms=12.0, color=INK, mec="white",
             mew=0.6, zorder=9, ls="none")

    axb.set_xscale("log")
    axb.set_yscale("log")
    axb.set_xlim(10 ** kl[0], 10 ** kl[-1])
    axb.set_ylim(10 ** cl[0], 10 ** cl[-1])
    axb.set_xlabel("刚度 $k$  (N/m)")
    axb.set_ylabel("阻尼 $c$  (N·s/m)")
    xt = [20, 30, 60, 100, 200]
    axb.set_xticks(xt)
    axb.set_xticklabels([str(t) for t in xt])
    axb.set_xticks([], minor=True)
    axb.set_yticks([0.2, 0.5, 1, 2, 5])
    axb.set_yticklabels(["0.2", "0.5", "1", "2", "5"])
    axb.set_yticks([], minor=True)
    clean(axb)

    cb = fig.colorbar(cf, ax=axb, fraction=0.048, pad=0.02, aspect=24)
    cb.set_ticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2])
    cb.set_ticklabels([r"$10^{-1.5}$", r"$10^{-1}$", r"$10^{-0.5}$", r"$10^{0}$",
                       r"$10^{0.5}$", r"$10^{1}$", r"$10^{1.5}$", r"$10^{2}$"])
    cb.set_label("损失 $L$", fontsize=8.8)
    cb.ax.tick_params(labelsize=8.0, length=2.2, pad=1.5)
    cb.outline.set_linewidth(0.5)
    cb.outline.set_edgecolor(FAINT)

    # 标注：真值与停滞点（白底，避免压线）
    box = dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none",
               alpha=0.88)
    axb.annotate("真值 $(60,\\ 1.2)$", xy=(K_TRUE, C_TRUE), xytext=(20.0, 3.05),
                 fontsize=8.0, color=INK, ha="left", va="center", zorder=11,
                 bbox=box,
                 arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.65,
                                 shrinkA=2, shrinkB=4))
    axb.annotate("停在 $(%.1f,\\ %.1f)$" % (K[-1, 3], C[-1, 3]),
                 xy=(K[-1, 3], C[-1, 3]), xytext=(104.0, 4.55),
                 fontsize=8.0, color=PURPLE, ha="left", va="center", zorder=11,
                 bbox=box,
                 arrowprops=dict(arrowstyle="-", color=PURPLE, lw=0.65,
                                 shrinkA=2, shrinkB=4))
    label(axb, 0.04, 0.955, "(b)", fs=9.6, color=MUTED, ha="left", va="top",
          transform=axb.transAxes)
    save(fig, "08", "fig08-01")


# ---------------------------------------------------------------- 图 8-2
# 左端固支、下边受均布载荷的悬臂剖面：四帧形状族 + 法向敏感度箭头（示意）。
H0, H1 = 0.74, 0.30          # 左端、右端高度


def hprof(x, t):
    """剖面高度：t=0 为矩形，t=1 为等弯曲应力的收敛形状（h² 随 x 线性下降）。"""
    x = np.clip(x, 0, 1)
    return H0 * np.sqrt(1.0 - (1.0 - (H1 / H0) ** 2) * t * x)


def dhprof(x, t):
    eps = 1e-4
    return (hprof(x + eps, t) - hprof(x - eps, t)) / (2 * eps)


def cant_poly(t, n=200):
    x = np.linspace(0.0, 1.0, n)
    top = np.column_stack([x, hprof(x, t)])
    bot = np.column_stack([x[::-1], np.zeros(n)])
    return np.vstack([top, bot])


def fig2():
    frames = [(0.00, "(a) 初值", 1.00),
              (0.42, "(b) 第 40 次", 0.68),
              (0.80, "(c) 第 120 次", 0.42),
              (1.00, "(d) 收敛", 0.26)]

    fig = plt.figure(figsize=(6.72, 2.16))
    gs = fig.add_gridspec(1, 4, wspace=0.04, left=0.010, right=0.990,
                          bottom=0.02, top=0.98)

    for j, (t, cap, amp) in enumerate(frames):
        ax = fig.add_subplot(gs[j])
        ax.set_xlim(-0.24, 1.16)
        ax.set_ylim(-0.40, 0.98)
        ax.axis("off")
        ax.set_aspect("equal")

        if t > 0:   # 初值轮廓与填色
            ax.add_patch(Polygon(cant_poly(t), closed=True, facecolor="#FDF3E7",
                                 edgecolor="none", zorder=1))
            ax.add_patch(Polygon(cant_poly(0.0), closed=True, facecolor="none",
                                 edgecolor=FAINT, lw=0.75, ls=(0, (3.2, 2.4)),
                                 zorder=2))
        ax.add_patch(Polygon(cant_poly(t), closed=True, facecolor="none",
                             edgecolor=ACCENT, lw=1.2, zorder=3,
                             joinstyle="round"))

        # 左端固支：粗线 + 斜影线
        ax.plot([0, 0], [0, hprof(0, t)], color=INK, lw=1.8, zorder=5,
                solid_capstyle="butt")
        for y in np.linspace(0.04, hprof(0, t) - 0.04, 7):
            ax.plot([0, -0.075], [y, y + 0.065], color=MUTED, lw=0.65, zorder=4)

        # 下边均布载荷
        for x in np.linspace(0.04, 0.96, 5):
            ax.annotate("", xy=(x, -0.17), xytext=(x, -0.005),
                        arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=0.8,
                                        mutation_scale=6.0, shrinkA=0, shrinkB=0),
                        zorder=5)
        if j == 0:
            label(ax, 0.52, -0.28, "均布载荷 $q$", fs=8.2, color=SLATE,
                  va="center", ha="center")

        # 法向敏感度：上边界向下（去料），自由端向左（去料）
        for x in np.linspace(0.10, 0.92, 8):
            xt = hprof(x, t)
            d = dhprof(x, t)
            u = np.array([-d, 1.0])
            u /= np.linalg.norm(u)
            s = -(0.20 + 0.80 * x ** 1.3)
            p = np.array([x, xt])
            ln = amp * 0.105 * s
            ax.annotate("", xy=(p + u * (-0.020 + ln)), xytext=(p + u * -0.020),
                        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.75,
                                        mutation_scale=5.0, shrinkA=0, shrinkB=0),
                        zorder=6)
        for y in np.linspace(0.16, 0.86, 3):
            p = np.array([1.0, y * hprof(1.0, t)])
            ln = amp * 0.075
            ax.annotate("", xy=(p[0] - 0.020 - ln, p[1]), xytext=(p[0] - 0.020, p[1]),
                        arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.75,
                                        mutation_scale=5.0, shrinkA=0, shrinkB=0),
                        zorder=6)

        label(ax, -0.22, 0.93, cap, fs=8.4, color=MUTED, ha="left", va="center")

    save(fig, "08", "fig08-02")


if __name__ == "__main__":
    fig1()
    fig2()
