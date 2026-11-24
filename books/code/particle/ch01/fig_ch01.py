import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from scipy.spatial import cKDTree

# ============================================================
# 图 1-1  二维离散元沙堆：真实计算，规模很小
#   圆盘颗粒，法向弹簧-阻尼 + 切向库仑摩擦（增量弹簧）+ 滚动阻力
#   地面与侧壁按同样的接触模型处理，否则底层没有摩擦，沙堆会摊成液体
# ============================================================
DT = 2.0e-3
K_N = 1000.0
K_T = 500.0
ZETA = 0.30
GRAV = 1.0
X0, X1 = 6.0, 58.0


def run_pile(mu, mu_roll, n=420, n_inject=62000, n_settle=34000, seed=1):
    rng = np.random.default_rng(seed)
    xy = np.zeros((0, 2))
    vel = np.zeros((0, 2))
    rad = np.zeros(0)
    omg = np.zeros(0)
    mass = np.zeros(0)
    tw = np.zeros((0, 3))          # 地面/左墙/右墙的切向位移
    tang = np.zeros((0, 2))
    pairs = np.zeros((0, 2), dtype=int)
    next_rebuild = 0

    for step in range(n_inject + n_settle):
        if step < n_inject and len(rad) < n and step % 260 == 0:
            for _k in range(2):
                rr = 0.30 + 0.10 * rng.random()
                near = np.abs(xy[:, 0] - 32.0) < 4.2
                ltop = float(np.max(xy[near, 1] + rad[near])) if np.any(near) else 0.0
                ys = max(2.0, ltop + 0.45)
                xs = 32.0 + rng.uniform(-2.8, 2.8)
                if np.any(near):
                    dd = np.hypot(xy[near, 0] - xs, xy[near, 1] - ys)
                    if np.any(dd < rad[near] + rr + 0.04):
                        continue
                xy = np.vstack([xy, [xs, ys]])
                vel = np.vstack([vel, [0.0, -0.2]])
                omg = np.append(omg, 0.0)
                rad = np.append(rad, rr)
                mass = np.append(mass, np.pi * rr * rr)
                tang = np.vstack([tang, [0.0, 0.0]])
                tw = np.vstack([tw, [0.0, 0.0, 0.0]])
                next_rebuild = step

        if step >= next_rebuild:
            tree = cKDTree(xy)
            new_pairs = tree.query_pairs(2 * rad.max() + 0.20, output_type="ndarray")
            if len(pairs) and len(new_pairs):
                book = {(int(a), int(b)): tang[q] for q, (a, b) in enumerate(pairs)}
                tang = np.array([book.get((int(a), int(b)), (0.0, 0.0)) for a, b in new_pairs])
            else:
                tang = np.zeros((len(new_pairs), 2))
            pairs = new_pairs
            next_rebuild = step + 20

        N = len(rad)
        acc = np.zeros((N, 2))
        alp = np.zeros(N)
        cpar = 2.0 * ZETA * np.sqrt(K_N * mass)

        # ---------- 颗粒-颗粒 ----------
        if len(pairs):
            i, j = pairs[:, 0], pairs[:, 1]
            d = xy[j] - xy[i]
            dist = np.linalg.norm(d, axis=1)
            sumr = rad[i] + rad[j]
            hit = dist < sumr
            if np.any(hit):
                i, j, d, dist, sumr = i[hit], j[hit], d[hit], dist[hit], sumr[hit]
                tid = np.nonzero(hit)[0]
                nrm = d / dist[:, None]
                delta = sumr - dist
                vrel = vel[j] - vel[i]
                vn = np.sum(vrel * nrm, axis=1)
                mn = mass[i] * mass[j] / (mass[i] + mass[j])
                cn = 2.0 * ZETA * np.sqrt(K_N * mn)

                Fn = np.maximum(K_N * delta - cn * vn, 0.0)

                # 接触点速度要带自转，否则摩擦力矩只驱动自转、不受约束
                r_i = rad[i][:, None] * nrm
                r_j = -rad[j][:, None] * nrm
                vc = (vel[j] + omg[j][:, None] * np.stack([-r_j[:, 1], r_j[:, 0]], axis=1)
                      - vel[i] - omg[i][:, None] * np.stack([-r_i[:, 1], r_i[:, 0]], axis=1))
                vn_c = np.sum(vc * nrm, axis=1)
                vt = vc - vn_c[:, None] * nrm
                tang[tid] += vt * DT
                tvec = tang[tid] - np.sum(tang[tid] * nrm, axis=1)[:, None] * nrm
                tang[tid] = tvec
                tmag = np.linalg.norm(tvec, axis=1)
                cap = mu * Fn
                scale = np.where(tmag > 1e-12,
                                 np.minimum(1.0, cap / np.maximum(K_T * tmag, 1e-12)), 0.0)
                tang[tid] = tvec * scale[:, None]
                tdir = np.where(tmag[:, None] > 1e-12, tvec / np.maximum(tmag, 1e-12)[:, None], 0.0)
                Ftvec = (K_T * tmag * scale)[:, None] * tdir

                f_on_i = -Fn[:, None] * nrm + Ftvec
                np.add.at(acc, i, f_on_i / mass[i, None])
                np.add.at(acc, j, -f_on_i / mass[j, None])

                T_i = r_i[:, 0] * Ftvec[:, 1] - r_i[:, 1] * Ftvec[:, 0]
                T_j = rad[j] / rad[i] * T_i
                np.add.at(alp, i, T_i / (0.5 * mass[i] * rad[i] ** 2))
                np.add.at(alp, j, T_j / (0.5 * mass[j] * rad[j] ** 2))

                dw = omg[i] - omg[j]
                Ii = 0.5 * mass[i] * rad[i] ** 2
                Ij = 0.5 * mass[j] * rad[j] ** 2
                Ieff = Ii * Ij / (Ii + Ij)
                Mr = np.minimum(mu_roll * 0.5 * sumr * Fn,
                                Ieff * np.abs(dw) / DT)
                Mr = -np.sign(dw) * Mr
                np.add.at(alp, i, Mr / (0.5 * mass[i] * rad[i] ** 2))
                np.add.at(alp, j, -Mr / (0.5 * mass[j] * rad[j] ** 2))

        # ---------- 墙：地面、左墙、右墙，法向 n 与切向 t 显式给出 ----------
        walls = [
            (np.array([0.0, 1.0]), np.array([1.0, 0.0]),
             np.maximum(rad - xy[:, 1], 0.0), xy[:, 1] <= rad + 1e-9, 0),
            (np.array([1.0, 0.0]), np.array([0.0, 1.0]),
             np.maximum(rad - (xy[:, 0] - X0), 0.0), xy[:, 0] - rad <= X0 + 1e-9, 1),
            (np.array([-1.0, 0.0]), np.array([0.0, 1.0]),
             np.maximum(rad - (X1 - xy[:, 0]), 0.0), xy[:, 0] + rad >= X1 - 1e-9, 2),
        ]
        for nw, tw_dir, pen, msk, kk in walls:
            if not np.any(msk):
                continue
            idx = np.nonzero(msk)[0]
            r_w = -nw[None, :] * rad[idx][:, None]
            vn = vel[idx] @ nw
            Fnw = np.maximum(K_N * pen[idx] - cpar[idx] * vn, 0.0)
            # 接触点速度 = 平动 + ω×r
            vc = vel[idx] + omg[idx][:, None] * np.stack([-r_w[:, 1], r_w[:, 0]], axis=1)
            vt = vc @ tw_dir
            tw[idx, kk] += vt * DT
            xw = np.clip(tw[idx, kk], -mu * Fnw / K_T, mu * Fnw / K_T)
            tw[idx, kk] = xw
            F_t = (-K_T * xw)[:, None] * tw_dir[None, :]
            acc[idx] += nw[None, :] * (Fnw / mass[idx])[:, None]
            acc[idx] += F_t / mass[idx][:, None]
            T_w = r_w[:, 0] * F_t[:, 1] - r_w[:, 1] * F_t[:, 0]
            Iw = 0.5 * mass[idx] * rad[idx] ** 2
            Mw = -np.sign(omg[idx]) * np.minimum(mu_roll * rad[idx] * Fnw,
                                                 Iw * np.abs(omg[idx]) / DT)
            alp[idx] += (T_w + Mw) / (0.5 * mass[idx] * rad[idx] ** 2)

        acc[:, 1] -= GRAV
        vel += acc * DT
        omg += alp * DT
        omg *= 0.9995
        xy += vel * DT

        # 只做位置兜底，速度交给接触力
        xy[:, 1] = np.maximum(xy[:, 1], rad)
        xy[:, 0] = np.clip(xy[:, 0], X0 + rad, X1 - rad)
    return xy, rad


def repose_angle(xy, rad, binw=1.0):
    """按竖条取自由表面，去掉顶部圆角与两端坡脚后线性拟合。"""
    xs = np.arange(xy[:, 0].min() - rad.max(), xy[:, 0].max() + rad.max(), binw)
    surf = []
    for a in xs:
        m = (xy[:, 0] >= a) & (xy[:, 0] < a + binw)
        if np.any(m):
            surf.append((a + binw / 2, np.max(xy[m, 1] + rad[m])))
    surf = np.array(surf)
    apex = int(np.argmax(surf[:, 1]))
    top = surf[apex, 1]
    angs, fits = [], []
    for lo, hi in ((0, apex), (apex + 1, len(surf))):
        sel = surf[lo:hi, :]
        sel = sel[(sel[:, 1] > 0.25 * top) & (sel[:, 1] < 0.80 * top)]
        if len(sel) < 5:
            continue
        a1, b1 = np.polyfit(sel[:, 0], sel[:, 1], 1)
        angs.append(np.degrees(np.arctan(abs(a1))))
        fits.append((a1, b1, sel[:, 0].min(), sel[:, 0].max()))
    return (float(np.mean(angs)) if angs else 0.0), surf, fits


pile_a = run_pile(0.25, 0.10, seed=11)
ang_a, surf_a, fit_a = repose_angle(*pile_a)
pile_b = run_pile(0.60, 0.40, seed=23)
ang_b, surf_b, fit_b = repose_angle(*pile_b)
print("休止角 A = %.1f deg   B = %.1f deg" % (ang_a, ang_b))
print("top A %.2f  B %.2f" % (surf_a[:, 1].max(), surf_b[:, 1].max()))

fig, axs = plt.subplots(1, 2, figsize=(6.75, 3.05))
for ax, (xy, rad), fit, ang, name, mr in [
        (axs[0], pile_a[0:2], fit_a, ang_a, "摩擦系数 0.25", 0.10),
        (axs[1], pile_b[0:2], fit_b, ang_b, "摩擦系数 0.60", 0.40)]:
    ax.set_aspect("equal")
    ax.axis("off")
    ax.fill_between([X0, X1], [-1.2, -1.2], [0, 0], color="#E7E2D8", zorder=1, lw=0)
    for (x, y), r in zip(xy, rad):
        ax.add_patch(Circle((x, y), r, facecolor="#F2DFC0", edgecolor="#8E7248",
                            lw=0.45, zorder=3))
    ax.plot([X0, X1], [0, 0], color=INK, lw=1.5, zorder=4, solid_capstyle="butt")
    for a1, b1, xa, xb in fit:
        xx = np.array([xa, xb])
        ax.plot(xx, a1 * xx + b1, color=ACCENT, lw=1.4, ls=(0, (5, 2)), zorder=6)
    ax.set_xlim(X0 - 1.2, X1 + 1.2)
    ax.set_ylim(-1.3, 22)
    ax.text(0.02, 0.97, name, transform=ax.transAxes, ha="left", va="top",
            fontsize=9.4, color=INK)
    ax.text(0.02, 0.885, "滚动阻力系数 %.2f" % mr, transform=ax.transAxes, ha="left",
            va="top", fontsize=8.3, color=MUTED)
    ax.text(0.975, 0.97, "%.1f°" % ang, transform=ax.transAxes, ha="right", va="top",
            fontsize=13, color=ACCENT, weight="bold")

save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  粮仓效应：Janssen 公式
#   dσz/dz = ρb g − λ σz ,  λ = 2 μw K / R
#   σz(z) = (ρb g / λ)(1 − exp(−λ z))
# ============================================================
R = 0.15
RHOB = 1500.0
G = 9.81
KK = 0.50
Z = np.linspace(0, 3.0, 400)
MUS = [0.2, 0.4, 0.6]
COLS = [BLUE, ACCENT, GREEN]

fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.25))

ax = axs[0]
ax.plot(RHOB * G * Z / 1000, Z, color=FAINT, lw=1.2, ls=(0, (4, 2)),
        label="静水压力 $\\rho_b g z$")
for mu, c in zip(MUS, COLS):
    lam = 2 * mu * KK / R
    s = RHOB * G / lam * (1 - np.exp(-lam * Z)) / 1000
    ax.plot(s, Z, color=c, lw=1.6, label="$\\mu_w$ = %.1f" % mu)
ax.invert_yaxis()
ax.set_xlabel("竖向应力 $\\sigma_z$  (kPa)")
ax.set_ylabel("深度 $z$  (m)")
ax.set_xlim(0, 46)
ax.set_ylim(3.12, -0.06)
clean(ax, grid=True)
ax.legend(loc="lower right", handlelength=1.5, labelspacing=0.32, borderpad=0.15,
          bbox_to_anchor=(0.98, 0.02))

ax = axs[1]
H = np.linspace(0, 3.0, 400)
for mu, c in zip(MUS, COLS):
    lam = 2 * mu * KK / R
    s = RHOB * G / lam * (1 - np.exp(-lam * H)) / 1000
    ax.plot(H, s, color=c, lw=1.6)
    ax.axhline(RHOB * G / lam / 1000, color=c, lw=0.8, ls=(0, (2, 2)), alpha=0.55)
    ax.plot([1 / lam], [RHOB * G / lam * (1 - np.exp(-1)) / 1000], "o", ms=3.6,
            color=c, zorder=5)
ax.annotate("虚线为饱和压力\n圆点对应 $H=\\lambda^{-1}$", xy=(1.10, 11.6),
            xytext=(1.62, 7.4), fontsize=8.2, color=MUTED,
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=0.22"))
ax.set_xlabel("装料高度 $H$  (m)")
ax.set_ylabel("仓底压力 (kPa)")
ax.set_xlim(0, 3)
ax.set_ylim(0, 15.0)
clean(ax, grid=True)
ax.text(0.03, 0.95, "装料超过约 1 m 后压力几乎不再上升", transform=ax.transAxes,
        fontsize=8.2, color=MUTED, va="top")

save(fig, "01", "fig01-02")

lam4 = 2 * 0.4 * KK / R
print("lambda^-1 (mu=0.4) = %.3f m, 饱和压力 %.0f Pa" % (1 / lam4, RHOB * G / lam4))
