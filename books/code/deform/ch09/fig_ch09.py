import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 9-1  空间哈希与 3x3 邻域查询（结构示意）
# ============================================================
fig, ax = canvas(6.8, 3.4)

x0, y0, W, H = 0.030, 0.135, 0.470, 0.770
nx, ny = 6, 5
cw, ch = W / nx, H / ny

# ---- 一片来回折叠的布带（投影到二维） ----
ns = 46
t = np.linspace(0.0, 1.0, ns + 1)
cx = x0 + 0.022 + (W - 0.044) * t
cy = 0.520 + 0.225 * np.sin(2 * np.pi * 1.55 * t + 0.75)
wdt = 0.041
U = np.column_stack([cx, cy + wdt])
L = np.column_stack([cx, cy - wdt])

tris = []
for i in range(ns):
    tris.append((U[i], L[i], U[i + 1]))
    tris.append((L[i], U[i + 1], L[i + 1]))

# ---- 按三角形质心登记到格子，统计每格数量 ----
count = np.zeros((nx, ny), dtype=int)
for a, b, c in tris:
    m = (a + b + c) / 3.0
    i = min(nx - 1, max(0, int((m[0] - x0) / cw)))
    j = min(ny - 1, max(0, int((m[1] - y0) / ch)))
    count[i, j] += 1

cmax = count.max()
for i in range(nx):
    for j in range(ny):
        if count[i, j]:
            alpha = 0.09 + 0.33 * count[i, j] / cmax
            ax.add_patch(Rectangle((x0 + i * cw, y0 + j * ch), cw, ch,
                                   facecolor=ACCENT, edgecolor="none",
                                   alpha=alpha, zorder=1))

# ---- 布带本身 ----
for a, b, c in tris:
    ax.add_patch(Polygon([a, b, c], closed=True, facecolor="#F4F7FC",
                         edgecolor=SLATE, lw=0.35, alpha=0.93, zorder=3))

# ---- 网格线 ----
grid(ax, x0, y0, W, H, nx, ny, color="#CBD5E1", lw=0.8)
ax.add_patch(Rectangle((x0, y0), W, H, facecolor="none", edgecolor=INK, lw=1.1, zorder=6))

# ---- 3x3 查询窗口 ----
qi, qj = 1, 1
ax.add_patch(Rectangle((x0 + qi * cw, y0 + qj * ch), 3 * cw, 3 * ch,
                       facecolor="none", edgecolor=BLUE, lw=1.5,
                       ls=(0, (5, 2)), zorder=7))
ax.add_patch(Rectangle((x0 + (qi + 1) * cw, y0 + (qj + 1) * ch), cw, ch,
                       facecolor="none", edgecolor=ACCENT, lw=1.6, zorder=8))

# ---- h 标注：第一列宽度 ----
yt = 0.068
ax.plot([x0, x0], [y0, yt - 0.003], color=FAINT, lw=0.7, zorder=5)
ax.plot([x0 + cw, x0 + cw], [y0, yt - 0.003], color=FAINT, lw=0.7, zorder=5)
dim_arrow(ax, (x0, yt), (x0 + cw, yt), "h", fs=8.2, color=MUTED, off=0.030)

# ---- 右侧说明 ----
tx = 0.528
lines = [
    ("每片三角形按覆盖的格子登记", ACCENT),
    ("查询时并起 3×3 个格子", BLUE),
    ("候选数 ≈ 9h²×面密度，与总数无关", INK),
    ("h 太小：一片跨多格，登记翻倍", MUTED),
    ("h 太大：单格塞满，退化成平方", MUTED),
]
for k, (s, col) in enumerate(lines):
    yy = 0.880 - k * 0.132
    ax.plot([tx - 0.014], [yy], "o", ms=3.0, color=col, zorder=9)
    label(ax, tx, yy, s, fs=8.0, color=col, ha="left", va="center")

label(ax, tx, 0.185, "一次查询只碰这九个格子", fs=8.0, color=BLUE,
      ha="left", va="center")
label(ax, tx, 0.105, "色深表示格内登记的三角形片数", fs=7.7, color=FAINT,
      ha="left", va="center")

save(fig, "09", "fig09-01")


# ============================================================
# 图 9-2  IPC 障碍势与斥力（真实函数）
# ============================================================
dhat = 1.0

def barrier(d):
    d = np.asarray(d, float)
    out = np.zeros_like(d)
    m = d < dhat
    dm = d[m]
    out[m] = -(dm - dhat) ** 2 * np.log(dm / dhat)
    return out

def neg_grad(d):
    """-db/dd，即背离方向的斥力（已除以 kappa）。"""
    d = np.asarray(d, float)
    out = np.zeros_like(d)
    m = d < dhat
    dm = d[m]
    out[m] = 2 * (dm - dhat) * np.log(dm / dhat) + (dm - dhat) ** 2 / dm
    return out

fig, axes = new(6.9, 3.0, ncols=2, gridspec_kw={"width_ratios": [1.0, 1.0], "wspace": 0.42})
ax1, ax2 = axes

d = np.linspace(0.02, 1.20, 2000)

# ---- 左：势 ----
ax1.plot(d, barrier(d), color=BLUE, lw=1.8, zorder=4)
ax1.axvline(dhat, color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=2)
ax1.fill_between([dhat, 1.20], 0, 4.0, color="#F3F4F6", zorder=0)
ax1.text(1.10, 1.05, "无障碍", fontsize=7.8, color=FAINT, rotation=90,
         ha="center", va="center", zorder=2)
ax1.text(0.975, 3.86, "激活距离 $\\hat{d}$", fontsize=8.0, color=MUTED,
         ha="right", va="top", zorder=5)
ax1.annotate("$d\\to 0$ 时发散", xy=(0.035, 3.72), xytext=(0.26, 3.35),
             fontsize=8.0, color=ACCENT,
             arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.9, mutation_scale=9))
ax1.set_xlim(0, 1.20)
ax1.set_ylim(0, 4.0)
ax1.set_xlabel("归一化距离 $d/\\hat{d}$")
ax1.set_ylabel("障碍势 $b/\\kappa$")
clean(ax1, grid=True)

# ---- 右：斥力 ----
ax2.plot(d, neg_grad(d), color=GREEN, lw=1.8, zorder=4)
ax2.axvline(dhat, color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=2)
ax2.set_xlim(0, 1.20)
ax2.set_ylim(0, 13.6)
ax2.set_xlabel("归一化距离 $d/\\hat{d}$")
ax2.set_ylabel("归一化斥力 $-\\hat{d}\\,b'/\\kappa$")
clean(ax2, grid=True)

for dd, txt, dx, dy, ha, va in [(0.5, "1.19", 0.045, 0.45, "left", "bottom"),
                                (0.1, "12.2", 0.045, -0.55, "left", "center")]:
    ax2.plot([dd], [neg_grad(dd)], "o", ms=4.2, mfc="white", mec=GREEN, mew=1.2, zorder=5)
    ax2.annotate(txt, xy=(dd, neg_grad(dd)), xytext=(dd + dx, neg_grad(dd) + dy),
                 fontsize=8.0, color=MUTED, ha=ha, va=va)

ax2.text(0.30, 9.1, "越近越陡，按 $1/d$ 放大", fontsize=7.9, color=MUTED,
         ha="left", va="center")

save(fig, "09", "fig09-02")
