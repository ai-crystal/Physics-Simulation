import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 3-1  弹簧振子在三种积分器下的能量
#   m = 1 kg, k = 100 N/m, w = 10 rad/s, x0 = 1 m, v0 = 0, dt = 1/60 s
# ============================================================
K, M, DT = 100.0, 1.0, 1.0 / 60.0
W = np.sqrt(K / M)
T_END = 4.0
NSTEP = int(round(T_END / DT))
E0 = 0.5 * K * 1.0 ** 2


def oscillator(mode, dt=DT, nstep=NSTEP):
    """返回能量序列。mode: explicit / symplectic / verlet"""
    x, v = 1.0, 0.0
    xs, vs = [x], [v]
    for _ in range(nstep):
        if mode == "explicit":
            a = -W * W * x
            x = x + dt * v
            v = v + dt * a
        elif mode == "symplectic":
            v = v + dt * (-W * W * x)
            x = x + dt * v
        else:  # velocity Verlet
            a = -W * W * x
            xn = x + dt * v + 0.5 * dt * dt * a
            an = -W * W * xn
            v = v + 0.5 * dt * (a + an)
            x = xn
        xs.append(x)
        vs.append(v)
    xs, vs = np.array(xs), np.array(vs)
    return 0.5 * M * vs ** 2 + 0.5 * K * xs ** 2, xs


t = np.arange(NSTEP + 1) * DT
E_exp, x_exp = oscillator("explicit")
E_sym, x_sym = oscillator("symplectic")
E_ver, x_ver = oscillator("verlet")

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.05),
                               gridspec_kw=dict(width_ratios=[1.18, 1.0], wspace=0.30))

# ---- 左：全程，对数纵轴 ----
for ax in (axL, axR):
    clean(ax, grid=True, spines=("left", "bottom"))
axL.semilogy(t, E_exp / E0, color=ACCENT, lw=1.5, zorder=4)
axL.semilogy(t, E_sym / E0, color=BLUE, lw=1.3, zorder=5)
axL.semilogy(t, E_ver / E0, color=GREEN, lw=1.3, zorder=6)
axL.axhline(1.0, color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
axL.set_xlim(0, 5.45)
axL.set_ylim(0.4, 2e4)
axL.set_xlabel("时间 $t$ (s)")
axL.set_ylabel("$E\\,/\\,E_0$")
axL.set_xticks([0, 1, 2, 3, 4])
axL.text(4.06, 700, "显式 Euler", color=ACCENT, fontsize=8.6, va="center", ha="left")
axL.text(4.06, 1.0, "半隐式 Euler\nVerlet", color=SLATE, fontsize=8.6, va="center", ha="left",
         linespacing=1.5)
axL.text(0.12, 3.1e3, "每步乘以 $(1+\\omega^2\\Delta t^2)$", color=MUTED,
         fontsize=8.2, va="center")

# ---- 右：前 1.2 s 放大，线性纵轴 ----
m = t <= 1.2001
axR.plot(t[m], E_sym[m] / E0, color=BLUE, lw=1.4, label="半隐式 Euler")
axR.plot(t[m], E_ver[m] / E0, color=GREEN, lw=1.4, label="Verlet")
axR.axhline(1.0, color=FAINT, lw=0.8, ls=(0, (4, 3)))
axR.set_xlim(0, 1.62)
axR.set_ylim(0.905, 1.145)
axR.set_xticks([0, 0.4, 0.8, 1.2])
axR.set_xlabel("时间 $t$ (s)")
axR.set_ylabel("$E\\,/\\,E_0$")
axR.text(1.235, 1.093, "半隐式\nEuler", color=BLUE, fontsize=8.4, va="center",
         linespacing=1.5)
axR.text(1.235, 1.038, "Verlet", color=GREEN, fontsize=8.4, va="center")
axR.text(0.04, 1.132, "虚线：精确能量 $E_0$", color=MUTED, fontsize=8.0, va="center")

save(fig, "03", "fig03-01")

# ============================================================
# 图 3-2  抛体射程的相对误差随步长变化
#   线性阻力 a = g - k v, v0 = (12, 18) m/s, k = 0.2 1/s, g = 9.8 m/s^2
# ============================================================
g = 9.8
kd = 0.2
v0 = np.array([12.0, 18.0])
vinf = np.array([0.0, -g / kd])


def exact(tq):
    return vinf * tq + (v0 - vinf) * (1.0 - np.exp(-kd * tq)) / kd


lo, hi = 0.1, 12.0
for _ in range(300):
    mid = 0.5 * (lo + hi)
    if exact(mid)[1] > 0:
        lo = mid
    else:
        hi = mid
t_flight = 0.5 * (lo + hi)
x_exact = exact(t_flight)[0]


def acc(v):
    return np.array([0.0, -g]) - kd * v


def shoot(nstep, mode):
    dt = t_flight / nstep
    x = np.zeros(2)
    v = v0.copy()
    for _ in range(nstep):
        if mode == "euler":
            xn = x + dt * v
            vn = v + dt * acc(v)
        elif mode == "symplectic":
            vn = v + dt * acc(v)
            xn = x + dt * vn
        elif mode == "verlet":
            a = acc(v)
            xn = x + dt * v + 0.5 * dt * dt * a
            vn = v + 0.5 * dt * (a + acc(v + dt * a))
        else:  # RK4
            def f(y):
                return np.concatenate([y[2:], acc(y[2:])])
            y = np.concatenate([x, v])
            k1 = f(y)
            k2 = f(y + 0.5 * dt * k1)
            k3 = f(y + 0.5 * dt * k2)
            k4 = f(y + dt * k3)
            y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
            xn, vn = y[:2], y[2:]
        x, v = xn, vn
    return x[0], dt


nsteps = [8 * 2 ** i for i in range(8)]
series = {}
for mode in ("euler", "symplectic", "verlet", "rk4"):
    err, dts = [], []
    for n in nsteps:
        xl, dt = shoot(n, mode)
        err.append(abs(xl - x_exact) / x_exact)
        dts.append(dt)
    series[mode] = (np.array(dts), np.array(err))

fig, ax = plt.subplots(figsize=(6.6, 3.4))
clean(ax, grid=True, spines=("left", "bottom"))
style = dict(euler=(ACCENT, "o", "显式 Euler"),
             symplectic=(BLUE, "s", "半隐式 Euler"),
             verlet=(GREEN, "^", "Verlet"),
             rk4=(PURPLE, "D", "RK4"))
handles = []
for mode in ("euler", "symplectic", "verlet", "rk4"):
    dts, err = series[mode]
    c, mk, lab = style[mode]
    p = np.polyfit(np.log(dts), np.log(err), 1)[0]
    ln, = ax.loglog(dts, err, color=c, marker=mk, ms=3.8, lw=1.3, mec="white", mew=0.6,
                    label="%s，斜率 %.1f" % (lab, p))
    handles.append(ln)

ax.set_xlim(2.4e-3, 5.2e-1)
ax.set_ylim(1.0e-16, 1.2e-1)
ax.set_xlabel("步长 $\\Delta t$ (s)")
ax.set_ylabel("射程相对误差")
ax.annotate("双精度舍入下限", xy=(3.05e-3, 1.2e-14), xytext=(4.4e-3, 6e-12),
            color=MUTED, fontsize=8.2, ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9,
                            connectionstyle="arc3,rad=-0.25"))
ax.legend(handles=handles, loc="center left", bbox_to_anchor=(1.02, 0.50),
          fontsize=8.4, handlelength=1.7, labelspacing=0.8, borderaxespad=0.0)
save(fig, "03", "fig03-02")

# ============================================================
# 图 3-3  显式 Euler 的稳定域，以及半隐式 Euler 的临界步长
# ============================================================
fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.9, 3.3),
                               gridspec_kw=dict(width_ratios=[1.0, 1.12], wspace=0.28))

# ---- (a) 复平面 ----
axA.set_aspect("equal")
axA.set_xlim(-2.55, 1.30)
axA.set_ylim(-1.95, 2.95)
for s in ("top", "right", "left", "bottom"):
    axA.spines[s].set_visible(True)
for s in ("top", "right"):
    axA.spines[s].set_color(GRID)
axA.set_xticks([-2, -1, 0])
axA.set_yticks([-1, 0, 1, 2])
axA.set_xlabel("Re$(\\lambda\\Delta t)$")
axA.set_ylabel("Im$(\\lambda\\Delta t)$")

disk = Circle((-1.0, 0.0), 1.0, facecolor=ACCENT, alpha=0.13, edgecolor=ACCENT, lw=1.1, zorder=2)
axA.add_patch(disk)
axA.plot([-1.0], [0.0], marker="+", ms=7, color=ACCENT, zorder=5)
axA.axhline(0, color=FAINT, lw=0.8, zorder=1)
axA.axvline(0, color=FAINT, lw=0.8, zorder=1)

wdts = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
axA.plot(np.zeros_like(wdts), wdts, color=BLUE, lw=1.0, ls=(0, (2, 2)), zorder=4)
axA.scatter(np.zeros_like(wdts), wdts, s=26, facecolor="white", edgecolor=BLUE,
            linewidth=0.9, zorder=6)
axA.scatter([0.0], [2.0], s=34, facecolor=BLUE, edgecolor="white", linewidth=0.8, zorder=7)
axA.text(-2.45, 1.95, "显式 Euler 的稳定域", color=ACCENT, fontsize=8.6,
         ha="left", va="center")
axA.text(-0.12, 2.66, "无阻尼振子的\n$\\lambda\\Delta t = \\mathrm{i}\\,\\omega\\Delta t$",
         color=BLUE, fontsize=8.4, ha="right", va="center", linespacing=1.5)
axA.annotate("$\\omega\\Delta t = 2$\n半隐式 Euler\n的临界值",
             xy=(0.05, 2.02), xytext=(0.16, 0.92), color=INK, fontsize=8.2,
             ha="left", va="center", linespacing=1.5,
             arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9,
                             connectionstyle="arc3,rad=0.25"))
axA.text(-2.4, -1.78, "圆内 $\\left|1+\\lambda\\Delta t\\right| < 1$：扰动衰减",
         color=MUTED, fontsize=8.2, ha="left", va="center")

# ---- (b) 位置随时间 ----
clean(axB, grid=True, spines=("left", "bottom"))
w = 10.0
tt = np.linspace(0, 2.0, 1200)
axB.plot(tt, np.cos(w * tt), color=FAINT, lw=1.4, ls=(0, (5, 3)), zorder=2)
for wdt, c in ((1.5, BLUE), (2.1, ACCENT)):
    dt = wdt / w
    x, v = 1.0, 0.0
    xs, ts = [x], [0.0]
    for i in range(400):
        v = v + dt * (-w * w * x)
        x = x + dt * v
        xs.append(x)
        ts.append((i + 1) * dt)
        if abs(x) > 3.0 or ts[-1] >= 1.999:
            break
    axB.plot(ts, xs, color=c, lw=1.5, marker="o", ms=2.8, mec="none", zorder=4)
axB.set_xlim(0, 3.05)
axB.set_ylim(-3.2, 3.2)
axB.set_xlabel("时间 $t$ (s)")
axB.set_ylabel("位置 $x$ (m)")
axB.text(2.06, np.cos(2.0 * w), "精确解", color=SLATE, fontsize=8.4, va="center")
axB.text(2.06, 1.30, "$\\omega\\Delta t = 1.5$", color=BLUE, fontsize=8.4, va="center")
axB.annotate("$\\omega\\Delta t = 2.1$\n第一步就跳到 $-3.4$ m",
             xy=(0.25, -3.02), xytext=(0.62, -2.30),
             color=ACCENT, fontsize=8.2, ha="left", va="center", linespacing=1.5,
             arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9,
                             connectionstyle="arc3,rad=0.22"))
save(fig, "03", "fig03-03")
