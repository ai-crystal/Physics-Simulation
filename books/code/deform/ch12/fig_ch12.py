"""第 12 章配图。

图 12-1  能量漂移（三种积分器，真实模拟）+ 收敛阶（真实拟合斜率）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ----------------------------------------------------------------- 模型
G, M, L0, N = 9.81, 0.1, 0.1, 8          # 重力、节点质量、自然长度、节数
K = 1500.0                                # 弹簧刚度 N/m
C = 1.5                                   # 粘性阻尼 N·s/m（右图用）


def forces(x, v, c=0.0):
    f = np.zeros_like(x)
    f[:, 1] -= M * G
    for i in range(N):
        d = x[i + 1] - x[i]
        ln = np.linalg.norm(d)
        fh = K * (ln - L0) * d / ln
        f[i + 1] -= fh
        f[i] += fh
    f -= c * v
    f[0] = 0.0                            # 顶端固定
    return f


def init():
    x = np.zeros((N + 1, 2))
    for i in range(N + 1):
        x[i] = [0.03 * i * i / N, -i * L0]      # 初始横向弓形 3 cm
    return x, np.zeros((N + 1, 2))


def energy(x, v):
    ke = 0.5 * M * np.sum(v[1:] ** 2)
    pe = 0.0
    for i in range(N):
        pe += 0.5 * K * (np.linalg.norm(x[i + 1] - x[i]) - L0) ** 2
    return ke + pe + np.sum(M * G * x[1:, 1])


def step_explicit(x, v, dt):
    f = forces(x, v)
    x = x + dt * v
    v = v + dt * f / M
    x[0] = 0.0; v[0] = 0.0
    return x, v


def step_semi(x, v, dt, c=0.0):
    f = forces(x, v, c)
    v = v + dt * f / M
    v[0] = 0.0
    x = x + dt * v
    x[0] = 0.0
    return x, v


def step_backward(x, v, dt, c=0.0):
    """后向 Euler：解 x_{n+1} = x_n + dt v_{n+1}，牛顿迭代 + 数值雅可比。"""
    xn = x + dt * v
    xn[0] = 0.0
    dofs = [(i, d) for i in range(1, N + 1) for d in (0, 1)]
    for _ in range(40):
        vn = (xn - x) / dt
        f = forces(xn, vn, c)
        r = (xn - x - dt * v - dt * dt * f / M)[1:].ravel()
        if np.abs(r).max() < 1e-14:
            break
        J = np.zeros((r.size, r.size))
        eps = 1e-7
        for a, (i, d) in enumerate(dofs):
            xp = xn.copy()
            xp[i, d] += eps
            fp = forces(xp, (xp - x) / dt, c)
            rp = (xp - x - dt * v - dt * dt * fp / M)[1:].ravel()
            J[:, a] = (rp - r) / eps
        dx = np.linalg.solve(J, -r)
        for a, (i, d) in enumerate(dofs):
            xn[i, d] += dx[a]
    vn = (xn - x) / dt
    vn[0] = 0.0
    xn[0] = 0.0
    return xn, vn


def step_rk4(x, v, dt, c=0.0):
    def dv(a, b):
        return b, forces(a, b, c) / M
    a1, b1 = dv(x, v)
    a2, b2 = dv(x + dt / 2 * a1, v + dt / 2 * b1)
    a3, b3 = dv(x + dt / 2 * a2, v + dt / 2 * b2)
    a4, b4 = dv(x + dt * a3, v + dt * b3)
    x2 = x + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
    v2 = v + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    x2[0] = 0.0; v2[0] = 0.0
    return x2, v2


# ----------------------------------------------------------------- 左：能量漂移
T, DT = 6.0, 1.0 / 240.0
STEPS = int(round(T / DT))
x0, v0 = init()
E0 = energy(x0, v0)

RUNS = [("显式 Euler", step_explicit, ACCENT, "-", 2.6),
        ("半隐式 Euler", step_semi, BLUE, "-", 0.9),
        ("后向 Euler", step_backward, GREEN, "--", 1.5)]

fig, (ax1, ax2) = new(6.85, 3.55, ncols=2,
                      gridspec_kw=dict(width_ratios=[1.12, 1.0]))
fig.subplots_adjust(wspace=0.30)

YLO, YHI = -0.135, 0.06
drift = {}
for name, st, col, ls, lw in RUNS:
    x, v = x0.copy(), v0.copy()
    ts, es = [0.0], [0.0]
    for s in range(STEPS):
        x, v = st(x, v, DT)
        e = (energy(x, v) - E0) / abs(E0)
        ts.append((s + 1) * DT)
        es.append(e)
        if not np.isfinite(e) or e > 40:
            break
    ts, es = np.array(ts), np.array(es)
    drift[name] = es
    keep = es <= YHI
    ax1.plot(ts[keep], es[keep], ls=ls, lw=lw, color=col,
             label=name, solid_capstyle="round")
    if not keep.all():
        k = np.argmax(~keep)
        ax1.annotate("", xy=(ts[max(k - 1, 1)], YHI * 0.96),
                     xytext=(0.34, 0.036),
                     arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0,
                                     connectionstyle="arc3,rad=-0.18"))

ax1.axhline(0.0, color=FAINT, lw=0.8)
ax1.set_xlim(0.0, 6.0)
ax1.set_ylim(YLO, YHI)
ax1.set_xlabel("时间 / s")
ax1.set_ylabel("能量相对变化 $(E-E_0)/|E_0|$")
ax1.grid(True, color=GRID, lw=0.7)
ax1.set_axisbelow(True)
clean(ax1)
ax1.legend(loc="center right", bbox_to_anchor=(1.0, 0.34), handlelength=1.9,
           borderpad=0.3, labelspacing=0.35, fontsize=8.6)

ax1.text(0.30, 0.048, "0.06 s 时已是 20 倍，继续指数增长",
         fontsize=8.2, color=ACCENT, ha="left", va="bottom")
ax1.text(2.05, 0.030, "在 2% 带内振荡，6 s 不漂移", fontsize=8.2, color=BLUE,
         ha="left", va="bottom")
ax1.text(3.35, -0.115, "6 s 掉 10.7%", fontsize=8.2, color=GREEN,
         ha="left", va="bottom")

# ----------------------------------------------------------------- 右：收敛阶
def run(dt, T, st):
    x, v = x0.copy(), v0.copy()
    for _ in range(int(round(T / dt))):
        x, v = st(x, v, dt, C)
    return x


T2 = 1.0
REF = run(1 / 20000.0, T2, step_rk4)
SCALE = np.linalg.norm((REF - x0)[1:])
DTS = np.array([1 / 240, 1 / 480, 1 / 960, 1 / 1920])

ORDER = [("半隐式 Euler", step_semi, BLUE, "o"),
         ("后向 Euler", step_backward, GREEN, "s"),
         ("RK4", step_rk4, PURPLE, "^")]
slopes = {}
for name, st, col, mk in ORDER:
    errs = []
    for dt in DTS:
        u = run(dt, T2, st)
        errs.append(np.linalg.norm((u - REF)[1:]) / SCALE)
    errs = np.array(errs)
    p = np.polyfit(np.log(DTS), np.log(errs), 1)[0]
    slopes[name] = p
    ax2.loglog(DTS, errs, ls="-", lw=1.2, color=col, marker=mk, ms=4.0,
               mfc="white", mew=1.0, label=f"{name}（斜率 {p:.2f}）")

ax2.set_xlabel("步长 $\\Delta t$ / s")
ax2.set_ylabel("末态位移相对误差")
ax2.invert_xaxis()
ax2.grid(True, which="major", color=GRID, lw=0.7)
ax2.set_axisbelow(True)
ax2.set_xticks(DTS)
ax2.set_xticklabels(["1/1920", "1/960", "1/480", "1/240"])
ax2.minorticks_off()
ax2.legend(loc="upper right", handlelength=1.6, borderpad=0.3,
           labelspacing=0.35, fontsize=8.4, bbox_to_anchor=(1.02, 0.99))
ax2.set_ylim(5e-10, 1e-1)
clean(ax2)

save(fig, "12", "fig12-01")

# ----------------------------------------------------------------- 诊断
print("E0 =", round(E0, 4), "J")
for k, v in drift.items():
    print(f"{k:12s} 末值 {v[-1]:+.4f}  范围 [{v.min():+.4f}, {v.max():+.4f}]")
_e = np.array(drift["显式 Euler"])
_t20 = next((i * DT for i, e in enumerate(_e) if e > 20), float("nan"))
print("显式 Euler 涨到 20 倍的时刻:", round(float(_t20), 4), "s")
print("显式 Euler 越界时刻:",
      round(float(np.array([0.0])[0]) + next((i * DT for i, e in
            enumerate(drift["显式 Euler"]) if e > 0.06), float("nan")), 4), "s")
for k, v in slopes.items():
    print(f"{k:12s} 拟合斜率 {v:.3f}")
