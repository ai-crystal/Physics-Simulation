import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 8-1  单摆的相空间
#   L = 1/2 m l^2 th'^2 + m g l cos(th)
#   归一化能量 e = E/(m g l) = 0.5*l*om^2/g - cos(th)
#   RK4，步长 1e-3 s，l = 1 m，g = 9.81 m/s^2
# ============================================================
G, L = 9.81, 1.0


def rhs(th, om, cs=0.0):
    return om, -(G / L) * np.sin(th) - cs * om


def rk4(th, om, h, n, cs=0.0):
    ths = np.empty(n + 1)
    oms = np.empty(n + 1)
    ths[0], oms[0] = th, om
    for i in range(n):
        k1 = rhs(th, om, cs)
        k2 = rhs(th + 0.5 * h * k1[0], om + 0.5 * h * k1[1], cs)
        k3 = rhs(th + 0.5 * h * k2[0], om + 0.5 * h * k2[1], cs)
        k4 = rhs(th + h * k3[0], om + h * k3[1], cs)
        th = th + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om = om + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        ths[i + 1], oms[i + 1] = th, om
    return ths, oms


def segments(th, om):
    """把折线在跨越 -pi/pi 处切断，避免出现横穿的假线。"""
    w = (th + np.pi) % (2 * np.pi) - np.pi
    cut = np.where(np.abs(np.diff(w)) > np.pi)[0]
    out, s0 = [], 0
    for i in cut:
        out.append((w[s0:i + 1], om[s0:i + 1]))
        s0 = i + 1
    out.append((w[s0:], om[s0:]))
    return out


fig, ax = plt.subplots(figsize=(6.6, 4.0))
clean(ax, grid=True)
ax.axvline(0, color="#D1D5DB", lw=0.7, zorder=1)
ax.axhline(0, color="#D1D5DB", lw=0.7, zorder=1)

H, NS = 1e-3, 6200
h_orb = None
for e in (-0.9, -0.6, -0.3, 0.0, 0.3, 0.6):
    om0 = np.sqrt(2 * (e + 1.0) * G / L)
    ths, oms = rk4(0.0, om0, H, NS)
    for seg in segments(ths, oms):
        ln, = ax.plot(seg[0], seg[1], color=BLUE, lw=1.0, alpha=0.55, zorder=3)
    if h_orb is None:
        h_orb = ln

om0 = np.sqrt(2 * 2.0 * G / L)
ths, oms = rk4(0.0, om0, H, 3200)
h_sep, = ax.plot(ths, oms, color=ACCENT, lw=1.5, ls=(0, (5, 3)), zorder=5)
ax.plot(-ths, -oms, color=ACCENT, lw=1.5, ls=(0, (5, 3)), zorder=5)

om0 = np.sqrt(2 * 2.10 * G / L)
ths, oms = rk4(0.35, om0, H, 2600)
h_rot = None
for seg in segments(ths, oms):
    h_rot, = ax.plot(seg[0], seg[1], color=PURPLE, lw=1.2, zorder=4)
for seg in segments(-ths, -oms):
    ax.plot(seg[0], seg[1], color=PURPLE, lw=1.2, zorder=4)

ths, oms = rk4(2.6, 0.0, 2e-3, 5000, cs=0.35)
h_dmp, = ax.plot(ths, oms, color=PINK, lw=1.2, ls=(0, (2, 2)), zorder=6)

ax.plot([0], [0], "o", ms=6.0, mfc="white", mec=INK, mew=1.3, zorder=8)
ax.plot([np.pi, -np.pi], [0, 0], "o", ms=6.0, mfc="white", mec=ACCENT, mew=1.3, zorder=8)
ax.plot([np.pi, -np.pi], [0, 0], "x", ms=5.0, color=ACCENT, mew=1.3, zorder=9)

h_st = Line2D([], [], marker="o", ls="none", mfc="white", mec=INK, mew=1.3, ms=6)
h_un = Line2D([], [], marker="x", ls="none", color=ACCENT, mew=1.3, ms=6)

ax.legend([h_orb, h_sep, h_rot, h_dmp, h_st, h_un],
          ["闭轨：摆动", "分界线 $e=1$", "开轨：旋转 $e=1.1$",
           "有阻尼 $c=0.35$", "稳定平衡", "不稳定平衡"],
          loc="lower center", bbox_to_anchor=(0.5, -0.34), ncol=3,
          frameon=False, fontsize=8.3, handlelength=2.4, columnspacing=1.8,
          labelspacing=0.45)

ax.set_xlim(-np.pi - 0.05, np.pi + 0.05)
ax.set_ylim(-6.6, 6.6)
ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
ax.set_xticklabels(["$-\\pi$", "$-\\pi/2$", "0", "$\\pi/2$", "$\\pi$"])
ax.set_xlabel("摆角 $\\theta$ (rad)")
ax.set_ylabel("角速度 $\\dot{\\theta}$ (rad/s)")

save(fig, "08", "fig08-01")

# ============================================================
# 图 8-2  一维弹簧的增量势
#   E(x) = m/(2h^2)(x - xt)^2 + k/2 (x - L0)^2,  xt = x_n + h v_n
#   m=1 kg, k=100 N/m, L0=1 m, x_n=1 m, v_n=2 m/s
#   h = 0.10 / 0.05 / 0.02 s
# ============================================================
M, K, L0, XN, VN = 1.0, 100.0, 1.0, 1.0, 2.0


def xstar(h):
    return (XN + h * VN + K * h * h / M * L0) / (1.0 + K * h * h / M)


fig, ax = plt.subplots(figsize=(6.6, 3.5))
clean(ax, grid=True)

xs = np.linspace(0.94, 1.30, 500)
handles = []
for h, c, a_, lw in ((0.10, INK, 1.0, 1.8), (0.05, SLATE, 0.45, 1.1), (0.02, FAINT, 0.75, 1.0)):
    xt = XN + h * VN
    E = M / (2 * h ** 2) * (xs - xt) ** 2 + K / 2 * (xs - L0) ** 2
    ln, = ax.plot(xs, E, color=c, alpha=a_, lw=lw, zorder=5)
    handles.append(ln)
    ax.plot([xstar(h)], [0.07], "o", ms=3.4, mfc="white", mec=c, mew=0.9,
            alpha=min(1.0, a_ + 0.2), zorder=6)

h = 0.10
xt = XN + h * VN
ax.plot(xs, M / (2 * h ** 2) * (xs - xt) ** 2, color=BLUE, lw=1.0, ls=(0, (4, 3)), zorder=4)
ax.plot(xs, K / 2 * (xs - L0) ** 2, color=GREEN, lw=1.0, ls=(0, (4, 3)), zorder=4)

xs1 = xstar(0.10)
ax.plot([xs1], [1.0], "o", ms=6.0, mfc="white", mec=ACCENT, mew=1.5, zorder=9)
ax.plot([xs1, xs1], [1.06, 1.86], color=ACCENT, lw=0.8, ls=(0, (3, 3)), zorder=4)
ax.plot([L0, L0], [0, 4.3], color=GREEN, lw=0.8, ls=(0, (3, 3)), zorder=3)
ax.plot([xt, xt], [0, 4.3], color=BLUE, lw=0.8, ls=(0, (3, 3)), zorder=3)

label(ax, L0 - 0.008, 4.48, "$L_0=1.0$", fs=8.3, color=GREEN, ha="center")
label(ax, xt + 0.008, 4.48, "$\\tilde{x}=1.2$", fs=8.3, color=BLUE, ha="center")
label(ax, xs1, 2.02, "$x^{\\star}=1.100$", fs=8.4, color=ACCENT, ha="center")
label(ax, 1.255, 3.05, "弹性势", fs=8.4, color=GREEN, ha="left")
label(ax, 1.297, 0.80, "惯性项", fs=8.4, color=BLUE, ha="right")
ax.legend(handles, ["$h=0.10$ s", "$h=0.05$ s", "$h=0.02$ s"],
          loc="lower center", bbox_to_anchor=(0.5, -0.33), ncol=3,
          frameon=False, fontsize=8.3, handlelength=2.4, columnspacing=2.2)

ax.set_xlim(0.955, 1.305)
ax.set_ylim(0, 4.9)
ax.set_xticks([0.96, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30])
ax.set_xlabel("位置 $x$ (m)")
ax.set_ylabel("增量势 $E$ (J)")

save(fig, "08", "fig08-02")

# ============================================================
# 图 8-3  ADMM 求解弹簧链的残差
#   min 1/2||x - xt||^2 + k/2 * sum (x_{i+1} - x_i - L0)^2
#   分裂 d = D x,  rho = 10, n = 10, k = 100 N/m, L0 = 1 m
# ============================================================
n, K2, L0b, RHO = 10, 100.0, 1.0, 10.0
xt2 = np.arange(n) * 0.9
D = np.zeros((n - 1, n))
for i in range(n - 1):
    D[i, i] = -1.0
    D[i, i + 1] = 1.0
DtD = D.T @ D


def obj(x):
    return 0.5 * np.sum((x - xt2) ** 2) + 0.5 * K2 * np.sum((D @ x - L0b) ** 2)


x = xt2.copy()
d = D @ x
u = np.zeros(n - 1)
Ainv = np.eye(n) + RHO * DtD
xs_exact = np.linalg.solve(np.eye(n) + K2 * DtD, xt2 + K2 * L0b * (D.T @ np.ones(n - 1)))
Emin = obj(xs_exact)

rs, ss, es = [], [], []
for it in range(80):
    x = np.linalg.solve(Ainv, xt2 + RHO * (D.T @ (d - u)))
    d_old = d.copy()
    d = (K2 * L0b + RHO * (D @ x + u)) / (K2 + RHO)
    u = u + D @ x - d
    rs.append(np.linalg.norm(D @ x - d))
    ss.append(np.linalg.norm(RHO * (D.T @ (d - d_old))))
    es.append(obj(x) - Emin)

rs, ss, es = map(np.array, (rs, ss, es))
k_it = np.arange(1, 31)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.15),
                               gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.34))
for ax in (axL, axR):
    clean(ax, grid=True)

h1, = axL.semilogy(k_it, rs[:30], color=BLUE, lw=1.4, zorder=5)
h2, = axL.semilogy(k_it, ss[:30], color=ACCENT, lw=1.4, ls=(0, (4, 3)), zorder=4)
axL.set_xlim(0, 31)
axL.set_ylim(1e-12, 3)
axL.set_xticks([0, 10, 20, 30])
axL.set_xlabel("迭代次数")
axL.set_ylabel("残差范数")
axL.legend([h1, h2], ["原始残差", "对偶残差"], loc="lower left",
           frameon=False, fontsize=8.3, handlelength=2.4, labelspacing=0.4)

h3, = axR.semilogy(k_it, np.maximum(es[:30], 1e-17), color=GREEN, lw=1.4, zorder=5)
axR.set_xlim(0, 31)
axR.set_ylim(1e-16, 10)
axR.set_xticks([0, 10, 20, 30])
axR.set_xlabel("迭代次数")
axR.set_ylabel("$E(\\mathbf{x}_k)-E^{\\star}$")
axR.text(15.5, 1.4e-9, "每步约降半个量级", color=GREEN, fontsize=8.3, ha="left")

save(fig, "08", "fig08-03")
