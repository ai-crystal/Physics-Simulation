import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 等轴测投影：三维点 -> 纸面坐标
# ============================================================
AZ, EL = np.deg2rad(35.0), np.deg2rad(24.0)


def proj(p, o=(0.0, 0.0), s=1.0):
    p = np.asarray(p, float)
    sx = p[..., 0] * np.cos(AZ) - p[..., 2] * np.sin(AZ)
    sy = p[..., 1] * np.cos(EL) - (p[..., 0] * np.sin(AZ) + p[..., 2] * np.cos(AZ)) * np.sin(EL)
    return np.stack([o[0] + s * sx, o[1] + s * sy], axis=-1)


# ============================================================
# 图 1-1  刚体状态与两个坐标系（示意图，非计算）
# ============================================================
fig, ax = canvas(6.9, 3.9)

HALF = np.array([0.52, 0.32, 0.18])      # 长方体三个半边长
ORG = (0.290, 0.600)
SCL = 0.270

# ---- 世界坐标系 ----
WO = np.array([0.100, 0.160])
for vec, lab, off, ha in ((np.array([1.0, 0, 0]), "$x$", (0.014, 0.004), "left"),
                          (np.array([0, 1.0, 0]), "$y$", (0.000, 0.016), "center"),
                          (np.array([0, 0, 1.0]), "$z$", (-0.008, -0.008), "right")):
    tip = proj(vec, WO, 0.140)
    arrow(ax, WO, tip, color=MUTED, lw=1.0, ms=7, z=4)
    label(ax, tip[0] + off[0], tip[1] + off[1], lab, fs=8.8, color=MUTED, ha=ha)
ax.plot([WO[0]], [WO[1]], "o", ms=3.0, color=MUTED, zorder=5)
label(ax, WO[0] - 0.050, WO[1] - 0.098, "世界坐标系", fs=8.4, color=MUTED, ha="left")

# ---- 长方体：8 个顶点与 12 条棱 ----
sg = np.array([[i, j, k] for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], float)
Vp = proj(sg * HALF, ORG, SCL)
for i in range(8):
    for j in range(i + 1, 8):
        if np.sum(sg[i] != sg[j]) == 1:
            far = (sg[i][0] + sg[j][0]) < 0      # 背面用浅色
            ax.plot([Vp[i][0], Vp[j][0]], [Vp[i][1], Vp[j][1]],
                    color=FAINT if far else INK, lw=0.8 if far else 1.1,
                    zorder=2 if far else 3)
idx = lambda v: np.where((sg == np.array(v, float)).all(1))[0][0]
ax.add_patch(Polygon([Vp[idx([-1, 1, 1])], Vp[idx([-1, 1, -1])],
                      Vp[idx([-1, -1, -1])], Vp[idx([-1, -1, 1])]],
                     closed=True, facecolor="#EEF0F6", edgecolor="none",
                     alpha=0.9, zorder=1))

# ---- 质心 c ----
cc = proj(np.zeros(3), ORG, SCL)
ax.plot([cc[0]], [cc[1]], "o", ms=4.2, color=INK, zorder=9)
label(ax, cc[0] - 0.012, cc[1] + 0.014, "$\\mathbf{c}$", fs=10.6, weight="bold", ha="right")

# ---- 局部坐标轴 ----
for d, lab, off, ha in ((np.array([1.0, 0, 0]), "$x_\\ell$", (0.012, -0.016), "left"),
                        (np.array([0, 1.0, 0]), "$y_\\ell$", (-0.004, 0.016), "center"),
                        (np.array([0, 0, 1.0]), "$z_\\ell$", (-0.010, 0.014), "right")):
    tip = proj(0.44 * d, ORG, SCL)
    arrow(ax, cc, tip, color=BLUE, lw=1.6, ms=8, z=8)
    label(ax, tip[0] + off[0], tip[1] + off[1], lab, fs=9.2, color=BLUE,
          weight="bold", ha=ha)

# ---- 角速度 ----
wd = np.array([0.55, 0.75, 0.35]); wd /= np.linalg.norm(wd)
wtip = proj(1.15 * wd, ORG, SCL)
arrow(ax, cc, wtip, color=ACCENT, lw=1.6, ms=9, z=8)
label(ax, wtip[0] + 0.012, wtip[1] - 0.002, "$\\boldsymbol{\\omega}$", fs=11.5,
      color=ACCENT, weight="bold", ha="left")

# ---- 线速度 ----
vd = np.array([0.35, -0.55, 0.30]); vd /= np.linalg.norm(vd)
vtip = proj(0.80 * vd, ORG, SCL)
arrow(ax, cc, vtip, color=GREEN, lw=1.5, ms=9, z=8)
label(ax, vtip[0] + 0.014, vtip[1] - 0.008, "$\\mathbf{v}$", fs=11.5,
      color=GREEN, weight="bold", ha="left")

# ---- 物质点 P 与 R x_l ----
P3 = np.array([-0.52, 0.32, 0.18])
Pp = proj(P3, ORG, SCL)
ax.plot([cc[0], Pp[0]], [cc[1], Pp[1]], color=PURPLE, lw=1.0, ls=(0, (3, 2)), zorder=6)
ax.plot([Pp[0]], [Pp[1]], "o", ms=3.6, color=PURPLE, zorder=9)
label(ax, Pp[0] - 0.012, Pp[1] + 0.002, "$P$", fs=9.6, color=PURPLE,
      weight="bold", ha="right")
label(ax, cc[0] + 0.32 * (Pp[0] - cc[0]), cc[1] + 0.32 * (Pp[1] - cc[1]) + 0.032,
      "$\\mathbf{R}\\,\\mathbf{x}_\\ell$", fs=8.8, color=PURPLE, rot=-34)

# ---- 左下公式 ----
label(ax, 0.335, 0.066,
      "$\\mathbf{x}_{\\mathrm{w}}=\\mathbf{c}+\\mathbf{R}\\,\\mathbf{x}_\\ell$", fs=10.2)

# ---- 右侧：状态清单 ----
ax.plot([0.520, 0.520], [0.050, 0.955], color=GRID, lw=1.0)
label(ax, 0.548, 0.905, "一步积分要读写的量", fs=9.4, weight="bold", ha="left")

rows = [("质心位置", "$\\mathbf{c}$", "3", BLUE),
        ("姿态四元数", "$\\mathbf{q}$", "4", BLUE),
        ("线速度", "$\\mathbf{v}$", "3", GREEN),
        ("角速度", "$\\boldsymbol{\\omega}$", "3", ACCENT)]
for i, (nm, sym, cnt, col) in enumerate(rows):
    y = 0.790 - i * 0.125
    ax.add_patch(Rectangle((0.546, y - 0.042), 0.436, 0.086, facecolor="white",
                           edgecolor=col, lw=1.0, zorder=3))
    label(ax, 0.562, y + 0.002, nm, fs=9.2, ha="left", z=6)
    label(ax, 0.700, y + 0.002, sym, fs=10.4, ha="left", color=col, weight="bold", z=6)
    label(ax, 0.966, y + 0.002, cnt + " 个", fs=9.2, ha="right", color=MUTED, z=6)

label(ax, 0.548, 0.276, "合计 13 个数，自由度 12", fs=9.4, ha="left", weight="bold")
label(ax, 0.548, 0.216, "多出的一个由 $|\\mathbf{q}|=1$ 占掉", fs=8.6, ha="left",
      color=MUTED)

ax.add_patch(Rectangle((0.546, 0.070), 0.436, 0.096, facecolor="#F7F8FA",
                       edgecolor=GRID, lw=0.9, zorder=1))
label(ax, 0.558, 0.138, "惯性张量 $\\mathbf{I}_\\ell$ 是常量，不进状态", fs=8.4, ha="left")
label(ax, 0.558, 0.102, "形状不变，建模时算一次就够", fs=8.4, ha="left", color=MUTED)

save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  四元数逐步积分不归一化时的模长漂移（真实计算）
#   q <- q + (dt/2)(0, w) ⊗ q
#   每步 |q|^2 放大 (1 + |w|^2 dt^2 / 4)，故 |q| ≈ exp(T |w|^2 dt / 8)
# ============================================================
def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                     w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])


OM = 8.0 * np.array([0.3, 0.5, 0.81]) / np.linalg.norm([0.3, 0.5, 0.81])   # rad/s，体坐标
Q0 = np.array([0.4, 0.5, -0.3, 0.7]); Q0 = Q0 / np.linalg.norm(Q0)
T_TOT = 60.0


def run_hist(dt, normalize):
    n = int(round(T_TOT / dt))
    q = Q0.copy()
    hist = np.empty(n)
    for i in range(n):
        q = q + 0.5 * dt * qmul(np.array([0.0, *OM]), q)
        if normalize:
            q = q / np.linalg.norm(q)
        hist[i] = np.linalg.norm(q)
    return hist


DT = 1.0 / 60.0
raw = run_hist(DT, False)
nor = run_hist(DT, True)
tt = np.arange(1, raw.size + 1) * DT
print("dt=1/60, 60 s: 不归一化 %.1f，归一化 %.12f" % (raw[-1], nor[-1]))

dts = np.array([1 / 480, 1 / 240, 1 / 120, 1 / 60, 1 / 30])
fin = np.array([run_hist(d, False)[-1] for d in dts])
print("末值随步长:", np.array2string(fin, precision=1))
slope = T_TOT * np.dot(OM, OM) / 8.0          # ln|q| ≈ slope * dt
print("解析指数 -T|w|^2/8 =", slope)

fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.05),
                        gridspec_kw=dict(width_ratios=[1.28, 1.0], wspace=0.31))

# ---- (a) 模长随时间 ----
ax = axs[0]
ax.semilogy(tt, raw, color=ACCENT, lw=1.7, label="不归一化")
ax.semilogy(tt, nor, color=BLUE, lw=1.2, ls=(0, (5, 3)), label="每步归一化")
ax.set_xlabel("时间 $t$（s）")
ax.set_ylabel("四元数模长 $|\\mathbf{q}|$")
ax.set_xlim(0, 63)
ax.set_ylim(0.80, 2.2e4)
ax.set_yticks([1, 10, 100, 1000, 10000])
ax.set_yticklabels(["1", "10", "$10^2$", "$10^3$", "$10^4$"])
clean(ax, grid=True)
ax.legend(loc="lower right", handlelength=1.9, borderpad=0.35)
ax.annotate("%.0f 倍" % raw[-1], xy=(T_TOT, raw[-1]), xytext=(28.0, 2.6e3),
            fontsize=9.0, color=ACCENT,
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9,
                            connectionstyle="arc3,rad=-0.20"))

# ---- (b) 末值随步长 ----
ax = axs[1]
dd = np.linspace(dts.min() * 0.85, dts.max() * 1.05, 200)
ax.semilogy(dd, np.exp(slope * dd), color=MUTED, lw=0.9, ls=(0, (4, 3)),
            label="解析 $e^{T|\\boldsymbol{\\omega}|^2\\Delta t/8}$")
ax.semilogy(dts, fin, "o", color=ACCENT, ms=4.8, label="数值积分")
ax.set_xlabel("步长 $\\Delta t$（s）")
ax.set_ylabel("60 s 后的 $|\\mathbf{q}|$")
ax.set_xlim(0.0, 0.038)
ax.set_ylim(1.0, 2.0e7)
clean(ax, grid=True)
ax.set_xticks([0, 1 / 120, 1 / 60, 1 / 30])
ax.set_xticklabels(["0", "1/120", "1/60", "1/30"])
ax.legend(loc="upper left", handlelength=1.9, borderpad=0.35, frameon=True,
          facecolor="white", edgecolor=GRID, framealpha=0.95)
ax.annotate("1/60", xy=(1 / 60, fin[3]), xytext=(0.0208, 55.0),
            fontsize=8.4, color=MUTED,
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=-0.25"))

fig.subplots_adjust(left=0.110, right=0.975, top=0.955, bottom=0.170)
save(fig, "01", "fig01-02")
