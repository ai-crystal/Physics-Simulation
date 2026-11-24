import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 3-1  一维两球碰撞：末速度与剩余动能随恢复系数变化（真实计算）
#   m1 = 1 kg, m2 = 3 kg, u1 = 2 m/s, u2 = 0
#   n 由球 1 指向球 2；k = 1/m1 + 1/m2；u = u2 - u1 = -2 m/s
#   J = -(1+e) u / k ；v1 = u1 - J/m1 ；v2 = u2 + J/m2
# ============================================================
m1, m2 = 1.0, 3.0
u1, u2 = 2.0, 0.0
k = 1.0 / m1 + 1.0 / m2
u_rel = u2 - u1
m_eff = 1.0 / k

e = np.linspace(0.0, 1.0, 401)
J = -(1.0 + e) * u_rel / k
v1 = u1 - J / m1
v2 = u2 + J / m2

E0 = 0.5 * m1 * u1 ** 2 + 0.5 * m2 * u2 ** 2
E1 = 0.5 * m1 * v1 ** 2 + 0.5 * m2 * v2 ** 2
ratio = E1 / E0
frac = 0.5 * m_eff * u_rel ** 2 / E0        # 相对运动那一份占初始动能的比例
v_cm = (m1 * u1 + m2 * u2) / (m1 + m2)

print("k =", k, " m_eff =", m_eff, " 相对运动能量占比 =", frac)
print("e=0 : J=%.3f v1=%.3f v2=%.3f E/E0=%.4f" % (J[0], v1[0], v2[0], ratio[0]))
print("e=0.5: J=%.3f v1=%.3f v2=%.3f E/E0=%.4f" % (J[200], v1[200], v2[200], ratio[200]))
print("e=1 : J=%.3f v1=%.3f v2=%.3f E/E0=%.4f" % (J[-1], v1[-1], v2[-1], ratio[-1]))

fig, (fa, fb) = plt.subplots(1, 2, figsize=(6.9, 3.2))

# ---- (a) 末速度 ----
fa.plot(e, v1, color=BLUE, lw=1.9, label=r"球 1  $v_1'$")
fa.plot(e, v2, color=ACCENT, lw=1.9, label=r"球 2  $v_2'$")
fa.axhline(v_cm, color=MUTED, lw=1.0, ls=(0, (4, 3)))
fa.axhline(0.0, color=GRID, lw=1.0)
fa.annotate(r"质心速度 $v_{\rm cm}=0.5$", xy=(0.42, v_cm), xytext=(0.30, 0.30),
            fontsize=8.4, color=MUTED, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8,
                            connectionstyle="arc3,rad=-0.25"))
fa.set_xlim(-0.02, 1.02)
fa.set_ylim(-1.45, 2.35)
fa.set_xlabel("恢复系数 $e$")
fa.set_ylabel("碰撞后速度  (m/s)")
fa.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
fa.set_yticks([-1, 0, 1, 2])
fa.legend(loc="upper left", bbox_to_anchor=(0.20, 0.99), handlelength=1.2,
          labelspacing=0.35)
fa.plot([0.0], [v1[0]], marker="o", ms=5, mfc="white", mec=BLUE, mew=1.2, zorder=6)
fa.plot([0.0], [v2[0]], marker="o", ms=5, mfc="white", mec=ACCENT, mew=1.2, zorder=6)
fa.annotate("$e=0$：两者同速", xy=(0.012, v1[0]), xytext=(0.16, 1.28),
            fontsize=8.4, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.8,
                            connectionstyle="arc3,rad=0.25"))
fa.annotate(r"$e=1$：$v_1'=-1$，$v_2'=1$", xy=(0.985, v1[-1]), xytext=(0.36, -1.26),
            fontsize=8.4, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8,
                            connectionstyle="arc3,rad=-0.20"))
fa.text(0.02, 1.055, "(a) 两条直线的交点就是 $e=0$", transform=fa.transAxes,
        fontsize=9.0, color=INK, ha="left", va="bottom")
clean(fa, grid=True)

# ---- (b) 剩余动能 ----
fb.plot(e, ratio, color=GREEN, lw=1.9)
fb.fill_between(e, ratio, 1.0, color=GREEN, alpha=0.09, lw=0)
fb.axhline(1.0, color=MUTED, lw=1.0, ls=(0, (4, 3)))
fb.set_xlim(-0.02, 1.02)
fb.set_ylim(0.10, 1.16)
fb.set_xlabel("恢复系数 $e$")
fb.set_ylabel(r"剩余动能  $E'/E_0$")
fb.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
fb.set_yticks([0.25, 0.5, 0.75, 1.0])
fb.plot([0.0], [ratio[0]], marker="o", ms=5, mfc="white", mec=GREEN, mew=1.2, zorder=6)
fb.annotate("$e=0$ 只剩 %.0f%%" % (100 * ratio[0]), xy=(0.02, ratio[0]),
            xytext=(0.19, 0.155), fontsize=8.4, color=GREEN,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8,
                            connectionstyle="arc3,rad=-0.22"))
fb.text(0.345, 0.855, r"$E'/E_0=1-%.2f\,(1-e^{2})$" % frac, fontsize=8.8, color=INK,
        ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=GRID, lw=0.7))
fb.text(0.02, 1.055, "(b) 丢掉的那一份随 $e$ 二次回升", transform=fb.transAxes,
        fontsize=9.0, color=INK, ha="left", va="bottom")
clean(fb, grid=True)

fig.subplots_adjust(wspace=0.32)
save(fig, "03", "fig03-01")


# ============================================================
# 图 3-2  顺序冲量的残差随扫描次数（真实计算）
#   十个接触：i=0 是箱 0 与地面，i=1..9 是箱 i-1 与箱 i。
#   法向向上；接触 i 的雅可比对箱 i 取 +1、对箱 i-1 取 -1。
#   A = J M^-1 J^T（三对角），b_i = 初始相对法向速度
#   全部箱子以 2 m/s 下落，故 b_0 = -2，其余为 0。
#   更新：lambda_i <- max(0, lambda_i - w * (A lambda + b)_i / A_ii)
#   残差取 max_i min(u_i, 0) 的绝对值（残余侵入速度）。
# ============================================================
NC = 10


def build(masses):
    inv = 1.0 / np.asarray(masses, float)
    A = np.zeros((NC, NC))
    for i in range(NC):
        A[i, i] += inv[i]
        if i > 0:
            A[i, i] += inv[i - 1]
            A[i, i - 1] -= inv[i - 1]
        if i + 1 < NC:
            A[i, i + 1] -= inv[i]
    b = np.zeros(NC)
    b[0] = -2.0
    return A, b


def pgs(A, b, sweeps, w=1.0):
    lam = np.zeros(NC)
    hist = []
    for _ in range(sweeps):
        for i in range(NC):
            r = A[i] @ lam + b[i]
            lam[i] = max(0.0, lam[i] - w * r / A[i, i])
        hist.append(max(np.max(np.maximum(-(A @ lam + b), 0.0)), 1e-14))
    return lam, np.array(hist)


SW = 200
A1, b1 = build(np.ones(NC))
lam1, h1 = pgs(A1, b1, SW, 1.0)
lam2, h2 = pgs(A1, b1, SW, 1.5)
A3, b3 = build(1.5 ** np.arange(NC))
lam3, h3 = pgs(A3, b3, SW, 1.0)
print("uniform  w=1.0 : resid(200)=%.3e  lam=%s" % (h1[-1], np.round(lam1, 2)))
print("uniform  w=1.5 : 1e-2 @ %d, 1e-3 @ %d" %
      (int(np.argmax(h2 < 1e-2)) + 1, int(np.argmax(h2 < 1e-3)) + 1))
print("graded 1.5^i   : resid(200)=%.3f  lam=%s" % (h3[-1], np.round(lam3, 2)))
print("graded resid @10,50,100,200 : %.3f %.3f %.3f %.3f" %
      (h3[9], h3[49], h3[99], h3[199]))

fig, ax = plt.subplots(figsize=(6.5, 3.6))
it = np.arange(1, SW + 1)
ax.semilogy(it, h1, color=BLUE, lw=1.8, label=r"等质量 $m_i=1$ kg，松弛因子 1")
ax.semilogy(it, h2, color=ACCENT, lw=1.8, ls=(0, (5, 2, 1, 2)),
            label=r"等质量，松弛因子 1.5")
ax.semilogy(it, h3, color=GREEN, lw=1.8, ls=(0, (6, 2)),
            label="质量比 1.5，逐层乘 1.5")

ax.axhline(1e-2, color=MUTED, lw=1.0, ls=(0, (4, 3)))
ax.text(3, 1.06e-2, r"判据 $10^{-2}$ m/s", fontsize=8.2, color=MUTED,
        ha="left", va="bottom")

ax.set_xlim(1, SW + 2)
ax.set_ylim(1e-4, 3.0)
ax.set_xlabel("扫描次数（每次扫完十个接触）")
ax.set_ylabel("残余侵入速度  (m/s)")
ax.set_xticks([1, 25, 50, 75, 100, 125, 150, 175, 200])
ax.legend(loc="lower left", bbox_to_anchor=(0.015, 0.02), handlelength=2.4,
          labelspacing=0.42)
clean(ax, grid=True)

n57, n87 = int(np.argmax(h2 < 1e-2)) + 1, int(np.argmax(h2 < 1e-3)) + 1
ax.plot([n57], [h2[n57 - 1]], marker="o", ms=5, mfc="white", mec=ACCENT, mew=1.2, zorder=6)
ax.annotate("第 %d 次扫描\n降到 $10^{-2}$" % n57, xy=(n57, h2[n57 - 1]),
            xytext=(72, 2.2e-2), fontsize=8.2, color=ACCENT,
            arrowprops=dict(arrowstyle="->", color=ACCENT, lw=0.8,
                            connectionstyle="arc3,rad=0.25"))
ax.annotate("质量悬殊时几乎停滞", xy=(150, h3[149]), xytext=(96, 1.35),
            fontsize=8.2, color=GREEN,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8,
                            connectionstyle="arc3,rad=-0.20"))
n149 = int(np.argmax(h1 < 1e-2)) + 1
ax.plot([n149], [h1[n149 - 1]], marker="o", ms=5, mfc="white", mec=BLUE, mew=1.2, zorder=6)
ax.annotate("等质量要 %d 次" % n149, xy=(n149, h1[n149 - 1]), xytext=(112, 2.4e-3),
            fontsize=8.2, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8,
                            connectionstyle="arc3,rad=0.18"))

save(fig, "03", "fig03-02")
