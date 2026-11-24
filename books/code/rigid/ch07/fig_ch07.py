import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

DT = 1.0 / 60.0


# ============================================================
# 图 7-1  Baumgarte 系数与恢复时间（真实 1D）
# ============================================================
def decay(beta, p0=0.05, n=110):
    """一维穿透的逐帧衰减：每步目标分离速度 beta*p/dt。"""
    p = p0
    out = [p]
    for _ in range(n):
        v = beta * p / DT          # 修正速度，向上
        p = p - v * DT             # 位置积分
        out.append(p)
    return np.array(out)


def recovery_steps(beta, p0=0.05, target=0.01, limit=5000):
    p = p0
    for i in range(limit):
        p = p - beta * p
        if p < target * p0:
            return i + 1
    return limit


fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.15),
                        gridspec_kw=dict(width_ratios=[1.18, 1.0], wspace=0.30))

ax = axs[0]
betas = [0.1, 0.2, 0.5, 0.8]
cols = [BLUE, ACCENT, GREEN, PURPLE]
for beta, c in zip(betas, cols):
    y = decay(beta)
    t = np.arange(len(y)) * DT
    ax.semilogy(t, y * 1000, color=c, lw=1.45, label=r"$\beta=%.1f$" % beta)
ax.set_xlim(0, 1.45)
ax.set_ylim(1e-4, 80)
ax.set_xlabel("时间 $t$（s）", fontsize=9.4)
ax.set_ylabel("穿透深度（mm）", fontsize=9.4)
ax.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 50])
ax.set_yticklabels(["$10^{-3}$", "$10^{-2}$", "$10^{-1}$", "1", "10", "50"])
clean(ax, grid=True)
ax.legend(loc="upper right", fontsize=8.2, handlelength=1.6, labelspacing=0.28)
ax.axhline(0.5, color=FAINT, lw=0.7, ls=(0, (2, 3)), zorder=1)
ax.text(1.40, 0.56, "初始值的 1%", fontsize=7.8, color=MUTED, ha="right", va="bottom")

ax = axs[1]
bs = np.linspace(0.02, 0.95, 60)
steps = np.array([recovery_steps(b) for b in bs])
tau = steps * DT
ana = DT * np.log(0.01) / np.log(1.0 - bs)
ax.semilogy(bs, ana, color=BLUE, lw=1.2, label="解析式")
ax.semilogy(bs[::3], tau[::3], "o", ms=3.4, color=ACCENT,
            mec="white", mew=0.5, label="逐帧模拟", zorder=4)
ax.set_xlim(0, 1.0)
ax.set_ylim(0.008, 6)
ax.set_xlabel(r"Baumgarte 系数 $\beta$", fontsize=9.4)
ax.set_ylabel("降到 1% 的恢复时间（s）", fontsize=9.4)
clean(ax, grid=True)
ax.legend(loc="upper left", fontsize=8.2, handlelength=1.6, labelspacing=0.28)
for b, lab, dx, dy in ((0.2, "0.34 s", 0.10, 2.2), (0.8, "0.05 s", -0.30, 0.42)):
    tt = DT * np.log(0.01) / np.log(1.0 - b)
    ax.plot([b], [tt], "o", ms=4.6, color=ACCENT, mec="white", mew=0.7, zorder=5)
    ax.annotate(lab, xy=(b, tt), xytext=(b + dx, tt * dy), fontsize=8.0, color=ACCENT,
                arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=0.8,
                                connectionstyle="arc3,rad=0.2"))
ax.text(0.965, 0.10, r"$\beta\to1$", fontsize=8.2, color=MUTED, ha="right")

fig.subplots_adjust(left=0.105, right=0.978, top=0.965, bottom=0.145)
save(fig, "07", "fig07-01")


# ============================================================
# 图 7-2  子步数对八层箱堆漂移的影响（真实 1D 链）
# ============================================================
def stack_run(substeps=1, iters=8, T=10.0, frame=1/60.0,
              nbox=8, beta=0.2, slop=0.0005, g=9.81):
    dt = frame / substeps
    n = nbox
    invm = np.ones(n)
    y = np.arange(n) * 1.0 + 0.5          # 箱高 1 m，底面贴地
    v = np.zeros(n)
    cache = {}
    for _ in range(int(round(T / frame))):
        for _s in range(substeps):
            v += -g * dt
            y += v * dt
            contacts = [(0, -1, -(y[0] - 0.5))]
            for i in range(1, n):
                contacts.append((i, i - 1, -((y[i] - 0.5) - (y[i - 1] + 0.5))))

            for (up, lo, pen) in contacts:
                lam = cache.get((up, lo), 0.0)
                if lam > 0.0:
                    v[up] += lam * invm[up]
                    if lo >= 0:
                        v[lo] -= lam * invm[lo]

            for _it in range(iters):
                for (up, lo, pen) in contacts:
                    u = v[up] - (v[lo] if lo >= 0 else 0.0)
                    k = invm[up] + (invm[lo] if lo >= 0 else 0.0)
                    b = -beta * max(0.0, pen - slop) / dt
                    dl = -(u + b) / k
                    old = cache.get((up, lo), 0.0)
                    new = max(0.0, old + dl)
                    dl = new - old
                    cache[(up, lo)] = new
                    v[up] += dl * invm[up]
                    if lo >= 0:
                        v[lo] -= dl * invm[lo]

            # 子步结束后的穿透，用于记录最大值
            pens = [max(0.0, -(y[0] - 0.5))]
            pens += [max(0.0, -((y[i] - 0.5) - (y[i - 1] + 0.5))) for i in range(1, n)]
            if _s == 0 and _ == 0:
                maxpen = max(pens)
            else:
                maxpen = max(maxpen, max(pens))

    pens = [max(0.0, -(y[0] - 0.5))]
    pens += [max(0.0, -((y[i] - 0.5) - (y[i - 1] + 0.5))) for i in range(1, n)]
    return (7.5 - y[-1]) * 1000.0, maxpen * 1000.0


subs = np.array([1, 2, 4, 8, 16])
drift, pen = [], []
for s in subs:
    d, p = stack_run(substeps=int(s))
    drift.append(d)
    pen.append(p)
drift = np.array(drift)
pen = np.array(pen)

fig, ax = plt.subplots(figsize=(6.4, 3.35))
ax.loglog(subs, drift, "o-", color=ACCENT, lw=1.5, ms=4.6,
          mec="white", mew=0.7, label="顶箱下沉")
ax.loglog(subs, pen, "s-", color=BLUE, lw=1.5, ms=4.2,
          mec="white", mew=0.7, label="最大穿透")
ref_x = np.array([1.0, 8.0])
ref_y = drift[0] * ref_x ** (-1.5)
ax.loglog(ref_x, ref_y, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1,
          label="参考：斜率 −1.5")

ax.set_xticks(subs)
ax.set_xticklabels([str(int(s)) for s in subs])
ax.set_xlim(0.85, 20)
ax.set_ylim(0.35, 30)
ax.set_xlabel("每帧子步数", fontsize=9.6)
ax.set_ylabel("长度（mm）", fontsize=9.6)
clean(ax, grid=True)
ax.legend(loc="lower left", fontsize=8.4, handlelength=1.9, labelspacing=0.3)
for s, d in zip(subs, drift):
    if s in (1, 8):
        ax.text(s * 1.10, d * 1.12, "%.1f" % d, fontsize=7.8, color=ACCENT, va="bottom")

fig.subplots_adjust(left=0.105, right=0.975, top=0.965, bottom=0.165)
save(fig, "07", "fig07-02")

print("drift", np.round(drift, 3))
print("pen  ", np.round(pen, 3))
