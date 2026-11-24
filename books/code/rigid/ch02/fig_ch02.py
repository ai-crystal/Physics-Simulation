import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 长方体的惯性张量：六个四面体精确积分
#   box 尺寸 a x b x c、质量 m、密度 rho = m/(abc)
#   每个四面体一个顶点在质心，其余三个是盒子的角点
#   ∫_T x x^T dV = V/20 ( Σ v_k v_k^T + (Σ v_k)(Σ v_k)^T )
#   I = Σ_T rho * ( tr(M_T) E - M_T )
# ============================================================
A, B, C = 0.6, 0.4, 0.2
MASS = 2.4
RHO = MASS / (A * B * C)
H = np.array([A, B, C]) / 2.0


def box_inertia(half, rho):
    """沿主对角线把盒子分成 6 个四面体，用四面体的二阶矩公式求和。"""
    def P(bits):
        return (np.array(bits, float) - 0.5) * (2.0 * half)

    tets = [((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)),
            ((0, 0, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1)),
            ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 1, 1)),
            ((0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)),
            ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1)),
            ((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1))]
    M2 = np.zeros((3, 3))
    vol = 0.0
    for tet in tets:
        v = np.array([P(b) for b in tet])
        V = abs(np.linalg.det(v[1:] - v[0])) / 6.0
        S = v.sum(0)
        M2 += V / 20.0 * (v.T @ v + np.outer(S, S))     # ∫ x x^T dV
        vol += V
    I = rho * (np.trace(M2) * np.eye(3) - M2)
    return I, len(tets), vol


I_box, ntets, VOL = box_inertia(H, RHO)
print("六个体积之和 %.6f（应为 %.6f）" % (VOL, A * B * C))
evals, evecs = np.linalg.eigh(I_box)
print("四面体数 %d" % ntets)
print("数值惯性张量\n", np.array2string(I_box, precision=6))
print("特征值", np.array2string(evals, precision=6))
analytic = np.array([MASS * (B ** 2 + C ** 2) / 12,
                     MASS * (A ** 2 + C ** 2) / 12,
                     MASS * (A ** 2 + B ** 2) / 12])
print("解析式   ", np.array2string(analytic, precision=6))
print("最大相对误差 %.2e" % np.max(np.abs(evals - analytic) / analytic))

# 转一下再验证：世界坐标下特征值不变，特征向量跟着转
ang = np.array([0.6, -0.35, 1.1])
Rx = np.array([[1, 0, 0], [0, np.cos(ang[0]), -np.sin(ang[0])], [0, np.sin(ang[0]), np.cos(ang[0])]])
Ry = np.array([[np.cos(ang[1]), 0, np.sin(ang[1])], [0, 1, 0], [-np.sin(ang[1]), 0, np.cos(ang[1])]])
Rz = np.array([[np.cos(ang[2]), -np.sin(ang[2]), 0], [np.sin(ang[2]), np.cos(ang[2]), 0], [0, 0, 1]])
Rchk = Rz @ Ry @ Rx
Iw = Rchk @ I_box @ Rchk.T
ev2 = np.linalg.eigvalsh(Iw)
print("转动后特征值", np.array2string(ev2, precision=6),
      "偏差 %.2e" % np.max(np.abs(ev2 - evals)))
print("I1 + I2 - I3 = %.6f" % (evals[0] + evals[1] - evals[2]))


# ============================================================
# 图 2-1  长方体的三个惯性主轴（真实计算）
#   左：主轴方向取数值特征向量；右：特征值与解析式对比
# ============================================================
AZ, EL = np.deg2rad(32.0), np.deg2rad(22.0)


def proj(p, o=(0.0, 0.0), s=1.0):
    p = np.asarray(p, float)
    sx = p[..., 0] * np.cos(AZ) - p[..., 2] * np.sin(AZ)
    sy = p[..., 1] * np.cos(EL) - (p[..., 0] * np.sin(AZ) + p[..., 2] * np.cos(AZ)) * np.sin(EL)
    return np.stack([o[0] + s * sx, o[1] + s * sy], axis=-1)


FIGW, FIGH = 6.9, 3.45
fig = plt.figure(figsize=(FIGW, FIGH))
axl = fig.add_axes([0.004, 0.02, 0.600, 0.96])
axl.set_xlim(0, 0.600 * FIGW); axl.set_ylim(0, 0.96 * FIGH)
axl.set_aspect("equal"); axl.axis("off")
axr = fig.add_axes([0.665, 0.215, 0.310, 0.625])

ORG, SCL = (1.45, 1.62), 3.95
sg = np.array([[i, j, k] for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], float)
Vp = proj(sg * H, ORG, SCL)
for i in range(8):
    for j in range(i + 1, 8):
        if np.sum(sg[i] != sg[j]) == 1:
            far = (sg[i][0] + sg[j][0]) < 0
            axl.plot([Vp[i][0], Vp[j][0]], [Vp[i][1], Vp[j][1]],
                     color=FAINT if far else INK, lw=0.8 if far else 1.1,
                     zorder=2 if far else 3)
idx = lambda v: np.where((sg == np.array(v, float)).all(1))[0][0]
axl.add_patch(Polygon([Vp[idx([-1, 1, 1])], Vp[idx([-1, 1, -1])],
                       Vp[idx([-1, -1, -1])], Vp[idx([-1, -1, 1])]],
                      closed=True, facecolor="#EEF0F6", edgecolor="none",
                      alpha=0.9, zorder=1))

cc = proj(np.zeros(3), ORG, SCL)
cols = [BLUE, ACCENT, GREEN]
AXL = 0.335
for k in range(3):
    d = evecs[:, k]
    if d[np.argmax(np.abs(d))] < 0:
        d = -d
    tip = proj(AXL * d, ORG, SCL)
    tail = proj(-AXL * d, ORG, SCL)
    axl.plot([tail[0], tip[0]], [tail[1], tip[1]], color=cols[k], lw=1.5,
             ls=(0, (6, 3)), zorder=7, alpha=0.95)
    arrow(axl, proj(0.80 * AXL * d, ORG, SCL), tip, color=cols[k], lw=1.6, ms=8, z=8)

lbl = [("$I_1 = 0.040$", (0.10, -0.16), "left"),
       ("$I_2 = 0.080$", (-0.10, 0.17), "right"),
       ("$I_3 = 0.104$", (-0.10, -0.13), "right")]
for k in range(3):
    d = evecs[:, k]
    if d[np.argmax(np.abs(d))] < 0:
        d = -d
    tip = proj(AXL * d, ORG, SCL)
    txt, off, ha = lbl[k]
    axl.text(tip[0] + off[0], tip[1] + off[1], txt, fontsize=8.8, color=cols[k],
             weight="bold", ha=ha, zorder=12)
axl.plot([cc[0]], [cc[1]], "o", ms=3.8, color=INK, zorder=10)
axl.text(0.12, 0.16, "棱与坐标轴对齐时，惯性张量是对角阵", fontsize=8.4,
         color=MUTED, ha="left")

# ---- 右：数值特征值与解析式（解析值画成横线） ----
xs = np.arange(3)
axr.bar(xs, evals * 1e3, width=0.52, color=ACCENT, edgecolor="none", zorder=3)
for x, v, a in zip(xs, evals * 1e3, analytic * 1e3):
    axr.plot([x - 0.26, x + 0.26], [a, a], color=INK, lw=1.3, ls=(0, (4, 2)), zorder=5)
    axr.text(x, v + 2.4, "%.1f" % v, fontsize=9.0, color=ACCENT, ha="center",
             va="bottom", weight="bold")
axr.set_xticks(xs)
axr.set_xticklabels(["$I_1$", "$I_2$", "$I_3$"])
axr.set_xlabel("绕 $x$ 轴　　绕 $y$ 轴　　绕 $z$ 轴", fontsize=8.6)
axr.set_ylabel("主惯性矩（$10^{-3}\ \mathrm{kg\cdot m^2}$）")
axr.set_xlim(-0.62, 2.62)
axr.set_ylim(0, 128)
axr.set_yticks([0, 40, 80, 120])
clean(axr, grid=True)
axr.text(0.02, 0.905, "柱：数值积分　虚线：解析式", transform=axr.transAxes,
         fontsize=8.2, color=MUTED, va="top", ha="left")

save(fig, "02", "fig02-01")


# ============================================================
# 图 2-2  三种初始角速度下的自由旋转（真实积分）
#   欧拉方程（体坐标，无力矩），RK4
#   I = diag(0.04, 0.08, 0.104) kg m^2
# ============================================================
II = np.array([0.04, 0.08, 0.104])
OMEGA0 = 6.0
EPS = 0.05


def deriv(w):
    I1, I2, I3 = II
    w1, w2, w3 = w
    return np.array([(I2 - I3) * w2 * w3 / I1,
                     (I3 - I1) * w3 * w1 / I2,
                     (I1 - I2) * w1 * w2 / I3])


def integrate(w0, T, dt):
    n = int(round(T / dt))
    out = np.empty((n + 1, 3))
    out[0] = w0
    w = w0.copy()
    for i in range(n):
        k1 = deriv(w)
        k2 = deriv(w + 0.5 * dt * k1)
        k3 = deriv(w + 0.5 * dt * k2)
        k4 = deriv(w + dt * k3)
        w = w + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[i + 1] = w
    return out


DT_SIM, T_SIM = 1e-4, 12.0
mid = np.array([EPS, OMEGA0, EPS])          # 绕中间轴（y）
hist = integrate(mid, T_SIM, DT_SIM)
tt = np.linspace(0, T_SIM, hist.shape[0])
zc = tt[1:][np.sign(hist[1:, 1]) != np.sign(hist[:-1, 1])]
print("w2 过零时刻", np.array2string(zc, precision=2))
print("中间轴：w2 的极值 %.3f / %.3f" % (hist[:, 1].min(), hist[:, 1].max()))
energy0 = 0.5 * np.sum(II * mid ** 2)
energy1 = 0.5 * np.sum(II * hist[-1] ** 2)
L0 = np.sum((II * mid) ** 2)
L1 = np.sum((II * hist[-1]) ** 2)
print("能量 %.8f -> %.8f（相对 %.1e）" % (energy0, energy1, abs(energy1 / energy0 - 1)))
print("|L|^2 %.8f -> %.8f（相对 %.1e）" % (L0, L1, abs(L1 / L0 - 1)))

starts = [np.array([OMEGA0, EPS, EPS]),
          np.array([EPS, OMEGA0, EPS]),
          np.array([EPS, EPS, OMEGA0])]
perp = [(1, 2), (0, 2), (0, 1)]
labels = ["绕 $I_1$（最长轴）", "绕 $I_2$（中间轴）", "绕 $I_3$（最短轴）"]
ccols = [BLUE, ACCENT, GREEN]
amp = []
for (w0, (p, q)) in zip(starts, perp):
    h = integrate(w0, T_SIM, DT_SIM)
    amp.append(np.hypot(h[:, p], h[:, q]))
print("垂轴模峰值", np.array2string(np.array([a.max() for a in amp]), precision=2))

fig, axs = plt.subplots(1, 2, figsize=(6.9, 3.05),
                        gridspec_kw=dict(width_ratios=[1.12, 1.0], wspace=0.30))

ax = axs[0]
ax.plot(tt, hist[:, 0], color=BLUE, lw=1.3, label="$\\omega_1$")
ax.plot(tt, hist[:, 1], color=ACCENT, lw=1.6, label="$\\omega_2$")
ax.plot(tt, hist[:, 2], color=GREEN, lw=1.3, label="$\\omega_3$")
ax.axhline(0, color=GRID, lw=1.0)
ax.set_xlim(0, T_SIM)
ax.set_ylim(-7.2, 7.2)
ax.set_xlabel("时间 $t$（s）")
ax.set_ylabel("体坐标角速度（rad/s）")
clean(ax, grid=True)
ax.legend(loc="upper right", ncol=3, handlelength=1.5, columnspacing=1.0,
          borderpad=0.3)

ax = axs[1]
for a, lab, c in zip(amp, labels, ccols):
    ax.semilogy(tt, a, color=c, lw=1.4, label=lab)
ax.axhline(EPS, color=FAINT, lw=0.9, ls=(0, (4, 3)))
ax.set_xlim(0, T_SIM)
ax.set_ylim(2e-3, 12)
ax.set_xlabel("时间 $t$（s）")
ax.set_ylabel("垂直于初始轴的角速度模（rad/s）")
clean(ax, grid=True)
ax.legend(loc="lower right", handlelength=1.5, borderpad=0.3, labelspacing=0.35,
          fontsize=8.2)
ax.axhline(EPS, color=FAINT, lw=0.9, ls=(0, (4, 3)))
ax.text(0.15, EPS * 1.30, "$\\varepsilon$", fontsize=9.0, color=MUTED)

fig.subplots_adjust(left=0.100, right=0.975, top=0.955, bottom=0.175)
save(fig, "02", "fig02-02")
