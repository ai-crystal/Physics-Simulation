import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from numpy.fft import fft2, ifft2, fftfreq
from matplotlib.gridspec import GridSpec

# ============================================================
# 图 10-1  二维浮力羽流（涡量-流函数形式，周期域，真实计算）
#   dw/dt + u.grad w = nu lap w + alpha dT/dx,   lap psi = w
#   u = dpsi/dy,  v = -dpsi/dx
# ============================================================
NX, NY = 160, 200
KXK = 2 * np.pi * fftfreq(NX, d=1.0)
KYK = 2 * np.pi * fftfreq(NY, d=1.0)
KX, KY = np.meshgrid(KXK, KYK)
K2 = KX ** 2 + KY ** 2
K2[0, 0] = 1.0
II, JJ = np.meshgrid(np.arange(NX), np.arange(NY))


def bilinear(f, x, y):
    x0 = np.floor(x); y0 = np.floor(y)
    fx = x - x0; fy = y - y0
    i0 = x0.astype(int) % NX; j0 = y0.astype(int) % NY
    i1 = (i0 + 1) % NX; j1 = (j0 + 1) % NY
    return (f[j0, i0] * (1 - fx) * (1 - fy) + f[j0, i1] * fx * (1 - fy)
            + f[j1, i0] * (1 - fx) * fy + f[j1, i1] * fx * fy)


def velocity(om):
    psi = ifft2(fft2(om) / K2).real
    return ifft2(1j * KY * fft2(psi)).real, ifft2(-1j * KX * fft2(psi)).real


def plume(steps=2400, dt=0.05, alpha=0.03, nu_om=0.08, decay=0.0002,
          src=3.0, srcw=2.5, wob=0.8, period=9.0):
    om = np.zeros((NY, NX))
    T = np.zeros((NY, NX))
    sponge = 1.0 - 0.9 * np.clip((JJ - NY * 0.80) / (NY * 0.20), 0, 1) ** 2
    for n in range(steps):
        u, v = velocity(om)
        om = bilinear(om, II - dt * u, JJ - dt * v)
        T = bilinear(T, II - dt * u, JJ - dt * v)
        cx = NX / 2 + wob * np.sin(2 * np.pi * n * dt / period)
        s = np.exp(-((II - cx) / srcw) ** 2) * np.exp(-((JJ - 5.0) / 3.0) ** 2)
        T = T + dt * src * s
        om = om + dt * alpha * (np.roll(T, -1, axis=1) - np.roll(T, 1, axis=1)) / 2.0
        lap = (np.roll(om, -1, axis=0) + np.roll(om, 1, axis=0)
               + np.roll(om, -1, axis=1) + np.roll(om, 1, axis=1) - 4 * om)
        om = om + dt * nu_om * lap
        T *= (1 - decay)
        T *= sponge
        om *= sponge
    return om, T


om, Temp = plume()
u, v = velocity(om)

fig = plt.figure(figsize=(6.4, 4.3))
gs = GridSpec(1, 2, figure=fig, wspace=0.06, left=0.01, right=0.99,
              bottom=0.02, top=0.98)

ax = fig.add_subplot(gs[0])
ax.imshow(Temp ** 0.75, origin="lower", cmap="copper",
          vmin=0.0, vmax=np.percentile(Temp ** 0.75, 99.2) * 0.62, interpolation="bilinear")
ax.axis("off")

ax = fig.add_subplot(gs[1])
lim = np.percentile(np.abs(om), 99.5)
ax.imshow(om, origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim,
          interpolation="bilinear")
ax.axis("off")

save(fig, "10", "fig10-01")

# ============================================================
# 图 10-2  黑体辐射的颜色与光谱（Planck 公式 + CIE 1931 配色函数）
# ============================================================
H_P = 6.62607015e-34
C_L = 2.99792458e8
K_B = 1.380649e-23


def planck(lam_nm, T):
    lam = np.asarray(lam_nm, float) * 1e-9
    return (2 * H_P * C_L ** 2 / lam ** 5) / (np.exp(H_P * C_L / (lam * K_B * T)) - 1.0)


def _g(x, mu, s1, s2):
    t = x - mu
    s = np.where(t < 0, s1, s2)
    return np.exp(-0.5 * (t / s) ** 2)


def cie(lam):
    xb = (1.056 * _g(lam, 599.8, 37.9, 31.0) + 0.362 * _g(lam, 442.0, 16.0, 26.7)
          - 0.065 * _g(lam, 501.1, 20.4, 26.2))
    yb = (0.821 * _g(lam, 568.8, 46.9, 40.5) + 0.286 * _g(lam, 530.9, 16.3, 31.1))
    zb = (1.217 * _g(lam, 437.0, 11.8, 36.0) + 0.681 * _g(lam, 459.0, 26.0, 13.8))
    return xb, yb, zb


LAM = np.arange(380.0, 781.0, 1.0)
XB, YB, ZB = cie(LAM)


def bb_color(T):
    B = planck(LAM, T)
    X = X = np.trapezoid(B * XB, LAM); Y = np.trapezoid(B * YB, LAM); Z = np.trapezoid(B * ZB, LAM)
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b = 0.0557 * X - 0.2040 * Y + 1.0570 * Z
    rgb = np.clip(np.array([r, g, b]), 0.0, None)
    if rgb.max() > 0:
        rgb = rgb / rgb.max()
    return np.clip(rgb, 0, 1) ** (1 / 2.2)


Ts = np.linspace(1000.0, 12000.0, 320)
band = np.array([bb_color(T) for T in Ts])[None, :, :]

fig = plt.figure(figsize=(6.6, 3.9))
gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 3.2], hspace=0.32,
              left=0.10, right=0.97, bottom=0.22, top=0.97)

ax = fig.add_subplot(gs[0])
ax.imshow(band, extent=[1000, 12000, 0, 1], aspect="auto", origin="lower")
ax.set_yticks([])
ax.set_xlim(1000, 12000)
ax.set_xticks([1000, 2000, 3000, 5000, 6500, 8000, 10000, 12000])
ax.set_xlabel("色温 $T$ / K")
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="x", labelsize=8.4, length=2.5)

ax = fig.add_subplot(gs[1])
LAM_FINE = np.linspace(100.0, 4000.0, 900)
for T, col in ((2000.0, ACCENT), (4000.0, PURPLE), (6500.0, BLUE)):
    B = planck(LAM_FINE, T)
    B = B / B.max()
    lmax = 2.897771955e-3 / T * 1e9
    ax.semilogx(LAM_FINE, B, color=col, lw=1.6,
                label="$T=%d$ K" % T)
    ax.axvline(lmax, color=col, lw=0.8, ls=(0, (4, 2)), alpha=0.55, zorder=1)

ax.set_xlim(100, 4000)
ax.set_ylim(0, 1.30)
ax.set_xticks([100, 200, 400, 1000, 2000, 4000])
ax.set_xticklabels(["100", "200", "400", "1000", "2000", "4000"])
ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.set_xlabel("波长 $\\lambda$ / nm")
ax.set_ylabel("归一化谱亮度")
clean(ax)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.grid(True, axis="y", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=3, fontsize=7.8,
          handlelength=1.6, columnspacing=1.6, borderaxespad=0.0)

save(fig, "10", "fig10-02")
