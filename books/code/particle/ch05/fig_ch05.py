import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 5-1  B 样条与权重分配（真实函数）
#   (a) 线性 / 二次 / 三次 B 样条
#   (b) 粒子从节点 i 走到节点 i+1 时，各节点的权重
# ============================================================

def spline_linear(s):
    a = np.abs(s)
    return np.where(a < 1.0, 1.0 - a, 0.0)


def spline_quad(s):
    a = np.abs(s)
    return np.where(a < 0.5, 0.75 - s * s,
                    np.where(a < 1.5, 0.5 * (1.5 - a) ** 2, 0.0))


def spline_cubic(s):
    a = np.abs(s)
    return np.where(a < 1.0, 2.0 / 3.0 - s * s + 0.5 * a ** 3,
                    np.where(a < 2.0, (2.0 - a) ** 3 / 6.0, 0.0))


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.45),
                               gridspec_kw=dict(width_ratios=[1.02, 1.0],
                                                wspace=0.26,
                                                bottom=0.315, top=0.97))

# ---------- (a) 三个核函数 ----------
s = np.linspace(-2.6, 2.6, 1401)
ax1.plot(s, spline_cubic(s), color=FAINT, lw=1.2, label="三次 B 样条")
ax1.plot(s, spline_quad(s), color=ACCENT, lw=2.0, label="二次 B 样条")
ax1.plot(s, spline_linear(s), color=BLUE, lw=1.2, ls=(0, (1.6, 1.6)), label="线性 B 样条")

for k in (-2, -1, 0, 1, 2):
    ax1.plot([k, k], [-0.045, 0], color=MUTED, lw=0.8, zorder=1)
    if k:
        ax1.text(k, -0.085, "$%d$" % k, fontsize=8, color=MUTED, ha="center", va="top")
ax1.text(0, -0.085, "$0$", fontsize=8, color=MUTED, ha="center", va="top")
ax1.text(-2.55, -0.085, "$s$", fontsize=8.5, color=MUTED, ha="left", va="top")

ax1.set_xlim(-2.65, 2.65)
ax1.set_ylim(-0.15, 1.08)
ax1.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax1.set_xticks([-2, -1, 0, 1, 2])
ax1.set_xticklabels([])
ax1.set_xlabel("到节点的距离（以格距计）")
ax1.set_ylabel("$N(s)$")
clean(ax1, grid=False)
ax1.legend(loc="upper right", bbox_to_anchor=(1.0, 1.02), handlelength=2.2,
           borderaxespad=0.0, labelspacing=0.45)
ax1.text(-2.52, 0.86, "支撑 $2h$", fontsize=8, color=BLUE, ha="left", va="center")
ax1.text(-2.52, 0.74, "支撑 $3h$", fontsize=8, color=ACCENT, ha="left", va="center")
ax1.text(-2.52, 0.62, "支撑 $4h$", fontsize=8, color=MUTED, ha="left", va="center")

# ---------- (b) 权重随粒子偏移变化 ----------
u = np.linspace(0.0, 1.0, 401)
# w_k = N(u - k)，k 为相对节点索引
# 粒子从节点 i 走到节点 i+1：w_k = N(u - k)
ax2.plot(u, spline_quad(u + 1.0), color=BLUE, lw=1.5, label="$w_{i-1}$")
ax2.plot(u, spline_quad(u), color=ACCENT, lw=2.0, label="$w_{i}$")
ax2.plot(u, spline_quad(u - 1.0), color=GREEN, lw=1.5, label="$w_{i+1}$")
ax2.plot(u, spline_quad(u - 2.0), color=PURPLE, lw=1.5, label="$w_{i+2}$")

ax2.plot(u, 1.0 - u, color=MUTED, lw=1.0, ls=(0, (1.6, 1.6)), label="线性：$w_i$、$w_{i+1}$")
ax2.plot(u, u, color=MUTED, lw=1.0, ls=(0, (1.6, 1.6)))

ax2.axvline(0.5, color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax2.annotate("", xy=(0.5, 1.185), xytext=(0.5, 1.10),
             arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8,
                             shrinkA=0, shrinkB=0, mutation_scale=7))
ax2.text(0.46, 1.135, "此处开始用到 $w_{i+2}$", fontsize=8, color=MUTED,
         ha="right", va="center")

ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1.22)
ax2.set_xticks([0, 0.5, 1.0])
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.set_xlabel("粒子相对节点 $i$ 的偏移 $s$（以格距计）")
ax2.set_ylabel("权重")
clean(ax2, grid=False)
h2, l2 = ax2.get_legend_handles_labels()
fig.legend(h2, l2, loc="lower center", bbox_to_anchor=(0.5, 0.012), ncol=5,
           frameon=False, fontsize=7.6, handlelength=1.8,
           columnspacing=1.35, handletextpad=0.6)

print("quad sum check:", [round(float(spline_quad(v + 1) + spline_quad(v)
                                    + spline_quad(v - 1) + spline_quad(v - 2)), 12)
                          for v in (0.0, 0.3, 0.5, 0.8, 1.0)])
save(fig, "05", "fig05-01")


# ============================================================
# 图 5-2  自由飞行弹性圆盘的角动量与动能（真实 MPM 计算）
#   二维 MPM：二次 B 样条、Neo-Hookean、无重力、无边界
#   PIC 与 APIC 的唯一差别是粒子是否携带 C_p
# ============================================================

def bspline_quad_1d(dx, h):
    """二次 B 样条与其导数，dx = x_p - x_i"""
    a = np.abs(dx) / h
    w = np.where(a < 0.5, 0.75 - a * a,
                 np.where(a < 1.5, 0.5 * (1.5 - a) ** 2, 0.0))
    dw = np.where(a < 0.5, -2.0 * dx / h ** 2,
                  np.where(a < 1.5, -np.sign(dx) * (1.5 - a) / h, 0.0))
    return w, dw


def run_disc(mode="APIC", n=64, R=0.22, rho=400.0, E=1.0e5, nu=0.3,
             omega=2.0, dt=1.0e-4, steps=1000, every=10):
    """圆盘自由飞行实验。返回 (步数, L/L0, K/K0) 数组。"""
    h = 1.0 / n
    ng = n + 1
    lam = E * nu / ((1 + nu) * (1 - 2 * nu))
    mu = E / (2 * (1 + nu))

    # 粒子：半径 R 的圆内，间距 h/2
    sp = h / 2.0
    g = np.arange(0.5 - R, 0.5 + R + 1e-9, sp)
    X, Y = np.meshgrid(g, g)
    P = np.stack([X.ravel(), Y.ravel()], 1)
    P = P[(P[:, 0] - 0.5) ** 2 + (P[:, 1] - 0.5) ** 2 < R * R]
    np_p = len(P)
    m = rho * sp * sp
    V0 = sp * sp

    d0 = P - 0.5
    v = np.stack([-omega * d0[:, 1], omega * d0[:, 0]], 1)   # 刚体转动
    C = np.zeros((np_p, 2, 2))
    F = np.tile(np.eye(2), (np_p, 1, 1))

    L0 = np.sum(m * (d0[:, 0] * v[:, 1] - d0[:, 1] * v[:, 0]))
    K0 = 0.5 * np.sum(m * (v * v).sum(1))
    I2 = np.eye(2)
    hist = [(0, 1.0, 1.0)]

    for step in range(steps):
        gm = np.zeros((ng, ng))
        gmv = np.zeros((ng, ng, 2))
        gf = np.zeros((ng, ng, 2))
        base = np.floor(P / h).astype(int)

        Wx, DWx, Ix = [], [], []
        Wy, DWy, Iy = [], [], []
        for k in (-1, 0, 1, 2):                    # 四个偏移，缺一不可
            w_, dw_ = bspline_quad_1d(P[:, 0] - (base[:, 0] + k) * h, h)
            Wx.append(w_); DWx.append(dw_); Ix.append(base[:, 0] + k)
            w_, dw_ = bspline_quad_1d(P[:, 1] - (base[:, 1] + k) * h, h)
            Wy.append(w_); DWy.append(dw_); Iy.append(base[:, 1] + k)
        Wx = np.stack(Wx, 1); DWx = np.stack(DWx, 1); Ix = np.stack(Ix, 1)
        Wy = np.stack(Wy, 1); DWy = np.stack(DWy, 1); Iy = np.stack(Iy, 1)

        # Neo-Hookean 应力
        J = F[:, 0, 0] * F[:, 1, 1] - F[:, 0, 1] * F[:, 1, 0]
        Finv = np.empty_like(F)
        Finv[:, 0, 0] = F[:, 1, 1] / J
        Finv[:, 0, 1] = -F[:, 0, 1] / J
        Finv[:, 1, 0] = -F[:, 1, 0] / J
        Finv[:, 1, 1] = F[:, 0, 0] / J
        FinvT = np.transpose(Finv, (0, 2, 1))
        Pm = mu * (F - FinvT) + lam * np.log(J)[:, None, None] * FinvT
        sig = Pm @ np.transpose(F, (0, 2, 1)) / J[:, None, None]
        Vp = V0 * J

        # ---- P2G ----
        for a in range(4):
            for b in range(4):
                w = Wx[:, a] * Wy[:, b]
                dwx = DWx[:, a] * Wy[:, b]
                dwy = Wx[:, a] * DWy[:, b]
                ix, iy = Ix[:, a], Iy[:, b]
                np.add.at(gm, (ix, iy), m * w)
                np.add.at(gmv, (ix, iy, 0), m * w * v[:, 0])
                np.add.at(gmv, (ix, iy, 1), m * w * v[:, 1])
                if mode == "APIC":
                    ox = ix * h - P[:, 0]
                    oy = iy * h - P[:, 1]
                    np.add.at(gmv, (ix, iy, 0), m * w * (C[:, 0, 0] * ox + C[:, 0, 1] * oy))
                    np.add.at(gmv, (ix, iy, 1), m * w * (C[:, 1, 0] * ox + C[:, 1, 1] * oy))
                np.add.at(gf, (ix, iy, 0), -Vp * (sig[:, 0, 0] * dwx + sig[:, 0, 1] * dwy))
                np.add.at(gf, (ix, iy, 1), -Vp * (sig[:, 1, 0] * dwx + sig[:, 1, 1] * dwy))

        act = gm > 1e-14
        vel = np.zeros_like(gmv)
        vel[act] = gmv[act] / gm[act][:, None]
        vel[act] += dt * gf[act] / gm[act][:, None]

        # ---- G2P ----
        vnew = np.zeros_like(v)
        Cacc = np.zeros((np_p, 2, 2))
        gv = np.zeros((np_p, 2, 2))
        for a in range(4):
            for b in range(4):
                w = Wx[:, a] * Wy[:, b]
                dwx = DWx[:, a] * Wy[:, b]
                dwy = Wx[:, a] * DWy[:, b]
                ix, iy = Ix[:, a], Iy[:, b]
                gi = vel[ix, iy]
                vnew += w[:, None] * gi
                gv[:, 0, 0] += dwx * gi[:, 0]
                gv[:, 0, 1] += dwy * gi[:, 0]
                gv[:, 1, 0] += dwx * gi[:, 1]
                gv[:, 1, 1] += dwy * gi[:, 1]
                if mode == "APIC":
                    ox = ix * h - P[:, 0]
                    oy = iy * h - P[:, 1]
                    Cacc[:, 0, 0] += w * gi[:, 0] * ox
                    Cacc[:, 0, 1] += w * gi[:, 0] * oy
                    Cacc[:, 1, 0] += w * gi[:, 1] * ox
                    Cacc[:, 1, 1] += w * gi[:, 1] * oy

        v = vnew
        if mode == "APIC":
            C = 4.0 / h ** 2 * Cacc          # D_p = h^2/4 I，直接乘
        F = (I2[None] + dt * gv) @ F
        P = P + dt * v

        if (step + 1) % every == 0:
            d = P - 0.5
            L = np.sum(m * (d[:, 0] * v[:, 1] - d[:, 1] * v[:, 0]))
            K = 0.5 * np.sum(m * (v * v).sum(1))
            hist.append((step + 1, L / L0, K / K0))

    return np.array(hist), np_p, L0, K0


dt = 1.0e-4
runs = [("PIC", 64, ACCENT, "-", "PIC（$64\\times64$）"),
        ("APIC", 64, BLUE, "-", "APIC（$64\\times64$）"),
        ("PIC", 128, MUTED, (0, (4, 2.5)), "PIC（$128\\times128$）")]

res = {}
NP_DISC = 0
for mode, n, col, ls, lab in runs:
    hh, npp, L0, K0 = run_disc(mode=mode, n=n, steps=1000, every=10)
    res[(mode, n)] = hh
    NP_DISC = npp
    print("%-5s n=%3d  N=%d  L0=%.4f  L/L0(t=20ms)=%.4f  L/L0end=%.4f  K/K0=%.2e"
          % (mode, n, npp, L0, hh[len(hh) // 5, 1], hh[-1, 1], hh[-1, 2]))

fig, (axL, axK) = plt.subplots(1, 2, figsize=(6.8, 3.0), sharex=True,
                               gridspec_kw=dict(wspace=0.24, bottom=0.185, top=0.965))

for mode, n, col, ls, lab in runs:
    hh = res[(mode, n)]
    t = hh[:, 0] * dt * 1000.0           # ms
    lw = 2.0 if mode == "APIC" else 1.5
    axL.plot(t, hh[:, 1], color=col, lw=lw, ls=ls, label=lab)
    axK.plot(t, hh[:, 2], color=col, lw=lw, ls=ls)

for ax, ylab in ((axL, "角动量 $L/L_0$"), (axK, "动能 $K/K_0$")):
    ax.axhline(1.0, color=FAINT, lw=0.8, ls=(0, (2, 3)), zorder=1)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.03, 1.07)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("时间（ms）")
    ax.set_ylabel(ylab)
    clean(ax, grid=False)

axL.legend(loc="upper right", bbox_to_anchor=(0.985, 0.87), handlelength=2.4,
           borderaxespad=0.0, labelspacing=0.42, fontsize=8.2)
save(fig, "05", "fig05-02")
