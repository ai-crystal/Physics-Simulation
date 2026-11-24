import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 11-1  参数到形态的映射（示意）
#   三行：内摩擦角 / 粘聚 / 刚度，各取低、高两档
#   坡角按库仑楔体 theta = arctan(mu) 画，直立高度按 2c/(rho g) 的比例画
# ============================================================
fig, ax = canvas(6.7, 3.75)
ax.set_ylim(0.055, 0.975)

CX = (0.350, 0.650)
GROUND = (0.720, 0.470, 0.220)
SAND = "#EFE0C4"
COLD = "#E7DCC4"

for cx, t in zip(CX, ("参数偏低", "参数偏高")):
    label(ax, cx, 0.930, t, fs=8.6, color=MUTED)


def ground_line(cx, y0, half=0.108):
    ax.plot([cx - half, cx + half], [y0, y0], color=INK, lw=1.1, zorder=5,
            solid_capstyle="round")


def pile(cx, y0, b, th_deg, fc, lw=1.0):
    """库仑楔体：坡角 th，底半宽 b。"""
    H = b * np.tan(np.deg2rad(th_deg))
    xs = np.linspace(-b, b, 121)
    ys = H * (1.0 - np.abs(xs) / b) ** 1.18
    ax.fill(cx + xs, y0 + ys, facecolor=fc, edgecolor=INK, lw=lw, zorder=3,
            joinstyle="round")


def tower(cx, y0, half, H, th_deg, fc):
    """直立壁 + 脚下的塌落裙。"""
    run = 0.024 / np.tan(np.deg2rad(th_deg))
    for s in (-1, 1):
        pts = [(cx + s * half, y0), (cx + s * (half + run), y0),
               (cx + s * half, y0 + 0.024)]
        ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=INK,
                             lw=0.9, zorder=3))
    ax.add_patch(FancyBboxPatch((cx - half, y0), 2 * half, H,
                                boxstyle="round,pad=0.001,rounding_size=0.008",
                                facecolor=fc, edgecolor=INK, lw=1.0, zorder=4))


def mound(cx, y0, b, H, fc):
    xs = np.linspace(-b, b, 121)
    ys = H * np.exp(-(xs / (0.52 * b)) ** 2)
    ax.fill(cx + xs, y0 + ys, facecolor=fc, edgecolor=INK, lw=1.0, zorder=3)


def cracked_block(cx, y0, half, H, fc):
    pts = [(cx - half, y0), (cx + half, y0), (cx + half, y0 + H * 0.86),
           (cx + half * 0.55, y0 + H), (cx - half * 0.5, y0 + H * 0.96),
           (cx - half, y0 + H * 0.80)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, edgecolor=INK,
                         lw=1.0, zorder=3, joinstyle="round"))
    ax.plot([cx - 0.032, cx - 0.014, cx - 0.006],
            [y0 + H + 0.002, y0 + H * 0.60, y0 + H * 0.28],
            color=INK, lw=0.8, zorder=4)
    ax.plot([cx + 0.024, cx + 0.036, cx + 0.028],
            [y0 + H * 0.94, y0 + H * 0.64, y0 + H * 0.40],
            color=INK, lw=0.8, zorder=4)
    ax.add_patch(Polygon([(cx + half + 0.005, y0), (cx + half + 0.029, y0),
                          (cx + half + 0.023, y0 + 0.015), (cx + half + 0.008, y0 + 0.013)],
                         closed=True, facecolor=fc, edgecolor=INK, lw=0.8, zorder=3))


# ---- 第一行：内摩擦角 ----
y0 = GROUND[0]
ground_line(CX[0], y0)
pile(CX[0], y0, 0.088, 14.0, SAND)          # arctan(0.25) = 14.0 度
ground_line(CX[1], y0)
pile(CX[1], y0, 0.088, 38.7, SAND)          # arctan(0.80) = 38.7 度
label(ax, CX[0], y0 - 0.028, "摊成薄毯", fs=8.4, color=MUTED, va="top")
label(ax, CX[1], y0 - 0.028, "坡面陡直", fs=8.4, color=MUTED, va="top")

# ---- 第二行：粘聚 ----
y0 = GROUND[1]
ground_line(CX[0], y0)
pile(CX[0], y0, 0.080, 32.0, SAND)
ground_line(CX[1], y0)
tower(CX[1], y0, 0.030, 0.104, 32.0, SAND)
label(ax, CX[0], y0 - 0.028, "只有锥顶", fs=8.4, color=MUTED, va="top")
label(ax, CX[1], y0 - 0.028, "顶住一段直壁", fs=8.4, color=MUTED, va="top")

# ---- 第三行：刚度 ----
y0 = GROUND[2]
ground_line(CX[0], y0)
mound(CX[0], y0, 0.100, 0.048, COLD)
ground_line(CX[1], y0)
cracked_block(CX[1], y0, 0.060, 0.086, COLD)
label(ax, CX[0], y0 - 0.028, "塌成软饼", fs=8.4, color=MUTED, va="top")
label(ax, CX[1], y0 - 0.028, "保持棱角并开裂", fs=8.4, color=MUTED, va="top")

# ---- 左侧参数名 ----
rows = [(GROUND[0], "内摩擦角", "$\\mu=0.25\\ \\to\\ 0.80$"),
        (GROUND[1], "粘聚", "$c=0\\ \\to\\ 4$ kPa"),
        (GROUND[2], "刚度", "$E$ 低 $\\to$ 高")]
for yy, name, val in rows:
    label(ax, 0.024, yy + 0.030, name, fs=9.2, color=INK, ha="left", va="center")
    label(ax, 0.024, yy - 0.012, val, fs=8.2, color=MUTED, ha="left", va="center")

frame_note(ax, "示意图：坡角按 $\\theta=\\arctan\\mu$，直立高度按 $2c/(\\rho g)$ 的比例，未按真实尺寸缩放")

save(fig, "11", "fig11-01")


# ============================================================
# 图 11-2  一次模拟的流程与重算回路（示意）
# ============================================================
fig, ax = canvas(6.7, 3.35)

labels = ["布局与\n碰撞体", "初始\n堆积", "分层\n求解", "表面\n重建", "渲染与\n合成"]
N = len(labels)
x0, x1, gap = 0.035, 0.965, 0.026
w = (x1 - x0 - gap * (N - 1)) / N
yb, hb = 0.772, 0.158
cents = []
for i, lab in enumerate(labels):
    x = x0 + i * (w + gap)
    box(ax, x, yb, w, hb, lab, fc="#FCFAF6", ec=INK, fs=8.8, lw=1.1)
    cents.append(x + w / 2)
    if i:
        arrow(ax, (cents[i - 1] + w / 2 + 0.002, yb + hb / 2),
              (x - 0.002, yb + hb / 2), color=FAINT, lw=1.0)

# 重算回路：渲染 -> 分层求解
sol_x = cents[2]
yfb = 0.520
ax.plot([cents[-1], cents[-1]], [yb - 0.004, yfb], color=ACCENT, lw=1.1,
        ls=(0, (4, 3)), zorder=1)
ax.plot([cents[-1], sol_x], [yfb, yfb], color=ACCENT, lw=1.1, ls=(0, (4, 3)), zorder=1)
arrow(ax, (sol_x, yfb), (sol_x, yb - 0.006), color=ACCENT, lw=1.1,
      ls=(0, (4, 3)), ms=9)
label(ax, 0.700, yfb + 0.022, "评审：改参数或边界，从缓存帧回滚", fs=8.0,
      color=ACCENT, va="bottom")

for xx, t in zip((0.590, 0.665, 0.740), ("$c_0$", "$c_1$", "$c_2$")):
    ax.plot([xx], [yfb], marker="s", ms=3.8, color=ACCENT, zorder=5)
    label(ax, xx, yfb - 0.020, t, fs=7.8, color=ACCENT, va="top")

# 三档分辨率：挂在分层求解这一格下面
cx_link = 0.432
ybar = 0.352
ax.plot([cx_link, cx_link], [yb - 0.004, ybar], color=FAINT, lw=0.9, zorder=1)
ax.plot([0.300, 0.800], [ybar, ybar], color=FAINT, lw=0.9, zorder=1)
label(ax, 0.286, ybar + 0.030, "分辨率分层", fs=8.0, color=MUTED, ha="right", va="center")
for cx, t in zip((0.300, 0.550, 0.800), ("近景\nDEM 逐颗", "中景\nMPM 网格", "远景\n简化模型")):
    ax.plot([cx, cx], [ybar, 0.310], color=FAINT, lw=0.9, zorder=1)
    box(ax, cx - 0.100, 0.205, 0.200, 0.105, t, fc="white", ec=SLATE, fs=8.0, lw=0.9)

frame_note(ax, "实线：一次完整模拟　　虚线：评审后的重算回路", y=0.070)
save(fig, "11", "fig11-02")

print("ok")
