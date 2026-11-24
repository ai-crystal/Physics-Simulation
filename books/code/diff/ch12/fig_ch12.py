import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 12-1  反向传播显存的代价模型  M = 4 * N * s * T * B
#   4 字节（单精度），B = 1，s 为每格每步保存的浮点数
# ============================================================
BYTES = 4
GB = 1e9
N = {64: 64 ** 3, 96: 96 ** 3, 128: 128 ** 3}
COL = {64: TEAL, 96: BLUE, 128: ACCENT}
S0 = 16


def mem_gb(n, s, T, B=1):
    return BYTES * n * s * T * B / GB


fig, axs = new(6.8, 3.5, ncols=2, gridspec_kw=dict(width_ratios=[1.12, 1.0], wspace=0.30))
ax1, ax2 = axs

# ---------- 左：显存随步数 ----------
T = np.logspace(np.log10(10), np.log10(2000), 200)
for k, n in N.items():
    ax1.plot(T, mem_gb(n, S0, T), color=COL[k], lw=1.6, zorder=3,
             label=f"${k}^3$，{n} 格点")

for cap, ls in ((24, (0, (5, 3))), (80, (0, (2, 2)))):
    ax1.axhline(cap, color=MUTED, lw=0.9, ls=ls, zorder=1)
    ax1.text(11.5, cap * 1.15, f"{cap} GB 显存", fontsize=8.0, color=MUTED,
             ha="left", va="bottom")

# 交点标注：128^3 与 24 GB
T_cross128 = 24.0 / mem_gb(N[128], S0, 1)
ax1.plot([T_cross128], [24], "o", ms=4.6, color=ACCENT, zorder=5)
ax1.annotate(f"{T_cross128:.0f} 步", xy=(T_cross128, 24), xytext=(152, 37),
             fontsize=8.2, color=ACCENT, ha="right", va="bottom",
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                             connectionstyle="arc3,rad=0.15"), zorder=6)

T_cross96 = 24.0 / mem_gb(N[96], S0, 1)
ax1.plot([T_cross96], [24], "o", ms=4.6, color=BLUE, zorder=5)

ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlim(10, 2000)
ax1.set_ylim(0.05, 400)
ax1.set_xlabel("rollout 步数 $T$")
ax1.set_ylabel("反向所需显存 (GB)")
clean(ax1, grid=True)
ax1.legend(loc="lower right", fontsize=8.2, handlelength=1.6, borderaxespad=0.5)

# ---------- 右：显存随每步保存量 ----------
S = np.linspace(2, 40, 300)
for k, n in N.items():
    ax2.plot(S, mem_gb(n, S, 200), color=COL[k], lw=1.6, zorder=3,
             label=f"${k}^3$")

m128 = mem_gb(N[128], S0, 200)
ax2.plot([S0], [m128], "o", ms=5.0, color=ACCENT, zorder=5)
ax2.annotate(f"{m128:.1f} GB",
             xy=(S0, m128), xytext=(15.4, 34.5),
             fontsize=8.2, color=ACCENT, ha="right", va="center",
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8,
                             connectionstyle="arc3,rad=-0.20"), zorder=6)

ax2.set_yscale("log")
ax2.set_xlim(0, 40)
ax2.set_ylim(0.1, 400)
ax2.set_xlabel("每格每步保存的浮点数 $s$")
ax2.set_ylabel("显存 (GB)，$T=200$")
clean(ax2, grid=True)
ax2.legend(loc="lower right", fontsize=8.2, handlelength=1.4, borderaxespad=0.6)

save(fig, "12", "fig12-01")
