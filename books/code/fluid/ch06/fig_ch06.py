# -*- coding: utf-8 -*-
"""第 6 章插图：三种界面表示、一维界面剖面。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


def radius(th):
    return 1.0 + 0.13 * np.sin(3 * th) + 0.06 * np.cos(5 * th)


def inside(X, Y):
    return np.sqrt(X ** 2 + Y ** 2) <= radius(np.arctan2(Y, X))


TH = np.linspace(0, 2 * np.pi, 721)
CX, CY = radius(TH) * np.cos(TH), radius(TH) * np.sin(TH)


def sdf(X, Y):
    """到离散曲线的最短距离，内部取负。"""
    d = np.full(X.shape, 1e9)
    for x0, y0 in zip(CX[::2], CY[::2]):
        d = np.minimum(d, np.hypot(X - x0, Y - y0))
    return np.where(inside(X, Y), -d, d)


# ---------------------------------------------------------------- 图 6-1
fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.95), gridspec_kw=dict(wspace=0.10))
LIM = 1.58

# 左：显式网格
ax = axs[0]
ax.fill(CX, CY, facecolor="#EFF4FF", edgecolor="none", zorder=1)
ax.plot(CX, CY, color=BLUE, lw=1.4, zorder=2)
idx = np.arange(0, 720, 30)
ax.scatter(CX[idx], CY[idx], s=12, facecolor="white", edgecolor=BLUE, lw=1.0, zorder=3)
ax.annotate("顶点", xy=(CX[24], CY[24]), xytext=(0.16, 1.42), fontsize=8.4, color=MUTED,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=-0.25"))
ax.text(0.5, -0.02, "显式三角网格", fontsize=9.0, color=INK, ha="center", va="top", transform=ax.transAxes)
ax.text(0.5, -0.11, "顶点随流体走，拓扑要重连", fontsize=8.0, color=MUTED, ha="center", va="top", transform=ax.transAxes)

# 中：Level Set
ax = axs[1]
gx = np.linspace(-LIM, LIM, 170)
GX, GY = np.meshgrid(gx, gx)
PHI = sdf(GX, GY)
for _ in range(4):  # 抹掉中线（medial axis）处的折痕，只影响远处的着色
    PHI = (PHI + np.roll(PHI, 1, 0) + np.roll(PHI, -1, 0)
           + np.roll(PHI, 1, 1) + np.roll(PHI, -1, 1)) / 5.0
ax.contourf(GX, GY, PHI, levels=np.linspace(-0.55, 1.0, 9), cmap="Blues_r", alpha=0.80,
            extend="min")
ax.contour(GX, GY, PHI, levels=[0], colors=[INK], linewidths=1.4)
ax.text(0.5, -0.02, "隐式距离函数", fontsize=9.0, color=INK, ha="center", va="top", transform=ax.transAxes)
ax.text(0.5, -0.11, r"$\phi=0$ 的等值面就是界面", fontsize=8.0, color=MUTED, ha="center", va="top", transform=ax.transAxes)

# 右：VOF
ax = axs[2]
n = 15
xe = np.linspace(-LIM, LIM, n + 1)
cw = xe[1] - xe[0]
sub = np.linspace(0.5 / 6, 1 - 0.5 / 6, 6)
for i in range(n):
    for j in range(n):
        PX, PY = np.meshgrid(xe[i] + sub * cw, xe[j] + sub[:, None] * cw)
        frac = inside(PX, PY).mean()
        ax.add_patch(Rectangle((xe[i], xe[j]), cw, cw, facecolor=TEAL,
                               alpha=0.05 + 0.80 * frac, edgecolor="none", zorder=2))
for x in xe:
    ax.plot([x, x], [-LIM, LIM], color="#D1D5DB", lw=0.5, zorder=3)
    ax.plot([-LIM, LIM], [x, x], color="#D1D5DB", lw=0.5, zorder=3)
ax.contour(GX, GY, PHI, levels=[0], colors=[INK], linewidths=1.0, linestyles="dashed", zorder=4)
ax.text(0.5, -0.02, "体积分数", fontsize=9.0, color=INK, ha="center", va="top", transform=ax.transAxes)
ax.text(0.5, -0.11, "每格只记液体占比", fontsize=8.0, color=MUTED, ha="center", va="top", transform=ax.transAxes)

for ax in axs:
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal")
    ax.axis("off")
save(fig, "06", "fig06-01")


# ---------------------------------------------------------------- 图 6-2
N = 64
dx = 1.0 / N
xc = (np.arange(N) + 0.5) * dx
x0, x1 = 0.28, 0.72
u, cfl = 1.0, 0.6
dt = cfl * dx / u
nst = 120


def phi_init(x):
    return np.maximum(x0 - x, x - x1)


def adv_sl(phi):
    """半拉格朗日回溯 + 线性插值（格子中心网格）。"""
    s = (xc - u * dt) / dx - 0.5
    i0 = np.floor(s).astype(int) % N
    fr = s - np.floor(s)
    return (1 - fr) * phi[i0] + fr * phi[(i0 + 1) % N]


def vof_init():
    lo = np.clip(x0, xc - dx / 2, xc + dx / 2)
    hi = np.clip(x1, xc - dx / 2, xc + dx / 2)
    return np.maximum(0.0, hi - lo) / dx


def adv_vof(C):
    """一阶迎风（donor cell）通量形式，u>0。"""
    Fl = u * np.roll(C, 1)
    Fr = u * C
    return C - dt / dx * (Fr - Fl)


def reinit(phi, niter=6, dtau=0.4 * dx):
    """一维 Hamilton-Jacobi 重初始化，Godunov 迎风。"""
    p0 = np.asarray(phi, float)
    sgn = p0 / np.sqrt(p0 ** 2 + dx ** 2)
    p = p0.copy()
    for _ in range(niter):
        dm = (p - np.roll(p, 1)) / dx
        dp = (np.roll(p, -1) - p) / dx
        pos = np.sqrt(np.maximum(dm, 0) ** 2 + np.minimum(dp, 0) ** 2)
        neg = np.sqrt(np.maximum(dp, 0) ** 2 + np.minimum(dm, 0) ** 2)
        p = p - dtau * sgn * (np.where(sgn > 0, pos, neg) - 1.0)
    return p


def gradmag(p):
    dm = (p - np.roll(p, 1)) / dx
    dp = (np.roll(p, -1) - p) / dx
    pos = np.sqrt(np.maximum(dm, 0) ** 2 + np.minimum(dp, 0) ** 2)
    neg = np.sqrt(np.maximum(dp, 0) ** 2 + np.minimum(dm, 0) ** 2)
    return np.where(p > 0, pos, neg)


def liquid_len(p):
    """由 phi 的零等值点（线性插值定位）算液体总长，周期边界。"""
    q = np.asarray(p, float)
    cr = []
    for i in range(N):
        a, b = q[i], q[(i + 1) % N]
        if a * b < 0:
            xa = xc[i]
            xb = xc[i] + dx if i < N - 1 else xc[0] + 1.0
            cr.append(xa + (xb - xa) * a / (a - b))
    cr.sort()
    if len(cr) < 2:
        return 0.0
    if len(cr) != 2:
        return 0.0
    seg = cr[-1] - cr[0]
    return min(seg, 1.0 - seg)


phi0 = phi_init(xc)
C = vof_init()
vol0 = liquid_len(phi0)

# A：只平流，不动 phi 的距离性质
phiA = phi0.copy()
volA = []
for _ in range(nst):
    phiA = adv_sl(phiA)
    volA.append(liquid_len(phiA))

# B：每步平流后重初始化
phiB = phi0.copy()
volB, volC, phi_last = [], [], None
for _ in range(nst):
    phiB = adv_sl(phiB)
    phi_adv = phiB.copy()
    phiB = reinit(phiB)
    C = adv_vof(C)
    volB.append(liquid_len(phiB))
    volC.append(C.sum() * dx)
    phi_last = phi_adv

fig = plt.figure(figsize=(7.2, 3.2))
gs = fig.add_gridspec(2, 3, width_ratios=[1.28, 1.0, 1.02], height_ratios=[1, 1],
                      wspace=0.66, hspace=0.64)
axp = fig.add_subplot(gs[0, 0])
axc = fig.add_subplot(gs[1, 0], sharex=axp)
axg = fig.add_subplot(gs[:, 1])
axv = fig.add_subplot(gs[:, 2])

axp.plot(xc, phi0, color=FAINT, lw=1.2, ls=(0, (5, 2)), label=r"初始 $\phi$")
axp.plot(xc, phiB, color=INK, lw=1.4, label="平流 120 步后")
axp.axhline(0, color="#D1D5DB", lw=0.8)
axp.set_ylabel(r"$\phi$")
axp.set_ylim(-0.46, 0.36)
axp.set_yticks([-0.2, 0.0, 0.2])
axp.legend(fontsize=7.4, loc="lower center", handlelength=1.6, borderaxespad=0.1,
           labelspacing=0.25, ncol=2)

axc.step(xc - dx / 2, vof_init(), where="post", color=FAINT, lw=1.4, label="初始 $C$")
axc.step(xc - dx / 2, C, where="post", color=GREEN, lw=1.2, label="平流后")
axc.set_xlabel("$x$")
axc.set_ylabel("$C$")
axc.set_ylim(-0.06, 1.22)
axc.set_yticks([0.0, 0.5, 1.0])
axc.legend(fontsize=7.0, loc="upper right", handlelength=1.6, borderaxespad=0.1,
           labelspacing=0.3)
for a in (axp, axc):
    a.set_xlim(0, 1)
    clean(a)

axg.plot(xc, gradmag(phiA), color=ACCENT, lw=1.3, ls=(0, (4, 1.6)), label="只平流")
axg.plot(xc, gradmag(phi_last), color=BLUE, lw=1.1, ls=(0, (2, 2)), label="平流后（重初始化前）")
axg.plot(xc, gradmag(phiB), color=INK, lw=1.3, label="重初始化后")
axg.axhline(1.0, color=MUTED, lw=0.9, ls=(0, (2, 2)))
axg.set_xlabel("$x$")
axg.set_ylabel(r"$|\nabla\phi|$", labelpad=6)
axg.set_ylim(0, 1.78)
axg.set_xlim(0, 1)
axg.set_yticks([0, 0.5, 1.0])
axg.legend(fontsize=7.0, loc="upper center", borderpad=0.2, handlelength=1.6, borderaxespad=0.1,
           labelspacing=0.25)
clean(axg, grid=True)

t = np.arange(1, nst + 1) * dt
axv.plot(t, np.array(volC) / vol0, color=GREEN, lw=1.5, label="VOF")
axv.plot(t, np.array(volB) / vol0, color=INK, lw=1.4, label="LS 每步重初始化")
axv.plot(t, np.array(volA) / vol0, color=ACCENT, lw=1.3, ls=(0, (4, 1.6)), label="LS 只平流")
axv.set_xlabel("时间 $t$ / s")
axv.set_ylabel("体积 / 初始体积")
axv.set_ylim(0.9985, 1.0006)
axv.text(0.05, 0.78, "纵轴放大 500 倍", transform=axv.transAxes, fontsize=7.0, color=MUTED, ha="left")
axv.legend(fontsize=7.0, loc="lower left", handlelength=1.6, borderaxespad=0.1,
           labelspacing=0.25)
clean(axv, grid=True)

save(fig, "06", "fig06-02")
print("vol  LS+reinit %.4f   LS-only %.4f   VOF %.4f"
      % (volB[-1] / vol0, volA[-1] / vol0, volC[-1] / vol0))
print("|grad| min  after adv %.3f  after reinit %.3f  (only-advected %.3f)"
      % (gradmag(phi_last).min(), gradmag(phiB).min(), gradmag(phiA).min()))
