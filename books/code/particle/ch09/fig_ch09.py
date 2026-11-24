import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np

# fig09-01 -------------------------------------------------------------
def poisson_disk(n_target, d, rng, k=30):
    """Bridson 二维泊松盘采样。"""
    cell = d / np.sqrt(2)
    gw = int(np.ceil(1.0 / cell))
    grid = -np.ones((gw + 2, gw + 2), dtype=int)
    pts, active = [], []

    def ok(p):
        gi, gj = int(p[0] / cell), int(p[1] / cell)
        for di in range(max(0, gi - 2), min(gw, gi + 3)):
            for dj in range(max(0, gj - 2), min(gw, gj + 3)):
                idx = grid[di, dj]
                if idx >= 0 and np.hypot(pts[idx][0] - p[0], pts[idx][1] - p[1]) < d:
                    return False
        return True

    p0 = np.array([0.5, 0.5]) + rng.normal(0, 0.12, 2)
    pts.append(p0); grid[int(p0[0] / cell), int(p0[1] / cell)] = 0; active.append(0)
    while active and len(pts) < n_target:
        ai = rng.integers(len(active))
        i = active[ai]
        found = False
        for _ in range(k):
            ang = rng.random() * 2 * np.pi
            rad = d * (1 + rng.random())
            p = pts[i] + rad * np.array([np.cos(ang), np.sin(ang)])
            if not (0.035 < p[0] < 0.965 and 0.035 < p[1] < 0.965):
                continue
            if ok(p):
                pts.append(p)
                grid[int(p[0] / cell), int(p[1] / cell)] = len(pts) - 1
                active.append(len(pts) - 1)
                found = True
                break
        if not found:
            active.pop(ai)
    return np.array(pts)


def panel(ax, P, R, link, over=None):
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0.03, 0.03), 0.94, 0.94, fill=False, ec="#D6D3CB", lw=0.9, zorder=0))
    for p, r in zip(P, R):
        ax.add_patch(Circle(p, r, fc="#FCFCFB", ec="#C9C6BE", lw=0.45, zorder=1))
    n = len(P)
    d = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    iu = np.triu_indices(n, 1)
    dv = d[iu]
    sel = np.nonzero(dv < link * 2 * R.mean())[0]
    for s in sel:
        a, b = iu[0][s], iu[1][s]
        if over is not None and d[a, b] < (R[a] + R[b]):
            c, lw, al = ACCENT, 0.9, 0.9
        else:
            c, lw, al = SLATE, 0.7, 0.75
        ax.plot([P[a, 0], P[b, 0]], [P[a, 1], P[b, 1]], color=c, lw=lw, alpha=al,
                zorder=3, solid_capstyle="round")


rng = np.random.default_rng(11)

# 随机撒点
R0 = 0.0255
N1 = 300
A = np.column_stack([rng.uniform(0.05, 0.95, N1), rng.uniform(0.05, 0.95, N1)])
rA = np.full(N1, R0)

# 泊松盘：最小间距 2.05r
B = poisson_disk(300, 2.05 * R0, rng)
rB = np.full(len(B), R0)

# 重力沉降：沉积成层，层内交错排列并带抖动，顶面留出自由表面
rC_list, C_list = [], []
y = 0.03 + R0
row = 0
while len(C_list) < 210 and y < 0.95:
    r_row = R0 * rng.uniform(0.94, 1.06)
    dx = 2.04 * r_row
    phase = (row % 2) * 0.5 * dx
    x = 0.03 + r_row + phase + rng.uniform(-0.18, 0.18) * r_row
    while x < 0.97 - r_row:
        rr = R0 * rng.uniform(0.93, 1.07)
        C_list.append((x + rng.uniform(-0.12, 0.12) * r_row,
                       y + rng.uniform(-0.12, 0.12) * r_row))
        rC_list.append(rr)
        x += dx + rng.uniform(-0.15, 0.15) * r_row
    y += 1.90 * R0
    row += 1
C = np.array(C_list)
rC = np.array(rC_list)

fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.62))
for ax in axs:
    ax.axis("off")
panel(axs[0], A, rA, 1.15, over=ACCENT)
panel(axs[1], B, rB, 1.08, over=None)
panel(axs[2], C, rC, 1.02, over=None)
fig.subplots_adjust(wspace=0.05, left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "09", "fig09-01")

# fig09-02 -------------------------------------------------------------
p = np.logspace(np.log10(5e3), np.log10(3.0e5), 400)
pref = 1.0e3
Cc_l, e0_l = 0.22, 0.90
Cc_d, e0_d = 0.06, 0.62
L = np.log10(p / pref)
e_l = e0_l - Cc_l * L
e_d0 = e0_d - Cc_d * L
L_y = (e0_l - e0_d) / (Cc_l - Cc_d)          # 屈服点 1.75 -> 56 kPa
e_d = np.where(L < L_y, e_d0, e_l)

fig, ax = plt.subplots(figsize=(6.6, 3.5))
py_ = 1e3 * 10 ** L_y
mL = p <= py_
ax.semilogx(p[mL] / 1e3, e_l[mL], color=ACCENT, lw=1.9, zorder=3)
ax.semilogx(p / 1e3, e_d, color=BLUE, lw=1.9, zorder=4)
ax.set_xlim(4, 400)
ax.set_ylim(0.25, 0.90)
ax.set_xlabel("平均有效应力 p (kPa，对数刻度)")
ax.set_ylabel("孔隙比 e")
clean(ax, grid=True)
ax2 = ax.twinx()
ax2.set_ylim(1 / (1 + 0.90), 1 / (1 + 0.25))
ax2.set_ylabel("体积分数 φ")
ax2.spines["top"].set_visible(False)
for s in ("left", "bottom"):
    ax2.spines[s].set_visible(False)

pk = 50.0
ek_l = e0_l - Cc_l * np.log10(pk)
ek_d = e0_d - Cc_d * np.log10(pk)
ax.axvline(pk, color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.plot([pk], [ek_l], "o", ms=4.6, color=ACCENT, zorder=6,
        markerfacecolor="white", markeredgewidth=1.3)
ax.plot([pk], [ek_d], "o", ms=4.6, color=BLUE, zorder=6,
        markerfacecolor="white", markeredgewidth=1.3)

# 屈服点
py = pref * 10 ** L_y
ax.plot([py / 1e3], [e0_l - Cc_l * L_y], "o", ms=3.4, color=MUTED, zorder=6)
ax.annotate("屈服后并入同一条正常固结线",
            xy=(py / 1e3 * 1.02, e0_l - Cc_l * L_y), xytext=(70, 0.575),
            fontsize=8.2, color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7,
                            shrinkA=2, shrinkB=4))

label(ax, 4.6, 0.855, r"$e=e_0-C_c\,\log_{10}(p/1\,\mathrm{kPa})$", fs=9.0, color=INK, ha="left")
label(ax, pk * 1.13, 0.72, "p = 50 kPa", fs=8.4, color=MUTED, ha="left")

label(ax, 118, 0.845, "50 kPa 处的体积模量", fs=8.2, color=MUTED, ha="left")
label(ax, 118, 0.806, "松堆  0.8 MPa", fs=8.6, color=ACCENT, ha="left")
label(ax, 118, 0.772, "密堆  2.9 MPa", fs=8.6, color=BLUE, ha="left")

# 图例（左下空白区）
ax.plot([6.0, 8.4], [0.352, 0.352], color=ACCENT, lw=1.9)
label(ax, 9.1, 0.352, r"松堆  $e_0=0.90$，$C_c=0.22$", fs=8.4, color=ACCENT, ha="left")
ax.plot([6.0, 8.4], [0.310, 0.310], color=BLUE, lw=1.9)
label(ax, 9.1, 0.310, r"密堆  $e_0=0.62$，$C_c=0.06$", fs=8.4, color=BLUE, ha="left")
label(ax, 6.0, 0.271, "密堆为超固结：屈服压力之前斜率更小", fs=8.0, color=MUTED, ha="left")
fig.subplots_adjust(left=0.11, right=0.88, top=0.97, bottom=0.145)
save(fig, "09", "fig09-02")
