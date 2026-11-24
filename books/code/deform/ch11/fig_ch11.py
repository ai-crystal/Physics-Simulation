"""第 11 章配图。

图 11-1  悬臂梁前四阶模态（有限元 + 解析对照）
图 11-2  子空间投影误差随基向量数（三种载荷）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from scipy.linalg import eigh

# ----------------------------------------------------------------- 梁的模型
L, E, RHO = 1.0, 3.5e9, 1200.0
B, H = 0.020, 0.005
A = B * H
I = B * H ** 3 / 12.0
EI, RHO_A = E * I, RHO * A
NEL = 40
LE = L / NEL
NDOF = 2 * (NEL + 1)

K = np.zeros((NDOF, NDOF))
M = np.zeros((NDOF, NDOF))
ke = EI / LE ** 3 * np.array([[12, 6 * LE, -12, 6 * LE],
                              [6 * LE, 4 * LE ** 2, -6 * LE, 2 * LE ** 2],
                              [-12, -6 * LE, 12, -6 * LE],
                              [6 * LE, 2 * LE ** 2, -6 * LE, 4 * LE ** 2]])
me = RHO_A * LE / 420.0 * np.array([[156, 22 * LE, 54, -13 * LE],
                                    [22 * LE, 4 * LE ** 2, 13 * LE, -3 * LE ** 2],
                                    [54, 13 * LE, 156, -22 * LE],
                                    [-13 * LE, -3 * LE ** 2, -22 * LE, 4 * LE ** 2]])
for e in range(NEL):
    d = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
    K[np.ix_(d, d)] += ke
    M[np.ix_(d, d)] += me

FREE = np.arange(2, NDOF)
Kr, Mr = K[np.ix_(FREE, FREE)], M[np.ix_(FREE, FREE)]
w2, V = eigh(Kr, Mr)
NM = 16
PHI_F = V[:, :NM]                      # 质量正交归一，Phi^T M Phi = I
FREQ_FE = np.sqrt(np.maximum(w2[:NM], 0.0)) / (2 * np.pi)

BL = np.array([1.875104068711961, 4.694091132974174,
               7.854757438237612, 10.995540734875466,
               14.1371681837383, 17.2787593048333])
FREQ_AN = BL ** 2 / (2 * np.pi) * np.sqrt(EI / (RHO_A * L ** 4))


def mode_shape(j, m=600):
    """用 Hermite 插值把节点挠度与转角还原成连续曲线。"""
    phi = np.zeros(NDOF)
    phi[FREE] = PHI_F[:, j]
    if phi[-2] < 0:                    # 自由端统一朝上
        phi = -phi
    xs = np.linspace(0.0, L, m)
    ys = np.zeros(m)
    for e in range(NEL):
        msk = (xs >= e * LE - 1e-12) & (xs <= (e + 1) * LE + 1e-12)
        xi = (xs[msk] - e * LE) / LE
        w0, t0 = phi[2 * e], phi[2 * e + 1]
        w1, t1 = phi[2 * e + 2], phi[2 * e + 3]
        ys[msk] = ((2 * xi ** 3 - 3 * xi ** 2 + 1) * w0
                   + (xi ** 3 - 2 * xi ** 2 + xi) * LE * t0
                   + (-2 * xi ** 3 + 3 * xi ** 2) * w1
                   + (xi ** 3 - xi ** 2) * LE * t1)
    return xs, ys / np.abs(ys).max()


# ----------------------------------------------------------------- 图 11-1
fig, (ax1, ax2) = new(6.8, 3.7, ncols=2, gridspec_kw=dict(width_ratios=[1.36, 1.0]))

cols = [ACCENT, BLUE, GREEN, PURPLE]
OFF, AMP = 1.62, 0.44
for j in range(4):
    xs, ys = mode_shape(j)
    y0 = OFF * (3 - j)
    ax1.plot([0.0, L], [y0, y0], color=GRID, lw=0.7, ls=(0, (3, 3)), zorder=1)
    ax1.plot(xs, y0 + AMP * ys, color=cols[j], lw=1.7, zorder=3,
             solid_capstyle="round")
    ax1.text(0.045, y0 + 0.50, f"{j + 1} 阶", fontsize=8.8, color=cols[j],
             weight="bold", ha="left", va="bottom", zorder=4)
    ax1.text(0.172, y0 + 0.505, f"{FREQ_FE[j]:.2f} Hz", fontsize=8.2,
             color=MUTED, ha="left", va="bottom", zorder=4)

# 固定端剖面线
ax1.add_patch(Rectangle((-0.075, -0.62), 0.055, 5.42, facecolor="#EDE8DF",
                        edgecolor=INK, lw=0.9, zorder=2, hatch="////"))
ax1.text(-0.142, 2.5, "固定端", fontsize=8.0, color=MUTED, rotation=90,
         ha="center", va="center")
ax1.annotate("", xy=(L, -0.72), xytext=(0.0, -0.72),
             arrowprops=dict(arrowstyle="<|-|>", color=FAINT, lw=0.8))
ax1.text(L / 2, -0.80, "$L = 1$ m", fontsize=8.2, color=MUTED,
         ha="center", va="top")
ax1.set_xlim(-0.20, L + 0.03)
ax1.set_ylim(-1.05, 5.62)
ax1.axis("off")

# 右：有限元与解析对照（横轴线性，纵轴对数）
from scipy.optimize import brentq
roots = []
for k in range(1, 15):
    a0 = (2 * k - 1) * np.pi / 2
    roots.append(brentq(lambda x: np.cos(x) * np.cosh(x) + 1, a0 - 1.2, a0 + 1.2))
FREQ_AN12 = np.array([r ** 2 / (2 * np.pi) * np.sqrt(EI / (RHO_A * L ** 4))
                      for r in roots])
DEV = FREQ_FE[:12] / FREQ_AN12[:12] - 1.0

n = np.arange(1, 13)
ax2.semilogy(n, FREQ_AN12[:12], ls="--", lw=1.0, color=MUTED, marker="s", ms=5.0,
             mfc="white", mec=MUTED, mew=0.9, label="式 11.4（解析）", zorder=2)
ax2.semilogy(n, FREQ_FE[:12], ls="none", marker="o", ms=3.0, color=ACCENT,
             label="40 单元有限元", zorder=3)
ax2.set_xlabel("模态阶次")
ax2.set_ylabel("频率 / Hz")
ax2.set_xticks([1, 3, 6, 9, 12])
ax2.set_xlim(0.2, 12.9)
ax2.set_ylim(0.8, 900)
ax2.grid(True, which="major", color=GRID, lw=0.7)
ax2.set_axisbelow(True)
ax2.legend(loc="upper left", handlelength=1.4, borderpad=0.25,
           labelspacing=0.32, handletextpad=0.45)
ax2.text(0.965, 0.04, "有限元偏高：4 阶 $4\\times10^{-6}$",
         transform=ax2.transAxes, fontsize=8.0, color=MUTED, ha="right",
         va="bottom")
ax2.text(0.965, 0.115, "12 阶 $4.5\\times10^{-4}$",
         transform=ax2.transAxes, fontsize=8.0, color=MUTED, ha="right",
         va="bottom")
clean(ax2)

print("偏差 4/8/12 阶:", ["%.2e" % DEV[k - 1] for k in (4, 8, 12)])

save(fig, "11", "fig11-01")

# ----------------------------------------------------------------- 图 11-2
def static_solve(f):
    u = np.zeros(NDOF)
    u[FREE] = np.linalg.solve(Kr, f[FREE])
    return u


def consistent_uniform(q0):
    """均布横向载荷的一致节点力。"""
    f = np.zeros(NDOF)
    for e in range(NEL):
        f[2 * e:2 * e + 4] += q0 * LE / 2 * np.array([1, LE / 6, 1, -LE / 6])
    return f


F_UNIF = consistent_uniform(-0.1)                 # 0.1 N/m 向下
F_TIP = np.zeros(NDOF); F_TIP[-2] = -0.1          # 自由端集中力 0.1 N
F_PINCH = np.zeros(NDOF)                          # 跨中一对反向力，相距 2.5 cm
F_PINCH[2 * (NEL // 2) + 2] = -0.1
F_PINCH[2 * (NEL // 2 + 1) + 2] = +0.1

CASES = [("均布载荷", F_UNIF, ACCENT, "-"),
         ("端部集中力", F_TIP, BLUE, "--"),
         ("跨中一对反向力", F_PINCH, GREEN, "-.")]
RS = np.arange(1, 17)

fig, (ax1, ax2) = new(6.9, 3.6, ncols=2, gridspec_kw=dict(width_ratios=[1.26, 1.0]))
fig.subplots_adjust(wspace=0.34)

for name, f, c, ls in CASES:
    u = static_solve(f)
    den = np.sqrt(u[FREE] @ (Kr @ u[FREE]))
    errs = []
    for r in RS:
        Bm = PHI_F[:, :r]
        a = Bm.T @ (Mr @ u[FREE])
        e = u[FREE] - Bm @ a
        errs.append(np.sqrt(e @ (Kr @ e)) / den)
    ax1.semilogy(RS, errs, ls=ls, lw=1.5, color=c, label=name)
    ax1.plot(RS[-1], errs[-1], "o", ms=3.6, color=c)

ax1.axhline(0.01, color=FAINT, lw=0.9, ls=(0, (4, 3)))
ax1.text(1.05, 0.0112, "1%", fontsize=8.2, color=MUTED, ha="left", va="bottom")
ax1.set_xlabel("基向量数 $r$")
ax1.set_ylabel("能量范数相对误差")
ax1.set_xlim(0.6, 17.6)
ax1.set_ylim(8e-5, 0.55)
ax1.set_xticks([1, 4, 8, 12, 16])
ax1.grid(True, which="major", color=GRID, lw=0.7)
ax1.set_axisbelow(True)
ax1.legend(loc="lower left", handlelength=2.2, borderpad=0.25,
           labelspacing=0.32, fontsize=8.6)
clean(ax1)

# 右：三种载荷的模态参与系数（相对一阶）
for name, f, c, ls in CASES:
    u = static_solve(f)
    a = np.abs(PHI_F.T @ (Mr @ u[FREE]))
    ax2.semilogy(np.arange(1, 9), a[:8] / a[0], ls="none", marker="o", ms=4.4,
                 color=c, mfc="white", mew=1.1, label=name)
ax2.set_xlabel("模态阶次")
ax2.set_ylabel("参与系数（相对一阶）")
ax2.set_xticks([1, 2, 3, 4, 5, 6, 7, 8])
ax2.set_xlim(0.6, 8.4)
ax2.set_ylim(3e-6, 3.0)
ax2.grid(True, which="major", color=GRID, lw=0.7)
ax2.set_axisbelow(True)
clean(ax2)

save(fig, "11", "fig11-02")

# ----------------------------------------------------------------- 诊断
print("FE   :", np.round(FREQ_FE[:6], 4))
print("解析 :", np.round(FREQ_AN, 4))
print("偏差 :", np.round(np.abs(FREQ_FE[:4] / FREQ_AN[:4] - 1), 8))
for name, f, c, ls in CASES:
    u = static_solve(f)
    den = np.sqrt(u[FREE] @ (Kr @ u[FREE]))
    e12 = []
    for r in RS:
        Bm = PHI_F[:, :r]
        a = Bm.T @ (Mr @ u[FREE])
        e = u[FREE] - Bm @ a
        e12.append(np.sqrt(e @ (Kr @ e)) / den)
    print(f"{name}: 最大位移 {np.abs(u[FREE]).max()*1e3:.2f} mm, "
          f"r=1 {e12[0]:.4f}, r=3 {e12[2]:.4f}, r=8 {e12[7]:.4f}, r=16 {e12[15]:.4f}")
