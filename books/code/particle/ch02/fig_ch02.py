import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 2-1  单次对撞：法向弹簧-阻尼
#   m* δ¨ = −k δ − c δ˙ (δ > 0)，分离后力截断为零
#   阻尼比与恢复系数： e = exp(−πζ/√(1−ζ²))
# ============================================================
MEFF = 6.9e-4        # 等效质量 (kg)，半径 5 mm 的石英球
KN = 2.0e4           # 法向刚度 (N/m)
V0 = 1.0             # 入射速度 (m/s)
DT = 2.0e-6


def impact(zeta, keep=True):
    """积分一次对撞，返回 (delta, F, e_meas)。"""
    c = 2.0 * zeta * np.sqrt(KN * MEFF)
    d, v = 0.0, V0
    dhist, fhist = [], []
    for _ in range(400000):
        F = max(KN * d + c * v, 0.0) if d > 0 else 0.0
        if keep:
            dhist.append(d)
            fhist.append(F)
        v += -F / MEFF * DT
        d += v * DT
        if d <= 0 and v < 0:
            break
    return np.array(dhist), np.array(fhist), -v / V0


def calibrate(e_target):
    """二分阻尼比，让数值恢复系数落在目标值上。"""
    lo, hi = 1e-4, 0.999
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if impact(mid, keep=False)[2] > e_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.15))

ax = axs[0]
rows = []
for et, cl, lab in [(0.15, MUTED, "$e=0.15$"), (0.5, ACCENT, "$e=0.5$"),
                    (0.9, BLUE, "$e=0.9$")]:
    z = calibrate(et)
    dh, fh, em = impact(z)
    ax.plot(dh * 1000, fh, color=cl, lw=1.5, label=lab)
    rows.append((et, z, 2.0 * z * np.sqrt(KN * MEFF)))
    print("目标 e=%.2f  ζ=%.3f  c=%.2f N s/m  δmax=%.4f mm  Fmax=%.2f N  e数值=%.3f"
          % (et, z, 2.0 * z * np.sqrt(KN * MEFF), dh.max() * 1000, fh.max(), em))
ax.set_xlabel("压入量 $\\delta$  (mm)")
ax.set_ylabel("法向力 $F_n$  (N)")
ax.set_xlim(0, 0.215)
ax.set_ylim(0, 8.4)
clean(ax, grid=True)
ax.legend(loc="upper left", handlelength=1.6, labelspacing=0.3, borderpad=0.15)

# 纯弹簧参照线与 k、c 的标注
dd = np.array([0.0, 0.215])
ax.plot(dd, KN * dd / 1000.0, color=FAINT, lw=1.0, ls=(0, (5, 2.5)), zorder=1)
txt = ["$k_n=2\\times10^{4}$ N/m",
       "$m^{*}=6.9\\times10^{-4}$ kg",
       "$e$ / $\\zeta$ / $c_n$  [N·s/m]",
       "0.15 / 0.93 / 6.89",
       "0.50 / 0.26 / 1.90",
       "0.90 / 0.03 / 0.26"]
ax.text(0.079, 6.30, "\n".join(txt), fontsize=6.9, color=INK, ha="left", va="top",
        linespacing=1.50)
ax.text(0.975, 0.965, "曲线围出的面积\n= 一次碰撞耗散的能量", transform=ax.transAxes,
        fontsize=8.2, color=MUTED, ha="right", va="top", linespacing=1.55)

ax = axs[1]
zs = np.linspace(0.004, 0.985, 40)
emeas = np.array([impact(z, keep=False)[2] for z in zs])
ax.plot(zs, emeas, "o", ms=3.4, color=ACCENT, label="逐次积分的结果")
zz = np.linspace(0.004, 0.995, 400)
ax.plot(zz, np.exp(-np.pi * zz / np.sqrt(1 - zz ** 2)), color=INK, lw=1.3,
        label="$e=\\exp(-\\pi\\zeta/\\sqrt{1-\\zeta^{2}})$")
ax.set_xlabel("阻尼比 $\\zeta$")
ax.set_ylabel("恢复系数 $e$")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.02)
clean(ax, grid=True)
ax.legend(loc="upper right", handlelength=1.6, labelspacing=0.3, borderpad=0.15)
ax.annotate("截断让回弹段失去阻尼，\n实测值高于解析式", xy=(0.62, 0.245), xytext=(0.10, 0.115),
            fontsize=8.0, color=MUTED,
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=-0.2"))

save(fig, "02", "fig02-01")


# ============================================================
# 图 2-2  刚度与临界步长
#   接触周期：t_c = 2π √(m*/k)，取 Δt = t_c/10
#   瑞利波  ：Δt_R = π R √(ρ/G) / (0.8766 + 0.163ν)
# ============================================================
RHO, GSHEAR, NU = 2650.0, 29.0e9, 0.20
KS = np.logspace(3, 9, 400)
RADII = [0.3e-3, 1.0e-3, 5.0e-3]
COLS = [BLUE, ACCENT, GREEN]

fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.25),
                        gridspec_kw=dict(wspace=0.40))
ax = axs[0]
for R, c in zip(RADII, COLS):
    m = RHO * 4.0 / 3.0 * np.pi * R ** 3
    dt_c = 2.0 * np.pi * np.sqrt(m / 2.0 / KS) / 10.0
    dt_r = np.pi * R * np.sqrt(RHO / GSHEAR) / (0.8766 + 0.163 * NU)
    ax.plot(KS, dt_c, color=c, lw=0.9, ls=(0, (4, 2)), alpha=0.85)
    ax.plot(KS, np.full_like(KS, dt_r), color=c, lw=0.9, ls=(0, (1.5, 1.8)), alpha=0.85)
    ax.plot(KS, np.minimum(dt_c, dt_r), color=c, lw=1.9,
            label="$R$ = %.1f mm" % (R * 1000))
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("法向刚度 $k_n$  (N/m)")
ax.set_ylabel("可用步长 $\\Delta t$  (s)")
ax.set_xlim(1e3, 1e9)
ax.set_ylim(1e-9, 4e-4)
clean(ax, grid=True)
ax.legend(loc="upper right", handlelength=1.8, labelspacing=0.3, borderpad=0.2)
ax.text(0.04, 0.08, "粗：两者取小　　虚线：$t_c/10$　　点线：瑞利波", transform=ax.transAxes,
        fontsize=7.9, color=MUTED, va="bottom")

ax = axs[1]
for R, c in zip(RADII, COLS):
    m = RHO * 4.0 / 3.0 * np.pi * R ** 3
    dt_c = 2.0 * np.pi * np.sqrt(m / 2.0 / KS) / 10.0
    dt_r = np.pi * R * np.sqrt(RHO / GSHEAR) / (0.8766 + 0.163 * NU)
    ax.plot(KS, 1.0 / np.minimum(dt_c, dt_r), color=c, lw=1.9,
            label="$R$ = %.1f mm" % (R * 1000))
ax.axhline(60 * 300, color=FAINT, lw=0.9, ls=(0, (4, 2)))
ax.text(1.4e3, 60 * 300 * 1.35, "实时 60 fps、每帧 300 步的预算", fontsize=8.0, color=MUTED,
        va="bottom")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("法向刚度 $k_n$  (N/m)")
ax.set_ylabel("每模拟一秒所需步数")
ax.set_xlim(1e3, 1e9)
ax.set_ylim(1e3, 1e10)
clean(ax, grid=True)
ax.legend(loc="upper right", handlelength=1.8, labelspacing=0.3, borderpad=0.2)

save(fig, "02", "fig02-02")

# 打印几个自检数字，便于核对图注
m03 = RHO * 4 / 3 * np.pi * 0.3e-3 ** 3
print("R=0.3mm  m=%.2e kg  Δt(t_c/10, k=1e6)=%.2e  Δt_R=%.2e" % (
    m03, 2 * np.pi * np.sqrt(m03 / 2 / 1e6) / 10,
    np.pi * 0.3e-3 * np.sqrt(RHO / GSHEAR) / (0.8766 + 0.163 * NU)))
m5 = RHO * 4 / 3 * np.pi * 5e-3 ** 3
print("R=5mm    m=%.2e kg  Δt(t_c/10, k=1e4)=%.2e  Δt_R=%.2e" % (
    m5, 2 * np.pi * np.sqrt(m5 / 2 / 1e4) / 10,
    np.pi * 5e-3 * np.sqrt(RHO / GSHEAR) / (0.8766 + 0.163 * NU)))
