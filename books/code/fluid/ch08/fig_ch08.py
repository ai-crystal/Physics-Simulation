import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np


# ================================================================ 图 8-1
# 传递流程示意：前两步共用，最后一步分成 PIC（覆盖）与 FLIP（叠加）。
fig, axs = plt.subplots(1, 2, figsize=(6.9, 3.35),
                        gridspec_kw=dict(width_ratios=[1.42, 1.0], wspace=0.18))
ax = axs[0]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

box(ax, 0.04, 0.815, 0.92, 0.125, "粒子：质量 $m_p$、位置 $\\mathbf{x}_p$、速度 $\\mathbf{v}_p$",
    fc="white", ec=INK, fs=8.5)
box(ax, 0.04, 0.605, 0.92, 0.125, "P2G：按权重把质量与动量累加到格点",
    fc="white", ec=INK, fs=8.5)
box(ax, 0.04, 0.395, 0.92, 0.125, "网格：加外力、解压力、投影，得 $\\mathbf{v}^{n+1}$",
    fc="white", ec=INK, fs=8.5)
arrow(ax, (0.50, 0.815), (0.50, 0.735), color=MUTED, lw=1.0)
arrow(ax, (0.50, 0.605), (0.50, 0.525), color=MUTED, lw=1.0)

box(ax, 0.04, 0.175, 0.43, 0.125, "PIC：$\\mathbf{v}_p\\leftarrow\\tilde{\\mathbf{v}}_p$",
    fc="#EFF4FF", ec=BLUE, fs=8.8, tc=BLUE)
box(ax, 0.53, 0.175, 0.43, 0.125, "FLIP：$\\mathbf{v}_p\\leftarrow\\mathbf{v}_p+\\Delta\\tilde{\\mathbf{v}}_p$",
    fc="#FDF2E9", ec=ACCENT, fs=8.8, tc=ACCENT)
arrow(ax, (0.31, 0.390), (0.24, 0.305), color=BLUE, lw=1.0, rad=-0.15)
arrow(ax, (0.69, 0.390), (0.76, 0.305), color=ACCENT, lw=1.0, rad=0.15)

ax.text(0.255, 0.105, "旧速度被丢掉", color=MUTED, fontsize=8.0, ha="center", va="center")
ax.text(0.745, 0.105, "旧速度保留", color=MUTED, fontsize=8.0, ha="center", va="center")

# 右图：同一格子里两个粒子的切向速度
ax = axs[1]
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
label(ax, 0.52, 0.955, "同一格内两个粒子", fs=8.6, color=INK)
label(ax, 0.52, 0.895, "的切向速度", fs=8.6, color=INK)

rows = [("原始", 1.00, 0.55, INK), ("PIC 之后", 0.78, 0.78, BLUE),
        ("FLIP 之后", 0.90, 0.70, ACCENT)]
for k, (name, a1, a2, col) in enumerate(rows):
    y = 0.68 - k * 0.235
    label(ax, 0.04, y + 0.085, name, fs=8.2, color=col, ha="left")
    ax.plot([0.42, 0.42], [y - 0.015, y + 0.175], color=FAINT, lw=0.9, zorder=1)
    arrow(ax, (0.42, y + 0.115), (0.42 + a1 * 0.46, y + 0.115), color=col, lw=1.7, ms=8)
    arrow(ax, (0.42, y + 0.025), (0.42 + a2 * 0.46, y + 0.025), color=col, lw=1.7, ms=8, alpha=0.45)

label(ax, 0.04, 0.035, "浅色箭头为另一个粒子", fs=7.6, color=MUTED, ha="left")

save(fig, "08", "fig08-01")


# ================================================================ 图 8-2
# 真实的二维 PIC / FLIP / APIC 角动量测试：
# 周期方格 64x64，每格 2x2 个粒子，初始为 Lamb-Oseen 涡，每步 P2G -> 投影 -> G2P。
N = 64
L = 1.0
dx = L / N
ppc = 2
rc = 0.12
cx = cy = 0.5
RHO = 1000.0


def vtheta(r):
    r = np.maximum(r, 1e-9)
    return (1.0 - np.exp(-r ** 2 / rc ** 2)) / r


RCUT = 0.18


def profile(r):
    """带紧支撑截断的环向速度：远处衰减到零，使速度场在周期域上连续。"""
    return vtheta(r) * np.exp(-(r / RCUT) ** 4)


_rg = np.linspace(1e-4, 0.45, 4000)
GAM = 1.0 / profile(_rg).max()                  # 峰值环向速度归一到 1 m/s


def vel(x, y):
    ddx = np.mod(x - cx + 0.5 * L, L) - 0.5 * L
    ddy = np.mod(y - cy + 0.5 * L, L) - 0.5 * L
    r = np.hypot(ddx, ddy)
    vt = GAM * profile(r)
    return -vt * ddy / np.maximum(r, 1e-9), vt * ddx / np.maximum(r, 1e-9)


def grad_num(x, y, eps=2e-4):
    vxp, vyp = vel(x + eps, y)
    vxm, vym = vel(x - eps, y)
    vxq, vyq = vel(x, y + eps)
    vxs, vys = vel(x, y - eps)
    C = np.empty((x.size, 2, 2))
    C[:, 0, 0] = (vxp - vxm) / (2 * eps)
    C[:, 0, 1] = (vxq - vxs) / (2 * eps)
    C[:, 1, 0] = (vyp - vym) / (2 * eps)
    C[:, 1, 1] = (vyq - vys) / (2 * eps)
    return C


def make_particles():
    gx, gy = np.meshgrid((np.arange(N) + 0.5) * dx, (np.arange(N) + 0.5) * dx)
    sub = (np.arange(ppc) + 0.5) / ppc - 0.5
    X, Y = [], []
    for a in sub:
        for b in sub:
            X.append((gx + a * dx).ravel())
            Y.append((gy + b * dx).ravel())
    return np.concatenate(X), np.concatenate(Y)


OFF = np.array([-1, 0, 1])


def weights(x, y):
    # 格点 i 位于 ((i+0.5)dx)，相对坐标 gx = x/dx - 0.5；取最近的格点做展开中心。
    gx = x / dx - 0.5
    gy = y / dx - 0.5
    i0 = np.floor(gx + 0.5).astype(int)
    j0 = np.floor(gy + 0.5).astype(int)
    fx = gx - i0
    fy = gy - j0
    wx = np.stack([0.5 * (0.5 - fx) ** 2, 0.75 - fx ** 2, 0.5 * (0.5 + fx) ** 2], 1)
    wy = np.stack([0.5 * (0.5 - fy) ** 2, 0.75 - fy ** 2, 0.5 * (0.5 + fy) ** 2], 1)
    return i0, j0, wx, wy


def project(vx, vy):
    kx = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    KX, KY = np.meshgrid(kx, kx)
    k2 = KX ** 2 + KY ** 2
    k2[0, 0] = 1.0
    vxh = np.fft.fft2(vx)
    vyh = np.fft.fft2(vy)
    kv = KX * vxh + KY * vyh
    vxh = vxh - KX * kv / k2
    vyh = vyh - KY * kv / k2
    vxh[0, 0] = 0.0
    vyh[0, 0] = 0.0
    return np.real(np.fft.ifft2(vxh)), np.real(np.fft.ifft2(vyh))


def run(mode, steps=200, dt=0.004):
    x, y = make_particles()
    vx, vy = vel(x, y)
    C = grad_num(x, y) if mode == "apic" else np.zeros((x.size, 2, 2))
    mass_p = RHO * (dx / ppc) ** 2

    i0, j0, wx, wy = weights(x, y)

    L0 = np.sum(mass_p * ((x - cx) * vy - (y - cy) * vx))
    hist = [1.0]

    for s in range(steps):
        # --- P2G
        mass = np.zeros((N, N))
        momx = np.zeros((N, N))
        momy = np.zeros((N, N))
        for a in range(3):
            for b in range(3):
                ii = (i0 + OFF[a]) % N
                jj = (j0 + OFF[b]) % N
                rx = (ii + 0.5) * dx - x
                ry = (jj + 0.5) * dx - y
                rx = np.mod(rx + 0.5 * L, L) - 0.5 * L
                ry = np.mod(ry + 0.5 * L, L) - 0.5 * L
                ux = vx + C[:, 0, 0] * rx + C[:, 0, 1] * ry
                uy = vy + C[:, 1, 0] * rx + C[:, 1, 1] * ry
                ker = wx[:, a] * wy[:, b]
                mass[jj, ii] += 0.0
                np.add.at(mass, (jj, ii), ker * mass_p)
                np.add.at(momx, (jj, ii), ker * mass_p * ux)
                np.add.at(momy, (jj, ii), ker * mass_p * uy)
        ok = mass > 1e-12
        gx = np.zeros((N, N))
        gy = np.zeros((N, N))
        gx[ok] = momx[ok] / mass[ok]
        gy[ok] = momy[ok] / mass[ok]

        gpx, gpy = gx.copy(), gy.copy()
        # --- 投影
        gx, gy = project(gx, gy)

        # --- G2P
        vx_new = np.zeros_like(vx)
        vy_new = np.zeros_like(vy)
        uold_x = np.zeros_like(vx)
        uold_y = np.zeros_like(vy)
        M = np.zeros((x.size, 2, 2))
        D = np.zeros((x.size, 2, 2))
        for a in range(3):
            for b in range(3):
                ii = (i0 + OFF[a]) % N
                jj = (j0 + OFF[b]) % N
                xi = (ii + 0.5) * dx
                yi = (jj + 0.5) * dx
                ker = wx[:, a] * wy[:, b]
                vx_new += ker * gx[jj, ii]
                vy_new += ker * gy[jj, ii]
                uold_x += ker * gpx[jj, ii]
                uold_y += ker * gpy[jj, ii]
                rx = np.mod(xi - x + 0.5 * L, L) - 0.5 * L
                ry = np.mod(yi - y + 0.5 * L, L) - 0.5 * L
                M[:, 0, 0] += ker * gx[jj, ii] * rx
                M[:, 0, 1] += ker * gx[jj, ii] * ry
                M[:, 1, 0] += ker * gy[jj, ii] * rx
                M[:, 1, 1] += ker * gy[jj, ii] * ry
                D[:, 0, 0] += ker * rx * rx
                D[:, 0, 1] += ker * rx * ry
                D[:, 1, 0] += ker * ry * rx
                D[:, 1, 1] += ker * ry * ry

        if mode == "pic":
            vx, vy = vx_new, vy_new
        elif mode == "flip":
            vx = vx + (vx_new - uold_x)
            vy = vy + (vy_new - uold_y)
        else:
            vx, vy = vx_new, vy_new
            det = D[:, 0, 0] * D[:, 1, 1] - D[:, 0, 1] * D[:, 1, 0]
            C = np.empty_like(D)
            C[:, 0, 0] = (M[:, 0, 0] * D[:, 1, 1] - M[:, 0, 1] * D[:, 1, 0]) / det
            C[:, 0, 1] = (M[:, 0, 1] * D[:, 0, 0] - M[:, 0, 0] * D[:, 0, 1]) / det
            C[:, 1, 0] = (M[:, 1, 0] * D[:, 1, 1] - M[:, 1, 1] * D[:, 1, 0]) / det
            C[:, 1, 1] = (M[:, 1, 1] * D[:, 0, 0] - M[:, 1, 0] * D[:, 0, 1]) / det

        x = np.mod(x + dt * vx, L)
        y = np.mod(y + dt * vy, L)
        i0, j0, wx, wy = weights(x, y)

        Lz = np.sum(mass_p * ((x - cx) * vy - (y - cy) * vx))
        hist.append(Lz / L0)
    return np.array(hist)


# ---------------------------------------------------------------- 跑三种方式并作图
if __name__ == "__main__":
    STEPS = 600
    DT = 0.004
    res = {k: run(k, steps=STEPS, dt=DT) for k in ("pic", "flip", "apic")}
    tt = np.arange(STEPS + 1) * DT

    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    clean(ax, grid=True)
    ax.set_xlim(0, STEPS * DT)
    ax.set_ylim(0.36, 1.08)
    ax.axhline(1.0, color=FAINT, lw=0.9, ls=":", zorder=1)

    style = dict(pic=(BLUE, "PIC"), flip=(ACCENT, "FLIP"), apic=(GREEN, "APIC"))
    for k, (col, name) in style.items():
        ax.plot(tt, res[k], color=col, lw=1.7, zorder=4,
                label=r"$\mathrm{%s}$  $L/L_0=%.2f$" % (name, res[k][-1]))

    ax.set_xlabel("时间 $t$ / s")
    ax.set_ylabel(r"$L_z\,/\,L_z(0)$")
    ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.legend(loc="lower left", frameon=False, fontsize=8.6,
              handlelength=2.0, labelspacing=0.35, bbox_to_anchor=(0.005, 0.02))

    save(fig, "08", "fig08-02")
