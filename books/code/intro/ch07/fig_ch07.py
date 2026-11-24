import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 图 7-1
def fig01():
    fig, ax = canvas(6.7, 3.9, (0, 1), (0, 1))
    x, w, h = 0.055, 0.40, 0.108
    ys = [0.905, 0.762, 0.619, 0.476, 0.333, 0.190]
    items = [
        ("速度场 $\\mathbf{u}^{n}$、烟密度、温度", PAPER, INK),
        ("半拉格朗日平流", "white", BLUE),
        ("加重力、浮力、粘性", "white", BLUE),
        ("解压力泊松方程", "white", ACCENT),
        ("投影，减掉压力梯度", "white", ACCENT),
        ("标量场按新速度平流", "white", GREEN),
    ]
    sub = ["上一帧的状态", "沿迹线回溯再插值",
           "得到临时速度 $\\mathbf{u}^{*}$", "全场同时满足不可压",
           "恢复 $\\nabla\\cdot\\mathbf{u}=0$", "交给渲染或下一帧"]

    for i, (t, fc, ec) in enumerate(items):
        box(ax, x, ys[i] - h / 2, w, h, "", fc=fc, ec=ec, lw=1.2)
        label(ax, x + 0.022, ys[i] + 0.021, t, fs=9.2, ha="left", color=INK)
        label(ax, x + 0.022, ys[i] - 0.025, sub[i], fs=8.0, ha="left", color=MUTED)
        if i:
            arrow(ax, (x + w / 2, ys[i - 1] - h / 2 - 0.004),
                  (x + w / 2, ys[i] + h / 2 + 0.004), color=FAINT, lw=1.1, ms=7)

    # 右侧注记
    notes = [
        (ys[1], BLUE, "耗散：每步插值\n等于一次低通滤波"),
        (ys[2], BLUE, "此时散度不为零"),
        (ys[3], ACCENT, "全局耦合，占一帧\n一半以上的时间"),
        (ys[4], ACCENT, "水面所在格子\n取相对压力为零"),
    ]
    for y, c, txt in notes:
        ax.plot([x + w + 0.012, 0.505], [y, y], color=c, lw=0.7, ls=(0, (3, 2)), zorder=1)
        ax.text(0.515, y, txt, fontsize=8.0, color=c, va="center", ha="left", linespacing=1.5)

    # 底部注记
    ax.plot([x + w / 2, x + w / 2], [ys[5] - h / 2 - 0.004, 0.075],
            color=GREEN, lw=0.9, ls=(0, (3, 2)))
    label(ax, x + w / 2, 0.05, "固壁与自由表面的边界条件在压力步里生效", fs=8.0, color=GREEN)
    save(fig, "07", "fig07-01")


# ---------------------------------------------------------------- 图 7-2
def fig02():
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 2.9),
                             gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.24))

    # 左：核函数形状（真实公式）
    ax = axes[0]
    r = np.linspace(0, 2.02, 400)
    h = 1.0
    q = r / h
    sigma = 10.0 / (7.0 * np.pi * h * h)
    Wc = np.where(q < 1, sigma * (1 - 1.5 * q**2 + 0.75 * q**3),
                  sigma * 0.25 * np.maximum(2 - q, 0)**3)
    Wc = np.where(q < 2, Wc, 0.0)
    k = 315.0 / (64.0 * np.pi * h**9)
    W6 = np.where(r < h, k * (h * h - r * r)**3, 0.0)
    ks = -45.0 / (np.pi * h**6)
    dWs = np.where(r < h, np.abs(ks * (h - r)**2), 0.0)

    ax.plot(r, Wc / Wc.max(), color=BLUE, lw=1.6, label="三次样条核")
    ax.plot(r, W6 / W6.max(), color=ACCENT, lw=1.6, label="poly6 核")
    ax.plot(r, dWs / dWs.max(), color=GREEN, lw=1.4, ls="--", label="spiky 的梯度模")
    ax.axvline(1.0, color=FAINT, lw=0.8, ls=":")
    ax.axvline(2.0, color=FAINT, lw=0.8, ls=":")
    clean(ax, grid=True)
    ax.set_xlim(0, 2.15)
    ax.set_ylim(-0.02, 1.24)
    ax.set_xlabel("$r/h$")
    ax.set_ylabel("归一化后的值")
    ax.set_xticks([0, 0.5, 1, 1.5, 2])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(loc="upper right", fontsize=8.0, handlelength=1.6,
              bbox_to_anchor=(1.02, 1.03))
    label(ax, 1.03, 0.14, "$r=h$", fs=8.0, color=MUTED, ha="left")
    label(ax, 1.97, 0.14, "$r=2h$", fs=8.0, color=MUTED, ha="right")

    # 右：邻居示意
    ax = axes[1]
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.55, 2.55)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Circle((0, 0), 2.0, fill=False, ec=FAINT, lw=1.0, ls="--"))
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec=GRID, lw=1.0, ls=":"))
    rng = np.random.default_rng(7)
    pts = []
    while len(pts) < 30:
        p = rng.uniform(-1.95, 1.95, 2)
        if not (0.35 < np.hypot(*p) < 1.95):
            continue
        if p[0] > 0.25 and -0.20 < p[1] < 0.55:      # 给 2h 的标注留出空带
            continue
        pts.append(p)
    for px, py in pts:
        rr = np.hypot(px, py)
        if rr < 1:
            wgt = 1 - 1.5 * rr**2 + 0.75 * rr**3
        else:
            wgt = 0.25 * (2 - rr)**3
        wgt = float(np.clip(wgt, 0.0, 1.0))
        ax.add_patch(Circle((px, py), 0.070 + 0.060 * wgt,
                            fc=BLUE, ec="none", alpha=0.22 + 0.60 * wgt, zorder=3))
    # 范围外的粒子：不贡献
    for px, py in [(-2.25, 0.85), (2.30, -0.85), (0.55, 2.42), (-2.32, -1.55)]:
        ax.add_patch(Circle((px, py), 0.072, fc=LIGHT, ec=FAINT, lw=0.8, zorder=3))
    ax.add_patch(Circle((0, 0), 0.135, fc=ACCENT, ec="white", lw=1.0, zorder=5))
    label(ax, 0.0, -0.004, "$i$", fs=8.2, color="white", z=6)
    arrow(ax, (0.16, 0.0), (1.94, 0.0), color=MUTED, lw=0.9, ms=7, ls=(0, (4, 2)))
    label(ax, 1.10, 0.16, "$2h$", fs=8.6, color=MUTED, ha="left")
    label(ax, -2.55, 2.36, "点越大，这个粒子对 $i$ 的核值越大", fs=8.0, color=MUTED, ha="left")
    label(ax, -2.55, -2.46, "浅色：落在 $2h$ 之外，不参与求和", fs=8.0, color=FAINT, ha="left")
    save(fig, "07", "fig07-02")


# ---------------------------------------------------------------- 图 7-3
def fig03():
    fig, ax = canvas(6.6, 2.9, (0, 1), (0, 1))
    rows = ["欧拉网格", "SPH", "FLIP / APIC", "MPM"]
    cols = ["大变形适应", "细节保留", "鲁棒性", "单帧成本低"]
    score = [[1, 2, 3, 2],
             [2, 3, 1, 3],
             [3, 3, 2, 1],
             [3, 2, 3, 1]]
    x0, y0 = 0.335, 0.74
    dx, dy = 0.152, 0.175
    for j, c in enumerate(cols):
        label(ax, x0 + j * dx, y0 + 0.125, c, fs=8.8, color=INK)
    ax.plot([x0 - 0.075, x0 + 3 * dx + 0.075], [y0 + 0.070, y0 + 0.070],
            color=GRID, lw=0.9)
    for i, rname in enumerate(rows):
        y = y0 - i * dy
        label(ax, x0 - 0.085, y, rname, fs=9.0, color=INK, ha="right")
        ax.plot([0.175, 0.955], [y - dy / 2, y - dy / 2], color="#F1F3F5", lw=0.8, zorder=0)
        for j in range(4):
            for k in range(4):
                filled = k < score[i][j]
                ax.plot([x0 + j * dx + (k - 1.5) * 0.0295], [y], "o",
                        ms=4.6, mfc=ACCENT if filled else "white",
                        mec=ACCENT if filled else GRID, mew=0.8, zorder=3)
    label(ax, 0.07, 0.045, "定性示意，只表示方法之间的相对倾向，不是实测量化得分", fs=8.0,
          color=FAINT, ha="left")
    save(fig, "07", "fig07-03")


fig01()
fig02()
fig03()
