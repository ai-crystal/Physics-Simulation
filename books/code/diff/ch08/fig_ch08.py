import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

DT = 1.0 / 120.0
NS = 360                 # 3 s @ 120 Hz
K_TRUE, C_TRUE = 60.0, 1.2
NOISE = 0.01


# ---------------- 单自由度阻尼振子：u'' = -k u - c u'
def step(u, v, k, c, dt=DT):
    a1u = v
    a1v = -k * u - c * v
    u2 = u + 0.5 * dt * a1u
    v2 = v + 0.5 * dt * a1v
    a2u = v2
    a2v = -k * u2 - c * v2
    u3 = u + 0.5 * dt * a2u
    v3 = v + 0.5 * dt * a2v
    a3u = v3
    a3v = -k * u3 - c * v3
    u4 = u + dt * a3u
    v4 = v + dt * a3v
    a4u = v4
    a4v = -k * u4 - c * v4
    return (u + dt / 6.0 * (a1u + 2 * a2u + 2 * a3u + a4u),
            v + dt / 6.0 * (a1v + 2 * a2v + 2 * a3v + a4v))


def rollout_u(k, c, n=NS):
    u, v = 1.0, 0.0
    out = np.empty(n + 1)
    out[0] = u
    for i in range(n):
        u, v = step(u, v, k, c)
        out[i + 1] = u
    return out


def make_obs():
    clean = rollout_u(K_TRUE, C_TRUE)
    rng = np.random.default_rng(3)
    return clean + rng.normal(0.0, NOISE * np.abs(clean).max(), clean.size)


def loss_grad(k, c, uo, h=1e-6):
    """L = 1/2 Σ (u_i - u*_i)^2，梯度由逐步灵敏度递推得到，雅可比用中心差分。"""
    u, v = 1.0, 0.0
    sk_u = sk_v = sc_u = sc_v = 0.0
    L = gk = gc = 0.0
    for i in range(len(uo) - 1):
        # 一步映射对 (u,v) 的雅可比
        up, vp = step(u + h, v, k, c); um, vm = step(u - h, v, k, c)
        j11, j21 = (up - um) / (2 * h), (vp - vm) / (2 * h)
        up, vp = step(u, v + h, k, c); um, vm = step(u, v - h, k, c)
        j12, j22 = (up - um) / (2 * h), (vp - vm) / (2 * h)
        # 一步映射对参数的导数
        up, vp = step(u, v, k + h, c); um, vm = step(u, v, k - h, c)
        dk_u, dk_v = (up - um) / (2 * h), (vp - vm) / (2 * h)
        up, vp = step(u, v, k, c + h); um, vm = step(u, v, k, c - h)
        dc_u, dc_v = (up - um) / (2 * h), (vp - vm) / (2 * h)
        # 推进状态与两个敏感度
        u, v = step(u, v, k, c)
        sk_u, sk_v = j11 * sk_u + j12 * sk_v + dk_u, j21 * sk_u + j22 * sk_v + dk_v
        sc_u, sc_v = j11 * sc_u + j12 * sc_v + dc_u, j21 * sc_u + j22 * sc_v + dc_v
        r = u - uo[i + 1]
        L += 0.5 * r * r
        gk += sk_u * r
        gc += sc_u * r
    return L, np.array([gk, gc])


def adam(p0, uo, iters=400, lr=(0.5, 0.012)):
    p = np.array(p0, float)
    m = np.zeros(2)
    vv = np.zeros(2)
    b1, b2 = 0.9, 0.999
    hist = []
    path = [p.copy()]
    for t in range(1, iters + 1):
        L, g = loss_grad(p[0], p[1], uo)
        hist.append(L)
        m = b1 * m + (1 - b1) * g
        vv = b2 * vv + (1 - b2) * g * g
        p = p - np.array(lr) * m / (1 - b1 ** t) / (np.sqrt(vv / (1 - b2 ** t)) + 1e-12)
        p = np.clip(p, [5.0, 0.02], [300.0, 9.0])
        path.append(p.copy())
    hist.append(loss_grad(p[0], p[1], uo)[0])
    return np.array(hist), np.array(path)


def loss_grid(Kg, Cg, uo):
    u = np.ones_like(Kg)
    v = np.zeros_like(Kg)
    L = np.zeros_like(Kg)
    for i in range(len(uo) - 1):
        a1u, a1v = v, -Kg * u - Cg * v
        a2u = v + 0.5 * DT * a1v
        a2v = -Kg * (u + 0.5 * DT * a1u) - Cg * a2u
        a3u = v + 0.5 * DT * a2v
        a3v = -Kg * (u + 0.5 * DT * a2u) - Cg * a3u
        a4u = v + DT * a3v
        a4v = -Kg * (u + DT * a3u) - Cg * (v + DT * a3v)
        u = u + DT / 6.0 * (a1u + 2 * a2u + 2 * a3u + a4u)
        v = v + DT / 6.0 * (a1v + 2 * a2v + 2 * a3v + a4v)
        L += 0.5 * (u - uo[i + 1]) ** 2
    return L


# ---------------------------------------------------------------- 图 8-1
def fig01():
    uo = make_obs()
    starts = [((18.0, 0.15), BLUE, r"$(18,\,0.15)$"),
              ((45.0, 0.20), GREEN, r"$(45,\,0.20)$"),
              ((120.0, 3.2), PURPLE, r"$(120,\,3.2)$"),
              ((230.0, 6.5), ACCENT, r"$(230,\,6.5)$")]
    runs = []
    for p0, col, lab in starts:
        hist, path = adam(p0, uo)
        runs.append((hist, path, col, lab, p0))
        print(f"  {lab} -> {path[-1]}  L={hist[-1]:.5f}")

    fig = plt.figure(figsize=(6.9, 2.95))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.16], wspace=0.30,
                          left=0.085, right=0.985, bottom=0.175, top=0.955)
    axa = fig.add_subplot(gs[0])
    axb = fig.add_subplot(gs[1])

    # ---- 左：损失下降
    for hist, path, col, lab, p0 in runs:
        axa.semilogy(np.arange(len(hist)), np.maximum(hist, 1e-3), color=col,
                     lw=1.45, label=lab)
    axa.axhline(0.0185, color=FAINT, lw=0.8, ls=(0, (1, 2)))
    label(axa, 396, 0.0118, "噪声底 0.0185", fs=7.8, color=MUTED, ha="right")
    axa.set_xlim(0, 400)
    axa.set_ylim(1e-3, 2.5e2)
    axa.set_xlabel("Adam 迭代次数")
    axa.set_ylabel("损失 L")
    axa.set_xticks([0, 100, 200, 300, 400])
    clean(axa, grid=True)
    axa.legend(loc="lower left", fontsize=7.6, handlelength=1.6,
               borderaxespad=0.3, labelspacing=0.35)

    # ---- 右：等高线与路径
    kk = np.logspace(np.log10(9.0), np.log10(250.0), 170)
    cc = np.linspace(0.03, 9.0, 150)
    KK, CC = np.meshgrid(kk, cc)
    LL = loss_grid(KK.ravel(), CC.ravel(), uo).reshape(KK.shape)
    lv = np.logspace(np.log10(0.02), np.log10(60.0), 13)
    axb.contourf(KK, CC, LL, levels=lv, cmap="YlOrBr", alpha=0.42, zorder=1)
    axb.contour(KK, CC, LL, levels=lv, colors="#B08A55", linewidths=0.5, zorder=2)
    for hist, path, col, lab, p0 in runs:
        axb.plot(path[:, 0], path[:, 1], color=col, lw=1.45, zorder=4)
        axb.scatter([p0[0]], [p0[1]], s=16, facecolor="white", edgecolor=col,
                    linewidth=0.9, zorder=5)
        axb.scatter([path[-1, 0]], [path[-1, 1]], s=13, color=col, zorder=5,
                    marker="X")
    axb.scatter([K_TRUE], [C_TRUE], s=95, marker="*", facecolor="white",
                edgecolor=INK, linewidth=1.0, zorder=6)
    label(axb, K_TRUE + 12, C_TRUE + 0.30, "真值", fs=8.2, color=INK, ha="left")
    axb.annotate("卡在斜坡上", xy=(80.0, 6.35), xytext=(126.0, 7.9),
                 fontsize=8.0, color=ACCENT,
                 arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.8,
                                 shrinkA=2, shrinkB=3))
    axb.set_xlim(9, 250)
    axb.set_xscale("log")
    axb.set_ylim(0.03, 9.0)
    axb.set_xlabel("刚度 k  (N/m)")
    axb.set_ylabel("阻尼 c  (N·s/m)")
    axb.set_xticks([10, 20, 50, 100, 200])
    axb.set_xticklabels(["10", "20", "50", "100", "200"])
    axb.set_yticks([2, 4, 6, 8])
    clean(axb)
    save(fig, "08", "fig08-01")


# ---------------------------------------------------------------- 图 8-2
def fig02():
    fig = plt.figure(figsize=(6.9, 2.15))
    gs = fig.add_gridspec(1, 4, wspace=0.10, left=0.02, right=0.98,
                          bottom=0.16, top=0.98)
    stages = [(0.0, "初值"), (0.35, "第 20 次"), (0.72, "第 60 次"), (1.0, "收敛")]
    x0, L = 0.10, 0.86
    for idx, (a, tag) in enumerate(stages):
        ax = fig.add_subplot(gs[idx])
        ax.set_xlim(-0.06, 1.10)
        ax.set_ylim(-0.62, 0.62)
        ax.set_aspect("equal")
        ax.axis("off")
        xs = np.linspace(0.0, 1.0, 200)
        h = 0.20 * (1.0 - 0.62 * a * xs ** 0.85) + 0.035 * a * np.exp(-((xs - 0.12) / 0.14) ** 2)
        dy = -0.34 * a * xs ** 2
        X = x0 + L * xs
        up = np.stack([X, h + dy], axis=1)
        lo = np.stack([X[::-1], -h[::-1] + dy[::-1]], axis=1)
        poly = np.vstack([up, lo])
        ax.add_patch(Polygon(poly, closed=True, facecolor="#FDF2E9",
                             edgecolor=ACCENT, lw=1.2, zorder=3))
        # 固定端斜线
        for j in range(6):
            yy = -0.24 + 0.095 * j
            ax.plot([x0, x0 - 0.035], [yy, yy - 0.045], color=MUTED, lw=0.7, zorder=4)
        ax.plot([x0, x0], [-0.245, 0.245], color=INK, lw=1.4, zorder=4)
        # 法向敏感度箭头
        for xt in (0.22, 0.44, 0.66, 0.86):
            hx = 0.20 * (1.0 - 0.62 * a * xt ** 0.85) + 0.035 * a * np.exp(-((xt - 0.12) / 0.14) ** 2)
            dxl = -0.34 * a * xt ** 2
            ln = 0.10 * (0.35 + 0.9 * a) * (1.25 - xt)
            arrow(ax, (x0 + L * xt, hx + dxl + 0.012),
                  (x0 + L * xt, hx + dxl + 0.045 + ln),
                  color=BLUE, lw=0.9, ms=6, z=5)
            arrow(ax, (x0 + L * xt, -hx + dxl - 0.012),
                  (x0 + L * xt, -hx + dxl - 0.045 - ln * 0.7),
                  color=BLUE, lw=0.9, ms=6, z=5)
        label(ax, x0 + L * 0.5, -0.55, tag, fs=8.4, color=MUTED)
        if idx == 0:
            label(ax, x0 + 0.005, 0.30, "固定端", fs=7.8, color=MUTED, ha="left")
            label(ax, x0 + L * 0.5, 0.45, "法向敏感度", fs=7.6,
                  color=BLUE, ha="center")
    save(fig, "08", "fig08-02")


fig01()
fig02()
