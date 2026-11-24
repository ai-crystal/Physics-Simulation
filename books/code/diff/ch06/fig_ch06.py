"""第 6 章配图。

图 6-1  隐函数定理的求导结构（示意）
图 6-2  弹簧链的材料参数梯度：伴随与中心差分对拍（真实计算）
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ----------------------------------------------------------- 弹簧链模型
N_NODE = 12                      # 节点数，0 号固定
M_SPR  = 11                      # 弹簧数
MASS   = 0.05                    # 每个节点质量 kg
L0     = 1.0 / M_SPR             # 原长 m
GRAV   = 9.81
DT     = 1.0 / 240.0
N_STEP = 120
K_BASE = 300.0                   # 基准刚度 N/m
SOFT_IDX = [4, 5, 6]             # 被调软的弹簧（0 起）
SOFT_F = 0.35
ANGLE  = np.deg2rad(30.0)


def true_k():
    k = np.full(M_SPR, K_BASE)
    k[SOFT_IDX] *= SOFT_F
    return k


def positions(y):
    """自由节点位移 -> 全部节点坐标（0 号固定在原点）。"""
    p = np.zeros((N_NODE, 2))
    p[1:, :] = y.reshape(-1, 2)
    return p


def spring_force(k):
    """返回 F(y) 与 dF/dy（2m x 2m）。"""
    def F(y):
        p = positions(y)
        f = np.zeros((N_NODE, 2))
        for e in range(M_SPR):
            d = p[e + 1] - p[e]
            l = np.hypot(d[0], d[1]) + 1e-15
            mag = k[e] * (l - L0) / l
            f[e] += mag * d
            f[e + 1] -= mag * d
        f[1:, 1] -= MASS * GRAV
        return f[1:, :].reshape(-1)

    def dF(y):
        p = positions(y)
        A = np.zeros((2 * (N_NODE - 1), 2 * (N_NODE - 1)))
        for e in range(M_SPR):
            d = p[e + 1] - p[e]
            l = np.hypot(d[0], d[1]) + 1e-15
            c = 1.0 - L0 / l
            B = k[e] * c * np.eye(2) + k[e] * L0 / l ** 3 * np.outer(d, d)
            ia, ib = e - 1, e          # 自由节点编号（节点 0 无自由度）
            for (i, sgn_i) in ((ia, -1.0), (ib, 1.0)):
                if i < 0:
                    continue
                for (j, sgn_j) in ((ia, -1.0), (ib, 1.0)):
                    if j < 0:
                        continue
                    A[2 * i:2 * i + 2, 2 * j:2 * j + 2] += -sgn_i * sgn_j * B
        return A

    return F, dF


def step(y_old, v_old, k, F, dF, iters=8):
    """隐式欧拉一步：解 R(y)=0。"""
    y = y_old + DT * v_old
    for _ in range(iters):
        R = (MASS / DT ** 2) * (y - y_old - DT * v_old) - F(y)
        J = (MASS / DT ** 2) * np.eye(y.size) - dF(y)
        dy = np.linalg.solve(J, -R)
        y = y + dy
        if np.linalg.norm(dy) < 1e-13:
            break
    v = (y - y_old) / DT
    return y, v


def rollout(k):
    F, dF = spring_force(k)
    y = np.zeros((N_STEP + 1, 2 * (N_NODE - 1)))
    v = np.zeros_like(y)
    th = ANGLE
    y[0, 0::2] = np.arange(1, N_NODE) * L0 * np.sin(th)
    y[0, 1::2] = -np.arange(1, N_NODE) * L0 * np.cos(th)
    for n in range(N_STEP):
        y[n + 1], v[n + 1] = step(y[n], v[n], k, F, dF)
    return y


def loss(y_end, y_ref):
    d = (y_end - y_ref).ravel()
    return 0.5 * float(d @ d)


def adjoint(k, ys, y_ref):
    """式 6.5 与 6.9：返回 dL/dk。

    把一步写成三点形式 R_n(y_{n+1}, y_n, y_{n-1}) = 0,
    对 R_n 引入乘子 nu_n 并对 y_m 取稳定值，得到
        J_n^T nu_n = (2m/dt^2) nu_{n+1} - (m/dt^2) nu_{n+2} - g_{n+1}
    其中 g 是损失对状态的直接导数，J 就是前向牛顿迭代里的那个矩阵。
    """
    F, dF = spring_force(k)
    gN = (ys[-1] - y_ref).ravel().copy()
    dim = gN.size
    nu = np.zeros((N_STEP + 2, dim))
    grad = np.zeros(M_SPR)
    E = np.eye(dim)
    c1, c2 = 2 * MASS / DT ** 2, MASS / DT ** 2

    for n in range(N_STEP - 1, -1, -1):
        g = gN if n + 1 == N_STEP else 0.0
        J = (MASS / DT ** 2) * E - dF(ys[n + 1])
        nu[n] = np.linalg.solve(J, c1 * nu[n + 1] - c2 * nu[n + 2] - g)

        p = positions(ys[n + 1])
        for e in range(M_SPR):
            d = p[e + 1] - p[e]
            l = np.hypot(d[0], d[1]) + 1e-15
            u = (l - L0) / l * d               # dF/dk_e，见式 6.7
            ia, ib = e - 1, e
            na = nu[n][2 * ia:2 * ia + 2] if ia >= 0 else np.zeros(2)
            nb = nu[n][2 * ib:2 * ib + 2]
            grad[e] += (nb - na) @ u
    return grad


# ----------------------------------------------------------- 图 6-2
def fig_chain():
    k_true = true_k()
    k_init = np.full(M_SPR, K_BASE)
    k_init[[8, 9]] *= SOFT_F
    ref = rollout(k_true)
    y_ref = ref[-1].ravel()
    ys = rollout(k_init)
    L0v = loss(ys[-1].ravel(), y_ref)
    grad = adjoint(k_init, ys, y_ref)

    # 中心差分对拍
    H = 1e-3
    fd = np.zeros(M_SPR)
    for e in range(M_SPR):
        kp = k_init.copy(); kp[e] *= (1 + H)
        km = k_init.copy(); km[e] *= (1 - H)
        lp = loss(rollout(kp)[-1].ravel(), y_ref)
        lm = loss(rollout(km)[-1].ravel(), y_ref)
        fd[e] = (lp - lm) / (2 * H * k_init[e])

    err = np.max(np.abs(grad - fd)) / np.max(np.abs(fd))
    print("loss =", L0v)
    print("grad =", np.array2string(grad, precision=6))
    print("fd   =", np.array2string(fd, precision=6))
    print("max rel err =", err)

    fig, (ax1, ax2) = new(6.9, 3.15, ncols=2,
                          gridspec_kw={"wspace": 0.30, "left": 0.085,
                                       "right": 0.985, "bottom": 0.175, "top": 0.93})
    xs = np.arange(1, M_SPR + 1)

    # (a) 刚度分布
    ax1.step(xs, k_true, where="mid", color=ACCENT, lw=1.6)
    ax1.plot(xs, k_true, "s", ms=4.2, color=ACCENT, mec="white", mew=0.7, zorder=4)
    ax1.step(xs, k_init, where="mid", color=MUTED, lw=1.3, ls=(0, (4, 2)))
    ax1.set_xlabel("弹簧编号", fontsize=9.2, labelpad=3)
    ax1.set_ylabel("刚度 k（N/m）", fontsize=9.2)
    ax1.set_xlim(0.5, M_SPR + 0.5)
    ax1.set_ylim(0, 360)
    ax1.tick_params(labelsize=8.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(True, axis="y", color=GRID, lw=0.6)
    ax1.set_axisbelow(True)
    ax1.annotate("真值：第 5 到 7 根调软", xy=(5.6, 118), xytext=(2.1, 205),
                 fontsize=8.2, color=ACCENT, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                                 shrinkA=3, shrinkB=3))
    ax1.annotate("初值：软段放错了两根", xy=(9.5, 108), xytext=(6.2, 40),
                 fontsize=8.2, color=MUTED, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8,
                                 shrinkA=3, shrinkB=3))

    # (b) 梯度
    ax2.axhline(0, color=FAINT, lw=0.8, zorder=1)
    ax2.plot(xs, grad, "-", color=BLUE, lw=1.3, zorder=3)
    ax2.plot(xs, grad, "o", ms=4.6, color=BLUE, mec="white", mew=0.8, zorder=4)
    ax2.plot(xs, fd, "x", ms=5.6, mew=1.3, color=ACCENT, zorder=5)
    ax2.set_xlabel("弹簧编号", fontsize=9.2, labelpad=3)
    ax2.set_ylabel("损失对刚度的导数", fontsize=9.2)
    ax2.set_xlim(0.5, M_SPR + 0.5)
    ax2.tick_params(labelsize=8.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(True, axis="y", color=GRID, lw=0.6)
    ax2.set_axisbelow(True)
    ax2.text(0.03, 0.94, f"最大相对偏差 {err:.0e}", transform=ax2.transAxes,
             fontsize=8.0, color=MUTED, ha="left", va="top")
    ax2.plot([], [], "o", ms=4.6, color=BLUE, label="伴随")
    ax2.plot([], [], "x", ms=5.4, mew=1.3, color=ACCENT, label="中心差分")
    ax2.legend(loc="lower left", fontsize=8.2, handletextpad=0.5,
               borderaxespad=0.6)

    save(fig, "06", "fig06-02")


# ----------------------------------------------------------- 图 6-1
def fig_ift():
    fig, ax = canvas(6.8, 3.35)

    Y1, Y2, H = 0.740, 0.400, 0.150
    A0, AW = 0.070, 0.200
    B0, BW = 0.340, 0.300
    C0, CW = 0.710, 0.200

    box(ax, A0, Y1, AW, H, "上一帧\n$x^{n},\\ v^{n}$", fc="#EFF4FF", ec=BLUE, fs=8.8)
    box(ax, B0, Y1, BW, H,
        "牛顿迭代解 $\\mathbf{g}=\\mathbf{0}$\n$\\mathbf{J}=\\mathbf{M}/\\Delta t^{2}+\\mathbf{K}$",
        fc="white", ec=INK, fs=8.6)
    box(ax, C0, Y1, CW, H, "本帧\n$x^{n+1}$", fc="#EFF4FF", ec=BLUE, fs=8.8)

    box(ax, C0, Y2, CW, H, "上游梯度\n$\\bar{x}^{n+1}$", fc="#FDECE3", ec=ACCENT, fs=8.8)
    box(ax, B0, Y2, BW, H,
        "解 $\\mathbf{J}^{\\mathsf{T}}\\lambda=\\bar{x}^{n+1}$\n$\\mathbf{J}$ 已经分解过",
        fc="white", ec=ACCENT, fs=8.6)
    box(ax, A0, Y2, AW, H, "$\\lambda$ 传给\n上一步", fc="#FDECE3", ec=ACCENT, fs=8.8)

    box(ax, B0, 0.075, BW, 0.128,
        "$\\partial L/\\partial\\boldsymbol{\\theta}$ 累加：\n"
        "$-\\left(\\partial\\mathbf{g}/\\partial\\boldsymbol{\\theta}\\right)^{\\mathsf{T}}\\lambda$",
        fc="white", ec=GREEN, fs=8.4)

    yc1, yc2 = Y1 + H / 2, Y2 + H / 2
    arrow(ax, (A0 + AW + 0.004, yc1), (B0 - 0.004, yc1), color=BLUE, lw=1.1, ms=9)
    arrow(ax, (B0 + BW + 0.004, yc1), (C0 - 0.004, yc1), color=BLUE, lw=1.1, ms=9)
    arrow(ax, (C0 - 0.004, yc2), (B0 + BW + 0.004, yc2), color=ACCENT, lw=1.1, ms=9)
    arrow(ax, (B0 - 0.004, yc2), (A0 + AW + 0.004, yc2), color=ACCENT, lw=1.1, ms=9)

    xm = C0 + CW / 2
    arrow(ax, (xm, Y1 - 0.006), (xm, Y2 + H + 0.006), color=MUTED, lw=1.0, ms=9)
    label(ax, xm + 0.016, (Y1 + Y2 + H) / 2, "同一个矩阵\n转置后复用", fs=7.8,
          color=MUTED, ha="left", va="center")

    xg = B0 + BW / 2
    arrow(ax, (xg, Y2 - 0.006), (xg, 0.208), color=GREEN, lw=1.0, ms=9,
          ls=(0, (4, 2.2)))

    label(ax, 0.010, yc1, "前向", fs=8.8, color=BLUE, ha="left", weight="bold")
    label(ax, 0.010, yc2, "反向", fs=8.8, color=ACCENT, ha="left", weight="bold")
    label(ax, xg, 0.036, "参数只在这一步出现", fs=7.8, color=MUTED,
          ha="center", va="center")

    save(fig, "06", "fig06-01")


if __name__ == "__main__":
    fig_ift()
    fig_chain()
