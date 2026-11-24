import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

FRAME = 1.0 / 60.0


# ============================================================
# 图 8-1  铰链约束误差随时间（真实 2D 模拟）
# ============================================================
def hinge_error(iters=4, sub=1, T=20.0, beta=0.2, L=1.0, m=1.0, g=9.81):
    """均质杆一端铰接，PGS 逐行求解二维点约束，Baumgarte 偏置。"""
    dt = FRAME / sub
    inertia = m * L * L / 12.0
    invm, invI = 1.0 / m, 1.0 / inertia
    x = np.array([-L / 2.0, 0.0])       # 质心，使杆端位于原点
    th = 0.0
    v = np.zeros(2)
    w = 0.0
    rloc = np.array([L / 2.0, 0.0])
    errs = []
    for _ in range(int(round(T / FRAME))):
        for _s in range(sub):
            v[1] += -g * dt
            for _it in range(iters):
                R = np.array([[np.cos(th), -np.sin(th)],
                              [np.sin(th), np.cos(th)]])
                r = R @ rloc
                p = x + r
                for row in (0, 1):
                    J = np.array([1.0 if row == 0 else 0.0,
                                  1.0 if row == 1 else 0.0,
                                  -r[1] if row == 0 else r[0]])
                    Jv = J[0] * v[0] + J[1] * v[1] + J[2] * w
                    k = invm * (J[0] ** 2 + J[1] ** 2) + invI * J[2] ** 2
                    lam = -(Jv + beta / dt * p[row]) / k
                    v[0] += invm * J[0] * lam
                    v[1] += invm * J[1] * lam
                    w += invI * J[2] * lam
            x += v * dt
            th += w * dt
        R = np.array([[np.cos(th), -np.sin(th)],
                      [np.sin(th), np.cos(th)]])
        errs.append(np.linalg.norm(x + R @ rloc))
    return np.array(errs)


t = np.arange(int(round(20.0 / FRAME))) * FRAME
cases = [(1, 1, ACCENT, "1 次迭代"),
         (4, 1, BLUE, "4 次迭代"),
         (4, 4, GREEN, "4 次迭代 + 4 子步")]
fig, ax = plt.subplots(figsize=(6.5, 3.3))
for it, sub, c, lab in cases:
    e = hinge_error(iters=it, sub=sub) * 1000.0
    ax.semilogy(t[1:], e[1:], color=c, lw=0.85, alpha=0.9, label=lab)

ax.set_xlim(0, 20)
ax.set_ylim(1e-3, 70)
ax.set_xlabel("时间 $t$（s）", fontsize=9.6)
ax.set_ylabel("铰点位置误差（mm）", fontsize=9.6)
clean(ax, grid=True)
ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.005, 1.0, 0.12),
          mode="expand", ncol=3, fontsize=8.0, handlelength=1.5,
          columnspacing=1.2, borderaxespad=0.2)

fig.subplots_adjust(left=0.105, right=0.982, top=0.885, bottom=0.155)
save(fig, "08", "fig08-01")

for it, sub, _c, _lab in cases:
    e = hinge_error(iters=it, sub=sub) * 1000.0
    print("iters=%d sub=%d mean_last=%.3f mm max=%.3f mm"
          % (it, sub, e[-600:].mean(), e.max()))


# ============================================================
# 图 8-2  柔度与跟随误差（真实计算）
# ============================================================
m = 1.0
g = 9.81
f = 2.0
omega = 2.0 * np.pi * f
alpha = np.logspace(-7, -2, 400)

sag_mm = alpha * m * g * 1000.0
ratio = omega ** 2 * alpha * m
follow_pct = ratio / np.abs(1.0 - ratio) * 100.0
a_res = 1.0 / (omega ** 2 * m)

fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.15),
                        gridspec_kw=dict(wspace=0.32))

ax = axs[0]
ax.loglog(alpha, sag_mm, color=ACCENT, lw=1.6)
ax.axhline(1.0, color=FAINT, lw=0.7, ls=(0, (2, 3)))
ax.set_xlim(1e-7, 1e-2)
ax.set_ylim(1e-3, 2e2)
ax.set_xlabel(r"柔度 $\alpha$（m/N）", fontsize=9.4)
ax.set_ylabel("静态下垂（mm）", fontsize=9.4)
clean(ax, grid=True)
for a0, lab, dx, dy, ha in ((1e-4, "0.98 mm", 1.45, 0.15, "left"),
                            (1e-3, "9.8 mm", 2.2, 0.32, "left")):
    y0 = a0 * m * g * 1000.0
    ax.plot([a0], [y0], "o", ms=4.2, color=ACCENT, mec="white", mew=0.7, zorder=5)
    ax.annotate(lab, xy=(a0, y0), xytext=(a0 * dx, y0 * dy),
                fontsize=8.0, color=ACCENT, ha=ha,
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.8,
                                connectionstyle="arc3,rad=-0.2"))
ax.text(1.15e-7, 1.25, "1 mm", fontsize=7.8, color=MUTED, va="bottom")

ax = axs[1]
ax.loglog(alpha, follow_pct, color=BLUE, lw=1.6)
ax.axvline(a_res, color=ACCENT, lw=1.0, ls=(0, (4, 3)))
ax.axhline(100.0, color=FAINT, lw=0.7, ls=(0, (2, 3)))
ax.set_xlim(1e-7, 1e-2)
ax.set_ylim(1e-3, 2e3)
ax.set_xlabel(r"柔度 $\alpha$（m/N）", fontsize=9.4)
ax.set_ylabel("跟随误差与目标振幅之比（%）", fontsize=9.4)
clean(ax, grid=True)
ax.text(1.15e-7, 130.0, "误差 = 目标振幅", fontsize=7.8, color=MUTED, va="bottom")
for a0, lab, dx, dy in ((1e-4, "1.6%", 2.6, 0.30), (1e-3, "19%", 2.6, 0.30)):
    r0 = omega ** 2 * a0 * m
    y0 = r0 / abs(1.0 - r0) * 100.0
    ax.plot([a0], [y0], "o", ms=4.2, color=BLUE, mec="white", mew=0.7, zorder=5)
    ax.annotate(lab, xy=(a0, y0), xytext=(a0 * dx, y0 * dy), fontsize=8.0, color=BLUE,
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8,
                                connectionstyle="arc3,rad=0.2"))

fig.subplots_adjust(left=0.10, right=0.982, top=0.965, bottom=0.155)
save(fig, "08", "fig08-02")

print("alpha_res=%.3e  sag(1e-4)=%.4f mm  follow=%.2f%%"
      % (a_res, 1e-4 * m * g * 1000, (omega**2 * 1e-4 * m) / abs(1 - omega**2 * 1e-4 * m) * 100))
