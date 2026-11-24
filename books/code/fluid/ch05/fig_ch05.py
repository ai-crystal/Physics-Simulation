# -*- coding: utf-8 -*-
"""第 5 章插图：涡对的涡量场、二维湍流能谱。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from matplotlib.colors import LinearSegmentedColormap

CMAP = LinearSegmentedColormap.from_list("vor", [BLUE, "#EDF2FB", "#FBF7F0", "#FBEFE0", ACCENT])


# ---------------------------------------------------------------- 图 5-1
def blob_pair():
    """两团高斯涡拆成粒子，Biot-Savart 求和，RK4 推进。"""
    sigma, d, G = 0.10, 1.0, 1.0
    cells = np.arange(-5, 6)
    off = cells * (2.6 * sigma / 5.0)
    OX, OY = np.meshgrid(off, off, indexing="ij")
    r2 = OX ** 2 + OY ** 2
    w = np.exp(-r2 / sigma ** 2).ravel()
    w = w / w.sum()
    X0 = np.stack([-d / 2 + OX.ravel(), OY.ravel()], 1)
    X1 = np.stack([+d / 2 + OX.ravel(), OY.ravel()], 1)
    X = np.vstack([X0, X1])
    Gam = np.concatenate([+G * w, -G * w])

    def vel(P):
        dx = P[:, None, 0] - X[None, :, 0]
        dy = P[:, None, 1] - X[None, :, 1]
        r2 = dx ** 2 + dy ** 2
        fac = np.where(r2 > 1e-14, (1.0 - np.exp(-r2 / sigma ** 2)) / np.maximum(r2, 1e-14),
                       1.0 / sigma ** 2)
        fac = fac * (Gam[None, :] / (2 * np.pi))
        return np.stack([-(fac * dy).sum(1), (fac * dx).sum(1)], 1)

    def vort(P):
        dx = P[:, None, 0] - X[None, :, 0]
        dy = P[:, None, 1] - X[None, :, 1]
        k = 1.0 / (np.pi * sigma ** 2) * np.exp(-(dx ** 2 + dy ** 2) / sigma ** 2)
        return (k * Gam[None, :]).sum(1)

    dt, T = 0.005, 2.0
    nst = int(round(T / dt))
    hist = [X.copy()]
    for _ in range(nst):
        k1 = vel(X)
        k2 = vel(X + 0.5 * dt * k1)
        k3 = vel(X + 0.5 * dt * k2)
        k4 = vel(X + dt * k3)
        X = X + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        hist.append(X.copy())

    m = w.size
    cx = np.array([h[:m, 0].mean() for h in hist])
    cy = np.array([h[:m, 1].mean() for h in hist])
    return X, hist[0], hist[-1], Gam, sigma, vort, cx, cy, d, G


X_end, Xa, Xb, Gam, sigma, vort, cx, cy, d, G = blob_pair()

gx = np.linspace(-1.02, 1.02, 250)
gy = np.linspace(-0.66, 0.66, 150)
GX, GY = np.meshgrid(gx, gy)
P = np.stack([GX.ravel(), GY.ravel()], 1)


def field(Xnow):
    dx = P[:, None, 0] - Xnow[None, :, 0]
    dy = P[:, None, 1] - Xnow[None, :, 1]
    k = 1.0 / (np.pi * sigma ** 2) * np.exp(-(dx ** 2 + dy ** 2) / sigma ** 2)
    return (k * Gam[None, :]).sum(1).reshape(GX.shape)


def vfield(Xnow):
    dx = P[:, None, 0] - Xnow[None, :, 0]
    dy = P[:, None, 1] - Xnow[None, :, 1]
    r2 = dx ** 2 + dy ** 2
    fac = np.where(r2 > 1e-14, (1.0 - np.exp(-r2 / sigma ** 2)) / np.maximum(r2, 1e-14),
                   1.0 / sigma ** 2) * (Gam[None, :] / (2 * np.pi))
    return (-(fac * dy).sum(1).reshape(GX.shape), (fac * dx).sum(1).reshape(GX.shape))


Wa = field(Xa)
Wb = field(Xb)
lev = np.array([-8, -4, -2, -1, -0.4, -0.1, 0.1, 0.4, 1, 2, 4, 8])

fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.10),
                        gridspec_kw=dict(width_ratios=[1, 1, 1.22], wspace=0.50))
for ax, W, Xn, tag in ((axs[0], Wa, Xa, "t = 0"), (axs[1], Wb, Xb, "t = 2 s")):
    ax.contourf(gx, gy, W, levels=lev, cmap=CMAP, extend="both")
    U, V = vfield(Xn)
    sp = 3
    ax.streamplot(gx[::sp], gy[::sp], U[::sp, ::sp], V[::sp, ::sp], color="#6B7280",
                  linewidth=0.45, density=(1.05, 1.05), arrowsize=0.42)
    ax.set_xlim(-1.02, 1.02)
    ax.set_ylim(-0.60, 0.66)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#D1D5DB")
    ax.text(-0.98, 0.68, tag, fontsize=8.8, color=MUTED, va="bottom")
axs[0].scatter([-d / 2], [0], s=14, color="white", edgecolor=INK, lw=0.8, zorder=5)
axs[0].scatter([+d / 2], [0], s=14, color="white", edgecolor=INK, lw=0.8, zorder=5)
axs[0].plot([-d / 2 - 0.12, -d / 2 + 0.12], [0, 0], color=INK, lw=0.7, zorder=5)
axs[0].plot([-d / 2, -d / 2], [-0.12, 0.12], color=INK, lw=0.7, zorder=5)

vth = G / (2 * np.pi * d)
tt = np.linspace(0, 2.0, len(cx))
axs[2].plot(tt, cy, color=ACCENT, lw=1.5, label="粒子求和，左团涡心")
axs[2].plot(tt, vth * tt, color=INK, lw=1.0, ls=(0, (4, 1.6)),
            label=r"理论 $\Gamma t/(2\pi d)$")
axs[2].set_xlim(0, 2.0)
axs[2].set_ylim(-0.05, 0.42)
axs[2].set_xlabel("时间 $t$ / s")
axs[2].set_ylabel("$y_c$")
clean(axs[2], grid=True)
axs[2].legend(loc="upper left", fontsize=8.2, handlelength=1.9, borderaxespad=0.2)
vm = (cy[-1] - cy[0]) / 2.0
axs[2].text(0.97, 0.05, "测得 $V=%.4f$\n理论 $%.4f$" % (vm, vth),
            transform=axs[2].transAxes, fontsize=8.0, color=MUTED, ha="right", va="bottom")

save(fig, "05", "fig05-01")
print("V measured %.4f theory %.4f" % (vm, vth))


# ---------------------------------------------------------------- 图 5-2
def run_2d():
    N, dt, nst, mu = 192, 0.008, 4000, 2e-13
    k1 = np.fft.fftfreq(N, d=1.0 / N)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    k2 = KX ** 2 + KY ** 2
    k2[0, 0] = 1.0
    kmod = np.sqrt(k2)
    km = N // 3
    deal = (np.abs(KX) <= km) & (np.abs(KY) <= km)
    Nrm = float(N ** 2)
    rng = np.random.default_rng(5)
    band = (kmod > 2) & (kmod <= 5)
    wh = np.zeros((N, N), complex)
    wh[band] = (rng.normal(size=band.sum()) + 1j * rng.normal(size=band.sum()))
    wh[band] *= Nrm / kmod[band]

    Lr = -mu * k2 ** 4
    Elin, Ehalf = np.exp(Lr * dt), np.exp(Lr * dt / 2)

    def nl(w):
        ph = -w / k2
        psi = np.real(np.fft.ifft2(ph))
        psix = np.real(np.fft.ifft2(1j * KX * ph))
        psiy = np.real(np.fft.ifft2(1j * KY * ph))
        wx = np.real(np.fft.ifft2(1j * KX * w))
        wy = np.real(np.fft.ifft2(1j * KY * w))
        return np.fft.fft2(psix * wy - psiy * wx) * deal

    kb = np.round(kmod).astype(int).ravel()
    acc = np.zeros(N // 2 + 2)
    ns = 0
    for step in range(nst):
        a = nl(wh)
        wm = (wh + dt * a) * Ehalf
        wh = wh * Elin + dt * nl(wm) * Ehalf
        if step > int(nst * 0.45) and step % 4 == 0:
            uh = 1j * KY * wh / k2
            vh = -1j * KX * wh / k2
            eh = 0.5 * (np.abs(uh) ** 2 + np.abs(vh) ** 2) / N ** 4 * (N / (2 * np.pi)) ** 2
            acc += np.bincount(kb, weights=eh.ravel(), minlength=N // 2 + 2)[:N // 2 + 2]
            ns += 1
    return np.arange(N // 2 + 2), acc / max(1, ns)


k, E = run_2d()
sel = (k >= 3) & (k <= 34)
fit = (k >= 8) & (k <= 24)
slope = np.polyfit(np.log(k[fit]), np.log(E[fit]), 1)[0]
print("fitted slope %.3f" % slope)
print("E[10..26]:", " ".join("%.2e" % v for v in E[10:27]))

fig, axs = plt.subplots(1, 2, figsize=(6.9, 2.90), gridspec_kw=dict(wspace=0.32))
ax = axs[0]
ax.loglog(k[sel], E[sel], color=ACCENT, lw=1.3, marker="o", ms=2.0, mfc=ACCENT, mew=0,
          label="二维模拟")
kk = np.linspace(6.0, 24.0, 30)
ax.loglog(kk, np.exp(np.polyval(np.polyfit(np.log(k[fit]), np.log(E[fit]), 1), np.log(kk))),
          color=INK, lw=1.0, label="拟合直线，斜率 $%.1f$" % slope)

# 右上角空区画两段参考斜率
k0, y0 = 16.0, 0.55
kref = np.linspace(16.0, 33.0, 20)
ax.loglog(kref, y0 * (kref / k0) ** (-5 / 3), color=MUTED, lw=1.0, ls=(0, (4, 1.6)))
ax.loglog(kref, y0 * (kref / k0) ** (-3), color=GREEN, lw=1.0, ls=(0, (4, 1.6)))
ax.text(33.5, y0 * (33.5 / k0) ** (-5 / 3), r"$-5/3$", fontsize=8.6, color=MUTED,
        ha="left", va="center")
ax.text(33.5, y0 * (33.5 / k0) ** (-3), r"$-3$", fontsize=8.6, color=GREEN,
        ha="left", va="center")
ax.set_xlim(2.6, 40)
ax.set_ylim(1.2e-3, 2.0e2)
ax.set_xticks([3, 5, 10, 20, 30])
ax.set_xticklabels(["3", "5", "10", "20", "30"])
ax.xaxis.set_minor_locator(plt.NullLocator())
ax.yaxis.set_minor_locator(plt.NullLocator())
ax.set_yticks([1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2])
ax.set_xlabel("波数 $k$")
ax.set_ylabel("能谱 $E(k)$")
clean(ax, grid=True)
ax.legend(fontsize=8.0, loc="lower left", handlelength=1.8, borderaxespad=0.2)

ax = axs[1]
kb = np.arange(8, 27)
sl = np.array([(np.log(E[j + 2]) - np.log(E[j - 2])) /
               (np.log(j + 2.0) - np.log(j - 2.0)) for j in kb])
ax.plot(kb, sl, color=BLUE, lw=0.9, marker="o", ms=2.4, mfc=BLUE, mew=0, alpha=0.9)
ax.axhline(-5 / 3, color=MUTED, lw=1.0, ls=(0, (4, 1.6)))
ax.axhline(-3, color=GREEN, lw=1.0, ls=(0, (4, 1.6)))
ax.text(31.5, -5 / 3 - 0.10, r"$-5/3$", fontsize=8.6, color=MUTED, ha="left", va="top")
ax.text(31.5, -3 - 0.10, r"$-3$", fontsize=8.6, color=GREEN, ha="left", va="top")
ax.set_xlim(3.5, 37)
ax.set_ylim(-6.1, -1.4)
ax.set_xticks([5, 10, 15, 20, 25, 30])
ax.set_yticks([-2, -3, -4, -5, -6])
ax.set_xlabel("波数 $k$")
ax.set_ylabel("局部斜率")
clean(ax, grid=True)

save(fig, "05", "fig05-02")
