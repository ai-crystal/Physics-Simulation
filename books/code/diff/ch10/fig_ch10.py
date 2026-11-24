import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ============================================================
# 图 10-1  显式差分与 Fourier 层的一次推进对照（示意）
# ============================================================
def fig1():
    fig, ax = canvas(6.8, 4.5)

    # ---------------- (a) 显式差分 ----------------
    label(ax, 0.030, 0.998, "(a) 显式差分：一次推进", fs=8.6, color=MUTED,
          ha="left", va="top")

    x0, w, h = 0.065, 0.375, 0.112
    ys = [0.840, 0.665, 0.490, 0.315]
    texts = ["$\\mathbf{u}_n$：网格上的采样",
             "局部模板算 $\\partial_x\\mathbf{u}$\n（3–5 个格点）",
             "时间积分（显式 / RK）",
             "$\\mathbf{u}_{n+1}$"]
    for k, (y, t) in enumerate(zip(ys, texts)):
        box(ax, x0, y - h / 2, w, h, t, fc="white", ec=INK, fs=8.4, lw=1.0)
        if k:
            arrow(ax, (x0 + w / 2, ys[k - 1] - h / 2 - 0.004),
                  (x0 + w / 2, y + h / 2 + 0.004), color=FAINT, lw=1.0, ms=7)

    label(ax, x0 + w / 2, 0.200, "核的物理尺度 = 几个格子\n信息每步只传一跳",
          fs=7.9, color=MUTED)

    # ---------------- (b) Fourier 层 ----------------
    label(ax, 0.545, 0.998, "(b) Fourier 层：一次推进", fs=8.6, color=MUTED,
          ha="left", va="top")

    x1, w1, h1 = 0.575, 0.395, 0.088
    ys1 = [0.865, 0.745, 0.625, 0.505, 0.385, 0.265, 0.145]
    texts1 = ["$\\mathbf{u}_n$：网格上的采样",
              "lifting：逐点线性升到 $d$ 通道",
              "FFT：$\\hat{\\mathbf{u}}$，波数 $0\\dots N/2$",
              "截断：只留前 $K$ 个模态，乘 $\\mathbf{R}$",
              "逆变换回空间",
              "加逐点线性 $\\mathbf{W}$，过激活",
              "$\\mathbf{u}_{n+1}$"]
    for k, (y, t) in enumerate(zip(ys1, texts1)):
        hi = (k == 3)
        box(ax, x1, y - h1 / 2, w1, h1, t,
            fc=SOFT[0] if hi else "white",
            ec=ACCENT if hi else INK, fs=8.2, lw=1.2 if hi else 1.0)
        if k:
            arrow(ax, (x1 + w1 / 2, ys1[k - 1] - h1 / 2 - 0.003),
                  (x1 + w1 / 2, y + h1 / 2 + 0.003), color=FAINT, lw=1.0, ms=6)

    label(ax, x1 + w1 / 2, 0.070, "$K$ 是超参，与网格点数无关",
          fs=7.9, color=ACCENT)

    save(fig, "10", "fig10-01")


# ============================================================
# 图 10-2  模态截断与相对误差（真实计算）
#   一维周期平流 u_t + c u_x = 0，c = 1，域长 1，t = 0.3
#   精确解：在傅里叶空间乘相位 e^{-i k c t}；截断到前 K 个模态后重建
# ============================================================
NGRID = 4096
CFL = 1.0
TEND = 0.3


def trunc_err(u0, K):
    uh = np.fft.rfft(u0)
    k = np.arange(uh.size)
    phase = np.exp(-2j * np.pi * k * CFL * TEND)
    mask = np.zeros_like(uh)
    mask[:K] = 1.0
    ref = np.fft.irfft(uh * phase, NGRID)
    rec = np.fft.irfft(uh * mask * phase, NGRID)
    return np.linalg.norm(rec - ref) / np.linalg.norm(ref)


def fig2():
    x = np.linspace(0.0, 1.0, NGRID, endpoint=False)
    gauss = np.exp(-((x - 0.5) / 0.06) ** 2)
    gauss /= np.linalg.norm(gauss)
    kink = 1.0 - 2.0 * np.abs(x - 0.5)
    kink /= np.linalg.norm(kink)

    Ks = np.array([2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128])
    eg = np.array([trunc_err(gauss, K) for K in Ks])
    ek = np.array([trunc_err(kink, K) for K in Ks])

    fig, ax = plt.subplots(figsize=(6.5, 3.7))
    clean(ax, grid=True)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.6, 180)
    ax.set_ylim(5e-17, 2.0)

    ax.plot(Ks, ek, "o-", color=ACCENT, lw=1.6, ms=4.2,
            mfc="white", mew=1.0)
    ax.plot(Ks, eg, "s-", color=BLUE, lw=1.6, ms=4.0,
            mfc="white", mew=1.0)

    sl = slice(4, None)
    p = np.polyfit(np.log(Ks[sl]), np.log(ek[sl]), 1)[0]

    ax.annotate("折角初值：约 $K^{-1.5}$", xy=(6.0, 1.34e-2), xytext=(2.1, 7.0e-4),
                fontsize=8.5, color=ACCENT, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.8, alpha=0.65))
    ax.text(36, 0.25, "光滑初值：指数下降，\n24 个模态即到机器精度",
            fontsize=8.4, color=BLUE, ha="left", va="top")

    ax.set_xlabel("保留的模态数 $K$")
    ax.set_ylabel("相对 $L^2$ 误差")
    ax.set_xticks([2, 4, 8, 16, 32, 64, 128])
    ax.set_xticklabels(["2", "4", "8", "16", "32", "64", "128"])
    ax.set_yticks([1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1e0])

    save(fig, "10", "fig10-02")

    print("gauss:", ", ".join("%d:%.2e" % (K, e) for K, e in zip(Ks, eg)))
    print("kink :", ", ".join("%d:%.2e" % (K, e) for K, e in zip(Ks, ek)))
    print("kink 拟合斜率 %.2f（K>=8）" % p)


if __name__ == "__main__":
    fig1()
    fig2()
