import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 12-1  从现象到成因的判别路径（示意）
# ============================================================
W, H = 6.9, 4.45
fig, ax = canvas(W, H)

# 顶部提示
box(ax, 0.030, 0.902, 0.940, 0.068,
    "先确认能稳定复现：固定步长 · 固定随机种子 · 固定初始状态",
    fc="#FDF2E9", ec=ACCENT, tc=ACCENT, fs=8.8, lw=1.0)

X_S, W_S = 0.030, 0.150      # 现象
X_Q = 0.215                  # 先量什么
X_F, W_F = 0.640, 0.330      # 改法

ax.text(X_S, 0.858, "现象", fontsize=8.8, color=MUTED, ha="left", va="center")
ax.text(X_Q, 0.858, "先量什么", fontsize=8.8, color=MUTED, ha="left", va="center")
ax.text(X_F, 0.858, "往哪里改", fontsize=8.8, color=MUTED, ha="left", va="center")
ax.plot([0.030, 0.970], [0.840, 0.840], color=GRID, lw=0.9)

rows = [
    ("穿透", ACCENT,
     "① 速度 × 步长 与最薄厚度之比\n② 这一帧到底有没有接触点\n③ 穿透是否随时间单调增长",
     "CCD / 子步 / 碰撞厚度"),
    ("爆炸", PINK,
     "① 最早出现 NaN 的是哪个量\n② 有效质量是否为 0\n③ 法向是否被归一化成零向量",
     "保护除法 / 速度上限 / 夹住深度"),
    ("抖动", PURPLE,
     "① 抖动频率是否等于步频\n② 是否有约束互相冲突\n③ 接触点是否每帧在跳",
     "热启动 / split impulse / 摩擦锚点"),
    ("下沉、漂移", TEAL,
     "① 穿透是否单调增长后稳定\n② 是否缺少热启动\n③ 切向锚点是否固定在世界坐标",
     "位置层迭代 / 子步 / 锚点跨帧保持"),
    ("关节散架", BLUE,
     "① 关节两端的质量比\n② 迭代次数与链长的关系\n③ 转动惯量是否过小",
     "软约束 / articulation / 子步"),
]

Y0, RH, GAP = 0.800, 0.138, 0.022
for i, (name, col, chk, fix) in enumerate(rows):
    y = Y0 - i * (RH + GAP)
    box(ax, X_S, y - RH, W_S, RH, "", fc="white", ec=col, lw=1.2)
    label(ax, X_S + W_S / 2, y - RH / 2, name, fs=9.4, color=col, weight="bold")

    ax.text(X_Q, y - RH / 2, chk, fontsize=7.5, color=INK, ha="left", va="center",
            linespacing=1.38)

    box(ax, X_F, y - RH, W_F, RH, "", fc=SOFT[i % len(SOFT)], ec=col, lw=0.9, alpha=0.75)
    label(ax, X_F + W_F / 2, y - RH / 2, fix, fs=8.0, color=INK)

    arrow(ax, (X_S + W_S + 0.004, y - RH / 2), (X_Q - 0.008, y - RH / 2),
          color=col, lw=0.9, ms=6)
    arrow(ax, (0.585, y - RH / 2), (X_F - 0.008, y - RH / 2),
          color=col, lw=0.9, ms=6, alpha=0.8)


save(fig, "12", "fig12-01")


# ============================================================
# 图 12-2  质量比对关节误差的影响（真实一维计算）
#   0 天花板(w=0) —杆(L=1, 双边)— 1 轻箱(m=1) —接触— 2 重箱(M=ratio)
#   顺序冲量 + Baumgarte，逐行更新，不加热启动
# ============================================================
GRAV, DT, BETA, L, TEND = 9.81, 1.0 / 120.0, 0.2, 1.0, 3.0


def sim(ratio, iters, tend=TEND, dt=DT):
    w = np.array([0.0, 1.0, 1.0 / ratio])
    y = np.array([0.0, -L, -L + 1.0])
    v = np.zeros(3)
    hist = []
    for _ in range(int(tend / dt)):
        v[1:] += -GRAV * dt
        y[1:] += v[1:] * dt
        lam = np.zeros(2)
        for _it in range(iters):
            # 杆：双边约束，(y0 - y1) = L
            i, j = 0, 1
            C = (y[i] - y[j]) - L
            bias = (BETA / dt) * C
            k = w[i] + w[j]
            dl = -(bias + (v[i] - v[j])) / k
            lam[0] += dl
            v[i] += w[i] * dl
            v[j] -= w[j] * dl
            # 接触：单边约束，法向由 1 指向 2
            i, j = 1, 2
            Cc = (y[j] - y[i]) - 1.0
            bias = (BETA / dt) * min(0.0, Cc)
            k = w[i] + w[j]
            dl = -(bias + (v[j] - v[i])) / k
            nl = max(0.0, lam[1] + dl)
            dl = nl - lam[1]
            lam[1] = nl
            v[i] -= w[i] * dl
            v[j] += w[j] * dl
        hist.append((y[0] - y[1]) - L)
    hist = np.array(hist)
    tail = hist[int(0.8 * len(hist)):]
    return tail.mean() * 1e3          # 毫米


ratios = np.array([1, 2, 3, 5, 10, 30, 100, 300, 1000, 3000, 10000])
curves = [(1, ACCENT, "-", "每步 1 次迭代"),
          (4, GREEN, "-", "每步 4 次迭代"),
          (16, BLUE, "-", "每步 16 次迭代")]

fig, ax = new(6.6, 3.5)
clean(ax, grid=True)
for it, c, ls, nm in curves:
    err = np.array([sim(r, it) for r in ratios])
    ax.loglog(ratios, err, ls=ls, marker="o", ms=3.4, lw=1.6, color=c,
              mec="white", mew=0.5, label=nm)

ax.set_xlabel("质量比 $M/m$（重箱 / 轻箱）")
ax.set_ylabel("杆的稳态伸长（mm）")
ax.set_xlim(0.9, 1.4e4)
ax.set_ylim(0.9, 1.2e5)
ax.legend(loc="upper left", fontsize=8.4, handlelength=2.0, labelspacing=0.5,
          borderaxespad=0.7)

ax.text(0.03, 0.028,
        "1:10$^4$ 时：1 次迭代 29.8 m，16 次 0.80 m",
        fontsize=7.8, color=MUTED, ha="left", va="bottom",
        transform=ax.transAxes)

save(fig, "12", "fig12-02")
