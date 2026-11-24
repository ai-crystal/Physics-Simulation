# -*- coding: utf-8 -*-
"""第 11 章插图：roofline 与工作点、优化顺序的收益（成本模型）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ---------------------------------------------------------------- 图 11-1
BW_GB = 2000.0          # GB/s
PEAK_T = 30.0           # TFLOP/s，fp32

I = np.logspace(-1, 2.7, 500)
ROOF = np.minimum(PEAK_T, BW_GB * I / 1000.0)   # GB/s * FLOP/B = GFLOP/s
RIDGE = PEAK_T / (BW_GB / 1000.0)               # 15 FLOP/字节

fig, ax = plt.subplots(figsize=(6.6, 3.75))
ax.set_xscale("log")
ax.set_yscale("log")
ax.fill_between(I, 1e-3, ROOF, color="#EFF4FF", zorder=1)
ax.plot(I, ROOF, color=BLUE, lw=1.9, zorder=3, solid_capstyle="round")

# 脊点
ax.plot([RIDGE, RIDGE], [0.13, PEAK_T], color=FAINT, lw=0.8, ls=(0, (3, 3)), zorder=2)
ax.plot([0.1, RIDGE], [PEAK_T, PEAK_T], color=FAINT, lw=0.8, ls=(0, (3, 3)), zorder=2)

ax.set_xlim(0.1, 500)
ax.set_ylim(0.13, 110)
ax.set_xlabel("算术强度（FLOP/字节）")
ax.set_ylabel("性能（TFLOP/s）")
clean(ax, grid=True)
ax.set_yticks([0.3, 1, 3, 10, 30, 100])
ax.set_yticklabels(["0.3", "1", "3", "10", "30", "100"])
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30, 100, 300])
ax.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30", "100", "300"])

# 两段的说明，用引线指到屋顶上
ax.annotate("带宽受限段  $P=B\\cdot I$", xy=(0.40, 0.80), xytext=(0.13, 12),
            fontsize=8.3, color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8))
ax.annotate("算力受限段  $P=P_{\\max}$", xy=(18, PEAK_T), xytext=(3.4, 62),
            fontsize=8.3, color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8))

label(ax, 18.5, 0.44, "脊点 15 FLOP/字节", fs=8.2, color=ACCENT, ha="left", va="center")

# 工作点（示意）
pts = [(0.25, 0.30, "稀疏矩阵乘", 0.315, 0.225),
       (0.46, 0.55, "七点差分", 0.60, 0.40),
       (1.10, 1.15, "SPH 邻域", 1.45, 0.85),
       (60.0, 18.0, "稠密矩阵乘", 78.0, 23.0)]
for x, y, txt, tx, ty in pts:
    ax.scatter([x], [y], s=34, color=ACCENT, edgecolor="white", lw=0.9, zorder=6)
    label(ax, tx, ty, txt, fs=8.2, color=INK, ha="left", va="center")

# 往右移的提示
ax.annotate("", xy=(4.55, 5.1), xytext=(1.75, 2.9),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.1,
                            connectionstyle="arc3,rad=-0.20", shrinkA=2, shrinkB=2))
label(ax, 1.62, 2.15, "融合、分块、降精度", fs=8.0, color=GREEN, ha="left", va="center")

frame_note(ax, "屋顶按 2000 GB/s 与 30 TFLOP/s（fp32）画出；工作点为示意", fs=7.4)
save(fig, "11", "fig11-01")


# ---------------------------------------------------------------- 图 11-2
# 成本模型：T = max(取回字节 / 有效带宽, 浮点运算数 / 有效算力)
N = 256 ** 3
FLOP_CELL = 13.0
B_AOS, B_SOA = 7 * 128.0, 7 * 4.0          # 每格取回字节
BW_PEAK = 2000e9
F_PEAK = 30e12
BW_SINGLE, F_SINGLE = 15e9, 2.5e9


def t_model(sweeps, bytes_cell, bw, f):
    B = N * bytes_cell * sweeps
    W = N * FLOP_CELL * sweeps
    return max(B / bw, W / f)


stages = [
    ("参照：交错布局\nJacobi 400 轮\n单线程", t_model(400, B_AOS, BW_SINGLE, F_SINGLE)),
    ("算法：多重网格\n等效 12 轮", t_model(12, B_AOS, BW_SINGLE, F_SINGLE)),
    ("布局：数组结构体\n合并访存", t_model(12, B_SOA, BW_SINGLE, F_SINGLE)),
    ("并行：占满全部 SM\n带宽 1400 GB/s", t_model(12, B_SOA, 0.70 * BW_PEAK, F_PEAK)),
    ("指令：向量化\n带宽 1850 GB/s", t_model(12, B_SOA, 0.925 * BW_PEAK, F_PEAK)),
]

ts = [s[1] for s in stages]
for i, t in enumerate(ts):
    print(f"  stage {i}: {t:.4g} s")


def fmt(t):
    if t >= 1:
        return f"{t:.3g} 秒"
    if t >= 1e-3:
        return f"{t * 1e3:.3g} 毫秒"
    return f"{t * 1e6:.2g} 微秒"


fig, ax = plt.subplots(figsize=(6.6, 3.6))
xs = np.arange(len(ts))
ax.set_yscale("log")
ax.bar(xs, ts, width=0.56, color=BLUE, alpha=0.80, edgecolor="white", lw=0.8, zorder=3)
ax.set_ylim(2e-3, 5e3)
ax.set_xlim(-0.62, len(ts) - 0.38)
ax.set_ylabel("时间（秒，对数轴）")
clean(ax, grid=True)
ax.set_yticks([1e-2, 1e-1, 1, 10, 100, 1000])
ax.set_yticklabels(["0.01", "0.1", "1", "10", "100", "1000"])
ax.set_xticks(xs)
ax.set_xticklabels([s[0] for s in stages], fontsize=8.2, linespacing=1.5)
ax.tick_params(axis="x", length=0, pad=5)

for i, t in enumerate(ts):
    label(ax, xs[i], t * 1.22, fmt(t), fs=8.4, color=INK, va="bottom")
    if i:
        fac = ts[i - 1] / t
        txt = f"×{fac:.2g}" if fac < 10 else f"×{fac:.0f}"
        label(ax, xs[i], t * 1.22 * 3.0, txt, fs=8.6, color=ACCENT, va="bottom", weight="bold")

ax.text(2.05, 1500, "模型参数：$N=256^{3}$，每格 13 次浮点运算，\n"
                   "交错布局每格取回 896 字节，数组结构体 28 字节；\n"
                   "峰值带宽 2000 GB/s，单精度 30 TFLOP/s。\n"
                   "按模型计算，非实测。",
        fontsize=7.5, color=MUTED, ha="left", va="top", linespacing=1.7,
        bbox=dict(facecolor="white", edgecolor="none", pad=4.5, alpha=1.0))
save(fig, "11", "fig11-02")
