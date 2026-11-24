import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ---------------- 图 13-1 三维网格内存 ----------------
N = np.array([32, 64, 128, 256, 512, 1024])
fig, ax = plt.subplots(figsize=(6.4, 3.2))
for b, c, lab in [(24, BLUE, "24 B/格点（6 个 float32）"),
                  (48, ACCENT, "48 B/格点（6 个 float64）"),
                  (96, GREEN, "96 B/格点（加粗层、外推、涡量）")]:
    ax.loglog(N, N ** 3 * b / 1e9, "-o", ms=3, color=c, lw=1.6, label=lab)
for gb, txt in [(8, "8 GB"), (32, "32 GB"), (128, "128 GB")]:
    ax.axhline(gb, color=FAINT, lw=0.8, ls="--")
    ax.text(1030, gb * 1.12, txt, fontsize=7.4, color=MUTED, ha="right")
clean(ax, grid=True)
ax.set_xlabel("单边分辨率 $N$")
ax.set_ylabel("内存 (GB)")
ax.set_xlim(30, 1100); ax.set_ylim(1e-2, 1e3)
ax.legend(fontsize=7.6, loc="upper left")
save(fig, "13", "fig13-01")


print("512^3 48B GB:", 512**3*48/1e9, "96B:", 512**3*96/1e9)
