import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import matplotlib.ticker as mticker

# ============================================================
# 图 12-1  同一批数的两种求和顺序（真实计算）
#   要算的是 sum_i (a_i - b_i)，a_i = 1 + d_i，b_i = 1，d_i ~ U(0, 1e-12)
#   顺序 A：先把所有 a_i 加起来，再把所有 b_i 减掉
#   顺序 B：逐对相减得到 d_i 再累加
#   参考值由 math.fsum 给出（几乎精确）；每个 N 取 5 个 seed 的中位数
# ============================================================
Ns = [100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000]
errA, errB = [], []
for NN in Ns:
    ea, eb = [], []
    for seed in range(5):
        rng = np.random.default_rng(seed)
        d = 1e-12 * rng.uniform(0.0, 1.0, NN)
        a = 1.0 + d
        bb = np.ones(NN)
        ref = math.fsum(d)
        sA = np.cumsum(np.concatenate([a, -bb]))[-1]     # 先正后负
        sB = np.cumsum((a - bb).ravel())[-1]             # 逐对相减再累加
        ea.append(abs(sA - ref) / ref)
        eb.append(abs(sB - ref) / ref)
    errA.append(np.median(ea))
    errB.append(np.median(eb))
    print("N=%7d  顺序A %.2e   顺序B %.2e" % (NN, errA[-1], errB[-1]))

fig, ax = new(6.7, 3.7)
clean(ax, grid=True, spines=("left", "bottom"))
ax.loglog(Ns, errA, "o-", color=ACCENT, lw=1.6, ms=4.2, zorder=4,
          label="顺序 A：先加完所有 $a_i$，再减所有 $b_i$")
ax.loglog(Ns, errB, "s-", color=BLUE, lw=1.6, ms=4.2, zorder=4,
          label="顺序 B：先逐对相减，再累加")
ax.axhline(1.0, color=MUTED, lw=0.9, ls=":", zorder=2)
ax.text(1.15e2, 1.22, "误差与总和同量级，结果已不可用", fontsize=8.2, color=MUTED,
        ha="left", va="bottom")
ax.set_xlim(80, 2.2e6)
ax.set_ylim(1e-8, 4.0)
ax.set_xlabel("项数 $N$")
ax.set_ylabel("相对误差 $|\\hat{S}-S|/|S|$")
ax.set_yticks([1e-8, 1e-6, 1e-4, 1e-2, 1e0])
ax.set_yticklabels(["$10^{-8}$", "$10^{-6}$", "$10^{-4}$", "$10^{-2}$", "$1$"])
ax.xaxis.set_minor_formatter(mticker.NullFormatter())
ax.yaxis.set_minor_formatter(mticker.NullFormatter())
ax.legend(loc="lower left", fontsize=8.4, handlelength=2.2, labelspacing=0.5,
          borderaxespad=0.4)

save(fig, "12", "fig12-01")

# ============================================================
# 图 12-2  收敛阶验证：y' = -y, y(0)=1, 积分到 T=5（真实计算）
#   误差 = |y_num(T) - exp(-5)|，步长 dt = 2^-2 ... 2^-9
# ============================================================
def euler(f, y0, T, dt):
    y, t = y0, 0.0
    for _ in range(int(round(T / dt))):
        y = y + dt * f(y, t)
        t += dt
    return y


def rk2(f, y0, T, dt):
    y, t = y0, 0.0
    for _ in range(int(round(T / dt))):
        k1 = f(y, t)
        k2 = f(y + 0.5 * dt * k1, t + 0.5 * dt)
        y = y + dt * k2
        t += dt
    return y


def rk4(f, y0, T, dt):
    y, t = y0, 0.0
    for _ in range(int(round(T / dt))):
        k1 = f(y, t)
        k2 = f(y + 0.5 * dt * k1, t + 0.5 * dt)
        k3 = f(y + 0.5 * dt * k2, t + 0.5 * dt)
        k4 = f(y + dt * k3, t + dt)
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        t += dt
    return y


def rk4_f32(y0, T, dt):
    """单精度（float32）的 RK4，用来暴露舍入地板。"""
    y = np.array(y0, dtype=np.float32)
    dtt = np.float32(dt)
    for _ in range(int(round(T / dt))):
        k1 = -y
        k2 = -(y + dtt / 2 * k1)
        k3 = -(y + dtt / 2 * k2)
        k4 = -(y + dtt * k3)
        y = y + dtt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return float(y)


fr = lambda y, t: -y
T_end = 5.0
y_exact = np.exp(-T_end)
dts = 2.0 ** (-np.arange(2, 10))
res = {}
for name, meth in (("Euler", euler), ("RK2", rk2), ("RK4", rk4)):
    errs = np.array([abs(meth(fr, 1.0, T_end, dt) - y_exact) for dt in dts])
    slope = np.polyfit(np.log(dts[:6]), np.log(errs[:6]), 1)[0]
    res[name] = (errs, slope)
    print("%s: 拟合斜率 %.2f" % (name, slope))

fig, ax = new(6.6, 3.8)
clean(ax, grid=True, spines=("left", "bottom"))
style = {"Euler": (MUTED, "o", (0, 15), "left"),
         "RK2": (ACCENT, "s", (2, -22), "left"),
         "RK4": (BLUE, "^", (4, 17), "left")}
for name in ("Euler", "RK2", "RK4"):
    errs, slope = res[name]
    c, m, off, ha = style[name]
    ax.loglog(dts, errs, m + "-", color=c, lw=1.4, ms=4.4, zorder=4)
    ax.annotate("%s，斜率 %.2f" % (name, slope),
                xy=(dts[5], errs[5]), xytext=off, textcoords="offset points",
                fontsize=8.6, color=c, ha=ha)

ax.axhline(2.2e-16, color=FAINT, lw=1.0, ls="--", zorder=2)
ax.text(1.9e-3, 4.2e-16, "双精度舍入水平", fontsize=8.2, color=FAINT, va="bottom")
ax.set_xlim(1.6e-3, 0.36)
ax.set_ylim(1e-18, 3.0)
ax.set_xlabel("步长 $\\Delta t$（s）")
ax.set_ylabel("末端误差 $|y_N - e^{-5}|$")
ax.set_xticks([0.25, 0.0625, 0.0156, 0.0039])
ax.set_xticklabels(["0.25", "1/16", "1/64", "1/256"])
ax.xaxis.set_minor_formatter(mticker.NullFormatter())
ax.yaxis.set_minor_formatter(mticker.NullFormatter())

save(fig, "12", "fig12-02")

# ============================================================
# 图 12-3  CSR 存储结构（示意图）
#   矩阵 4x4，非零位置：第 0 行 {0,1}，第 1 行 {0,1,2}，第 2 行 {1,2}，第 3 行 {3}
#   row_ptr = [0, 2, 5, 7, 8]，col_idx = [0,1, 0,1,2, 1,2, 3]
# ============================================================
rows = [[0, 1], [0, 1, 2], [1, 2], [3]]
cols_idx = []
for i, cl in enumerate(rows):
    cols_idx.extend(cl)
row_ptr = [0]
for r in rows:
    row_ptr.append(row_ptr[-1] + len(r))
nnz = len(cols_idx)
print("col_idx =", cols_idx, " row_ptr =", row_ptr, " nnz =", nnz)

fig, ax = canvas(6.9, 3.6, (0, 1), (0.10, 1.0))

# ---- 左：矩阵 ----
cw2, ch2 = 0.052, 0.078
mx0, my0 = 0.105, 0.315          # 左下角
for i in range(4):
    for j in range(4):
        ax.add_patch(Rectangle((mx0 + j * cw2, my0 + (3 - i) * ch2), cw2, ch2,
                               facecolor="white", edgecolor=GRID, lw=0.9, zorder=2))
ax.add_patch(Rectangle((mx0, my0), 4 * cw2, 4 * ch2, facecolor="none",
                       edgecolor=INK, lw=1.2, zorder=4))
label(ax, mx0 + 2 * cw2, my0 + 4 * ch2 + 0.135, "矩阵 $\mathbf{A}$", fs=9.4)
label(ax, mx0 + 2 * cw2, my0 + 4 * ch2 + 0.085, "圈内标号 = 存储顺序", fs=8.0, color=MUTED)

n = 0
for i, cl in enumerate(rows):
    for j in cl:
        cx = mx0 + (j + 0.5) * cw2
        cy = my0 + (3 - i + 0.5) * ch2
        n += 1
        ax.add_patch(Circle((cx, cy), 0.0160, facecolor=ACCENT, edgecolor="none",
                            zorder=5, alpha=0.88))
        label(ax, cx, cy, "%d" % n, fs=7.8, color="white", weight="bold", z=6)

for i in range(4):
    label(ax, mx0 - 0.020, my0 + (3.5 - i) * ch2, "%d" % i, fs=8.2, color=MUTED)
label(ax, mx0 - 0.046, my0 + 2 * ch2, "行", fs=8.4, color=MUTED, rot=90)
for j in range(4):
    label(ax, mx0 + (j + 0.5) * cw2, my0 + 4 * ch2 + 0.022, "%d" % j, fs=8.2, color=MUTED)

# ---- 右：三个数组 ----
x0 = 0.500
bw, bh = 0.056, 0.058
y_rp, y_val, y_col = 0.860, 0.700, 0.510
shade = [SOFT[0], LIGHT, SOFT[0], LIGHT]

for i, cl in enumerate(rows):
    xs = x0 + row_ptr[i] * bw
    xw = (row_ptr[i + 1] - row_ptr[i]) * bw
    for yy in (y_val, y_col):
        ax.add_patch(Rectangle((xs, yy), xw, bh, facecolor=shade[i], edgecolor="none",
                               zorder=1))
    if i == 3:
        label(ax, xs + xw - 0.004, y_val + bh + 0.024, "行 %d" % i, fs=7.8,
              color=MUTED, ha="right")
    else:
        label(ax, xs + xw / 2, y_val + bh + 0.024, "行 %d" % i, fs=7.8, color=MUTED)

for k in range(nnz):
    x = x0 + k * bw
    box(ax, x, y_val, bw, bh, "$v_{%d}$" % (k + 1), fc="none", ec=ACCENT, fs=8.4, lw=0.9, z=3)
    box(ax, x, y_col, bw, bh, "%d" % cols_idx[k], fc="none", ec=BLUE, fs=8.4, lw=0.9, z=3)

for k in range(5):
    xb = x0 + row_ptr[k] * bw
    box(ax, xb - 0.021, y_rp, 0.042, 0.046, "%d" % row_ptr[k], fc="white", ec=GREEN,
        fs=8.2, lw=0.9, z=4)
    if k < 4:
        ax.plot([xb, xb], [y_rp - 0.004, y_val + bh + 0.008], color=GREEN, lw=0.7,
                ls=(0, (2, 2)), zorder=2)

label(ax, x0 - 0.038, y_rp + 0.023, "$\mathtt{row\_ptr}$", fs=8.6, ha="right", color=GREEN)
label(ax, x0 - 0.038, y_val + bh / 2, "$\mathtt{val}$", fs=8.6, ha="right", color=ACCENT)
label(ax, x0 - 0.038, y_col + bh / 2, "$\mathtt{col\_idx}$", fs=8.6, ha="right", color=BLUE)

ax.text(0.045, 0.965, "同一批非零值按行存进三个一维数组（示意图）", fontsize=8.8,
        color=INK, ha="left", va="top")
ax.text(0.045, 0.240, "$\mathtt{row\_ptr}[i]$ 到 $\mathtt{row\_ptr}[i+1]-1$ "
                     "就是第 $i$ 行在 $\mathtt{val}$ 与 $\mathtt{col\_idx}$ 中的下标区间",
        fontsize=8.4, color=INK, ha="left", va="top")
ax.text(0.045, 0.170, "非零数 $\mathrm{nnz}=%d$；三个数组总长 $=%d+%d+5=%d$，"
                     "每行的非零个数可以不同" % (nnz, nnz, nnz, 2 * nnz + 5),
        fontsize=8.4, color=MUTED, ha="left", va="top")

ax.plot([0.345, 0.345], [0.13, 0.95], color=GRID, lw=0.9)

save(fig, "12", "fig12-03")
