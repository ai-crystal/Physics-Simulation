import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

RHO_S = 2650.0      # 石英砂
RHO_F = 1000.0      # 水
MU = 1.0e-3         # 水在 20 摄氏度的动力黏度
G = 9.81


def cd_stokes(Re):
    return 24.0 / Re


def cd_schiller(Re):
    return 24.0 / Re * (1.0 + 0.15 * Re ** 0.687)


def cd_cgw(Re):
    return cd_schiller(Re) + 0.42 / (1.0 + 42500.0 / Re ** 1.16)


def terminal_velocity(d):
    """由力平衡解终端速度：0.5 Cd rho A v^2 = (rho_s-rho_f) V g"""
    v = (RHO_S - RHO_F) * G * d ** 2 / (18 * MU)      # 斯托克斯初值
    for _ in range(2000):
        Re = RHO_F * v * d / MU
        cd = cd_cgw(max(Re, 1e-6))
        v_new = np.sqrt(4.0 / 3.0 * d * (RHO_S - RHO_F) * G / (RHO_F * cd))
        if abs(v_new - v) < 1e-12 * max(v, 1e-12):
            v = v_new
            break
        v = 0.5 * v + 0.5 * v_new
    return v


def fig01():
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.05))

    # ---------------- 左：拖曳系数随雷诺数
    ax = axes[0]
    Re = np.logspace(-1, 5, 600)
    ax.loglog(Re, cd_stokes(Re), "--", color=FAINT, lw=1.2,
              label=r"斯托克斯 $24/\mathrm{Re}$")
    m = Re <= 800
    ax.loglog(Re[m], cd_schiller(Re[m]), "-", color=BLUE, lw=1.7,
              label="希勒-瑙曼（$\\mathrm{Re}\\leq 800$）")
    ax.loglog(Re, cd_cgw(Re), "-", color=ACCENT, lw=1.6,
              label="克利夫特-格雷斯-韦伯")
    ax.axhline(0.44, color=FAINT, lw=0.8, ls=":")
    ax.text(0.30, 0.235, "黏性区", fontsize=8, color=MUTED, ha="center")
    ax.text(30.0, 0.235, "过渡区", fontsize=8, color=MUTED, ha="center")
    ax.text(2.0e4, 0.235, "惯性区", fontsize=8, color=MUTED, ha="center")
    ax.set_xlabel(r"雷诺数 $\mathrm{Re}$")
    ax.set_ylabel(r"拖曳系数 $C_D$")
    ax.set_xlim(0.1, 1e5)
    ax.set_ylim(0.2, 300)
    clean(ax, grid=True)
    ax.legend(loc="upper right", handlelength=2.0, labelspacing=0.55)

    # ---------------- 右：石英砂在水中的终端速度
    ax = axes[1]
    d = np.logspace(-5, -1.7, 200)
    v = np.array([terminal_velocity(x) for x in d])
    ax.loglog(d, v, "-", color=BLUE, lw=1.8)
    vs = (RHO_S - RHO_F) * G * d ** 2 / (18 * MU)
    ax.loglog(d, vs, "--", color=FAINT, lw=1.1, label=r"斯托克斯标度 $d^{2}$")
    vn = np.sqrt(4.0 / 3.0 * d * (RHO_S - RHO_F) * G / (RHO_F * 0.44))
    ax.loglog(d, vn, ":", color=MUTED, lw=1.3, label=r"牛顿标度 $d^{1/2}$")
    ax.plot([2.5e-4], [terminal_velocity(2.5e-4)], "o", ms=4.6, mfc="white",
            mec=ACCENT, mew=1.2, zorder=5)
    ax.annotate("0.25 mm 砂", xy=(2.5e-4, terminal_velocity(2.5e-4)),
                xytext=(6.0e-4, 6.0e-3), fontsize=8, color=ACCENT, ha="left",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.7))
    ax.set_xlabel("粒径 $d$（m）")
    ax.set_ylabel("终端速度（m/s）")
    ax.set_xlim(2e-5, 3e-2)
    ax.set_ylim(1e-5, 3)
    clean(ax, grid=True)
    ax.legend(loc="lower right", handlelength=2.0, labelspacing=0.55)

    fig.subplots_adjust(wspace=0.33)
    save(fig, "08", "fig08-01")


def fig02():
    fig, ax = canvas(6.8, 3.35)

    # ---------------- 上排：固相
    box(ax, 0.03, 0.70, 0.25, 0.19, "固相状态\n$\\mathbf{v}_s,\\ \\phi,\\ \\mathbf{F}_p$", fs=9.0)
    box(ax, 0.36, 0.70, 0.26, 0.19, "有效应力\n$\\boldsymbol{\\sigma}'=\\boldsymbol{\\sigma}-p\\,\\mathbf{I}$", fs=9.0)
    box(ax, 0.70, 0.70, 0.27, 0.19, "固相更新\n$\\mathbf{v}_s,\\ \\phi$", fs=9.0)
    arrow(ax, (0.28, 0.795), (0.358, 0.795), color=INK, lw=1.1)
    arrow(ax, (0.62, 0.795), (0.698, 0.795), color=INK, lw=1.1)

    # ---------------- 下排：液相
    box(ax, 0.03, 0.10, 0.25, 0.19, "液相状态\n$\\mathbf{u}_f,\\ p$", fs=9.0)
    box(ax, 0.36, 0.10, 0.26, 0.19, "散度约束\n$\\nabla\\cdot[(1-\\phi)\\mathbf{u}_f]=-\\partial_t\\phi$", fs=8.6)
    box(ax, 0.70, 0.10, 0.27, 0.19, "压力投影\n$\\mathbf{u}_f,\\ p$", fs=9.0)
    arrow(ax, (0.28, 0.195), (0.358, 0.195), color=INK, lw=1.1)
    arrow(ax, (0.62, 0.195), (0.698, 0.195), color=INK, lw=1.1)

    # ---------------- 中间三条交换通道
    arrow(ax, (0.155, 0.30), (0.155, 0.69), color=ACCENT, lw=1.4, ms=9)
    label(ax, 0.175, 0.495, "孔隙压力 $p$", fs=8.6, color=ACCENT, ha="left")

    arrow(ax, (0.49, 0.69), (0.49, 0.30), color=TEAL, lw=1.4, ms=9)
    label(ax, 0.510, 0.495, "体积分数 $\\phi$", fs=8.6, color=TEAL, ha="left")

    arrow(ax, (0.835, 0.30), (0.835, 0.69), color=PURPLE, lw=1.4, ms=9, style="<|-|>")
    label(ax, 0.815, 0.495, "拖曳 $\\beta\\,(\\mathbf{u}_f-\\mathbf{v}_s)$", fs=8.6,
          color=PURPLE, ha="right")

    # ---------------- 边框与注
    ax.add_patch(FancyBboxPatch((0.012, 0.055), 0.976, 0.905,
                                boxstyle="round,pad=0.006,rounding_size=0.012",
                                fc="none", ec=GRID, lw=1.0, ls=(0, (4, 3)), zorder=0))
    label(ax, 0.03, 0.028, "同一时间步内交替：孔隙压力进固相本构，体积分数进流体散度，拖曳力双向等量反号。",
          fs=7.6, color=MUTED, ha="left")
    save(fig, "08", "fig08-02")


if __name__ == "__main__":
    fig01()
    fig02()
