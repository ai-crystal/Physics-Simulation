import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 4-1  三种超弹模型的单轴拉伸（真实公式计算）
#   mu = 1e4 Pa, lambda = 1.5e4 Pa (nu = 0.3)
#   Neo-Hookean : Psi = mu/2 (I1-3) - mu lnJ + lam/2 (lnJ)^2
#                 P   = mu (F - F^-T) + lam lnJ F^-T
#   StVK        : Psi = mu |E|^2 + lam/2 (trE)^2,  E = (F^T F - I)/2
#                 P   = F (2 mu E + lam trE I)
#   Corotated   : Psi = mu |F-R|^2 + lam/2 (J-1)^2
#                 P   = 2 mu (F-R) + lam (J-1) J F^-T
#   单轴：F = diag(l1, l2, l2)，l2 由 P22 = 0 用二分法解出
# ============================================================
MU = 1e4
NU = 0.3
LAM = 2 * MU * NU / (1 - 2 * NU)
print("mu = %.0f Pa, lambda = %.0f Pa" % (MU, LAM))


def P_neo(F):
    J = np.linalg.det(F)
    Fi = np.linalg.inv(F).T
    return MU * (F - Fi) + LAM * np.log(J) * Fi


def P_stvk(F):
    E = 0.5 * (F.T @ F - np.eye(3))
    S = 2 * MU * E + LAM * np.trace(E) * np.eye(3)
    return F @ S


def P_corot(F):
    J = np.linalg.det(F)
    Fi = np.linalg.inv(F).T
    U, s, Vt = np.linalg.svd(F)
    R = U @ Vt
    return 2 * MU * (F - R) + LAM * (J - 1) * J * Fi


def uniaxial(pfun, l1):
    """解 P22(l2) = 0，返回 (P11, l2)；无解时返回 (nan, nan)。"""
    def f(l2):
        return pfun(np.diag([l1, l2, l2]))[1, 1]

    grid = np.linspace(1e-4, 6.0, 500)
    vals = np.array([f(x) for x in grid])
    k = np.nonzero(np.sign(vals[:-1]) * np.sign(vals[1:]) < 0)[0]
    if len(k) == 0:
        return np.nan, np.nan
    lo, hi = grid[k[0]], grid[k[0] + 1]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    l2 = 0.5 * (lo + hi)
    return pfun(np.diag([l1, l2, l2]))[0, 0], l2


L1 = np.linspace(0.62, 2.9, 460)
models = [("Neo-Hookean", P_neo, BLUE),
          ("StVK", P_stvk, ACCENT),
          ("共旋", P_corot, GREEN)]

res = {}
for name, pf, c in models:
    P = np.array([uniaxial(pf, x)[0] for x in L1]) / 1e3
    res[name] = P
    ok = ~np.isnan(P)
    print("%-12s 能算到的最大伸长 %.3f   P11(2)=%.2f kPa" %
          (name, L1[ok][-1], P[np.argmin(np.abs(L1 - 2.0))]))

fig, (fa, fb) = plt.subplots(1, 2, figsize=(6.9, 3.4))

for name, pf, c in models:
    P = res[name]
    fa.plot(L1, P, color=c, lw=1.9, label=name, solid_capstyle="round")
    fb.plot(L1, np.gradient(P, L1), color=c, lw=1.9, label=name,
            solid_capstyle="round")

fa.axhline(0, color=GRID, lw=1.0)
fa.set_xlim(0.6, 2.95)
fa.set_ylim(-22, 100)
fa.set_xlabel("伸长比 $\\lambda_1$")
fa.set_ylabel("名义应力 $P_{11}$  (kPa)")
fa.set_xticks([0.5, 1.0, 1.5, 2.0, 2.5])
fa.legend(loc="lower right", handlelength=1.4, labelspacing=0.35, borderaxespad=0.6)
fa.text(0.03, 0.905, "(a) 单轴拉伸曲线", transform=fa.transAxes, fontsize=9.2,
        color=INK, ha="left", va="bottom")
clean(fa)

ok = ~np.isnan(res["StVK"])
l_end = L1[ok][-1]
fa.plot([l_end], [res["StVK"][ok][-1]], marker="o", ms=5.5, mfc="white",
        mec=ACCENT, mew=1.3, zorder=6)
label(fa, l_end + 0.09, res["StVK"][ok][-1] - 8, "$\\lambda_1=%.2f$" % l_end,
      fs=8.4, color=ACCENT, ha="left", va="center")

fb.axhline(0, color=GRID, lw=1.0)
fb.set_xlim(0.6, 2.95)
fb.set_ylim(-6, 82)
fb.set_xlabel("伸长比 $\\lambda_1$")
fb.set_ylabel("切线刚度 $\\mathrm{d}P_{11}/\\mathrm{d}\\lambda_1$  (kPa)")
fb.set_xticks([0.5, 1.0, 1.5, 2.0, 2.5])
fb.text(0.03, 0.905, "(b) 切线刚度", transform=fb.transAxes, fontsize=9.2,
        color=INK, ha="left", va="bottom")
fb.plot([1.0], [26.0], marker="o", ms=6.0, mfc="white", mec=MUTED, mew=1.2, zorder=7)
clean(fb)

fig.subplots_adjust(wspace=0.30)
save(fig, "04", "fig04-1")


# ============================================================
# 图 4-2  Maxwell 模型的应力松弛（真实计算）
#   阶跃应变 eps0 = 5%，总模量 1 MPa，sigma(0) = 50 kPa
#   单支路：sigma = E eps0 exp(-t/tau)
#   三支路 Prony：(E_i, tau_i) = (0.5,0.02), (0.3,0.2), (0.2,2.0) MPa
# ============================================================
eps0 = 0.05
E_tot = 1.0e6
taus = [0.02, 0.2, 2.0]
branches = [(0.5e6, 0.02), (0.3e6, 0.2), (0.2e6, 2.0)]
print("sigma(0) = %.1f kPa" % (E_tot * eps0 / 1e3))

t1 = np.linspace(0, 1.0, 1200)
sig1 = [E_tot * eps0 * np.exp(-t1 / tau) / 1e3 for tau in taus]

t2 = np.logspace(-3, 1.0, 800)
sig_pron = sum(E * eps0 * np.exp(-t2 / tau) for E, tau in branches) / 1e3
sig_single = E_tot * eps0 * np.exp(-t2 / 0.2) / 1e3
k1 = np.argmin(np.abs(t2 - 1.0))
print("t=1s  单支路 %.2f kPa   三支路 %.2f kPa" % (sig_single[k1], sig_pron[k1]))

fig, (fa, fb) = plt.subplots(1, 2, figsize=(6.9, 3.3))

cols = [ACCENT, BLUE, GREEN]
for tau, s_, c in zip(taus, sig1, cols):
    fa.plot(t1, s_, color=c, lw=1.9, label="$\\tau = %g$ s" % tau)
fa.set_xlim(0, 1.0)
fa.set_ylim(0, 56)
fa.set_xlabel("时间 $t$  (s)")
fa.set_ylabel("应力 $\\sigma$  (kPa)")
fa.set_yticks([0, 10, 20, 30, 40, 50])
fa.legend(loc="upper right", handlelength=1.4, labelspacing=0.3, borderaxespad=0.5)
fa.text(0.03, 0.905, "(a) 单支路", transform=fa.transAxes, fontsize=9.2,
        color=INK, ha="left", va="bottom")
clean(fa)

fb.semilogx(t2, sig_pron, color=ACCENT, lw=2.0, label="三支路 Prony")
fb.semilogx(t2, sig_single, color=BLUE, lw=1.7, ls=(0, (5, 3)),
            label="单支路 $\\tau=0.2$ s")
fb.set_xlim(1e-3, 10)
fb.set_ylim(0, 56)
fb.set_xlabel("时间 $t$  (s，对数轴)")
fb.set_ylabel("应力 $\\sigma$  (kPa)")
fb.set_yticks([0, 10, 20, 30, 40, 50])
fb.legend(loc="lower left", handlelength=1.8, labelspacing=0.3, borderaxespad=0.7)
fb.text(0.03, 0.905, "(b) 广义 Maxwell", transform=fb.transAxes, fontsize=9.2,
        color=INK, ha="left", va="bottom")
fb.axvline(1.0, color=GRID, lw=1.0, ls=(0, (4, 3)), zorder=1)
fb.plot([1.0], [sig_pron[k1]], marker="o", ms=6.0, mfc="white", mec=ACCENT,
        mew=1.3, zorder=7)
fb.plot([1.0], [sig_single[k1]], marker="o", ms=6.0, mfc="white", mec=BLUE,
        mew=1.3, zorder=7)
label(fb, 1.15, 41, "$t=1$ s", fs=8.6, color=MUTED, ha="left", va="center")
clean(fb)

fig.subplots_adjust(wspace=0.30)
save(fig, "04", "fig04-2")
