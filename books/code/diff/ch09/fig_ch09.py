import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import itertools
import numpy as np


# ============================================================
# 图 9-1  一次消息传递（示意）
# ============================================================
def fig1():
    fig, ax = canvas(6.8, 3.3)

    # ---------- (a) 局部图 ----------
    label(ax, 0.02, 0.995, "(a) 一张局部图", fs=8.6, color=MUTED, ha="left", va="top")

    ci = (0.215, 0.485)
    nb = [(0.075, 0.815), (0.065, 0.180), (0.360, 0.815), (0.365, 0.180)]
    for p in nb:
        ax.plot([ci[0], p[0]], [ci[1], p[1]], color="#C9CDD4", lw=1.1, zorder=1)
    for p in nb:
        ax.plot([p[0]], [p[1]], "o", ms=8.5, mfc="white", mec=INK, mew=1.0, zorder=3)
    ax.plot([ci[0]], [ci[1]], "o", ms=9.5, mfc=SOFT[0], mec=ACCENT, mew=1.2, zorder=3)

    label(ax, ci[0] + 0.048, ci[1] + 0.005, "$i$", fs=9.5, color=ACCENT)
    label(ax, ci[0], ci[1] - 0.105, "$\\mathbf{h}_i$", fs=9.2, color=ACCENT)
    for p in nb:
        dy = 0.070 if p[1] > 0.5 else -0.070
        label(ax, p[0], p[1] + dy, "$j$", fs=9.0, color=MUTED)
    label(ax, 0.425, 0.815, "$\\mathbf{h}_j$", fs=9.2, color=MUTED)
    label(ax, 0.180, 0.675, "$\\mathbf{e}_{ij}$", fs=9.2, color=BLUE)
    label(ax, 0.215, 0.040, "邻居集合 $\\mathcal{N}(i)$，每条边带一个相对位置",
          fs=7.9, color=MUTED)

    ax.annotate("", xy=(0.478, 0.500), xytext=(0.438, 0.500),
                arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=1.1))

    # ---------- (b) 一次消息传递 ----------
    label(ax, 0.500, 0.995, "(b) 一次消息传递", fs=8.6, color=MUTED, ha="left", va="top")

    cx, bw, bh = 0.720, 0.300, 0.122
    ys = [0.865, 0.690, 0.515, 0.340, 0.165]
    texts = ["输入\n$\\mathbf{h}_i,\\ \\mathbf{h}_j,\\ \\mathbf{e}_{ij}$",
             "边网络\n$\\phi_e$",
             "对入边求和\n$\\bar{\\mathbf{e}}_i=\\sum_{j}\\mathbf{e}_{ij}$",
             "节点网络\n$\\phi_h$",
             "新特征\n$\\mathbf{h}_i^{\\,l+1}$"]
    for k, (y, t) in enumerate(zip(ys, texts)):
        ec = ACCENT if k in (1, 3) else INK
        fc = "white"
        box(ax, cx - bw / 2, y - bh / 2, bw, bh, t, fc=fc, ec=ec, fs=8.6, lw=1.0)
        if k:
            arrow(ax, (cx, ys[k - 1] - bh / 2 - 0.004), (cx, y + bh / 2 + 0.004),
                  color=FAINT, lw=1.0, ms=7)
    label(ax, 0.905, ys[2], "置换不变", fs=8.0, color=GREEN, ha="left")
    label(ax, 0.905, ys[4], "层叠 $L$ 次\n信息传 $L$ 跳", fs=8.0, color=MUTED,
          ha="left", va="center")

    save(fig, "09", "fig09-01")


# ============================================================
# 图 9-2  自回归 rollout 的误差增长（真实计算）
#   系统：x'' = -x - 0.35 x^3，dt = 0.05 s，RK4
#   代理：状态的多项式特征上的一次映射，最小二乘拟合
#   参考解 300 条轨迹，每条 400 步；测试 32 组未见初值，推 800 步
# ============================================================
DT = 0.05
CUB = 0.35


def rhs(s):
    x, v = s[:, 0], s[:, 1]
    return np.stack([v, -x - CUB * x ** 3], axis=1)


def rk4(s):
    k1 = rhs(s)
    k2 = rhs(s + 0.5 * DT * k1)
    k3 = rhs(s + 0.5 * DT * k2)
    k4 = rhs(s + DT * k3)
    return s + DT / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def feats(s, deg):
    x, v = s[:, 0], s[:, 1]
    cols = []
    for d in range(deg + 1):
        for comb in itertools.combinations_with_replacement(range(2), d):
            c = np.ones(s.shape[0])
            if 0 in comb:
                c = c * x ** comb.count(0)
            if 1 in comb:
                c = c * v ** comb.count(1)
            cols.append(c)
    return np.stack(cols, axis=1)


def rollout_err(W, deg, ref, reset=0):
    n = ref.shape[1]
    s = ref[:, 0].copy()
    e = np.zeros(n)
    for k in range(n):
        if reset and k % reset == 0:
            s = ref[:, k].copy()
        e[k] = np.sqrt(np.mean((s - ref[:, k]) ** 2))
        s = s + feats(s, deg) @ W
    return e


def fig2():
    rng = np.random.default_rng(0)

    S0 = rng.uniform(-1.5, 1.5, (300, 2))
    T = np.zeros((300, 400, 2))
    s = S0.copy()
    for k in range(400):
        T[:, k] = s
        s = rk4(s)

    X = T[:, :-1].reshape(-1, 2)
    Y = T[:, 1:].reshape(-1, 2)
    W, err1 = {}, {}
    for deg in (2, 3):
        F = feats(X, deg)
        W[deg] = np.linalg.lstsq(F, Y - X, rcond=None)[0]
        err1[deg] = np.sqrt(np.mean((X + F @ W[deg] - Y) ** 2))

    N = 800
    S = rng.uniform(-1.5, 1.5, (32, 2))
    ref = np.zeros((32, N, 2))
    s = S.copy()
    for k in range(N):
        ref[:, k] = s
        s = rk4(s)

    e3 = rollout_err(W[3], 3, ref)
    e2 = rollout_err(W[2], 2, ref)
    e3r = rollout_err(W[3], 3, ref, reset=40)

    n = np.arange(N)
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    clean(ax, grid=True)
    ax.set_yscale("log")
    ax.set_xlim(0, N - 1)
    ax.set_ylim(1.5e-6, 40)

    ax.plot(n, e2, color=ACCENT, lw=1.7)
    ax.plot(n, e3, color=BLUE, lw=1.7)
    ax.plot(n, np.where(e3r > 0, e3r, np.nan), color=GREEN, lw=1.25, ls="--")

    ax.text(N - 10, 4.2, "二次特征代理，单步误差 $6.8\\times 10^{-3}$",
            fontsize=8.4, color=ACCENT, ha="right", va="bottom")
    ax.text(N - 10, 2.4e-3, "三次特征代理，单步误差 $2.3\\times 10^{-6}$",
            fontsize=8.4, color=BLUE, ha="right", va="bottom")
    ax.text(470, 6.6e-5, "同一模型，每 40 步\n用真值重置一次",
            fontsize=8.2, color=GREEN, ha="left", va="bottom")

    ax.set_xlabel("自回归步数")
    ax.set_ylabel("整条轨迹上的均方根误差")

    save(fig, "09", "fig09-02")

    print("one-step: deg2 %.3e  deg3 %.3e" % (err1[2], err1[3]))
    print("800 步误差: deg2 %.3e  deg3 %.3e  reset %.3e" % (e2[-1], e3[-1], e3r.max()))


if __name__ == "__main__":
    fig1()
    fig2()
