import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import matplotlib.ticker as mticker

# ============================================================
# 图 4-1  MPM 一轮循环（示意图）
# ============================================================
fig, ax = canvas(6.6, 3.75)

box(ax, 0.035, 0.735, 0.355, 0.155,
    "粒子状态\n$m_p,\\ \\mathbf{x}_p,\\ \\mathbf{v}_p,\\ \\mathbf{F}_p$",
    fc=SOFT[1], ec=BLUE, fs=9.0, tc=INK)
box(ax, 0.610, 0.735, 0.355, 0.155,
    "网格质量与动量\n$m_i,\\ (m\\mathbf{v})_i,\\ \\mathbf{f}_i$",
    fc=SOFT[4], ec=ACCENT, fs=9.0, tc=INK)
box(ax, 0.610, 0.085, 0.355, 0.155,
    "节点速度\n$\\mathbf{v}_i \\leftarrow \\mathbf{v}_i + \\Delta t\\,\\mathbf{f}_i/m_i$",
    fc=SOFT[4], ec=ACCENT, fs=9.0, tc=INK)
box(ax, 0.035, 0.085, 0.355, 0.155,
    "粒子速度与梯度\n$\\mathbf{v}_p,\\ \\nabla\\mathbf{v}_p$",
    fc=SOFT[2], ec=GREEN, fs=9.0, tc=INK)

arrow(ax, (0.398, 0.812), (0.602, 0.812), color=BLUE, lw=1.3, ms=9)
label(ax, 0.500, 0.845, "P2G", fs=8.8, color=BLUE, weight="bold")

arrow(ax, (0.788, 0.730), (0.788, 0.252), color=ACCENT, lw=1.3, ms=9)
label(ax, 0.836, 0.491, "解动量方程", fs=8.6, color=ACCENT, rot=90)

arrow(ax, (0.602, 0.163), (0.398, 0.163), color=GREEN, lw=1.3, ms=9)
label(ax, 0.500, 0.196, "G2P", fs=8.8, color=GREEN, weight="bold")

arrow(ax, (0.212, 0.247), (0.212, 0.730), color=MUTED, lw=1.3, ms=9)
label(ax, 0.163, 0.489, "更新 $\\mathbf{F}$，推进 $\\mathbf{x}$", fs=8.4, color=MUTED, rot=90)

# 中央：粒子落在网格上的示意
gx, gy, gw, gh = 0.412, 0.415, 0.176, 0.190
grid(ax, gx, gy, gw, gh, 4, 4, color=GRID, lw=0.7)
rng = np.random.default_rng(7)
px = gx + gw * (0.08 + 0.84 * rng.random(11))
py = gy + gh * (0.08 + 0.84 * rng.random(11))
ax.scatter(px, py, s=12, color=PURPLE, alpha=0.85, zorder=5, linewidths=0)
for i in range(5):
    for j in range(5):
        ax.scatter([gx + gw * i / 4], [gy + gh * j / 4], s=6, color=MUTED, zorder=6, linewidths=0)
label(ax, 0.500, 0.375, "同一团材料的两种表示", fs=7.6, color=FAINT)

save(fig, "04", "fig04-01")


# ============================================================
# 图 4-2  一维弹性杆：MPM 与解析解
#   自由边界、纯拉伸/压缩呼吸模态 u(x,0) = A cos(pi x / L)
#   E = 1e6 Pa, rho = 1000, L = 1, A = 5 mm
#   c = 31.62 m/s, omega = 99.35 rad/s, T = 63.2 ms
# ============================================================
E, RHO, L, AMP = 1.0e6, 1000.0, 1.0, 5.0e-3
C = np.sqrt(E / RHO)
OMEGA = np.pi * C / L
TPER = 2.0 * np.pi / OMEGA


def shape2(x, dx, off):
    s = x / dx
    i = np.floor(s).astype(int)
    f = s - i
    nodes = np.stack([i - 1 + off, i + off, i + 1 + off], axis=1)
    w = np.stack([0.5 * (1 - f) ** 2, 0.75 - (f - 0.5) ** 2, 0.5 * f * f], axis=1)
    dw = np.stack([-(1 - f), 1 - 2 * f, f], axis=1) / dx
    return nodes, w, dw


def run_mpm(N, ppc=2, nper=1.5, nrec=420):
    """一维 MPM，返回 (时间数组, 左端粒子位移, 解析位移)。"""
    dx = L / N
    dt = 0.32 * dx / C
    M = N * ppc
    sp = dx / ppc
    x0 = (np.arange(M) + 0.5) * sp
    xp = x0 + AMP * np.cos(np.pi * x0 / L)
    vp = np.zeros(M)
    Fp = 1.0 - np.pi * AMP / L * np.sin(np.pi * x0 / L)
    up = AMP * np.cos(np.pi * x0 / L).copy()
    mp = RHO * sp
    off = 4
    ng = off + N + 12
    nnode = ng + off + 1

    nstep = int(nper * TPER / dt)
    rec = max(1, nstep // nrec)
    ts, us = [], []
    for step in range(nstep):
        nodes, w, dw = shape2(xp, dx, off)
        sig = E * (Fp - 1.0)
        mi = np.zeros(nnode)
        mvi = np.zeros(nnode)
        fi = np.zeros(nnode)
        np.add.at(mi, nodes, w * mp)
        np.add.at(mvi, nodes, w * (mp * vp)[:, None])
        np.add.at(fi, nodes, -sp * sig[:, None] * dw)
        mi = np.maximum(mi, 1e-13)
        vi = mvi / mi + dt * fi / mi
        v = np.sum(w * vi[nodes], axis=1)
        g = np.sum(dw * vi[nodes], axis=1)
        vp = v
        Fp = Fp * (1.0 + dt * g)
        xp = xp + dt * vp
        up = up + dt * vp
        if step % rec == 0:
            ts.append(step * dt)
            us.append(up[0])
    ts = np.array(ts)
    us = np.array(us)
    ua = AMP * np.cos(OMEGA * ts)
    err = np.abs(us - ua).max() / AMP
    return ts, us, ua, err, dx, dt


ts, us, ua, err, dx, dt = run_mpm(200)
print(f"N=200 dx={dx*1e3:.2f} mm dt={dt:.3e} s err={err:.4f}")

res = []
for N in (50, 100, 200, 400):
    tt, uu, uu_a, e, dxx, dtt = run_mpm(N, nrec=260)
    res.append((dxx, e))
    print(f"  N={N:3d} dx={dxx*1e3:5.2f} mm dt={dtt:.2e} err={e:.4f}")

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.0),
                               gridspec_kw=dict(width_ratios=[1.25, 1.0], wspace=0.34))
for a in (axL, axR):
    clean(a, grid=True, spines=("left", "bottom"))

axL.plot(ts * 1e3, ua * 1e3, color=BLUE, lw=1.6, zorder=4, label="解析解")
step_m = max(1, len(ts) // 70)
axL.plot(ts[::step_m] * 1e3, us[::step_m] * 1e3, color=ACCENT, lw=1.2,
         marker="o", ms=2.7, mfc="white", mew=0.85, zorder=5, label="MPM")
axL.set_xlim(0, ts[-1] * 1e3)
axL.set_ylim(-6.4, 7.6)
axL.set_xlabel("时间 (ms)")
axL.set_ylabel("$u$ (mm)")
axL.set_yticks([-5, 0, 5])
axL.legend(loc="upper right", fontsize=8.2, handlelength=1.6, borderpad=0.2,
           labelspacing=0.35, handletextpad=0.5)

dxs = np.array([r[0] for r in res])
errs = np.array([r[1] for r in res])
axR.plot(dxs * 1e3, errs, color=GREEN, lw=1.2, marker="o", ms=4.6, zorder=4)
ref = errs[2] * (dxs * 1e3) / (dxs[2] * 1e3)
axR.plot(dxs * 1e3, ref, color=FAINT, lw=1.0, ls=(0, (4, 3)), zorder=3)
axR.set_xscale("log")
axR.set_yscale("log")
axR.set_xlim(2.25, 28)
axR.set_ylim(0.013, 0.33)
axR.set_xlabel(r"网格尺寸 $\Delta x$ (mm)")
axR.set_ylabel("相对误差")
axR.set_xticks([2.5, 5, 10, 20])
axR.set_xticklabels(["2.5", "5", "10", "20"])
axR.set_yticks([0.02, 0.05, 0.1, 0.2])
axR.set_yticklabels(["0.02", "0.05", "0.1", "0.2"])
axR.xaxis.set_minor_formatter(mticker.NullFormatter())
axR.yaxis.set_minor_formatter(mticker.NullFormatter())
axR.text(2.45, 0.0192, "斜率 1", fontsize=8.0, color=FAINT, ha="left", va="top")
axR.text(0.965, 0.055, r"$\Delta t = 0.32\,\Delta x/c$", fontsize=8.0, color=MUTED,
         ha="right", va="bottom", transform=axR.transAxes)

save(fig, "04", "fig04-02")
