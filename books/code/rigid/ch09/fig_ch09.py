import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ============================================================
# 图 9-1  保守前进的 12 次迭代（真实计算）
#   胶囊：半长 0.4 m，半径 0.02 m，绕质心 omega = 6 rad/s
#         整体下落 v = 1.5 m/s，初始最低点离地 1.18 m
#   上界 v_max = v + omega * L/2 = 3.9 m/s
#   距离函数 d(t) = y_c(t) - (L/2)|sin(w t)| - r
# ============================================================
L2, R_CAP, OM, V, Y0 = 0.4, 0.02, 6.0, 1.5, 1.2
VMAX = V + OM * L2


def gap(t):
    return Y0 - V * t - L2 * abs(np.sin(OM * t)) - R_CAP


# 真实首次接触时刻：密扫 + 二分
tf = np.linspace(0.0, 1.2, 400001)
gf = gap(tf)
i0 = int(np.argmax(gf < 0))
lo, hi = tf[i0 - 1], tf[i0]
for _ in range(90):
    mid = 0.5 * (lo + hi)
    if gap(mid) < 0:
        hi = mid
    else:
        lo = mid
tstar = 0.5 * (lo + hi)

# 保守前进
tk = [0.0]
dk = [gap(0.0)]
t = 0.0
while gap(t) > 1e-7 and len(tk) < 300:
    t += gap(t) / VMAX
    tk.append(t)
    dk.append(gap(t))
tk, dk = np.array(tk), np.array(dk)

fig, (ax1, ax2) = new(6.9, 3.15, ncols=2, gridspec_kw=dict(width_ratios=[1.35, 1.0],
                                                          wspace=0.30))

# ---------- (a) 距离函数与迭代落点 ----------
tt = np.linspace(0.0, 0.70, 2000)
ax1.plot(tt, np.maximum(gap(tt), 0.0), color=INK, lw=1.3, zorder=3)
ax1.axhline(0.0, color=FAINT, lw=0.9, zorder=1)
ax1.plot(tk, dk, "o", ms=3.6, mfc=BLUE, mec=BLUE, mew=0.8, zorder=6)
for k, dx, dy in ((1, -2, 7), (11, 7, 3)):
    ax1.annotate(str(k), (tk[k], dk[k]), textcoords="offset points",
                 xytext=(dx, dy), fontsize=7.6, color=BLUE, zorder=8,
                 ha="right" if dx < 0 else "left")
ax1.axvline(tstar, color=ACCENT, lw=1.1, ls=(0, (3, 2.4)), zorder=2)
ax1.annotate(r"首次接触 $t^{*}=0.629$ s", xy=(tstar - 0.004, 0.015),
             xytext=(0.215, 0.135), fontsize=8.0, color=ACCENT, ha="left",
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                             shrinkA=4, shrinkB=3))
ax1.annotate("杆在旋转，最低点被抬起" + chr(10) + "间隙不减反增", xy=(0.507, gap(0.507) + 0.010),
             xytext=(0.428, 0.632), fontsize=7.9, color=MUTED, ha="center",
             va="center", arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.9,
                             mutation_scale=7, shrinkA=3, shrinkB=3))
ax1.set_xlim(0.0, 0.70)
ax1.set_ylim(0.0, 1.46)
ax1.set_xlabel("时间 / s")
ax1.set_ylabel("间隙 $d$ / m")
clean(ax1, grid=True)
ax1.text(0.025, 0.975, "（a）距离函数与每次迭代的落点", transform=ax1.transAxes,
         fontsize=9.0, color=INK, weight="bold", va="top")

# ---------- (b) 估计误差 ----------
err = np.abs(tk - tstar)
kk = np.arange(len(tk))
ax2.semilogy(kk, np.maximum(err, 1e-12), "-o", color=BLUE, lw=1.2, ms=3.4,
             mfc=BLUE, mec=BLUE, mew=0.8, zorder=4)
ax2.set_xlim(-0.6, 14.2)
ax2.set_ylim(1e-10, 4e1)
ax2.set_xticks(np.arange(0, 13, 2))
ax2.set_xlabel("迭代次数 $k$")
ax2.set_ylabel(r"$|t_k - t^{*}|$ / s")
ax2.annotate("第 12 步：$1.1" + chr(92) + "times10^{-8}$ s", xy=(len(tk) - 1, err[-1]),
             xytext=(4.2, 2.4e-9), fontsize=7.8, color=ACCENT, ha="left",
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8, shrinkA=2,
                             shrinkB=3))
clean(ax2, grid=True)
ax2.text(0.03, 0.975, "（b）估计误差随迭代", transform=ax2.transAxes,
         fontsize=9.0, color=INK, weight="bold", va="top")

save(fig, "09", "fig09-01")


# ============================================================
# 图 9-2  离散检测与扫掠体的对比（示意）
# ============================================================
W, H = 6.8, 3.25
fig, ax = canvas(W, H)
K = W / H


def ball(x, y, r=0.030, fc="#DCE6FA", ec=INK, ls="-", lw=1.2, z=5, alpha=1.0):
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * K, facecolor=fc, edgecolor=ec,
                         lw=lw, linestyle=ls, zorder=z, alpha=alpha))


# 分隔线
ax.plot([0.500, 0.500], [0.10, 0.93], color=GRID, lw=1.0, ls=(0, (4, 3)))

# ---------------- 左：只在两个采样位置查 ----------------
PL_L, PW = 0.252, 0.011
ax.add_patch(Rectangle((PL_L, 0.300), PW, 0.400, facecolor="#E5E7EB",
                       edgecolor=INK, lw=0.9, zorder=3))
ball(0.088, 0.500)                                   # 第 n 帧
ball(0.392, 0.500, fc="none", ec=SLATE, ls=(0, (3, 2.6)), lw=1.1)   # 第 n+1 帧
arrow(ax, (0.130, 0.500), (0.348, 0.500), color=SLATE, lw=1.0,
      ls=(0, (3, 2.6)), ms=7)
label(ax, 0.088, 0.392, "第 $n$ 帧", fs=8.4)
label(ax, 0.392, 0.392, "第 $n+1$ 帧", fs=8.4, color=SLATE)
label(ax, PL_L + PW / 2, 0.735, "薄板", fs=8.4, color=MUTED, va="bottom")

label(ax, 0.040, 0.930, "（a）只查两个采样位置", fs=9.2, ha="left", weight="bold")
label(ax, 0.040, 0.868, "两次都在板外，判为无接触", fs=8.3, ha="left", color=ACCENT)

ax.plot([0.060, 0.450], [0.200, 0.200], color=GRID, lw=2.2, solid_capstyle="round",
        zorder=1)
ax.plot([0.060, 0.200], [0.200, 0.200], color=SLATE, lw=2.2, solid_capstyle="round",
        zorder=2)
ax.plot([0.060, 0.060], [0.186, 0.214], color=MUTED, lw=0.9)
ax.plot([0.450, 0.450], [0.186, 0.214], color=MUTED, lw=0.9)
label(ax, 0.060, 0.146, "0", fs=7.8, color=MUTED)
label(ax, 0.450, 0.146, r"$\Delta t$", fs=8.0, color=MUTED)
label(ax, 0.300, 0.146, "整步走完", fs=7.8, color=MUTED)

# ---------------- 右：查扫掠体 ----------------
PL_R = 0.800
ax.add_patch(Rectangle((PL_R, 0.300), PW, 0.400, facecolor="#E5E7EB",
                       edgecolor=INK, lw=0.9, zorder=3))
X0, X1, YB = 0.560, 0.768, 0.500
rr = 0.030
# 扫掠体：胶囊形区域
ax.add_patch(Rectangle((X0, YB - rr * K), X1 - X0, 2 * rr * K,
                       facecolor=SOFT[1], edgecolor="none", zorder=2))
ax.add_patch(Ellipse((X0, YB), 2 * rr, 2 * rr * K, facecolor=SOFT[1],
                     edgecolor="none", zorder=2))
ax.add_patch(Ellipse((X1, YB), 2 * rr, 2 * rr * K, facecolor=SOFT[1],
                     edgecolor="none", zorder=2))
for s in (-1, 1):
    ax.plot([X0, X1], [YB + s * rr * K, YB + s * rr * K], color=BLUE, lw=0.9,
            ls=(0, (3, 2.4)), zorder=3)
ax.add_patch(Arc((X0, YB), 2 * rr, 2 * rr * K, theta1=90, theta2=270,
                 edgecolor=BLUE, lw=0.9, ls=(0, (3, 2.4)), zorder=3))
ax.add_patch(Arc((X1, YB), 2 * rr, 2 * rr * K, theta1=-90, theta2=90,
                 edgecolor=BLUE, lw=0.9, ls=(0, (3, 2.4)), zorder=3))
ax.annotate("扫掠体", xy=(0.648, YB + rr * K + 0.004), xytext=(0.545, 0.700),
            fontsize=8.3, color=BLUE, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8, shrinkA=3, shrinkB=2))

ball(X0, YB)                                                  # 起点
ball(X1, YB, fc="#FDF2E9", ec=ACCENT, lw=1.3)                 # 首次接触
ax.plot([PL_R, PL_R], [0.276, 0.724], color=ACCENT, lw=0.9, ls=(0, (1.2, 2.2)),
        zorder=4)
label(ax, X0, 0.392, "第 $n$ 帧", fs=8.4)
label(ax, 0.760, 0.628, r"首次接触 $t^{*}$", fs=8.4, color=ACCENT, ha="right",
      va="bottom")

label(ax, 0.538, 0.930, "（b）查扫掠体", fs=9.2, ha="left", weight="bold")
label(ax, 0.538, 0.868, "交出 $t^{*}$ 与法向，不只是布尔值", fs=8.3, ha="left",
      color=ACCENT)

ax.plot([0.545, 0.930], [0.200, 0.200], color=GRID, lw=2.2, solid_capstyle="round",
        zorder=1)
ax.plot([0.545, 0.768], [0.200, 0.200], color=BLUE, lw=2.2, solid_capstyle="round",
        zorder=2)
ax.plot([0.768, 0.782], [0.200, 0.200], color=ACCENT, lw=2.2, solid_capstyle="round",
        zorder=2)
ax.plot([0.545, 0.545], [0.186, 0.214], color=MUTED, lw=0.9)
ax.plot([0.930, 0.930], [0.186, 0.214], color=MUTED, lw=0.9)
label(ax, 0.545, 0.146, "0", fs=7.8, color=MUTED)
label(ax, 0.930, 0.146, r"$\Delta t$", fs=8.0, color=MUTED)
label(ax, 0.650, 0.240, "推进到 $t^{*}$", fs=7.8, color=BLUE)
label(ax, 0.845, 0.240, "再解接触", fs=7.8, color=ACCENT)

save(fig, "09", "fig09-02")
