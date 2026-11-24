# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


def fig01_01():
    """模拟在一帧之内的位置：六个步骤围成一个回环。"""
    fig, ax = canvas(6.8, 3.0)
    names = ["几何表示", "离散化", "力的计算", "时间积分", "碰撞与约束", "交给渲染"]
    caps = ["网格 / 粒子\n/ 距离场", "节点 / 单元\n/ 采样点",
            "重力 / 弹性\n/ 压力", "显式 或\n隐式", "检测 与\n响应",
            "表面重建\n/ 光照"]
    fcs = [SOFT[1], SOFT[1], SOFT[0], SOFT[0], SOFT[0], SOFT[2]]
    x0, x1, gap = 0.035, 0.965, 0.026
    n = len(names)
    w = (x1 - x0 - gap * (n - 1)) / n
    y, h = 0.50, 0.20
    xs = []
    for i in range(n):
        x = x0 + i * (w + gap)
        box(ax, x, y, w, h, names[i], fc=fcs[i], fs=8.8)
        label(ax, x + w / 2, y - 0.045, caps[i], fs=8.0, color=MUTED, va="top")
        xs.append((x, x + w))
        if i:
            arrow(ax, (xs[i - 1][1] + 0.004, y + h / 2), (x - 0.004, y + h / 2),
                  color=FAINT, lw=1.1, ms=7)
    xa = (xs[2][0] + xs[2][1]) / 2
    xb = (xs[5][0] + xs[5][1]) / 2
    curve_arrow(ax, [(xb, y + h + 0.01), (xb, 0.88), (xa, 0.88), (xa, y + h + 0.01)],
                color=ACCENT, lw=1.1, ms=7)
    label(ax, (xa + xb) / 2, 0.838, "下一帧：n → n + 1", fs=8.2, color=ACCENT)
    bracket(ax, xs[0][0], xs[1][1], 0.20, "建模，只做一次", color=SLATE, fs=8.4, dy=-0.075)
    bracket(ax, xs[2][0], xs[4][1], 0.20, "求解，每一步都做", color=SLATE, fs=8.4, dy=-0.075)
    bracket(ax, xs[5][0], xs[5][1], 0.20, "呈现", color=SLATE, fs=8.4, dy=-0.075)
    save(fig, "01", "fig01-01")


def fig01_02():
    """一维自由落体：半隐式格式在三种步长下的位置，以及与解析解之差。"""
    g = 9.81
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.9, 3.05))
    t_end = 2.0
    tt = np.linspace(0, t_end, 400)
    ax1.plot(tt, 0.5 * g * tt ** 2, color=INK, lw=1.8, zorder=5,
             label=r"解析解  $\frac{1}{2}gt^{2}$")
    dts = [1 / 240, 1 / 60, 1 / 15]
    cols = [BLUE, ACCENT, PURPLE]
    for dt, c in zip(dts, cols):
        n = int(round(t_end / dt))
        v = np.zeros(n + 1)
        x = np.zeros(n + 1)
        for k in range(n):
            v[k + 1] = v[k] + g * dt
            x[k + 1] = x[k] + v[k + 1] * dt
        tn = np.arange(n + 1) * dt
        mk = max(1, n // 10)
        lab = r"半隐式  $\Delta t=1/%d$ s" % round(1 / dt)
        ax1.plot(tn, x, color=c, lw=1.0, ls="--", marker="o", ms=3.2,
                 markevery=mk, label=lab, zorder=3)
        ax2.plot(tn, (x - 0.5 * g * tn ** 2) * 1000, color=c, lw=1.3,
                 marker="o", ms=3.2, markevery=mk,
                 markeredgecolor="white", markeredgewidth=0.5)
    ax1.set_xlabel("时间 t (s)")
    ax1.set_ylabel("下落距离 x (m)")
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(0, 24.0)
    ax1.set_yticks(np.arange(0, 21, 5))
    ax1.legend(loc="upper left", fontsize=8.2, handlelength=1.6,
               borderaxespad=0.5, labelspacing=0.4)
    clean(ax1, grid=True)

    ax2.set_xlabel("时间 t (s)")
    ax2.set_ylabel("与解析解之差 (mm)")
    ax2.set_xlim(0, 2.0)
    ax2.set_ylim(-30, 760)
    ax2.axhline(0, color=FAINT, lw=1.0)
    clean(ax2, grid=True)
    ax2.annotate("偏差随时间线性增长，\n斜率正比于 $\\Delta t$",
                 xy=(1.55, 470), xytext=(0.35, 640), fontsize=8.2, color=INK,
                 ha="left", va="center",
                 arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9,
                                 shrinkA=2, shrinkB=3))
    fig.subplots_adjust(wspace=0.32)
    save(fig, "01", "fig01-02")


def fig01_03():
    """四类使用者在真实、速度、可控三个方向上的侧重（定性等级表）。"""
    fig, ax = canvas(6.9, 2.95)
    cols = ["真实", "速度", "可控"]
    rows = [
        ("游戏", ["中", "强", "强"], BLUE, "一帧十六毫秒，不能炸"),
        ("影视", ["强", "弱", "强"], PURPLE, "近景经得起看，听导演的"),
        ("工业", ["强", "弱", "弱"], ACCENT, "有实测数据，要报误差"),
        ("机器人", ["中", "强", "中"], GREEN, "成千上万个，还要能求导"),
    ]
    x0, y0, cw, ch, rh = 0.135, 0.72, 0.115, 0.135, 0.155
    # 列标题
    for j, c in enumerate(cols):
        label(ax, x0 + j * cw + cw / 2, y0 + 0.045, c, fs=9.4, weight="bold")
    for i, (nm, vals, c, note) in enumerate(rows):
        yy = y0 - (i + 1) * rh
        label(ax, x0 - 0.03, yy + ch / 2, nm, fs=9.2, color=c, ha="right",
              weight="bold")
        for j, v in enumerate(vals):
            xx = x0 + j * cw
            ax.add_patch(Rectangle((xx, yy), cw - 0.012, ch,
                                   facecolor={ "强": "#F3E3D6", "中": "#F7F7F5",
                                               "弱": "#FFFFFF" }[v],
                                   edgecolor="#E2DDD4", lw=0.8, zorder=1))
            if v == "强":
                ax.add_patch(Rectangle((xx, yy), 0.016, ch, facecolor=c,
                                       edgecolor="none", zorder=2))
            label(ax, xx + (cw - 0.012) / 2, yy + ch / 2, v, fs=10.2,
                  color=c if v == "强" else MUTED,
                  weight="bold" if v == "强" else "normal")
        # 右侧说明：与行同高
        ax.plot([x0 + 3 * cw + 0.012, x0 + 3 * cw + 0.030],
                [yy + ch / 2, yy + ch / 2], color=c, lw=1.0, zorder=3)
        label(ax, x0 + 3 * cw + 0.040, yy + ch / 2, note, fs=8.4, color=MUTED,
              ha="left")
    frame_note(ax, "定性等级，只表示相对侧重")
    save(fig, "01", "fig01-03")


if __name__ == "__main__":
    fig01_01()
    fig01_02()
    fig01_03()
