import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 第 11 章插图
#   图 11-1  三种波谱合成的高度场（真实 FFT 计算）
#   图 11-2  溃坝的浅水特征线与水深剖面（真实 1D 计算）
# ============================================================
G = 9.81


# ------------------------------------------------------------
# 图 11-1
#   线性深水波，ω = sqrt(g k)。谱 S(ω) 转成二维波数谱：
#       S_k(k) = S(ω) * dω/dk = S(ω) * sqrt(g/k)/2
#       P2D(k,θ) = S_k(k) * D(θ) / k
#   高斯场：h0(k) = (ξ1 + i ξ2)/sqrt(2) * sqrt(P2D Δk²)
#   实值化：h(k) = h0(k) + conj(h0(-k))
#   高度场：h(x) = Re{IFFT2[h(k)]}
# ------------------------------------------------------------
def spectrum_pm(w, U, alpha=0.0081):
    """Pierson-Moskowitz 谱, 单位 m^2 s。U 取 19.5 m 高度风速。"""
    wp = 0.877 * G / U
    return alpha * G ** 2 / w ** 5 * np.exp(-1.25 * (wp / w) ** 4)


def spectrum_jonswap(w, U, gamma=3.3):
    """JONSWAP：PM 谱乘峰值增强因子。"""
    wp = 0.877 * G / U
    sigma = np.where(w <= wp, 0.07, 0.09)
    r = np.exp(-(w - wp) ** 2 / (2.0 * sigma ** 2 * wp ** 2))
    norm = 1.0 / (0.5 + 0.065 * gamma ** 0.803)
    return spectrum_pm(w, U) * gamma ** r * norm


def make_field(kind, L=256.0, N=256, U=12.0, seed=7, s=4.0):
    """返回 N×N 高度场。"""
    rng = np.random.default_rng(seed)
    n = np.fft.fftfreq(N, d=1.0 / N)          # 0..N/2, -N/2..-1
    kx = 2 * np.pi * n / L
    KX, KY = np.meshgrid(kx, kx, indexing="xy")
    K = np.hypot(KX, KY)
    K[0, 0] = 1e-12
    theta = np.arctan2(KY, KX)
    dk = 2 * np.pi / L

    # 方向分布 D(θ) = cos^{2s}(θ/2)，数值归一（∫D dθ = 1）
    th = np.linspace(-np.pi, np.pi, 7201)
    D = np.cos(0.5 * th) ** (2 * s)
    D = D / np.trapezoid(D, th)
    Dk = np.interp(theta, th, D)

    if kind == "PM":
        w = np.sqrt(G * K)
        S_k = spectrum_pm(w, U) * 0.5 * np.sqrt(G / K)
    elif kind == "JONSWAP":
        w = np.sqrt(G * K)
        S_k = spectrum_jonswap(w, U) * 0.5 * np.sqrt(G / K)
    else:  # Phillips
        Lp = U ** 2 / G
        S_k = np.exp(-1.0 / (K * Lp) ** 2) / K ** 4 * np.cos(theta) ** 2
        S_k = S_k * 1.0

    P2D = S_k * Dk / K                        # 二维方差密度

    xi_r = rng.standard_normal((N, N))
    xi_i = rng.standard_normal((N, N))
    h0 = (xi_r + 1j * xi_i) / np.sqrt(2.0) * np.sqrt(np.maximum(P2D, 0.0) * dk ** 2)

    # h0(-k)：索引 i -> (-i) mod N
    idx = np.arange(N)
    neg = (-idx) % N
    h0_minus = h0[np.ix_(neg, neg)]
    ht = h0 + np.conj(h0_minus)
    ht[0, 0] = 0.0                            # 去掉平均高度
    return np.real(np.fft.ifft2(ht)) * N ** 2


L, N = 256.0, 256
fields = {}
for kind in ("PM", "JONSWAP", "Phillips"):
    fields[kind] = make_field(kind, L, N, U=12.0, seed=7)

hs = {k: 4.0 * v.std() for k, v in fields.items()}
print("各谱高度场 4σ (m):", {k: round(v, 3) for k, v in hs.items()})
hs_target = 3.1
for k in fields:
    fields[k] *= hs_target / hs[k]
print("归一后 4σ:", {k: round(4 * v.std(), 3) for k, v in fields.items()})

x = np.linspace(0, L, N, endpoint=False)
jmid = N // 2

fig = plt.figure(figsize=(6.9, 4.7))
gs = fig.add_gridspec(2, 3, height_ratios=[2.25, 1.0], hspace=0.42, wspace=0.16,
                      left=0.075, right=0.985, top=0.965, bottom=0.10)
names = [("PM", "PM 谱"), ("JONSWAP", "JONSWAP 谱"), ("Phillips", "Phillips 谱")]

ls = matplotlib.colors.LightSource(azdeg=315, altdeg=38)
vmax = max(np.abs(v).max() for v in fields.values())

for i, (k, _) in enumerate(names):
    ax = fig.add_subplot(gs[0, i])
    h = fields[k]
    rgb = ls.shade(h, cmap=plt.cm.Blues, vert_exag=1.0, blend_mode="soft",
                   vmin=-vmax, vmax=vmax)
    ax.imshow(rgb, extent=[0, L, 0, L], origin="lower", interpolation="bicubic")
    ax.set_xlim(0, L); ax.set_ylim(0, L)
    ax.set_xticks([0, 64, 128, 192, 256])
    ax.set_yticks([0, 64, 128, 192, 256])
    ax.set_xlabel("x (m)", labelpad=2)
    if i == 0:
        ax.set_ylabel("y (m)", labelpad=2)
    else:
        ax.set_yticklabels([])
    clean(ax, spines=("left", "bottom"))
    ax.tick_params(pad=2)

    bx = fig.add_subplot(gs[1, i])
    bx.plot(x, h[jmid], color=BLUE, lw=1.15)
    bx.axhline(0.0, color=GRID, lw=0.8)
    bx.set_xlim(0, L)
    bx.set_ylim(-2.1, 2.1)
    bx.set_xticks([0, 64, 128, 192, 256])
    bx.set_yticks([-2, 0, 2])
    bx.set_xlabel("x (m)", labelpad=2)
    if i == 0:
        bx.set_ylabel("η (m)", labelpad=2)
    else:
        bx.set_yticklabels([])
    clean(bx, spines=("left", "bottom"))
    bx.tick_params(pad=2)

label(fig, 0.075, 0.985, "高度场", fs=9, color=MUTED, ha="left", va="bottom")
label(fig, 0.075, 0.475, "中线剖面", fs=9, color=MUTED, ha="left", va="bottom")
save(fig, "11", "fig11-01")


# ------------------------------------------------------------
# 图 11-2  溃坝：Ritter 解析解 + HLL 有限体积
# ------------------------------------------------------------
g = G
h0 = 10.0
c0 = np.sqrt(g * h0)
x0, x1 = -220.0, 320.0


def ritter(x, t):
    xi = x / t
    h = np.where(xi <= -c0, h0, np.where(xi < 2 * c0,
                                         (2 * c0 - xi) ** 2 / (9 * g), 0.0))
    u = np.where(xi <= -c0, 0.0, np.where(xi < 2 * c0, 2.0 / 3 * (xi + c0), 0.0))
    return h, u


def hll_solve(Nc=800, T=12.0, cfl=0.5, hfloor=1e-6):
    dx = (x1 - x0) / Nc
    xc = x0 + (np.arange(Nc) + 0.5) * dx
    h = np.where(xc < 0.0, h0, hfloor)
    q = np.zeros(Nc)
    t = 0.0
    while t < T - 1e-12:
        c = np.sqrt(g * np.maximum(h, 0.0))
        u = q / np.maximum(h, hfloor)
        smax = np.max(np.abs(u) + c) + 1e-9
        dt = min(cfl * dx / smax, T - t)
        hL, hR = h[:-1], h[1:]
        qL, qR = q[:-1], q[1:]
        uL = qL / np.maximum(hL, hfloor)
        uR = qR / np.maximum(hR, hfloor)
        cL = np.sqrt(g * np.maximum(hL, 0.0))
        cR = np.sqrt(g * np.maximum(hR, 0.0))
        FL = np.stack([qL, qL * uL + 0.5 * g * hL ** 2], axis=-1)
        FR = np.stack([qR, qR * uR + 0.5 * g * hR ** 2], axis=-1)
        sL = np.minimum(uL - cL, uR - cR)
        sR = np.maximum(uL + cL, uR + cR)
        den = np.where(np.abs(sR - sL) < 1e-12, 1e-12, sR - sL)
        U = np.stack([h, q], axis=-1)
        Fhll = (sR[:, None] * FL - sL[:, None] * FR
                + sL[:, None] * sR[:, None] * (U[1:] - U[:-1])) / den[:, None]
        F = np.zeros((Nc, 2))
        F[:-1] = Fhll
        F[-1] = FR[-1]
        F[0] = FL[0]
        Un = U.copy()
        Un[1:-1] = U[1:-1] - dt / dx * (F[1:-1] - F[:-2])
        Un[0] = U[0] - dt / dx * (F[0] - F[0])
        Un[-1] = U[-1] - dt / dx * (F[-1] - F[-1])
        h = np.maximum(Un[:, 0], hfloor)
        q = Un[:, 1]
        q[h <= 1.5 * hfloor] = 0.0
        t += dt
    return xc, h


xc, hn = hll_solve()

fig = plt.figure(figsize=(6.9, 3.35))
gsf = fig.add_gridspec(1, 2, wspace=0.26, left=0.085, right=0.985,
                       top=0.965, bottom=0.155)

# ---- (a) x-t 平面上的特征线 ----
ax = fig.add_subplot(gsf[0, 0])
tmax = 12.0
# 静水区
ax.add_patch(Rectangle((x0, 0), -c0 * tmax - x0, tmax, facecolor="#EFF4FF",
                       edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 0), 2 * c0 * tmax, tmax, facecolor="#ECFDF5",
                       edgecolor="none", zorder=0))
# 稀疏扇
cs = np.linspace(c0, 1e-9, 60)
for c in cs[::4]:
    slope = 2 * c0 - 3 * c
    ax.plot([0, slope * tmax], [0, tmax], color=BLUE, lw=0.75, alpha=0.75, zorder=2)
for c in cs[1::4]:
    slope = 2 * c0 - 3 * c
    ax.plot([0, slope * tmax], [0, tmax], color=BLUE, lw=0.75, alpha=0.4, zorder=2)
# 静水区特征线
for xt in np.arange(-210, -c0 * tmax, 26):
    ax.plot([xt, xt - c0 * tmax], [0, tmax], color=FAINT, lw=0.6, ls=(0, (5, 3)), zorder=1)
# 激波（干底波前）
ax.plot([0, 2 * c0 * tmax], [0, tmax], color=ACCENT, lw=1.7, ls="--", zorder=4)
ax.plot([0, -c0 * tmax], [0, tmax], color=MUTED, lw=1.1, zorder=3)
ax.set_xlim(x0, x1); ax.set_ylim(0, tmax)
ax.set_xlabel("x (m)", labelpad=2)
ax.set_ylabel("t (s)", labelpad=2)
ax.set_xticks([-200, -100, 0, 100, 200, 300])
ax.set_yticks([0, 4, 8, 12])
clean(ax)
label(ax, -150, 10.3, "静水 $h_0$", fs=8.4, color=MUTED)
label(ax, 96, 10.3, "稀疏扇", fs=8.4, color=BLUE)
label(ax, 262, 5.2, "干底", fs=8.4, color=MUTED)
label(ax, 122, 2.05, "波前 $2\\sqrt{gh_0}\\,t$", fs=8.0, color=ACCENT, rot=30)
ax.text(-212, 12.45, "(a)", fontsize=8.6, color=INK, ha="left", va="top")

# ---- (b) 水深剖面 ----
bx = fig.add_subplot(gsf[0, 1])
cols = [BLUE, TEAL, PURPLE]
for t, cc in zip((4.0, 8.0, 12.0), cols):
    hh, _ = ritter(x, t)
    bx.plot(x, hh, color=cc, lw=1.6)
bx.plot(xc[::40], hn[::40], "o", ms=3.6, mfc="white", mec=ACCENT, mew=1.0,
        label="HLL（$N=800$）")
bx.set_xlim(-60, 300); bx.set_ylim(-0.4, 10.6)
bx.set_xlabel("x (m)", labelpad=2)
bx.set_ylabel("水深 $h$ (m)", labelpad=2)
bx.set_xticks([0, 100, 200, 300])
bx.set_yticks([0, 2, 4, 6, 8, 10])
clean(bx)
bx.legend(loc="upper right", bbox_to_anchor=(0.99, 0.99), handlelength=1.1,
          labelspacing=0.3, borderaxespad=0.2)
for t, cc, yy in zip((4.0, 8.0, 12.0), cols, (9.05, 8.35, 7.65)):
    bx.text(0.03, yy, f"t = {t:.0f} s", transform=bx.get_yaxis_transform(),
            fontsize=8.2, color=cc, ha="left", va="center")
bx.text(0.985, 0.03, "(b)", transform=bx.transAxes, fontsize=8.6, color=INK,
        ha="right", va="bottom")

save(fig, "11", "fig11-02")

print("front at t=12: %.1f m" % (2 * c0 * 12))
