import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 1-1
# 正问题与反问题的数据流（结构示意）。
def fig01():
    fig, ax = canvas(6.7, 3.55)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.plot([0.0, 1.0], [0.0, 1.0], alpha=0.0, lw=0.1)

    yf, yb = 0.715, 0.315
    hb, ht = 0.155, 0.15

    # 上排：正问题
    box(ax, 0.045, yf - ht / 2, 0.170, ht, r"参数 $\theta$", fc=SOFT[1], ec=BLUE, fs=9.4)
    box(ax, 0.285, yf - ht / 2, 0.200, ht, "求解器\n" + r"$\mathcal{S}$", fc="white", ec=INK, fs=9.4)
    box(ax, 0.555, yf - ht / 2, 0.200, ht, "轨迹\n" + r"$\mathbf{x}_{0:T}$", fc=SOFT[1], ec=BLUE, fs=9.4)

    arrow(ax, (0.217, yf), (0.283, yf), color=MUTED, lw=1.1)
    arrow(ax, (0.487, yf), (0.553, yf), color=MUTED, lw=1.1)

    # 下排：反问题
    box(ax, 0.100, yb - hb / 2, 0.200, hb, "更新\n" + r"$\theta\leftarrow\theta-\eta\nabla L$",
        fc=SOFT[3], ec=PURPLE, fs=9.0)
    box(ax, 0.360, yb - hb / 2, 0.195, hb, "梯度\n" + r"$\nabla_{\theta}L$",
        fc=SOFT[3], ec=PURPLE, fs=9.0)
    box(ax, 0.615, yb - hb / 2, 0.225, hb, "损失\n" + r"$L(\mathbf{x}_{0:T},\mathbf{x}^{*})$",
        fc="white", ec=INK, fs=9.0)
    box(ax, 0.875, yb - hb / 2, 0.105, hb, "观测\n" + r"$\mathbf{x}^{*}$",
        fc=SOFT[0], ec=ACCENT, fs=8.8)

    arrow(ax, (0.873, yb), (0.842, yb), color=MUTED, lw=1.1)
    arrow(ax, (0.613, yb), (0.557, yb), color=MUTED, lw=1.1)
    arrow(ax, (0.358, yb), (0.302, yb), color=MUTED, lw=1.1)

    # 轨迹 -> 损失（竖直）
    arrow(ax, (0.678, yf - ht / 2 - 0.006), (0.678, yb + hb / 2 + 0.006),
          color=MUTED, lw=1.1)
    label(ax, 0.691, (yf - ht / 2 + yb + hb / 2) / 2, "比对", fs=8.2, color=MUTED,
          ha="left")

    # 更新 -> 参数（闭环）
    arrow(ax, (0.132, yb + hb / 2 + 0.006), (0.132, yf - ht / 2 - 0.006),
          color=PURPLE, lw=1.2, ls=(0, (3, 2)))
    label(ax, 0.148, (yb + hb / 2 + yf - ht / 2) / 2, "下一轮", fs=8.2,
          color=PURPLE, ha="left")

    label(ax, 0.500, 0.930, "正问题：从参数出发，沿箭头算一遍", fs=9.0, color=INK)
    label(ax, 0.500, 0.185, "反问题：从观测出发，反向回传梯度，改完参数再算",
          fs=9.0, color=PURPLE)
    label(ax, 0.500, 0.058,
          "上排每跑一遍，才有一份损失；下排每走一圈，都要重跑上排",
          fs=8.2, color=FAINT)

    save(fig, "01", "fig01-01")


# ---------------------------------------------------------------- 图 1-2
# 一维参数辨识的损失景观（真实计算：带阻尼单摆，两种观测窗口）。
def fig02():
    g, L = 9.81, 1.0
    c_true = 0.9
    dt = 0.001
    T_short, T_long = 0.3, 4.0
    n_obs = 60

    def sim(c, t_end):
        ns = int(round(t_end / dt))
        th, om = 1.0, 0.0
        out = np.empty(ns + 1)
        out[0] = th
        for i in range(ns):
            def f(a, b):
                return b, -c * b - (g / L) * np.sin(a)
            k1 = f(th, om)
            k2 = f(th + 0.5 * dt * k1[0], om + 0.5 * dt * k1[1])
            k3 = f(th + 0.5 * dt * k2[0], om + 0.5 * dt * k2[1])
            k4 = f(th + dt * k3[0], om + dt * k3[1])
            th += dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            om += dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            out[i + 1] = th
        return out

    cs = np.linspace(0.05, 3.0, 300)

    def landscape(t_end):
        ns = int(round(t_end / dt))
        idx = np.linspace(0, ns, n_obs).astype(int)
        rng = np.random.default_rng(5)
        obs = sim(c_true, t_end)[idx] + 0.01 * rng.standard_normal(n_obs)
        loss = np.array([np.mean((sim(c, t_end)[idx] - obs) ** 2) for c in cs])
        return loss / loss.min(), obs, idx

    n_s, obs_s, idx_s = landscape(T_short)
    n_l, obs_l, idx_l = landscape(T_long)
    c_s, c_l = cs[np.argmin(n_s)], cs[np.argmin(n_l)]

    fig = plt.figure(figsize=(6.8, 3.25))
    ax = fig.add_axes([0.088, 0.175, 0.485, 0.775])
    ax.semilogy(cs, n_l, color=ACCENT, lw=1.7, zorder=4)
    ax.semilogy(cs, n_s, color=BLUE, lw=1.6, ls=(0, (5, 2)), zorder=4)
    ax.axvline(c_true, color=FAINT, lw=0.9, ls=(0, (2, 2)), zorder=1)
    label(ax, c_true, 1.9e3, r"真值 $c^{*}=0.9$", fs=8.2, color=MUTED,
          bbox=dict(facecolor="white", edgecolor="none", pad=1.6))
    label(ax, 2.55, 7.4, "0.3 s", fs=8.6, color=BLUE, ha="left")
    label(ax, 2.55, 780, "4 s", fs=8.6, color=ACCENT, ha="left")
    ax.set_xlabel(r"阻尼系数 $c$ (s$^{-1}$)", labelpad=2)
    ax.set_ylabel(r"归一化损失 $L/L_{\min}$", labelpad=2)
    ax.set_xlim(0, 3.05)
    ax.set_ylim(1.0, 3.0e3)
    ax.tick_params(labelsize=8.8, length=2.8, pad=2)
    clean(ax, grid=True)

    ax2 = fig.add_axes([0.665, 0.175, 0.320, 0.775])
    ax2.axvspan(0, T_short, color=GOLD, alpha=0.13, lw=0, zorder=1)
    ax2.plot(np.linspace(0, T_long, 4001), sim(c_true, T_long),
             color=ACCENT, lw=1.4, zorder=4)
    ax2.plot(np.linspace(0, T_short, 301), sim(c_true, T_short),
             color=ACCENT, lw=2.0, zorder=5)
    ax2.plot(np.linspace(0, T_long, 4001), sim(0.20, T_long),
             color=BLUE, lw=1.2, zorder=3)
    ax2.plot(np.linspace(0, T_long, 4001), sim(2.60, T_long),
             color=GREEN, lw=1.2, zorder=3)
    ax2.plot(np.linspace(0, T_long, 4001)[idx_l], obs_l, "o", ms=1.5,
             color=FAINT, zorder=2)
    ax2.axhline(0, color=GRID, lw=0.8, zorder=1)
    ax2.set_xlabel("时间 t (s)", labelpad=2)
    ax2.set_ylabel(r"摆角 $\theta$ (rad)", labelpad=2)
    ax2.set_xlim(0, T_long)
    ax2.set_ylim(-1.45, 1.30)
    ax2.tick_params(labelsize=8.8, length=2.8, pad=2)
    clean(ax2, grid=True)
    label(ax2, 0.10, -1.33, "阴影：短窗只用这一段", fs=7.6, color=ACCENT,
          ha="left")
    for x0, y0, t, cl in [(0.02, 0.0, r"$c=0.90$", ACCENT),
                          (0.0, 0.0, r"$c=0.20$", BLUE),
                          (0.0, 0.0, r"$c=2.60$", GREEN)]:
        pass
    h = [Line2D([], [], color=ACCENT, lw=1.5),
         Line2D([], [], color=BLUE, lw=1.2),
         Line2D([], [], color=GREEN, lw=1.2),
         Line2D([], [], color=FAINT, lw=0, marker="o", ms=2.4)]
    ax2.legend(h, [r"$c=0.90$（真值）", r"$c=0.20$", r"$c=2.60$", "观测"],
               loc="upper right", fontsize=7.5, handlelength=1.5,
               labelspacing=0.3, borderaxespad=0.35)

    save(fig, "01", "fig01-02")
    print("c_short=%.3f  c_long=%.3f  L_short(3.0)/Lmin=%.1f  L_long(3.0)/Lmin=%.0f"
          % (c_s, c_l, n_s[-1], n_l[-1]))


if __name__ == "__main__":
    fig01()
    fig02()
