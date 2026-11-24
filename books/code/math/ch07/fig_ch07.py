import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 7-1  牛顿法：好初值与坏初值
#   f(x) = x^3 - 2x + 2,  f'(x) = 3x^2 - 2
#   好初值 x0 = 2.0 -> 收敛到 -1.769292
#   坏初值 x0 = 1.5 -> 落入 1.0 <-> 0.0 的二周期
# ============================================================
F = lambda x: x ** 3 - 2 * x + 2
DF = lambda x: 3 * x ** 2 - 2


def newton(x0, n=8):
    xs = [x0]
    x = x0
    for _ in range(n):
        d = DF(x)
        if abs(d) < 1e-14:
            break
        x = x - F(x) / d
        xs.append(x)
    return np.array(xs)


xg = newton(2.0, 7)
xb = newton(1.5, 6)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.15),
                               gridspec_kw=dict(width_ratios=[1.30, 1.0], wspace=0.33))

# ---------------- 左：切线构造 ----------------
clean(axL, grid=True)
xx = np.linspace(-2.25, 2.25, 500)
axL.plot(xx, F(xx), color=INK, lw=1.5, zorder=5)
axL.axhline(0, color=SLATE, lw=0.9, zorder=2)
axL.axvline(0, color="#D1D5DB", lw=0.7, zorder=1)

# 好初值：前四步的切线（(x_k, f) 到 (x_{k+1}, 0) 就是切线）
for k in range(4):
    axL.plot([xg[k], xg[k]], [0, F(xg[k])], color=BLUE, lw=0.9, ls=(0, (2, 2)), zorder=3)
    axL.plot([xg[k], xg[k + 1]], [F(xg[k]), 0], color=BLUE, lw=1.15, zorder=4)
axL.plot(xg, F(xg), "o", ms=3.4, color=BLUE, zorder=6)

# 坏初值：1.0 与 0.0 之间的二周期
for xa, xbn in ((1.0, 0.0), (0.0, 1.0)):
    axL.plot([xa, xa], [0, F(xa)], color=PINK, lw=0.9, ls=(0, (2, 2)), zorder=3)
    axL.plot([xa, xbn], [F(xa), 0], color=PINK, lw=1.5, zorder=4)
axL.plot([0.0, 1.0], [0.0, 0.0], "o", ms=4.0, color=PINK, zorder=6)

# 根
r = xg[-1]
axL.plot([r], [0], "o", ms=5.2, mfc="white", mec=GREEN, mew=1.4, zorder=7)
axL.annotate("根 %.5f" % r, xy=(r + 0.05, 0.05), xytext=(0.42, -2.75),
             fontsize=8.4, color=GREEN,
             arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.8, shrinkA=2, shrinkB=3))

label(axL, 1.92, 7.55, "初值 $x_0=2.0$", fs=8.6, color=BLUE, ha="right", weight="bold")
label(axL, 1.92, 6.92, "七步后残差 $10^{-3}$", fs=8.3, color=BLUE, ha="right")
label(axL, 2.28, -3.55, "初值 $x_0=1.5$", fs=8.6, color=PINK, ha="right", weight="bold")
label(axL, 2.28, -4.15, "跳进 1 与 0 的循环", fs=8.3, color=PINK, ha="right")
axL.annotate("", xy=(0.55, -0.12), xytext=(1.62, -3.72),
             arrowprops=dict(arrowstyle="-|>", color=PINK, lw=0.8,
                             connectionstyle="arc3,rad=0.18", shrinkA=2, shrinkB=3))

label(axL, -2.18, -4.35, "$f(x)=x^3-2x+2$", fs=9.0, color=INK, ha="left")
axL.set_xlim(-2.3, 2.35)
axL.set_ylim(-5.0, 8.6)
axL.set_xticks([-2, -1, 0, 1, 2])
axL.set_yticks([-4, -2, 0, 2, 4, 6, 8])
axL.set_xlabel("$x$")
axL.set_ylabel("$f(x)$")

# ---------------- 右：残差历史 ----------------
clean(axR, grid=True)
kg = np.arange(len(xg))
kb = np.arange(len(xb))
rg = np.abs(F(xg))
rb = np.abs(F(xb))
axR.semilogy(kg, np.maximum(rg, 1e-14), "-o", color=BLUE, ms=4.0, lw=1.3, zorder=5)
axR.semilogy(kb, rb, "-s", color=PINK, ms=4.0, lw=1.3, zorder=4)
axR.set_ylim(8e-15, 6.0)
axR.set_xlim(-0.25, 7.4)
axR.set_xticks([0, 2, 4, 6])
axR.set_xlabel("迭代步 $k$")
axR.set_ylabel("$|f(x_k)|$")

axR.text(0.18, 8e-8, "二周期：残差\n在两个值间跳动", color=PINK, fontsize=8.3,
         va="top", ha="left", linespacing=1.55)
axR.text(4.30, 2.2e-6, "二次收敛", color=BLUE, fontsize=8.6, va="center", ha="left")

save(fig, "07", "fig07-01")

# ============================================================
# 图 7-2  回溯线搜索
#   f(x) = x^3 - 2x + 2, 从 x0 = 1.0 出发
#   牛顿方向 p = -f/f' = -1.0
#   价值函数 phi(alpha) = 0.5 * f(x0 + alpha*p)^2
#   Armijo: phi(alpha) <= phi(0) + c*alpha*phi'(0), c = 1e-4
# ============================================================
fig, ax = plt.subplots(figsize=(6.6, 3.25))
clean(ax, grid=True)

x0, p = 1.0, -1.0
phi = lambda a: 0.5 * F(x0 + a * p) ** 2
dphi0 = F(x0) * DF(x0) * p          # = -1.0
phi0 = phi(0.0)
C1 = 1e-4

aa = np.linspace(0, 1.12, 600)
ax.semilogy(aa, phi(aa), color=INK, lw=1.6, zorder=5)
ax.semilogy(aa, phi0 + C1 * aa * dphi0, color=GREEN, lw=1.0, ls=(0, (5, 3)), zorder=4)

trial = [1.0, 0.5, 0.25]
for a in trial:
    ok = phi(a) <= phi0 + C1 * a * dphi0
    ax.plot([a], [phi(a)], "o", ms=5.4, mfc=("white" if ok else ACCENT),
            mec=(GREEN if ok else ACCENT), mew=1.4, zorder=7)
ax.plot([0.0], [phi0], "o", ms=5.0, color=INK, zorder=7)

ax.text(0.045, 2.22, "全步长 $\\alpha=1$ 使残差翻倍，\n逐次减半，到 $1/4$ 才下降",
        color=INK, fontsize=8.5, ha="left", va="top", linespacing=1.6)
ax.plot([0.055], [1.55], "o", ms=5.2, mfc="white", mec=ACCENT, mew=1.4, zorder=7)
ax.text(0.085, 1.55, "不满足 Armijo", color=ACCENT, fontsize=8.2, ha="left", va="center")
ax.plot([0.055], [1.36], "o", ms=5.2, mfc="white", mec=GREEN, mew=1.4, zorder=7)
ax.text(0.085, 1.36, "满足 Armijo", color=GREEN, fontsize=8.2, ha="left", va="center")
ax.text(0.83, 0.462, "Armijo 上限", color=GREEN, fontsize=8.3, ha="center", va="top")

ax.set_xlim(-0.02, 1.14)
ax.set_ylim(0.36, 2.35)
ax.set_yticks([0.4, 0.6, 1.0, 1.5, 2.0])
ax.set_yticklabels(["0.4", "0.6", "1.0", "1.5", "2.0"])
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel("步长 $\\alpha$")
ax.set_ylabel("$\\phi(\\alpha)=\\frac{1}{2}f(x_0+\\alpha p)^2$")

save(fig, "07", "fig07-02")

# ============================================================
# 图 7-3  force-gap 平面上的互补分区（示意图）
# ============================================================
fig, ax = canvas(6.5, 4.0, xlim=(-1.42, 1.52), ylim=(-1.02, 1.46))

ax.add_patch(Rectangle((0, 0), 1.52, 1.46, facecolor="#ECFDF5", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((-1.42, -0.70), 1.42, 2.16, facecolor="#FDF2F8", edgecolor="none", zorder=1))
ax.add_patch(Rectangle((0.02, 0.02), 1.50, 1.44, facecolor="#FFFBEB", edgecolor="none", zorder=2))

ax.annotate("", xy=(1.50, 0), xytext=(-1.40, 0),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
ax.annotate("", xy=(0, 1.44), xytext=(0, -1.00),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1))
label(ax, 1.48, -0.09, "间隙 $g$", fs=9.4, ha="right", va="top")
label(ax, 0.09, 1.42, "法向力 $\\lambda$", fs=9.4, ha="left", va="top")

ax.plot([0.035, 1.42], [0, 0], color=ACCENT, lw=2.4, zorder=6, solid_capstyle="round")
ax.plot([0, 0], [0.035, 1.40], color=ACCENT, lw=2.4, zorder=6, solid_capstyle="round")
ax.plot([0], [0], "o", ms=6.0, mfc="white", mec=ACCENT, mew=1.6, zorder=8)

label(ax, 0.62, 0.115, "分离：$g>0,\\ \\lambda=0$", fs=9.0, color=ACCENT, ha="center")

label(ax, -0.12, 0.98, "接触：$g=0$，$\\lambda>0$", fs=9.0, color=ACCENT, ha="right")
arrow(ax, (-0.10, 0.98), (-0.03, 0.98), color=ACCENT, lw=0.9, ms=7)

label(ax, 0.20, 0.86, "非互补：$g>0$ 且 $\\lambda>0$", fs=8.6, color=MUTED, ha="left")
label(ax, 0.20, 0.72, "迭代中允许，收敛后必须离开", fs=8.0, color=FAINT, ha="left")

label(ax, -0.74, 0.60, "穿透：$g<0$", fs=9.2, color=PINK, ha="center", weight="bold")
label(ax, -0.74, 0.46, "任何 $\\lambda$ 都不可接受", fs=8.2, color=PINK, ha="center")
ax.plot([-0.74], [-0.34], "o", ms=5.0, color=PINK, zorder=7)
label(ax, -0.74, -0.50, "迭代中常见的起点", fs=8.2, color=MUTED, ha="center", va="top")
ax.annotate("", xy=(-0.04, 0.33), xytext=(-0.66, -0.26),
            arrowprops=dict(arrowstyle="-|>", color=SLATE, lw=1.0, ls=(0, (4, 3)),
                            connectionstyle="arc3,rad=0.30"))

label(ax, 0.24, -0.20, "原点：刚好接触、无挤压", fs=8.2, color=ACCENT, ha="left", va="top")

save(fig, "07", "fig07-03")
