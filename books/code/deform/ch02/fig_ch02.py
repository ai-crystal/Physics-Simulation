import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 2-1  距离约束的投影（示意图）
#   三点在第 1 行被违反，第 2 行按逆质量分配修正，第 3 行满足
#   取 m1 = 1、m2 = 3（圆面积正比于质量），L0 = 0.30，违反量 C = 0.09
# ============================================================
W, H = 6.6, 3.9
ASP = W / H
fig, ax = canvas(W, H)


def ball(x, y, r, text="", fc="white", ec=INK, ls="-", tc=INK, lw=1.3, z=5, alpha=1.0):
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r * ASP, facecolor=fc, edgecolor=ec,
                         lw=lw, ls=ls, zorder=z, alpha=alpha))
    if text:
        label(ax, x, y, text, fs=8.6, color=tc, z=z + 1)


def tick(x, y, h=0.038, color=MUTED):
    ax.plot([x, x], [y - h, y + h], color=color, lw=0.9, zorder=4)


def dim(x0, x1, y, text, color=MUTED, fs=8.2, up=0.030):
    arrow(ax, (x0, y), (x1, y), color=color, lw=0.9, style="<|-|>", ms=7, z=6)
    label(ax, (x0 + x1) / 2, y + up, text, fs=fs, color=color)


M1, M2 = 1.0, 3.0
R1, R2 = 0.021, 0.021 * np.sqrt(M2 / M1)
L0, C = 0.30, 0.09
X1A = 0.150
X2A = X1A + L0 + C
d1 = C * (1 / M1) / (1 / M1 + 1 / M2)      # 0.0675
d2 = C * (1 / M2) / (1 / M1 + 1 / M2)      # 0.0225
X1B, X2B = X1A + d1, X2A - d2

# ---------- 第一行：预测位置 ----------
yA = 0.845
ball(X1A, yA, R1, "$m_1$", ec=INK)
ball(X2A, yA, R2, "$m_2$", ec=INK)
dim(X1A, X2A, yA + 0.115, "$|\\mathbf{x}_2-\\mathbf{x}_1|$", color=INK, up=0.032)
dim(X1A, X1A + L0, yA - 0.088, "$L_0$", color=MUTED, up=-0.052)
arrow(ax, (X1A + L0, yA - 0.088), (X2A, yA - 0.088), color=ACCENT, lw=2.4, ms=1,
      style="-", z=6)
label(ax, (X1A + L0 + X2A) / 2, yA - 0.135, "$C$", fs=9.0, color=ACCENT)

# ---------- 第二行：分配修正 ----------
yB = 0.500
ball(X1A, yB, R1, "", ec=FAINT, ls=(0, (2.5, 2.5)), lw=1.0, z=3)
ball(X2A, yB, R2, "", ec=FAINT, ls=(0, (2.5, 2.5)), lw=1.0, z=3)
ball(X1B, yB, R1, "$m_1$", ec=BLUE, tc=BLUE)
ball(X2B, yB, R2, "$m_2$", ec=BLUE, tc=BLUE)
arrow(ax, (X1A, yB - 0.078), (X1B, yB - 0.078), color=BLUE, lw=1.1, ms=7, z=6)
arrow(ax, (X2A, yB - 0.078), (X2B, yB - 0.078), color=BLUE, lw=1.1, ms=7, z=6)
label(ax, (X1A + X1B) / 2, yB - 0.115, r"$\Delta\mathbf{x}_1$", fs=8.4, color=BLUE)
label(ax, (X2A + X2B) / 2, yB - 0.115, r"$\Delta\mathbf{x}_2$", fs=8.4, color=BLUE)

# ---------- 第三行：投影之后 ----------
yC = 0.150
ball(X1B, yC, R1, "$m_1$", ec=INK)
ball(X2B, yC, R2, "$m_2$", ec=INK)
dim(X1B, X2B, yC + 0.100, "$L_0$", color=GREEN, up=0.032)
label(ax, 0.045, yA, "①", fs=9.2, color=FAINT, ha="left")
label(ax, 0.045, yB, "②", fs=9.2, color=FAINT, ha="left")
label(ax, 0.045, yC, "③", fs=9.2, color=FAINT, ha="left")

# ---------- 右侧文字 ----------
tx = 0.680
label(ax, tx, yA + 0.030, "预测位置违反约束", fs=8.8, color=INK, ha="left")
label(ax, tx, yA - 0.018, "$C=0.09$", fs=8.8, color=ACCENT, ha="left")
label(ax, tx, yB + 0.030, "各自挪一段，$m$ 大的少挪", fs=8.8, color=BLUE, ha="left")
label(ax, tx, yB - 0.018, "$\\Delta\\mathbf{x}_1:\\Delta\\mathbf{x}_2=w_1:w_2$", fs=8.8,
      color=BLUE, ha="left")
label(ax, tx, yC + 0.030, "距离回到 $L_0$，连线方向不变", fs=8.8, color=GREEN, ha="left")
label(ax, tx, yC - 0.018, "$m_1\\Delta\\mathbf{x}_1+m_2\\Delta\\mathbf{x}_2=0$", fs=8.8,
      color=GREEN, ha="left")

ax.set_ylim(0.03, 1.0)
save(fig, "02", "fig02-01")


# ============================================================
# 图 2-2  等效刚度随扫描次数（真实计算）
#   11 个质点的链，10 段，L0 = 0.1 m，m = 0.1 kg，一端固定，
#   另一端施加 1 N 恒力，dt = 1/60 s，跑到静态平衡
#   刚度 = 力 / 总伸长；纯投影 alpha = 0，XPBD 取 alpha = 1/k
# ============================================================
def relax(iters, k, N=11, L0=0.1, mass=0.1, F=1.0, dt=1 / 60.,
          maxsteps=3000, damp=0.9, tol=1e-11):
    alpha = 0.0 if k is None else 1.0 / k
    at = alpha / dt ** 2
    w = 1.0 / mass
    x = np.arange(N) * L0
    v = np.zeros(N)
    for s in range(maxsteps):
        v[-1] += F / mass * dt
        xold = x.copy()
        x = x + v * dt
        lam = np.zeros(N - 1)
        for _ in range(iters):
            for c in range(N - 1):
                d = x[c + 1] - x[c]
                Cc = abs(d) - L0
                sg = 1.0 if d >= 0 else -1.0
                wa = 0.0 if c == 0 else w
                dl = (-Cc - at * lam[c]) / (wa + w + at)
                lam[c] += dl
                if c != 0:
                    x[c] -= w * dl * sg
                x[c + 1] += w * dl * sg
        x[0] = 0.0
        v = (x - xold) / dt * damp
        v[0] = 0.0
        if s > 200 and np.abs(x - xold).max() < tol:
            break
    return F / (x[-1] - (N - 1) * L0)


ITERS = [1, 2, 4, 8, 16, 32, 64, 128]
CURVES = [(None, "PBD（$\\alpha=0$）", INK, "-"),
          (100.0, "$\\alpha=0.01$  →  10 N/m", GREEN, "-"),
          (1000.0, "$\\alpha=0.001$  →  100 N/m", BLUE, "-"),
          (10000.0, "$\\alpha=0.0001$  →  1000 N/m", ACCENT, "-")]

fig, ax = plt.subplots(figsize=(6.6, 3.5))
for k, lab, color, ls in CURVES:
    ys = [relax(n, k) for n in ITERS]
    ax.plot(ITERS, ys, color=color, lw=1.8, ls=ls, marker="o", ms=4.2,
            mfc="white", mew=1.1, label=lab)
    print("%-26s" % lab, " ".join("%8.2f" % y for y in ys))

for tgt in (10, 100, 1000):
    ax.axhline(tgt, color=FAINT, lw=0.8, ls=(0, (2, 3)), zorder=0)


ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.85, 175)
ax.set_ylim(6, 1.2e5)
ax.set_xticks(ITERS)
ax.set_xticklabels([str(n) for n in ITERS])
ax.set_xlabel("每个时间步的扫描次数")
ax.set_ylabel("等效刚度  (N/m)")
ax.legend(loc="upper left", handlelength=1.8, labelspacing=0.32, borderpad=0.2)
clean(ax, grid=True)
ax.tick_params(which="minor", length=2, color=GRID)

save(fig, "02", "fig02-02")
