import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from scipy.optimize import brentq

MU, LAM = 1.0e4, 1.5e4          # Pa, nu = 0.3


def lateral_nh(l1):
    f = lambda l2: MU * (l2 ** 2 - 1.0) + LAM * np.log(l1 * l2 ** 2)
    return brentq(f, 1e-3, 3.0)


def lateral_stvk(l1):
    # mu(l2^2-1) + lam/2 (l1^2 + 2 l2^2 - 3) = 0
    a = MU + LAM
    b = 0.5 * LAM * (l1 ** 2 - 3.0) - MU
    v = -b / a
    return np.sqrt(v) if v > 0 else np.nan


def lateral_corot(l1):
    f = lambda l2: 2 * MU * (l2 - 1.0) + LAM * (l1 * l2 ** 2 - 1.0) * l1 * l2
    return brentq(f, 1e-3, 3.0)


def p11_nh(l1, l2):
    J = l1 * l2 ** 2
    return MU * (l1 - 1.0 / l1) + LAM * np.log(J) / l1


def p11_stvk(l1, l2):
    E11 = 0.5 * (l1 ** 2 - 1)
    trE = 0.5 * (l1 ** 2 + 2 * l2 ** 2 - 3)
    return l1 * (2 * MU * E11 + LAM * trE)


def p11_corot(l1, l2):
    J = l1 * l2 ** 2
    return 2 * MU * (l1 - 1.0) + LAM * (J - 1.0) * l2 ** 2


models = [
    ("Neo-Hookean", lateral_nh, p11_nh, BLUE),
    ("St. Venant-Kirchhoff", lateral_stvk, p11_stvk, ACCENT),
    ("共旋 corotated", lateral_corot, p11_corot, GREEN),
]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.9, 3.3),
                               gridspec_kw=dict(wspace=0.30))
for ax in (axL, axR):
    clean(ax, grid=True)
    ax.set_xlabel(r"伸长比 $\lambda_1$")

for name, lat, stress, c in models:
    l1s = np.linspace(0.5, 2.6, 400)
    P, K = [], []
    for l1 in l1s:
        try:
            l2 = lat(l1)
        except Exception:
            P.append(np.nan); K.append(np.nan); continue
        if not np.isfinite(l2):
            P.append(np.nan); K.append(np.nan); continue
        P.append(stress(l1, l2))
        h = 1e-4
        try:
            K.append((stress(l1 + h, lat(l1 + h)) - stress(l1 - h, lat(l1 - h))) / (2 * h))
        except Exception:
            K.append(np.nan)
    axL.plot(l1s, np.array(P) / 1e3, color=c, lw=1.8, label=name)
    axR.plot(l1s, np.array(K) / 1e3, color=c, lw=1.8, label=name)

axL.set_ylabel(r"名义应力 $P_{11}$ (kPa)")
axR.set_ylabel(r"切线刚度 $\mathrm{d}P_{11}/\mathrm{d}\lambda_1$ (kPa)")
axL.set_xlim(0.5, 2.6); axR.set_xlim(0.5, 2.6)
axL.set_ylim(-30, 80); axR.set_ylim(-20, 120)
axL.legend(loc="upper left", fontsize=7.6)
axR.legend(loc="upper left", fontsize=7.6)
axL.axhline(0, color=SLATE, lw=0.8)
axR.axhline(0, color=SLATE, lw=0.8)
save(fig, "04", "fig04-01")

# ---------------- 图 4-2  Maxwell 应力松弛 ----------------
fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.9, 3.2),
                               gridspec_kw=dict(wspace=0.28))
t = np.linspace(0, 3, 600)
eps0 = 0.05

for tau, c in [(0.02, BLUE), (0.2, ACCENT), (2.0, GREEN)]:
    axL.semilogy(t, 1.0e6 * eps0 * np.exp(-t / tau) / 1e3, color=c, lw=1.7,
                 label=r"$\tau=%.2f$ s" % tau)
axL.set_xlabel("时间 (s)"); axL.set_ylabel("应力 (kPa)")
axL.set_xlim(0, 3); axL.set_ylim(0.01, 60)
axL.legend(fontsize=7.8); axL.grid(True, color=GRID, lw=0.6); axL.set_axisbelow(True)
clean(axL, spines=("left", "bottom"))

# 三支路 Prony
E = np.array([0.5e6, 0.3e6, 0.2e6]); TAU = np.array([0.02, 0.2, 2.0])
sig_multi = eps0 * np.sum(E[:, None] * np.exp(-t[None, :] / TAU[:, None]), axis=0)
axR.semilogy(t, sig_multi / 1e3, color=ACCENT, lw=2.0, label="三支路 Prony")
axR.semilogy(t, eps0 * 1.0e6 * np.exp(-t / 0.2) / 1e3, color=BLUE, lw=1.4,
             ls="--", label=r"单支路 $\tau=0.2$ s，$E=1$ MPa")
axR.set_xlabel("时间 (s)"); axR.set_ylabel("应力 (kPa)")
axR.set_xlim(0, 3); axR.set_ylim(0.01, 60)
axR.legend(fontsize=7.6); axR.grid(True, color=GRID, lw=0.6); axR.set_axisbelow(True)
clean(axR, spines=("left", "bottom"))
save(fig, "04", "fig04-02")

print("P11 at l1=1:", p11_nh(1, 1) / 1e3, p11_stvk(1, 1) / 1e3, p11_corot(1, 1) / 1e3)
print("l2 stvk at 2.08:", lateral_stvk(2.08))
print("multi at 1s:", np.interp(1.0, t, sig_multi) / 1e3)
print("single at 1s:", 1e6 * 0.05 * np.exp(-5) / 1e3)
