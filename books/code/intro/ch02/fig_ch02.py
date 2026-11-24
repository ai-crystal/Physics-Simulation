# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


def fig02_01():
    """力学史时间线：每一个年份都是一次视角更换。"""
    fig, ax = canvas(6.9, 3.3)
    items = [
        (1687, "牛顿《原理》", 0.30),
        (1755, "欧拉方程", 0.16),
        (1788, "拉格朗日力学", -0.30),
        (1834, "哈密顿形式", 0.16),
        (1845, "纳维-斯托克斯", -0.16),
        (1883, "雷诺数", -0.30),
        (1964, "粒子网格法", 0.30),
        (2020, "可微与学习", -0.30),
    ]
    lo, hi = 1655, 2050
    y0 = 0.50
    ax.plot([0.045, 0.975], [y0, y0], color=INK, lw=1.2, zorder=2)
    for yr, nm, off in items:
        x = 0.06 + 0.90 * (yr - lo) / (hi - lo)
        end = y0 + off - 0.035 if off > 0 else y0 + off + 0.035
        ax.plot([x, x], [y0, end], color=FAINT, lw=0.7, zorder=1)
        ax.scatter([x], [y0], s=18, color=ACCENT, zorder=4,
                   edgecolor="white", linewidth=0.6)
        label(ax, x, y0 + off, str(yr), fs=8.6, color=ACCENT, weight="bold")
        dy = 0.078 if off > 0 else -0.078
        label(ax, x, y0 + off + dy, nm, fs=8.4, color=INK)
    label(ax, 0.978, y0 + 0.05, "年", fs=8.0, color=FAINT, ha="right")
    save(fig, "02", "fig02-01")


def shoot(k, v0=(30.0, 30.0), g=9.81, dt=2e-4):
    """RK4 积分质点在重力与二次阻力下的轨迹，返回落地前的采样点。"""
    def acc(v):
        sp = np.hypot(v[0], v[1])
        return np.array([-k * sp * v[0], -g - k * sp * v[1]])

    p = np.array([0.0, 0.0])
    v = np.array(v0, float)
    xs, ys = [0.0], [0.0]
    for _ in range(400000):
        k1v = acc(v); k1p = v
        k2v = acc(v + 0.5 * dt * k1v); k2p = v + 0.5 * dt * k1v
        k3v = acc(v + 0.5 * dt * k2v); k3p = v + 0.5 * dt * k2v
        k4v = acc(v + dt * k3v); k4p = v + dt * k3v
        v = v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        p = p + dt / 6.0 * (k1p + 2 * k2p + 2 * k3p + k4p)
        if p[1] < 0:
            break
        xs.append(p[0])
        ys.append(p[1])
    return np.array(xs), np.array(ys)


def fig02_02():
    """抛体轨迹：无阻力时是抛物线，有阻力时上升段与下降段不再对称。"""
    g = 9.81
    v0x, v0y = 30.0, 30.0
    fig, ax = plt.subplots(figsize=(6.9, 3.2))
    t = np.linspace(0, 2 * v0y / g, 400)
    ax.plot(v0x * t, v0y * t - 0.5 * g * t ** 2, color=INK, lw=1.9, zorder=6,
            label="无阻力（解析解）　射程 183 m")
    ax.axhline(0, color=FAINT, lw=1.0, zorder=1)
    for k, c in [(0.001, BLUE), (0.003, ACCENT), (0.006, PURPLE)]:
        xs, ys = shoot(k, (v0x, v0y), g)
        ax.plot(xs, ys, color=c, lw=1.5, zorder=5,
                label="k = %.3f 1/m　射程 %d m" % (k, round(xs[-1])))
        ax.scatter([xs[-1]], [0], s=16, color=c, zorder=7,
                   edgecolor="white", linewidth=0.6)
    label(ax, 100, 50.5, "上升段几乎重合\n下降段快速散开", fs=8.2, color=INK)
    ax.set_xlabel("水平距离 x (m)")
    ax.set_ylabel("高度 y (m)")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 57)
    ax.legend(loc="upper right", fontsize=8.0, handlelength=1.7,
              borderaxespad=0.5, labelspacing=0.35)
    clean(ax, grid=True)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.96, bottom=0.16)
    save(fig, "02", "fig02-02")


def fig02_03():
    """按物质类型分支的方法演化，年份为代表性工作。"""
    fig, ax = canvas(6.9, 3.70)
    heads = ["刚体", "可变形体", "流体", "颗粒与多相"]
    cols = [
        ["罚力与投影", "LCP  1994", "序列冲量  2005"],
        ["有限元  1987", "弹簧质点  1995", "PBD  2007"],
        ["PIC  1964", "FLIP  1986", "网格流体  1999"],
        ["DEM  1979", "MPM  2013", "积雪压实  2013"],
    ]
    cents = [0.135, 0.385, 0.635, 0.885]
    w, h = 0.205, 0.088
    ys = [0.855, 0.675, 0.500, 0.325]
    for cx, hd, col in zip(cents, heads, cols):
        box(ax, cx - w / 2, ys[0] - h / 2, w, h, hd, fc=SOFT[1], fs=9.4, weight="bold")
        for j, m in enumerate(col):
            y = ys[j + 1]
            box(ax, cx - w / 2, y - h / 2, w, h, m, fs=8.4,
                fc="white", ec=MUTED, ls="-")
            if j:
                arrow(ax, (cx, ys[j] - h / 2 - 0.004), (cx, y + h / 2 + 0.004),
                      color=FAINT, lw=1.0, ms=7)
        arrow(ax, (cx, ys[0] - h / 2 - 0.004), (cx, ys[1] + h / 2 + 0.004),
              color=FAINT, lw=1.0, ms=7)
        arrow(ax, (cx, ys[3] - h / 2 - 0.006), (cx, 0.190),
              color=FAINT, lw=1.0, ms=7, ls=(0, (3, 2)))
    band(ax, 0.035, 0.095, 0.930, 0.092, "", fc="#FBF7F0", ec=GRID)
    label(ax, 0.500, 0.141, "可微模拟 2019　·　图网络 2021：接在四支之上",
          fs=8.8, color=ACCENT)
    save(fig, "02", "fig02-03")


if __name__ == "__main__":
    fig02_01()
    fig02_02()
    fig02_03()
