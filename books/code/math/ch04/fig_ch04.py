import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np


# ---------------------------------------------------------------- 图 4-1
# 绝对稳定域：把 y' = lam*y 代入格式，得到放大因子 R(z)，z = lam*dt，
# 稳定域就是 |R(z)| < 1 的那块复平面区域。四条 R(z) 都是标准结果。
def R_explicit(z):
    return 1.0 + z


def R_midpoint(z):
    return 1.0 + z + z ** 2 / 2.0


def R_rk4(z):
    return 1.0 + z + z ** 2 / 2.0 + z ** 3 / 6.0 + z ** 4 / 24.0


def R_backward(z):
    return 1.0 / (1.0 - z)


xs = np.linspace(-5.0, 3.2, 500)
ys = np.linspace(-4.0, 4.0, 500)
Z = xs[None, :] + 1j * ys[:, None]

methods = [
    ("显式 Euler", r"$R(z)=1+z$", R_explicit, r"实轴交点 $-2$", (-1.0, -0.72)),
    ("中点法（二阶）", r"$R(z)=1+z+z^2/2$", R_midpoint, r"实轴交点 $-2$", (-1.0, -0.72)),
    ("经典 RK4", r"$R(z)=\sum_{j=0}^{4} z^{j}/j!$", R_rk4,
     r"实轴交点 $-2.785$", (-1.75, -1.05)),
    ("后向 Euler", r"$R(z)=1/(1-z)$", R_backward, r"整个左半平面都稳定", (-3.0, -2.35)),
]

fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.6))
for ax, (name, formula, Rf, note, sxy) in zip(axes.ravel(), methods):
    M = np.abs(Rf(Z))
    ax.contourf(xs, ys, M, levels=[0.0, 1.0], colors=["#E8EEF8"], zorder=1)
    ax.contour(xs, ys, M, levels=[1.0], colors=[INK], linewidths=1.1, zorder=4)
    ax.axhline(0, color=FAINT, lw=0.7, zorder=2)
    ax.axvline(0, color=FAINT, lw=0.7, zorder=2)
    ax.plot([-5.0, 3.2], [0, 0], color=MUTED, lw=0.8, zorder=3)
    ax.plot([0, 0], [-4.0, 4.0], color=MUTED, lw=0.8, zorder=3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(-5.0, 3.2)
    ax.set_ylim(-4.0, 4.0)
    ax.set_xticks([-4, -2, 0, 2])
    ax.set_yticks([-2, 0, 2])
    ax.tick_params(labelsize=8)
    ax.set_xlabel(r"$\mathrm{Re}\,z$", fontsize=8.6, labelpad=1.5)
    ax.set_ylabel(r"$\mathrm{Im}\,z$", fontsize=8.6, labelpad=1.5)
    label(ax, -4.85, 3.45, name, fs=9.4, color=INK, ha="left")
    label(ax, -4.85, 2.85, formula, fs=8.6, color=ACCENT, ha="left")
    label(ax, -4.85, -3.55, note, fs=8.0, color=MUTED, ha="left")
    label(ax, sxy[0], sxy[1], "稳定", fs=8.6, color=BLUE)

fig.subplots_adjust(left=0.085, right=0.985, top=0.975, bottom=0.085,
                    wspace=0.28, hspace=0.42)
save(fig, "04", "fig04-01")


# ---------------------------------------------------------------- 图 4-2
# 刚性方程 y' = -50 (y - cos t)，y(0)=0。
# 解析解 y = A cos t + B sin t - A e^{-50 t}，A = 2500/2501，B = 50/2501。
A = 2500.0 / 2501.0
B = 50.0 / 2501.0


def exact(t):
    return A * np.cos(t) + B * np.sin(t) - A * np.exp(-50.0 * t)


def run_explicit(dt, T=1.5):
    t, y = 0.0, 0.0
    ts, ys = [0.0], [0.0]
    while t < T - 1e-12:
        y = y + dt * (-50.0 * (y - np.cos(t)))
        t += dt
        ts.append(t)
        ys.append(y)
    return np.array(ts), np.array(ys)


def run_backward(dt, T=1.5):
    t, y = 0.0, 0.0
    ts, ys = [0.0], [0.0]
    while t < T - 1e-12:
        y = (y + 50.0 * dt * np.cos(t + dt)) / (1.0 + 50.0 * dt)
        t += dt
        ts.append(t)
        ys.append(y)
    return np.array(ts), np.array(ys)


te = np.linspace(0, 1.5, 1500)
fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.5))

ax = axes[0]
clean(ax)
ax.plot(te, exact(te), color=INK, lw=1.6, zorder=5, label="解析解")
for dt, col in ((0.03, BLUE), (0.05, ACCENT)):
    tt, yy = run_explicit(dt)
    yy = np.where(np.abs(yy) > 3.0, np.nan, yy)
    ax.plot(tt, yy, color=col, lw=1.0, marker="o", ms=1.8, zorder=4,
            label=r"显式 Euler，$\Delta t=%s$" % ("0.03" if dt < 0.04 else "0.05"))
ax.set_xlim(0, 1.5)
ax.set_ylim(-3.0, 3.0)
ax.set_xlabel("t")
ax.set_ylabel(r"$y$")
label(ax, 0.52, 2.36, r"$\Delta t=0.05 > 2/50$，发散后出界", fs=8.2, color=ACCENT, ha="left")
ax.legend(loc="lower left", fontsize=8.0, frameon=False, handlelength=2.0)
label(ax, 0.05, 2.72, "显式：受稳定界约束", fs=9.2, color=INK, ha="left")

ax = axes[1]
clean(ax)
ax.plot(te, exact(te), color=INK, lw=1.6, zorder=5, label="解析解")
tt, yy = run_backward(0.25)
ax.plot(tt, yy, color=GREEN, lw=1.2, marker="s", ms=3.0, zorder=4,
        label=r"后向 Euler，$\Delta t=0.25$")
ax.set_xlim(0, 1.5)
ax.set_ylim(-0.4, 1.4)
ax.set_xlabel("t")
ax.set_ylabel(r"$y$")
ax.legend(loc="lower left", fontsize=8.0, frameon=False, handlelength=2.0)
label(ax, 0.05, 1.28, "隐式：步长由精度定", fs=9.2, color=INK, ha="left")
label(ax, 0.62, 1.12, "最大误差 0.076；每单位时间只需 4 步", fs=8.0, color=GREEN, ha="left")

fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.15, wspace=0.26)
save(fig, "04", "fig04-02")


# ---------------------------------------------------------------- 图 4-3
# 弹簧振子：m = 1 kg，k = 100 N/m，omega = 10 rad/s，
# x0 = 1 m，v0 = 0，dt = 1/60 s，积分 20 s。
k, m, dt, T = 100.0, 1.0, 1.0 / 60.0, 20.0
w = np.sqrt(k / m)
N = int(T / dt)


def energy_trace(mode):
    x, v = 1.0, 0.0
    out = np.empty(N + 1)
    out[0] = 1.0
    for n in range(N):
        if mode == "explicit":
            xn = x + dt * v
            vn = v + dt * (-k / m * x)
        elif mode == "semi":
            vn = v + dt * (-k / m * x)
            xn = x + dt * vn
        elif mode == "verlet":
            xn = x + dt * v + 0.5 * dt * dt * (-k / m * x)
            vn = v + 0.5 * dt * (-k / m * (x + xn))
        elif mode == "rk4":
            def f(s):
                return np.array([s[1], -k / m * s[0]])
            s = np.array([x, v])
            k1 = f(s)
            k2 = f(s + 0.5 * dt * k1)
            k3 = f(s + 0.5 * dt * k2)
            k4 = f(s + dt * k3)
            s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
            xn, vn = s[0], s[1]
        x, v = xn, vn
        out[n + 1] = (0.5 * m * v * v + 0.5 * k * x * x) / (0.5 * k)
    return out


tr = {mode: energy_trace(mode) for mode in ("explicit", "semi", "verlet", "rk4")}
tgrid = np.arange(N + 1) * dt

fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.6))

ax = axes[0]
clean(ax, grid=True)
ax.semilogy(tgrid, tr["explicit"], color=ACCENT, lw=1.2, label="显式 Euler")
ax.semilogy(tgrid, tr["semi"], color=BLUE, lw=1.2, label="半隐式 Euler")
ax.semilogy(tgrid, tr["verlet"], color=GREEN, lw=1.2, label="Verlet")
ax.semilogy(tgrid, tr["rk4"], color=PURPLE, lw=1.2, label="RK4")
ax.set_ylim(0.5, 1e16)
ax.set_xlim(0, T)
ax.set_xlabel("t（s）")
ax.set_ylabel(r"$E/E_0$（对数）")
ax.legend(loc="upper left", fontsize=8.0, frameon=False, ncol=2,
          handlelength=1.8, columnspacing=1.0)
label(ax, 6.5, 4e10, r"每步乘 $1+(\omega\Delta t)^2$", fs=8.2, color=ACCENT, ha="left")
label(ax, 7.2, 4e4, r"$m=1$ kg，$k=100$ N/m，$\Delta t=1/60$ s", fs=8.0, color=MUTED,
      ha="left")

ax = axes[1]
clean(ax, grid=True)
ax.plot(tgrid, tr["semi"], color=BLUE, lw=0.9, alpha=0.9)
ax.plot(tgrid, tr["verlet"], color=GREEN, lw=1.2)
ax.plot(tgrid, tr["rk4"], color=PURPLE, lw=1.6)
ax.set_xlim(0, T)
ax.set_ylim(0.895, 1.20)
ax.set_xlabel("t（s）")
ax.set_ylabel(r"$E/E_0$")
label(ax, 0.5, 1.152, r"半隐式：包络 $0.923$–$1.091$", fs=8.2, color=BLUE, ha="left",
      bbox=dict(fc="white", ec="none", alpha=0.92, pad=1.4))
label(ax, 0.5, 1.098, r"Verlet 与 RK4：偏差都小于 1%", fs=8.2, color=GREEN, ha="left",
      bbox=dict(fc="white", ec="none", alpha=0.92, pad=1.4))
label(ax, 10.4, 0.915, r"RK4 单调降到 $0.99964$", fs=8.2, color=PURPLE, ha="left",
      bbox=dict(fc="white", ec="none", alpha=0.92, pad=1.4))
label(ax, 10.4, 0.950, "Verlet 在 0.993–1.000 之间", fs=8.2, color=GREEN, ha="left",
      bbox=dict(fc="white", ec="none", alpha=0.92, pad=1.4))

fig.subplots_adjust(left=0.095, right=0.985, top=0.965, bottom=0.155, wspace=0.30)
save(fig, "04", "fig04-03")
