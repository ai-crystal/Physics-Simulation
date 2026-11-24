import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 6-1  弹簧拉滑块的粘滑（真实 1D 模拟）
#   m x'' = k (v_d t - x) - f_fric ；静摩擦上限 mu_s m g，动摩擦 mu_k m g
# ============================================================
m, k, vd = 1.0, 200.0, 0.01
mus, muk, gg = 0.5, 0.35, 9.81
dt = 2e-5
T = 6.0

N = int(round(T / dt))
tt = np.empty(N)
xx = np.empty(N)
vv = np.empty(N)
x, v = 0.0, 0.0
stuck = True
slips = []          # 突滑区间 (start, end)
t_slip = None
for i in range(N):
    t = i * dt
    F = k * (vd * t - x)
    if stuck:
        if abs(F) <= mus * m * gg:
            v = 0.0
        else:
            stuck = False
            v = 0.0
            t_slip = t
    if not stuck:
        f = muk * m * gg * np.sign(v if v != 0 else F)
        a = (F - f) / m
        vn = v + a * dt
        if v * vn < 0:
            vn = 0.0
            stuck = True
            slips.append((t_slip, t))
        v = vn
        x += v * dt
    tt[i], xx[i], vv[i] = t, x, v

print("slip events:", [(round(a, 3), round(b, 3)) for a, b in slips])
print("peak speed %.4f m/s" % np.abs(vv).max())

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.7, 4.7), sharex=True,
                               gridspec_kw=dict(height_ratios=[1.38, 1.0], hspace=0.14))
fig.subplots_adjust(left=0.105, right=0.975, bottom=0.11, top=0.97)

for a, b in slips:
    for ax in (ax1, ax2):
        ax.axvspan(a, b, color=ACCENT, alpha=0.13, lw=0, zorder=0)

ax1.plot(tt, vd * tt * 1e3, color=MUTED, lw=1.3, ls=(0, (5, 3)), label="驱动端 $v_d t$", zorder=3)
ax1.plot(tt, xx * 1e3, color=INK, lw=1.7, label="滑块 $x$", zorder=4)
ax1.set_ylabel("位移（mm）", fontsize=9.6)
ax1.set_xlim(0, T)
ax1.set_ylim(-4, 68)
ax1.grid(True, color=GRID, lw=0.7)
ax1.set_axisbelow(True)
clean(ax1)
ax1.legend(loc="upper left", handlelength=2.0, bbox_to_anchor=(0.005, 1.03))

# 弹簧伸长：两条曲线之间的竖直距离
ax1.annotate("", xy=(4.58, 46.0), xytext=(4.58, 18.0),
             arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.0, mutation_scale=8))
ax1.text(4.72, 31.5, "弹簧伸长", fontsize=8.5, color=GREEN, ha="left", va="center")

ax1.annotate("粘住：滑块不动", xy=(2.25, 0.5), xytext=(1.55, 3.0), fontsize=8.6, color=INK,
             ha="center", va="bottom",
             arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9, shrinkA=2, shrinkB=3))
ax1.annotate("突滑", xy=(2.57, 9.0), xytext=(2.80, 4.2), fontsize=8.6, color=ACCENT,
             ha="left", va="bottom",
             arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, shrinkA=2, shrinkB=3))

ax2.plot(tt, vv, color=ACCENT, lw=1.4, zorder=3)
ax2.axhline(0, color=FAINT, lw=0.8, zorder=1)
ax2.axhline(vd, color=MUTED, lw=1.0, ls=(0, (5, 3)), zorder=2)
ax2.set_ylabel("速度（m/s）", fontsize=9.6)
ax2.set_xlabel("时间（s）", fontsize=9.6)
ax2.set_ylim(-0.012, 0.145)
ax2.set_yticks([0, 0.04, 0.08, 0.12])
ax2.grid(True, color=GRID, lw=0.7)
ax2.set_axisbelow(True)
clean(ax2)
ax2.text(0.14, 0.0135, "驱动速度 0.01 m/s", fontsize=8.2, color=MUTED, ha="left", va="bottom")
ax2.text(2.75, 0.130, "峰值 0.115 m/s", fontsize=8.4, color=ACCENT, ha="left", va="center")

save(fig, "06", "fig06-01")


# ============================================================
# 图 6-2  摩擦系数对三层堆叠的影响（真实 1D 模拟）
#   竖直方向先解法向冲量，水平方向再解带 |p| <= mu*lam 的切向冲量
# ============================================================
g = 9.81
dt2 = 1.0 / 120.0
nbox, mb, F = 3, 1.0, 10.0
iters = 60
A = np.zeros((nbox, nbox))
for j in range(nbox):
    A[j, j] += 1.0 / mb
    if j >= 1:
        A[j, j] += 1.0 / mb
        A[j, j - 1] -= 1.0 / mb
    if j + 1 < nbox:
        A[j, j + 1] -= 1.0 / mb


def run(mu, T=1.5, keep=False):
    w = np.zeros(nbox)
    u = np.zeros(nbox)
    pos = np.zeros(nbox)
    hist = []
    for _ in range(int(round(T / dt2))):
        # 法向：先加一步重力
        w = w - g * dt2
        bn = w.copy()
        bn[1:] = w[1:] - w[:-1]
        lam = np.zeros(nbox)
        for _ in range(iters):
            for j in range(nbox):
                s = bn[j] + A[j] @ lam - A[j, j] * lam[j]
                lam[j] = max(0.0, -s / A[j, j])
        # 水平：外力只作用在顶箱
        u[2] += F * dt2 / mb
        bs = np.zeros(nbox)
        bs[0] = u[0]
        bs[1:] = u[1:] - u[:-1]
        p = np.zeros(nbox)
        for _ in range(iters):
            for j in range(nbox):
                s = bs[j] + A[j] @ p - A[j, j] * p[j]
                cap = mu * lam[j]
                p[j] = min(cap, max(-cap, -s / A[j, j]))
        for j in range(nbox):
            u[j] += p[j] - (p[j + 1] if j + 1 < nbox else 0.0)
        for j in range(nbox):
            w[j] += lam[j] - (lam[j + 1] if j + 1 < nbox else 0.0)
        pos += u * dt2
        if keep:
            hist.append(pos[2])
    return (np.array(hist), pos[2]) if keep else pos[2]


mu_star = F / (mb * g)
his8, d8 = run(0.80, keep=True)
his11, d11 = run(1.10, keep=True)
mu_list = np.linspace(0.05, 1.50, 30)
disp = np.array([run(mu) for mu in mu_list])
print("mu*=%.4f  disp(0.8)=%.3f  disp(1.10)=%.2e  disp(0.05)=%.2f"
      % (mu_star, d8, d11, disp[0]))

th = np.arange(len(his8)) * dt2
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.4),
                               gridspec_kw=dict(width_ratios=[1.05, 1.0], wspace=0.32))
fig.subplots_adjust(left=0.10, right=0.98, bottom=0.15, top=0.965)

ax1.plot(th, his11, color=GREEN, lw=1.7, label="μ = 1.10（站住）")
ax1.plot(th, his8, color=ACCENT, lw=1.7, label="μ = 0.80（滑走）")
ax1.set_xlim(0, 1.5)
ax1.set_ylim(-0.15, 3.0)
ax1.set_xlabel("时间（s）", fontsize=9.4)
ax1.set_ylabel("顶箱水平位移（m）", fontsize=9.4)
ax1.grid(True, color=GRID, lw=0.7)
ax1.set_axisbelow(True)
clean(ax1)
ax1.legend(loc="upper left", handlelength=1.8, bbox_to_anchor=(0.0, 1.03))
ax1.annotate("μ 越过阈值后位移为 0", xy=(1.12, 0.03), xytext=(0.86, 0.30),
             fontsize=8.3, color=GREEN, ha="left", va="bottom",
             arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9, shrinkA=2, shrinkB=3))
ax1.annotate("匀加速 $\\frac{1}{2}at^2$，$a=2.15$ m/s$^2$", xy=(1.26, 1.70), xytext=(0.06, 2.44),
             fontsize=8.3, color=ACCENT, ha="left", va="center",
             arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, shrinkA=3, shrinkB=3))

ax2.semilogy(mu_list, np.maximum(disp, 1e-10), color=INK, lw=1.5, marker="o", ms=3.4,
             mfc="white", mew=1.0, zorder=4)
ax2.axvline(mu_star, color=ACCENT, lw=1.2, ls=(0, (5, 3)), zorder=2)
ax2.annotate("μ* = F/mg = 1.02", xy=(1.005, 9e-10), xytext=(0.03, 3.2e-10),
             fontsize=8.4, color=ACCENT, ha="left", va="bottom",
             arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, shrinkA=3, shrinkB=3))
ax2.set_xlim(0, 1.55)
ax2.set_ylim(1e-10, 40)
ax2.set_xlabel("摩擦系数 μ", fontsize=9.4)
ax2.set_ylabel("1.5 s 后位移（m）", fontsize=9.4)
ax2.grid(True, axis="y", color=GRID, lw=0.7)
ax2.set_axisbelow(True)
clean(ax2)
ax2.text(1.32, 1.2e-8, "数值蠕变", fontsize=8.2, color=MUTED, ha="center", va="bottom")

save(fig, "06", "fig06-02")
