# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np

# ================================================================ 一维双质量耦合
# m1 x1'' = -k (x1 - x2),   m2 x2'' = -k (x2 - x1)
# 精确解：质心 X 不动，相对位移 D = x1 - x2 做角频率 w 的简谐振动。
M1, M2, KK = 1.0, 4.0, 400.0
AMPL = 0.01                     # 初始位移 -a, +a
MTOT = M1 + M2
W = np.sqrt(KK * (1.0 / M1 + 1.0 / M2))
X0 = AMPL * (M2 - M1) / MTOT
D0 = -2.0 * AMPL


def exact_x1(t):
    return X0 + (M2 / MTOT) * D0 * np.cos(W * t)


def integrate(order, dt, T):
    x1, x2 = -AMPL, AMPL
    v1 = v2 = 0.0
    n = int(round(T / dt))
    out = np.empty(n + 1)
    out[0] = x1
    for i in range(n):
        if order == "sync":
            f1, f2 = -KK * (x1 - x2), -KK * (x2 - x1)
            v1 += dt * f1 / M1
            v2 += dt * f2 / M2
            x1 += dt * v1
            x2 += dt * v2
        elif order == "ab":                     # 先 1 后 2
            v1 += dt * (-KK * (x1 - x2)) / M1
            x1 += dt * v1
            v2 += dt * (-KK * (x2 - x1)) / M2
            x2 += dt * v2
        else:                                   # 先 2 后 1
            v2 += dt * (-KK * (x2 - x1)) / M2
            x2 += dt * v2
            v1 += dt * (-KK * (x1 - x2)) / M1
            x1 += dt * v1
        out[i + 1] = x1
    return out


# ---- 图 8-1 ------------------------------------------------------
DT0 = 1.0 / 960.0
T_MAIN = 1.0
n_main = int(round(T_MAIN / DT0))
t_main = np.linspace(0.0, T_MAIN, n_main + 1)
e_ab = integrate("ab", DT0, T_MAIN) - exact_x1(t_main)
e_ba = integrate("ba", DT0, T_MAIN) - exact_x1(t_main)
e_sy = integrate("sync", DT0, T_MAIN) - exact_x1(t_main)

print("dt = 1/960, t = 1 s：ab %+.3e   ba %+.3e   sync %+.3e"
      % (e_ab[n_main // 2], e_ba[n_main // 2], e_sy[n_main // 2]))

dts = np.array([1.0 / 120, 1.0 / 240, 1.0 / 480, 1.0 / 960, 1.0 / 1920, 1.0 / 3840])
ea, eb, es = [], [], []
for dt in dts:
    T = 1.0
    n = int(round(T / dt))
    tt = np.linspace(0.0, T, n + 1)
    ea.append(abs(integrate("ab", dt, T)[-1] - exact_x1(T)))
    eb.append(abs(integrate("ba", dt, T)[-1] - exact_x1(T)))
    es.append(abs(integrate("sync", dt, T)[-1] - exact_x1(T)))
ea, eb, es = np.array(ea), np.array(eb), np.array(es)

# 拟合斜率（去掉最粗的两档，避免分辨率不足）
slope = np.polyfit(np.log(dts[2:]), np.log(eb[2:]), 1)[0]
print("拟合斜率 = %.2f" % slope)

fig, axs = plt.subplots(1, 2, figsize=(6.9, 3.15),
                        gridspec_kw=dict(width_ratios=[1.55, 1.0], wspace=0.34))

# (a) 误差随时间
ax = axs[0]
ax.axhline(0.0, color=FAINT, lw=0.9, zorder=2)
ax.plot(t_main, e_ab * 1e3, color=ACCENT, lw=1.7, zorder=4, label="先 1 后 2")
ax.plot(t_main, e_ba * 1e3, color=BLUE, lw=1.7, zorder=4, label="先 2 后 1")
ax.plot(t_main, e_sy * 1e3, color=MUTED, lw=1.3, ls=(0, (5, 2)), zorder=3,
        label="同步推进")
clean(ax, grid=True)
ax.set_xlim(0, T_MAIN)
ax.set_ylim(-2.05, 2.35)
ax.set_xlabel(r"$t$ / s")
ax.set_ylabel(r"$x_{1}$ 误差 / mm", labelpad=2.0)
ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.legend(loc="lower left", ncol=3, handlelength=1.7, columnspacing=1.2,
          bbox_to_anchor=(0.0, 1.005), borderaxespad=0.2)
ax.text(0.025, 0.94, "(a)", transform=ax.transAxes, fontsize=9, color=INK, va="top")

# (b) 误差随步长
ax = axs[1]
ax.loglog(dts, ea * 1e3, "o-", color=ACCENT, lw=1.4, ms=3.6, zorder=4, label="先 1 后 2")
ax.loglog(dts, eb * 1e3, "s-", color=BLUE, lw=1.4, ms=3.4, zorder=4, label="先 2 后 1")
ax.loglog(dts, es * 1e3, "^--", color=MUTED, lw=1.1, ms=3.2, zorder=3, label="同步推进")
# 斜率 1 的参考线：放在数据下方，避开所有点
A = 0.60 * es[2] / dts[2]
xg = np.array([1.0 / 960, 1.0 / 200])
ax.loglog(xg, A * xg, color=FAINT, lw=1.0, ls=(0, (2, 2)), zorder=2)
ax.text(xg[1], A * xg[1] * 1.5, "斜率 1", fontsize=8.0, color=FAINT, ha="right", va="bottom")
clean(ax, grid=True)
ax.set_xlabel(r"$\Delta t$ / s")
ax.set_ylabel("误差 / mm", labelpad=2.0)
ax.set_xticks([1.0 / 3840, 1.0 / 960, 1.0 / 240])
ax.set_xticklabels(["1/3840", "1/960", "1/240"])
ax.minorticks_off()
ax.text(0.035, 0.94, "(b)", transform=ax.transAxes, fontsize=9, color=INK, va="top")

save(fig, "08", "fig08-01")


# ---- 图 8-2：子循环时间线（示意）------------------------------
fig, ax = canvas(6.7, 3.15)

XL, XR = 0.150, 0.945
NSUB = 4                # 每个大步内的小步数
NSTEP = 3               # 画三个大步


def tx(t):
    """把时间 t（以大步为单位）映射到画布坐标。"""
    return XL + (XR - XL) * t / NSTEP


# 慢系统
y_slow, h_slow = 0.795, 0.075
for k in range(NSTEP):
    x = tx(k)
    ax.add_patch(Rectangle((x, y_slow), tx(k + 1) - x - 0.004, h_slow,
                           facecolor="#E8EDF5", edgecolor="#C7D2E3", lw=0.9, zorder=2))
    ax.text((x + tx(k + 1)) / 2, y_slow + h_slow / 2, r"$\Delta t_{s}$",
            ha="center", va="center", fontsize=8.6, color=INK, zorder=4)
ax.text(0.012, y_slow + h_slow / 2, "慢系统", ha="left", va="center",
        fontsize=8.6, color=INK)
ax.text(0.012, y_slow - 0.018, "刚体", ha="left", va="center", fontsize=8.0, color=MUTED)

# 快系统
y_fast, h_fast = 0.575, 0.075
for k in range(NSTEP):
    for j in range(NSUB):
        t0 = k + j / NSUB
        t1 = k + (j + 1) / NSUB
        ax.add_patch(Rectangle((tx(t0), y_fast), tx(t1) - tx(t0) - 0.003, h_fast,
                               facecolor="#ECFDF5", edgecolor="#A7D8C4", lw=0.8, zorder=2))
    ax.text((tx(k) + tx(k + 1)) / 2, y_fast + h_fast / 2, r"$\Delta t_{s}/n$",
            ha="center", va="center", fontsize=8.2, color=GREEN, zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.6))
ax.text(0.012, y_fast + h_fast / 2, "快系统", ha="left", va="center",
        fontsize=8.6, color=INK)
ax.text(0.012, y_fast - 0.018, "布料", ha="left", va="center", fontsize=8.0, color=MUTED)

# 交换时刻
for k in range(NSTEP + 1):
    x = tx(k)
    ax.plot([x, x], [0.185, 0.885], color=ACCENT, lw=0.9, ls=(0, (3, 3)), zorder=1)
ax.text(tx(1) + 0.008, 0.895, "交换", ha="left", va="bottom", fontsize=8.0, color=ACCENT)

# 界面量：零阶保持
y0, y1 = 0.245, 0.415
vals = [0.78, 0.58, 0.66]
xs, ys = [], []
for k in range(NSTEP):
    xs += [tx(k), tx(k + 1)]
    ys += [y0 + vals[k] * (y1 - y0)] * 2
ax.fill_between(xs, y0, ys, step=None, color="#EFF4FF", zorder=1)
ax.plot(xs, ys, color=BLUE, lw=1.6, zorder=4)
for k in range(1, NSTEP):
    ax.plot([tx(k), tx(k)], [y0 + vals[k - 1] * (y1 - y0), y0 + vals[k] * (y1 - y0)],
            color=BLUE, lw=1.6, zorder=4)
ax.plot([XL, XR], [y0, y0], color="#D1D5DB", lw=0.8, zorder=2)
ax.text(0.012, (y0 + y1) / 2 + 0.030, "界面量", ha="left", va="center",
        fontsize=8.4, color=INK)
ax.text(0.012, (y0 + y1) / 2 - 0.030, "零阶保持", ha="left", va="center",
        fontsize=8.0, color=MUTED)

# 时间轴
ax.annotate("", xy=(XR + 0.01, 0.105), xytext=(XL, 0.105),
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9))
ax.text(XR + 0.018, 0.105, "时间", ha="left", va="center", fontsize=8.2, color=MUTED)

# n 的标注
ax.annotate("", xy=(tx(0.0), 0.535), xytext=(tx(1.0), 0.535),
            arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.9))
ax.text((tx(0) + tx(1)) / 2, 0.500, r"$n=4$ 个小步", ha="center", va="center",
        fontsize=8.0, color=MUTED)

save(fig, "08", "fig08-02")
