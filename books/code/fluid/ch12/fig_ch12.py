import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ---------------- 图 12-1 浮标的垂荡周期 ----------------
R, H = 0.25, 0.6
rho_f, g = 1000.0, 9.81
V = np.pi * R ** 2 * H
A = np.pi * R ** 2
m_a = 0.7 * rho_f * np.pi * R ** 3

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.9, 3.1), gridspec_kw=dict(wspace=0.30))
sigma = np.linspace(0.05, 1.2, 300)
m = sigma * rho_f * V
T0 = 2 * np.pi / np.sqrt(rho_f * g * A / m)
T1 = 2 * np.pi / np.sqrt(rho_f * g * A / (m + m_a))
axL.plot(sigma, T1, color=ACCENT, lw=1.8, label="含附加质量")
axL.plot(sigma, T0, color=BLUE, lw=1.5, ls="--", label="不含附加质量")
clean(axL, grid=True)
axL.set_xlabel(r"密度比 $\sigma=\rho_s/\rho_f$")
axL.set_ylabel("垂荡周期 (s)")
axL.set_xlim(0, 1.2); axL.set_ylim(0, 2.2)
axL.legend(fontsize=8)

r = m_a / (sigma * rho_f * V)
ratio = np.sqrt(1 + r)
axR.plot(np.linspace(0, 8, 200), np.sqrt(1 + np.linspace(0, 8, 200)), color=MUTED, lw=1.4)
pts = [0.9, 0.6, 0.3, 0.1]
rr = m_a / (np.array(pts) * rho_f * V)
axR.scatter(rr, np.sqrt(1 + rr), s=28, color=ACCENT, zorder=5, edgecolor="white", linewidth=0.8)
for s0, x, y in zip(pts, rr, np.sqrt(1 + rr)):
    axR.annotate(r"$\sigma=%.2f$" % s0, (x, y), xytext=(4, -10),
                 textcoords="offset points", fontsize=7.6, color=MUTED)
clean(axR, grid=True)
axR.set_xlabel(r"质量比 $r=m_a/m$")
axR.set_ylabel(r"$T/T_0$")
axR.set_xlim(0, 8); axR.set_ylim(1, 3.6)
save(fig, "12", "fig12-01")

# ---------------- 图 12-2 分区耦合的稳定性 ----------------
def radius(rr, wdt, n=400):
    w2 = 1.0
    # 状态 (x_n, x_{n-1}, a_{n-1})
    M = np.array([[2 - w2 * wdt ** 2, -1.0, -rr * wdt ** 2],
                  [1.0, 0.0, 0.0],
                  [-w2, 0.0, -rr]])
    ev = np.linalg.eigvals(M)
    return np.max(np.abs(ev))


rs = np.linspace(0.05, 4.0, 300)
fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.9, 3.1), gridspec_kw=dict(wspace=0.30))
for wdt, c, lab in [(0.01, BLUE, r"$\omega\Delta t=0.01$"),
                    (0.05, ACCENT, r"$\omega\Delta t=0.05$"),
                    (0.10, GREEN, r"$\omega\Delta t=0.10$")]:
    axL.plot(rs, [radius(rr, wdt) for rr in rs], color=c, lw=1.6, label=lab)
axL.plot(rs, np.maximum(1, rs), color=SLATE, lw=0.9, ls=":")
clean(axL, grid=True)
axL.set_xlabel(r"质量比 $r=m_a/m$")
axL.set_ylabel("谱半径")
axL.set_ylim(0.9, 4.2)
axL.legend(fontsize=7.8, loc="upper left")

wdt = 0.02
for rr, c in [(0.6, BLUE), (2.5, PINK)]:
    x = [0.01, 0.01]
    a_prev = 0.0
    for n in range(200):
        a = -(1.0 * x[-1] + rr * a_prev)
        xn = 2 * x[-1] - x[-2] + wdt ** 2 * a
        x.append(xn)
        a_prev = a
    axR.semilogy(np.arange(len(x)) * wdt, np.abs(x), color=c, lw=1.4,
                 label=r"$r=%.1f$" % rr)
clean(axR, grid=True)
axR.set_xlabel(r"时间 (s)，$\omega=1$")
axR.set_ylabel(r"$|x|$ (m)")
axR.set_ylim(1e-4, 1e3)
axR.legend(fontsize=8)
save(fig, "12", "fig12-02")

print("T at sigma=0.9:", 2*np.pi/np.sqrt(rho_f*g*A/(0.9*rho_f*V+m_a)))
print("r at 0.9/0.6/0.3/0.1:", m_a/(np.array(pts)*rho_f*V))
print("512^3 48B GB:", 512**3*48/1e9, "96B:", 512**3*96/1e9)
