import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 11-1  渲染帧与物理子步的时间线（示意）
# ============================================================
W, H = 6.8, 3.6
fig, ax = canvas(W, H)

X0, X1 = 0.225, 0.945          # 时间轴映射
T = 100.0                      # 显示 0–100 ms，12 个物理子步
def tx(t):
    return X0 + (X1 - X0) * t / T

# 显示帧时刻（间隔不均，模拟帧率抖动）
frames = [0.0, 15.2, 31.8, 47.1, 63.9, 80.4, 96.2]
Y_R, Y_P = 0.845, 0.625
Y_BAR = 0.752

label(ax, 0.020, Y_R, "显示帧", fs=9.4, ha="left")
label(ax, 0.020, Y_P, "物理子步", fs=9.4, ha="left")
label(ax, 0.036, Y_R - 0.048, "间隔不均", fs=7.8, color=MUTED, ha="left")
label(ax, 0.036, Y_P - 0.048, "步长固定", fs=7.8, color=MUTED, ha="left")

ax.plot([X0 - 0.010, X1 + 0.012], [Y_R, Y_R], color="#D8DDE5", lw=1.6, zorder=1,
        solid_capstyle="round")
ax.plot([X0 - 0.010, X1 + 0.012], [Y_P, Y_P], color="#D8DDE5", lw=1.6, zorder=1,
        solid_capstyle="round")

# 显示帧刻度
for i, t in enumerate(frames):
    x = tx(t)
    ax.plot([x, x], [Y_R, Y_R + 0.036], color=INK, lw=1.4, zorder=4)
    ax.text(x, Y_R + 0.044, f"{i}", fontsize=7.6, color=MUTED, ha="center", va="bottom")

# 物理子步：固定 1/120 s
h = 1000.0 / 120.0
sub = [k * h for k in range(int(T / h) + 1)]
for k, t in enumerate(sub):
    x = tx(t)
    ax.plot([x, x], [Y_P, Y_P - 0.036], color=ACCENT, lw=1.0, zorder=4)
    ax.text(x, Y_P - 0.046, f"{k+1}", fontsize=7.2, color=ACCENT, ha="center", va="top")

# 每帧跑了几步：括号 + 标注
for i in range(len(frames) - 1):
    t0, t1 = frames[i], frames[i + 1]
    n = int(np.floor(t1 / h + 1e-9)) - int(np.floor(t0 / h + 1e-9))
    xa, xb = tx(t0), tx(t1)
    ax.plot([xa, xa, xb, xb], [Y_R - 0.008, Y_BAR, Y_BAR, Y_P + 0.008],
            color=SLATE, lw=0.7, ls=(0, (3, 3)), alpha=0.85, zorder=2)
    ax.text((xa + xb) / 2, Y_BAR + 0.010, f"{n} 步", fontsize=7.8, color=SLATE,
            ha="center", va="bottom")

# 时间轴
ax.plot([X0 - 0.010, X1 + 0.012], [0.512, 0.512], color=GRID, lw=1.2, zorder=1)
for t, s, ha in [(0.0, "0", "center"), (50.0, "50", "center"), (100.0, "100 ms", "left")]:
    x = tx(t)
    ax.plot([x, x], [0.512, 0.504], color=MUTED, lw=0.8, zorder=2)
    ax.text(x + (0.004 if ha == "left" else 0.0), 0.494, s, fontsize=7.8,
            color=MUTED, ha=ha, va="top")

# ---------- 底部：一帧之内的插值 ----------
px0, px1 = 0.085, 0.915
ax.add_patch(Rectangle((px0, 0.045), px1 - px0, 0.372, facecolor="#FCFCFD",
                       edgecolor=GRID, lw=0.8, zorder=1))

yA = 0.332
ax.plot([0.150, 0.860], [yA, yA], color="#D8DDE5", lw=1.3, zorder=2,
        solid_capstyle="round")

xn1, xr, xn = 0.380, 0.492, 0.600
for x, tag in [(xn1, r"$\mathbf{x}_{n-1}$"), (xn, r"$\mathbf{x}_{n}$")]:
    ax.plot([x, x], [yA - 0.026, yA + 0.026], color=ACCENT, lw=1.5, zorder=4)
    ax.text(x, yA - 0.036, tag, fontsize=10.5, color=ACCENT, ha="center", va="top")

ax.plot([xr, xr], [yA - 0.010, yA + 0.075], color=INK, lw=0.8, ls=(0, (3, 2)), zorder=3)
ax.plot([xr], [yA], "o", ms=6.2, color=INK, zorder=6, mec="white", mew=0.9)
ax.text(xr, yA + 0.062, "这一帧画在这里", fontsize=8.2, color=INK, ha="center", va="bottom")

# α 括号
ax.annotate("", xy=(xn1, 0.170), xytext=(xr, 0.170),
            arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
ax.text(xr + 0.014, 0.170, r"$\alpha\,h$", fontsize=9.2, color=MUTED,
        ha="left", va="center")

ax.text(0.108, 0.060,
        r"插值：$(1-\alpha)\,\mathbf{x}_{n-1}+\alpha\,\mathbf{x}_{n}$，"
        r"$\alpha=a/h$，$a$ 是累加器余下的时间",
        fontsize=8.4, color=INK, ha="left", va="bottom")

save(fig, "11", "fig11-01")


# ============================================================
# 图 11-2  固定步长与可变步长的弹跳轨迹（真实一维计算）
#   半隐式；落地时 y 夹到 0，法向速度乘 -e
# ============================================================
G, E, H0 = 9.81, 0.85, 1.0
TEND = 2.25


def run(step, tend=TEND):
    y, v, t = H0, 0.0, 0.0
    ts, ys = [0.0], [y]
    n = 0
    while t < tend:
        dt = step(n)
        n += 1
        v -= G * dt
        y += v * dt
        if y < 0.0:
            y = 0.0
            v = -E * v
        t += dt
        ts.append(t)
        ys.append(y)
    return np.array(ts), np.array(ys)


fixed60 = run(lambda n: 1.0 / 60.0)
fixed240 = run(lambda n: 1.0 / 240.0)
variable = run(lambda n: (1.0 / 60.0) * (1 + 0.35 * np.sin(2.3 * n)) / 4.0)


def apexes(ts, ys, tol=2e-3):
    out = []
    for i in range(1, len(ys) - 1):
        if ys[i] >= ys[i - 1] and ys[i] > ys[i + 1] and ys[i] > tol:
            out.append((ts[i], ys[i]))
    return out


ap60 = apexes(*fixed60)
ap240 = apexes(*fixed240)
apv = apexes(*variable)

fig, (axa, axb) = new(6.9, 3.25, ncols=2)
for a in (axa, axb):
    clean(a, grid=True)

axa.plot(fixed240[0], fixed240[1], color=BLUE, lw=1.8, zorder=5,
         label=r"固定 $\Delta t=1/240$ s")
axa.plot(variable[0], variable[1], color=GREEN, lw=1.2, ls=(0, (5, 2)), zorder=4,
         label=r"可变 $\Delta t$，均值 1/240 s")
axa.plot(fixed60[0], fixed60[1], color=ACCENT, lw=1.1, zorder=3,
         label=r"固定 $\Delta t=1/60$ s")

axa.set_xlim(0, TEND)
axa.set_ylim(0, 1.06)
axa.set_xlabel("时间（s）")
axa.set_ylabel("高度（m）")
axa.legend(loc="upper right", fontsize=7.6, handlelength=2.0, borderaxespad=0.5,
           labelspacing=0.45)

axa.annotate("", xy=(ap240[2][0] - 0.010, ap240[2][1] + 0.010),
             xytext=(ap60[2][0] - 0.006, ap60[2][1] + 0.004),
             arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.7))
axa.text(1.70, 0.600, "第 3 次的顶点差", fontsize=7.6, color=MUTED,
         ha="right", va="bottom")

# 右图：每次弹起的最高点（连线）
nb = min(5, len(ap60), len(ap240), len(apv))
idx = np.arange(1, nb + 1)
series = [(ap60, ACCENT, "-", 1.2, r"固定 1/60 s", "o"),
          (ap240, BLUE, "-", 1.8, r"固定 1/240 s", "o"),
          (apv, GREEN, (0, (5, 2)), 1.2, r"可变", "s")]
for ap, c, ls, lw, nm, mk in series:
    ys = [a[1] for a in ap[:nb]]
    axb.plot(idx, ys, ls=ls, lw=lw, color=c, marker=mk, ms=3.6 if mk == "o" else 3.0,
             mec="white", mew=0.6, zorder=4, label=nm)

axb.set_xticks(idx)
axb.set_xlim(0.55, nb + 0.75)
axb.set_ylim(0, 0.80)
axb.set_xlabel("第几次弹起")
axb.set_ylabel("最高点（m）")
axb.legend(loc="upper right", fontsize=7.6, handlelength=2.0, borderaxespad=0.5,
           labelspacing=0.45)

d3 = (ap240[2][1] - ap60[2][1]) / ap240[2][1] * 100
axb.annotate("", xy=(3.0, ap60[2][1]), xytext=(3.0, ap240[2][1]),
             arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.8))
axb.text(3.10, 0.5 * (ap60[2][1] + ap240[2][1]), f"相差 {d3:.0f}%", fontsize=7.8,
         color=MUTED, ha="left", va="center")

save(fig, "11", "fig11-02")
