import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 5-1  刚体状态：局部坐标 / 世界坐标 / 惯性主轴
# ============================================================
fig, ax = canvas(6.7, 3.6)

th = np.deg2rad(22.0)
u = np.array([np.cos(th), np.sin(th)])
vv = np.array([-np.sin(th), np.cos(th)])
C = np.array([0.245, 0.545])
hl, hw = 0.130, 0.072
P = [C + hl * u + hw * vv, C + hl * u - hw * vv, C - hl * u - hw * vv, C - hl * u + hw * vv]
Pb = [q + np.array([0.020, -0.016]) for q in P]
ax.add_patch(Polygon(Pb, closed=True, facecolor="#DCE6FA", edgecolor=INK, lw=1.1, zorder=1))
ax.add_patch(Polygon(P, closed=True, facecolor="#EFF4FF", edgecolor=INK, lw=1.2, zorder=3))

# 惯性主轴椭圆（虚线）
ax.add_patch(Ellipse(C, 2 * 0.185, 2 * 0.090, angle=22.0, fill=False,
                     edgecolor=PURPLE, lw=1.0, ls=(0, (4, 3)), zorder=6))

# 局部坐标轴
arrow(ax, C, C + 0.210 * u, color=BLUE, lw=1.5, z=7, ms=9)
arrow(ax, C, C + 0.125 * vv, color=BLUE, lw=1.5, z=7, ms=9)
label(ax, *(C + 0.238 * u + 0.028 * vv), "$x_\\ell$", fs=9.5, color=BLUE, weight="bold")
label(ax, *(C + 0.125 * vv - 0.030 * u), "$y_\\ell$", fs=9.5, color=BLUE, weight="bold", ha="right")

# 角速度
arrow(ax, C + np.array([0.0, 0.020]), C + np.array([0.0, 0.175]), color=ACCENT, lw=1.5, z=7, ms=9)
label(ax, C[0], C[1] + 0.207, "$\\omega$", fs=10.5, color=ACCENT, weight="bold")

# 质心
ax.plot([C[0]], [C[1]], "o", ms=4.2, color=INK, zorder=8)
ax.plot([C[0], C[0]], [0.402, C[1] - 0.012], color=INK, lw=0.7, zorder=2)
label(ax, C[0], 0.372, "质心 $\\mathbf{c}$", fs=8.8)

# 世界坐标轴
o = np.array([0.085, 0.185])
arrow(ax, o, o + np.array([0.105, 0.0]), color=MUTED, lw=1.1, z=5, ms=8)
arrow(ax, o, o + np.array([0.0, 0.105]), color=MUTED, lw=1.1, z=5, ms=8)
arrow(ax, o, o + np.array([-0.052, 0.052]), color=MUTED, lw=1.1, z=5, ms=8)
label(ax, 0.202, 0.185, "$x$", fs=8.6, color=MUTED)
label(ax, 0.085, 0.305, "$y$", fs=8.6, color=MUTED)
label(ax, 0.016, 0.235, "$z$", fs=8.6, color=MUTED)
label(ax, 0.030, 0.120, "世界坐标系", fs=8.2, color=MUTED, ha="left")

# 顶部小图例
ax.plot([0.030, 0.070], [0.945, 0.945], color=BLUE, lw=1.5)
label(ax, 0.078, 0.945, "局部坐标轴，随物体一起转", fs=8.2, ha="left")
ax.plot([0.030, 0.070], [0.885, 0.885], color=PURPLE, lw=1.0, ls=(0, (4, 3)))
label(ax, 0.078, 0.885, "惯性主轴，$\\mathbf{I}_\\ell$ 的特征向量", fs=8.2, ha="left")

# 世界坐标公式
label(ax, 0.250, 0.048, "$\\mathbf{x}_{\\mathrm{w}} = \\mathbf{c} + \\mathbf{R}\\,\\mathbf{x}_{\\ell}$",
      fs=9.8, ha="center")

# 右侧分隔与状态清单
ax.plot([0.505, 0.505], [0.045, 0.965], color=GRID, lw=0.9)
label(ax, 0.535, 0.925, "状态：13 个数", fs=9.4, ha="left", weight="bold")

rows = [("$\\mathbf{c}$", "质心位置", "3"),
        ("$\\mathbf{q}$", "姿态四元数", "4"),
        ("$\\mathbf{v}$", "线速度", "3"),
        ("$\\boldsymbol{\\omega}$", "角速度", "3")]
ys = [0.790, 0.680, 0.570, 0.460]
for (sym, name, num), y in zip(rows, ys):
    label(ax, 0.545, y, sym, fs=9.6, ha="left")
    label(ax, 0.630, y, name, fs=8.8, ha="left")
    label(ax, 0.945, y, num, fs=9.6, ha="right", color=ACCENT, weight="bold")

ax.plot([0.535, 0.955], [0.400, 0.400], color=GRID, lw=0.9)
label(ax, 0.535, 0.335, "合计 13 个数", fs=9.0, ha="left")
label(ax, 0.535, 0.245,
      "四元数多出的一个分量\n由 $|\\mathbf{q}| = 1$ 约束住，自由度是 12",
      fs=8.2, ha="left", va="top", color=MUTED)

save(fig, "05", "fig05-01")


# ============================================================
# 图 5-2  顺序冲量求解的一轮
# ============================================================
fig, ax = canvas(6.7, 3.8)

steps = ["取下一个接触 $j$，读法向 $\\mathbf{n}$ 与相对速度 $u_j$",
         "求增量 $\\Delta\\lambda = -u_j \\,/\\, k_j$\n$k_j$ 为这个接触的有效质量",
         "累加后裁剪：$\\lambda_j \\leftarrow \\max(0,\\ \\lambda_j + \\Delta\\lambda)$\n只能推、不能拉",
         "把实际冲量写回两个物体的速度",
         "所有接触扫完一遍，记作一轮"]

x0, w = 0.145, 0.545
h, gap, ytop = 0.105, 0.048, 0.855
cents = []
for i, s in enumerate(steps):
    y = ytop - i * (h + gap)
    col = ACCENT if i == 2 else INK
    box(ax, x0, y - h / 2, w, h, s, fc="white", ec=col, fs=8.8, lw=1.2 if i == 2 else 1.0)
    cents.append(y)
    if i:
        arrow(ax, (x0 + w / 2, cents[i - 1] - h / 2 - 0.004),
              (x0 + w / 2, y + h / 2 + 0.004), color=FAINT, lw=1.0, ms=8)

curve_arrow(ax, [(x0 + w + 0.004, cents[-1]), (0.760, cents[-1]),
                 (0.760, cents[0]), (x0 + w + 0.008, cents[0])],
            color=ACCENT, lw=1.1, ms=9)
label(ax, 0.800, (cents[0] + cents[-1]) / 2, "再来一轮", fs=8.6, color=ACCENT, rot=90)

label(ax, 0.145, 0.952, "对接触列表依次执行", fs=9.2, ha="left", weight="bold")
label(ax, 0.145, 0.125, "轮数用尽或残差足够小则停", fs=8.4, ha="left", color=MUTED)
label(ax, 0.145, 0.060, "每个接触看到的，都是别人已经改过的速度", fs=8.4,
      ha="left", color=MUTED)

save(fig, "05", "fig05-02")


# ============================================================
# 图 5-3  一维堆叠的 PGS 收敛（真实计算）
# ============================================================
def pgs_stack(N, iters, m=1.0, g=9.81, dt=1.0 / 60.0):
    """N 个盒子叠在无穷大质量的地面上，重力作用后解法向非穿透约束。
    接触 j 位于盒子 j-1（地面记为 0）与盒子 j 之间，自下而上逐点扫。"""
    v = -g * dt * np.ones(N)
    lam = np.zeros(N)
    res = []
    for _ in range(iters):
        for j in range(N):
            vlow = v[j - 1] if j > 0 else 0.0
            u = v[j] - vlow
            keff = 1.0 / m if j == 0 else 2.0 / m
            new = max(0.0, lam[j] - u / keff)
            d = new - lam[j]
            lam[j] = new
            v[j] += d / m
            if j > 0:
                v[j - 1] -= d / m
        viol = [max(0.0, -((v[j] - (v[j - 1] if j > 0 else 0.0)))) for j in range(N)]
        res.append(max(viol))
    return np.array(res), lam


def iters_to(N, tol=1e-4, cap=6000):
    r, _ = pgs_stack(N, cap)
    idx = np.where(r < tol)[0]
    return (idx[0] + 1) if len(idx) else cap


fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))

ax = axs[0]
for N, col in [(3, GREEN), (5, BLUE), (10, ACCENT)]:
    r, _ = pgs_stack(N, 320)
    ax.semilogy(np.arange(1, len(r) + 1), np.maximum(r, 1e-16), color=col, lw=1.5,
                label=f"N = {N}")
ax.axhline(1e-4, color=FAINT, lw=1.0, ls=(0, (4, 3)), label="容差 $10^{-4}$ m/s")
ax.set_xlabel("迭代轮数")
ax.set_ylabel("最大穿透速度（m/s）")
ax.set_ylim(3e-6, 3e-1)
ax.set_xlim(0, 346)
ax.legend(loc="upper right", handlelength=1.9, labelspacing=0.35)
clean(ax, grid=True)

ax = axs[1]
Ns = [2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
its = np.array([iters_to(N) for N in Ns], float)
ax.loglog(Ns, its, "o-", ms=4.0, color=ACCENT, mfc=ACCENT, mec="white", mew=0.8,
          lw=1.3, label="实测", zorder=4)
ref = its[-1] * (np.array(Ns, float) / Ns[-1]) ** 2
ax.loglog(Ns, ref, color=MUTED, lw=0.9, ls=(0, (4, 3)), label="$\\propto N^2$", zorder=2)
ax.set_xticks([2, 3, 4, 6, 8, 10, 16, 24])
ax.set_xticklabels(["2", "3", "4", "6", "8", "10", "16", "24"])
ax.minorticks_off()
ax.set_xlabel("堆叠层数 N")
ax.set_ylabel("达到容差所需轮数")
ax.set_ylim(6, 3200)
ax.legend(loc="upper left", handlelength=1.9)
clean(ax, grid=True)

fig.tight_layout(w_pad=2.4)
save(fig, "05", "fig05-03")
