import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ---------------------------------------------------------------- 模型
# 双摆（杆端质点 m1=m2=1 kg，杆长 L1=L2=1 m），状态 x = [th1, th2, w1, w2]
G = 9.81
DT = 1.0 / 600.0
TMAX = 8.0
P = 1.0          # 名义杆长（辨识参数即 L1）
PREF = 1.05      # 参考轨迹的杆长


def rhs(x, L1, L2, c):
    t1, t2, w1, w2 = x
    m1 = m2 = 1.0
    d = t1 - t2
    den = 2 * m1 + m2 - m2 * np.cos(2 * t1 - 2 * t2)
    a1 = (-G * (2 * m1 + m2) * np.sin(t1) - m2 * G * np.sin(t1 - 2 * t2)
          - 2 * np.sin(d) * m2 * (w2 * w2 * L2 + w1 * w1 * L1 * np.cos(d))) / (L1 * den) - c * w1
    a2 = (2 * np.sin(d) * (w1 * w1 * L1 * (m1 + m2) + G * (m1 + m2) * np.cos(t1)
                           + w2 * w2 * L2 * m2 * np.cos(d))) / (L2 * den) - c * w2
    return np.array([w1, w2, a1, a2])


def step(x, L1=P, c=0.0, dt=DT):
    k1 = rhs(x, L1, 1.0, c)
    k2 = rhs(x + 0.5 * dt * k1, L1, 1.0, c)
    k3 = rhs(x + 0.5 * dt * k2, L1, 1.0, c)
    k4 = rhs(x + dt * k3, L1, 1.0, c)
    return x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def jac_step(x, c, h=1e-6):
    A = np.zeros((4, 4))
    for j in range(4):
        e = np.zeros(4)
        e[j] = h
        A[:, j] = (step(x + e, P, c) - step(x - e, P, c)) / (2 * h)
    return A


def dstep_dp(x, c, h=1e-6):
    return (step(x, P + h, c) - step(x, P - h, c)) / (2 * h)


def record(x0, c, T=TMAX):
    """一次前向，记下逐时刻的跟踪损失分项与若干雅可比。"""
    n = int(round(T / DT))
    x = x0.copy()
    xr = x0.copy()
    S = np.zeros(4)
    terms = np.zeros(n)
    svals = []
    for i in range(n):
        A = jac_step(x, c)
        Cp = dstep_dp(x, c)
        x = step(x, P, c)
        xr = step(xr, PREF, c)
        S = A @ S + Cp
        terms[i] = S @ (x - xr)
    return terms


def lyapunov(x0, c, T=8.0, d0=1e-7):
    x = x0.copy()
    y = x0 + np.array([d0, 0, 0, 0])
    n = int(round(T / DT))
    s = 0.0
    for _ in range(n):
        x = step(x, P, c)
        y = step(y, P, c)
        d = np.linalg.norm(y - x)
        if d > 1e-6:
            y = x + (y - x) * (d0 / d)
            s += np.log(d / d0)
    return s / (n * DT)


X0_CHAOS = np.array([2.4, 2.2, 0.0, 0.0])
X0_QUASI = np.array([0.45, 0.35, 0.0, 0.0])
CASES = [
    ("混沌（无阻尼）", X0_CHAOS, 0.0, ACCENT),
    ("准周期（无阻尼）", X0_QUASI, 0.0, BLUE),
    ("阻尼（$c=3$ /s）", X0_CHAOS, 3.0, GREEN),
]


def main():
    # ---------- 三个系统各跑一遍，拿到逐时刻分项 ----------
    data = []
    for name, x0, c, col in CASES:
        terms = record(x0, c)
        data.append((name, terms, col))
    lam = lyapunov(X0_CHAOS, 0.0, 8.0)

    # ---------------------------------------------------------------- 图 7-1
    Ts = np.arange(0.25, TMAX + 1e-9, 0.25)
    fig = plt.figure(figsize=(6.5, 3.35))
    ax = fig.add_axes([0.115, 0.155, 0.865, 0.815])
    for name, terms, col in data:
        n = len(terms)
        cum = np.cumsum(terms)
        vals = np.array([abs(cum[int(round(T / DT)) - 1]) for T in Ts])
        ax.semilogy(Ts, vals, color=col, lw=1.5, marker="o", ms=2.6,
                    markerfacecolor="white", markeredgewidth=0.7, label=name)
    # 阻尼平台
    label(ax, 6.05, 1.25e3, "饱和于 5.3×10²", fs=8.2, color=GREEN, ha="left")

    ax.set_xlim(0, 8.1)
    ax.set_ylim(1.0, 6.0e9)
    ax.set_xlabel("窗口长度 T  (s)")
    ax.set_ylabel("梯度范数 |∂L/∂θ|")
    ax.set_xticks([0, 2, 4, 6, 8])
    clean(ax, grid=True)
    ax.legend(loc="lower right", fontsize=8.4, handlelength=2.0,
              borderaxespad=0.4, ncol=1)
    label(ax, 0.32, 1.6e9, f"混沌：λ ≈ {lam:.1f} /s", fs=8.8, color=ACCENT, ha="left")
    label(ax, 0.32, 1.6e8, "8 s 内梯度涨 6 个数量级", fs=8.8, color=ACCENT, ha="left")
    save(fig, "07", "fig07-01")

    # ---------------------------------------------------------------- 图 7-2
    fig = plt.figure(figsize=(6.9, 3.35))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.28,
                          left=0.085, right=0.985, bottom=0.285, top=0.955)
    axa = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])

    def smooth(w, m=121):
        box = np.ones(m) / m
        num = np.convolve(w, box, mode="same")
        den = np.convolve(np.ones_like(w), box, mode="same")
        return num / den

    ts = (np.arange(len(data[0][1])) + 1) * DT
    for name, terms, col in data:
        env = smooth(np.abs(terms))
        axa.plot(ts, env / env.max(), color=col, lw=1.45)
    axa.set_xlim(0, 8.1)
    axa.set_ylim(-0.03, 1.10)
    axa.set_xlabel("时刻 t  (s)")
    axa.set_ylabel("逐时刻分项 |τ| 的包络（归一化）")
    axa.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axa.set_xticks([0, 2, 4, 6, 8])
    clean(axa, grid=True)
    label(axa, 0.16, 0.93, "(a)", fs=9.6, color=MUTED, ha="left")

    Ks = np.arange(0.25, TMAX + 1e-9, 0.25)
    for name, terms, col in data:
        w = np.abs(terms)
        tot = w.sum()
        R = np.array([w[-int(round(K / DT)):].sum() / tot for K in Ks])
        axb.plot(Ks, R, color=col, lw=1.5, marker="o", ms=2.5,
                 markerfacecolor="white", markeredgewidth=0.7)
    axb.set_xlim(0, 8.1)
    axb.set_ylim(-0.03, 1.06)
    axb.set_xlabel("截断窗口长度 K  (s)")
    axb.set_ylabel("保留的分项质量比例")
    axb.set_xticks([0, 2, 4, 6, 8])
    axb.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    clean(axb, grid=True)
    label(axb, 0.16, 0.93, "(b)", fs=9.6, color=MUTED, ha="left")

    handles = [Line2D([0], [0], color=c, lw=1.6) for _, _, c in data]
    fig.legend(handles, [n for n, _, _ in data], loc="lower center", ncol=3,
               frameon=False, fontsize=8.4, handlelength=1.8,
               bbox_to_anchor=(0.5, 0.015), columnspacing=1.6)
    save(fig, "07", "fig07-02")


main()
