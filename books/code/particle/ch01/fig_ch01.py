import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from matplotlib.patches import RegularPolygon, Arc

# ============================================================
# 图 1-1  休止角与颗粒形状（示意图）
#   左：圆颗粒堆，颗粒几乎不能互锁，滚动阻力小
#   右：棱角颗粒堆，颗粒卡在邻居的凹坑里，滑动前要先挤开邻居
# ============================================================
RNG = np.random.default_rng(7)
RG = 0.0125          # 颗粒半径（画布坐标）
Y0 = 0.030           # 地面高度


def pile_grains(apex_x, half_base, height, r, seed=1, jitter=0.14):
    """在三角形区域里按六角格点摆颗粒，返回落在内部的圆心（已抬到地面上）。"""
    rng = np.random.default_rng(seed)
    pts = []
    d = 2.0 * r * 1.04
    dy = d * 0.866
    y = r * 1.05
    row = 0
    while y < height - r * 0.3:
        frac = (height - y) / height
        half = half_base * frac
        n = int(2 * half / d) + 1
        xs = np.linspace(apex_x - half + r, apex_x + half - r, max(n, 1))
        if row % 2:
            xs = xs + d * 0.5
        for x in xs:
            if abs(x - apex_x) < half - r * 0.95:
                px = x + rng.normal(0, jitter * r)
                py = y + rng.normal(0, jitter * r)
                if py > r * 0.5:
                    pts.append((px, Y0 + py))
        y += dy
        row += 1
    return np.array(pts)


def draw_pile(ax, apex_x, half_base, height, round_grains=True, seed=3):
    pts = pile_grains(apex_x, half_base, height, RG, seed=seed)
    for x, y in pts:
        if round_grains:
            ax.add_patch(Circle((x, y), RG, facecolor="#F2DFC0", edgecolor="#8E7248",
                                lw=0.4, zorder=3))
        else:
            nv = 4 + int(RNG.integers(0, 3))
            ax.add_patch(RegularPolygon((x, y), nv, radius=RG * 1.10,
                                        orientation=RNG.uniform(0, 2 * np.pi),
                                        facecolor="#EFE0C4", edgecolor="#8E7248",
                                        lw=0.45, zorder=3))
    return pts


def angle_arc(ax, toe, slope_deg, rad, text):
    ax.add_patch(Arc(toe, 2 * rad, 2 * rad, theta1=0, theta2=slope_deg,
                     color=MUTED, lw=0.9, zorder=6))
    ax.text(toe[0] - 0.016, toe[1] + 0.006, text, fontsize=9.0, color=ACCENT,
            ha="right", va="bottom", zorder=7)


fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.75))
for ax in axs:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.425)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0.03, 0.006), 0.94, 0.024, facecolor="#E7E2D8",
                           edgecolor="none", zorder=1))
    ax.plot([0.03, 0.97], [Y0, Y0], color=INK, lw=1.2, zorder=2,
            solid_capstyle="butt")

# ---------- 左：圆颗粒 ----------
ax = axs[0]
HB, H = 0.42, 0.42 * np.tan(np.deg2rad(20.0))
draw_pile(ax, 0.50, HB, H, round_grains=True, seed=11)
ax.plot([0.50 - HB, 0.50], [Y0, Y0 + H], color=ACCENT, lw=1.3, ls=(0, (5, 2)),
        zorder=6)
angle_arc(ax, (0.50 - HB, Y0), 20.0, 0.075, "约 20°")
gx = 0.50 - 0.26
gy = Y0 + 0.26 * np.tan(np.deg2rad(20.0)) + RG * 2.2
ax.add_patch(Circle((gx, gy), RG * 1.5, facecolor="white", edgecolor=ACCENT,
                    lw=1.0, zorder=8))
ax.add_patch(Arc((gx, gy), 0.062, 0.062, theta1=200, theta2=330, color=ACCENT,
                 lw=1.0, zorder=9))
arrow(ax, (gx + 0.031, gy - 0.008), (gx + 0.036, gy - 0.040), color=ACCENT,
      lw=0.9, ms=6)
ax.text(0.02, 0.408, "圆颗粒", fontsize=9.6, color=INK, ha="left", va="top")
ax.text(0.02, 0.356, "滚动阻力小，坡面上留不住", fontsize=8.2, color=MUTED,
        ha="left", va="top")

# ---------- 右：棱角颗粒 ----------
ax = axs[1]
HB2, H2 = 0.40, 0.40 * np.tan(np.deg2rad(33.0))
draw_pile(ax, 0.50, HB2, H2, round_grains=False, seed=23)
ax.plot([0.50 - HB2, 0.50], [Y0, Y0 + H2], color=ACCENT, lw=1.3, ls=(0, (5, 2)),
        zorder=6)
angle_arc(ax, (0.50 - HB2, Y0), 33.0, 0.065, "约 33°")
cx, cy = 0.50 - 0.10, Y0 + H2 * 0.46
ax.add_patch(Circle((cx, cy), RG * 3.0, facecolor="none", edgecolor=BLUE, lw=0.95,
                    ls=(0, (2, 2)), zorder=9))
arrow(ax, (cx - RG * 3.4, cy + RG * 1.2), (cx - RG * 3.4, cy + RG * 3.4),
      color=BLUE, lw=0.85, ms=6, z=9)
arrow(ax, (cx + RG * 0.9, cy + RG * 1.4), (cx + RG * 0.9, cy + RG * 3.6),
      color=BLUE, lw=0.85, ms=6, z=9)
ax.text(0.02, 0.408, "棱角颗粒", fontsize=9.6, color=INK, ha="left", va="top")
ax.text(0.02, 0.356, "互相卡住，滑动前要先挤开邻居", fontsize=8.2, color=MUTED,
        ha="left", va="top")

save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  粮仓效应：Janssen 公式
#   dσz/dz = ρb g − λ σz ,  λ = 2 μw K / R
#   σz(z) = (ρb g / λ)(1 − exp(−λ z))
# ============================================================
R = 0.15
RHOB = 1500.0
G = 9.81
KK = 0.50
Z = np.linspace(0, 3.0, 400)
MUS = [0.2, 0.4, 0.6]
COLS = [BLUE, ACCENT, GREEN]

fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.25))

ax = axs[0]
ax.plot(RHOB * G * Z / 1000, Z, color=FAINT, lw=1.2, ls=(0, (4, 2)),
        label="静水压力 $\\rho_b g z$")
for mu, c in zip(MUS, COLS):
    lam = 2 * mu * KK / R
    s = RHOB * G / lam * (1 - np.exp(-lam * Z)) / 1000
    ax.plot(s, Z, color=c, lw=1.6, label="$\\mu_w$ = %.1f" % mu)
ax.invert_yaxis()
ax.set_xlabel("竖向应力 $\\sigma_z$  (kPa)")
ax.set_ylabel("深度 $z$  (m)")
ax.set_xlim(0, 46)
ax.set_ylim(3.12, -0.06)
clean(ax, grid=True)
ax.legend(loc="upper right", handlelength=1.5, labelspacing=0.32, borderpad=0.15,
          bbox_to_anchor=(0.985, 0.985))

ax = axs[1]
Hh = np.linspace(0, 3.0, 400)
for mu, c in zip(MUS, COLS):
    lam = 2 * mu * KK / R
    s = RHOB * G / lam * (1 - np.exp(-lam * Hh)) / 1000
    ax.plot(Hh, s, color=c, lw=1.6)
    ax.axhline(RHOB * G / lam / 1000, color=c, lw=0.8, ls=(0, (2, 2)), alpha=0.55)
    ax.plot([1 / lam], [RHOB * G / lam * (1 - np.exp(-1)) / 1000], "o", ms=3.6,
            color=c, zorder=5)
ax.annotate("虚线为饱和压力\n圆点对应 $H=\\lambda^{-1}$", xy=(1.32, 9.6),
            xytext=(1.52, 2.2), fontsize=8.2, color=MUTED,
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=-0.25"))
ax.set_xlabel("装料高度 $H$  (m)")
ax.set_ylabel("仓底压力 (kPa)")
ax.set_xlim(0, 3)
ax.set_ylim(0, 15.0)
clean(ax, grid=True)
ax.text(0.04, 0.055, "装料超过约 1 m 后压力几乎不再上升", transform=ax.transAxes,
        fontsize=8.2, color=MUTED, va="bottom")

save(fig, "01", "fig01-02")

lam4 = 2 * 0.4 * KK / R
print("lambda^-1 (mu=0.4) = %.3f m, 饱和压力 %.0f Pa, 1m 处 %.0f Pa" % (
    1 / lam4, RHOB * G / lam4, RHOB * G / lam4 * (1 - np.exp(-lam4))))
