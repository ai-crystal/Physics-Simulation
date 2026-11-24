import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ============================================================
# 图 10-1  浸没比例与附加质量（公式直接计算）
#   静水平衡：V_sub / V = rho_b / rho_f
#   球体附加质量：m_a = 0.5 * rho_f * V  =>  m_a / m_b = rho_f / (2 rho_b)
# ============================================================
rho_f = 1000.0
mats = [("泡沫", 50.0), ("松木", 500.0), ("橡木", 720.0), ("冰", 917.0)]

fig, (ax1, ax2) = new(6.9, 3.15, ncols=2,
                      gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.30))

# ---------- (a) 平衡时的浸没比例 ----------
s = np.linspace(0.0, 1.0, 400)
ax1.plot(s, s, color=INK, lw=1.4, zorder=3)
ax1.fill_between(s, 0.0, s, color=SOFT[1], zorder=1)

for name, rho in mats:
    sr = rho / rho_f
    ax1.plot([sr], [sr], "o", ms=5.0, mfc="white", mec=ACCENT, mew=1.3, zorder=6)

rows = [(0.300, "泡沫 0.05"), (0.215, "松木 0.50"),
        (0.130, "橡木 0.72"), (0.045, "冰 0.92")]
for ty, txt in rows:
    ax1.plot([0.660], [ty], "o", ms=4.6, mfc="white", mec=ACCENT, mew=1.2, zorder=6)
    ax1.text(0.690, ty, txt, fontsize=8.2, color=ACCENT, ha="left", va="center")

ax1.set_xlim(0.0, 1.04)
ax1.set_ylim(0.0, 1.04)
ax1.set_xlabel(r"密度比 $\rho_b/\rho_f$")
ax1.set_ylabel(r"浸没体积比例 $V_{sub}/V$")
clean(ax1, grid=True)
ax1.text(0.035, 0.962, "（a）平衡时的浸没比例", transform=ax1.transAxes,
         fontsize=9.0, color=INK, weight="bold", va="top")

# ---------- (b) 附加质量与自重之比 ----------
sr = np.logspace(np.log10(0.05), np.log10(2.2), 500)
ratio = 1.0 / (2.0 * sr)
ax2.loglog(sr, ratio, color=BLUE, lw=1.5, zorder=4)
ax2.axhline(1.0, color=ACCENT, lw=1.0, ls=(0, (3, 2.4)), zorder=3)
ax2.axvline(0.5, color=ACCENT, lw=0.9, ls=(0, (1.4, 2.2)), zorder=3)
ax2.fill_between(sr, 1.0, np.maximum(ratio, 1.0), where=(ratio > 1.0),
                 color=SOFT[0], zorder=1)
ax2.text(0.058, 1.52, "附加质量大于自重", fontsize=8.2, color=ACCENT, ha="left")
ax2.text(0.560, 1.16, r"$m_a = m_b$", fontsize=8.0, color=ACCENT, ha="left")

for name, rho in mats:
    s0 = rho / rho_f
    ax2.plot([s0], [1.0 / (2.0 * s0)], "o", ms=4.6, mfc="white", mec=BLUE,
             mew=1.2, zorder=6)

ax2.set_xlim(0.044, 2.4)
ax2.set_ylim(0.2, 16.0)
ax2.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0, 2.0])
ax2.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1", "2"])
ax2.set_yticks([0.25, 0.5, 1, 2, 5, 10])
ax2.set_yticklabels(["0.25", "0.5", "1", "2", "5", "10"])
ax2.set_xlabel(r"密度比 $\rho_b/\rho_f$")
ax2.set_ylabel(r"$m_a/m_b$")
clean(ax2, grid=True)
ax2.text(0.035, 0.962, "（b）球的附加质量与自重之比", transform=ax2.transAxes,
         fontsize=9.0, color=INK, weight="bold", va="top")

save(fig, "10", "fig10-01")


# ============================================================
# 图 10-2  交替耦合的穿透（真实一维模拟）
#   两个质量各 1 kg，耦合刚度 k = 2e4 N/m，阻尼 c = 20 N*s/m
#   初始穿透 2 cm，omega = sqrt(k(1/mb+1/mf)) = 200 rad/s
#   交替耦合：先按旧的穿透算力更新流体一侧，再用同一个力更新刚体
#   联合隐式：对两个质量同时做后向欧拉，解 2x2 线性系统
# ============================================================
MB = MF = 1.0
K = 2.0e4
C = 20.0
P0 = 0.02
OMEGA = np.sqrt(K * (1.0 / MB + 1.0 / MF))


def run(dt, T, mode):
    n = int(round(T / dt))
    xb, xf = P0, 0.0
    vb, vf = 0.0, 0.0
    ts, ps = [0.0], [P0]
    for i in range(n):
        if mode == "stagger":
            F = K * (xb - xf) + C * (vb - vf)
            vf2 = vf + dt * F / MF
            xf2 = xf + dt * vf2
            vb2 = vb - dt * F / MB
            xb2 = xb + dt * vb2
        else:
            A = np.array([[MB + dt * C + dt * dt * K, -dt * C - dt * dt * K],
                          [-dt * C - dt * dt * K, MF + dt * C + dt * dt * K]])
            rhs = np.array([MB * vb - dt * K * (xb - xf),
                            MF * vf + dt * K * (xb - xf)])
            vb2, vf2 = np.linalg.solve(A, rhs)
            xb2 = xb + dt * vb2
            xf2 = xf + dt * vf2
        xb, xf, vb, vf = xb2, xf2, vb2, vf2
        ts.append((i + 1) * dt)
        ps.append(xb - xf)
    return np.array(ts), np.array(ps)


T = 0.2
t_a, p_a = run(1.0 / 60.0, T, "stagger")
t_b, p_b = run(1.0 / 240.0, T, "stagger")
t_c, p_c = run(1.0 / 60.0, T, "implicit")


def envelope(t, p):
    sgn = np.sign(p)
    cut = np.where(sgn[1:] != sgn[:-1])[0]
    bounds = np.concatenate(([0], cut + 1, [len(p)]))
    tp, ap = [], []
    for a, b in zip(bounds[:-1], bounds[1:]):
        seg = np.abs(p[a:b])
        k = a + int(np.argmax(seg))
        tp.append(t[k])
        ap.append(abs(p[k]))
    return np.array(tp), np.array(ap)


eb_t, eb_a = envelope(t_b, p_b)
ec_t, ec_a = envelope(t_c, p_c)

fig, ax = new(6.8, 3.3)
ax.semilogy(t_a, np.abs(p_a), color=ACCENT, lw=1.5,
            label=r"交替耦合，$\Delta t = 1/60$ s", zorder=4)
ax.semilogy(eb_t, eb_a, "-o", color=BLUE, lw=1.2, ms=3.4, mfc=BLUE, mec=BLUE,
            label=r"交替耦合，$\Delta t = 1/240$ s", zorder=3)
ax.semilogy(ec_t, ec_a, "-o", color=GREEN, lw=1.2, ms=3.0, mfc=GREEN, mec=GREEN,
            label=r"联合隐式，$\Delta t = 1/60$ s", zorder=3)

ax.annotate("每步放大约十倍", xy=(0.056, 34.0), xytext=(0.078, 2.2),
            fontsize=8.2, color=ACCENT, ha="left",
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9,
                            mutation_scale=8, shrinkA=3, shrinkB=3))
ax.set_xlim(0.0, T)
ax.set_ylim(1e-8, 300.0)
ax.set_xlabel("时间 / s")
ax.set_ylabel("穿透幅度 / m")
ax.legend(loc="upper right", fontsize=7.8, handlelength=1.8)
clean(ax, grid=True)
save(fig, "10", "fig10-02")
