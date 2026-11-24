import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 6-1  雪的压实硬化（真实本构公式）
#   (a) E(J_P) = E0 exp(a (1 - J_P))          式 (6.3)
#   (b) 一维压缩：J_E = J / J_P，弹性压缩量被夹在 theta_c
#       sigma = E(J_P)(J_E - 1)                式 (6.2)(6.4)
# ============================================================
E0 = 1.4e5          # 未压实时的杨氏模量 (Pa)
THETA_C = 0.025     # 允许的弹性压缩量


def E_of_JP(JP, a):
    return E0 * np.exp(a * (1.0 - JP))


def compress_1d(a, J_end=0.5, nstep=4000):
    """从 J=1 压到 J=J_end，按奇异值夹断更新 J_P，返回 (压缩量, 压应力 kPa)"""
    J_list = np.linspace(1.0, J_end, nstep)
    JP = 1.0
    out_s = []
    out_sig = []
    for J in J_list:
        JE = J / JP
        if JE < 1.0 - THETA_C:                 # 弹性压缩量触顶，超出部分转成塑性
            JP = J / (1.0 - THETA_C)
            JE = 1.0 - THETA_C
        sig = E_of_JP(JP, a) * (JE - 1.0)      # 一维：压为负
        out_s.append(1.0 - J)
        out_sig.append(-sig / 1000.0)
    return np.array(out_s), np.array(out_sig)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.15),
                               gridspec_kw=dict(wspace=0.27, bottom=0.175,
                                                top=0.955, left=0.085, right=0.985))

# ---------- (a) 模量随压实 ----------
JP = np.linspace(1.0, 0.5, 400)
for a, c, lab in ((0.7, GREEN, "$a=0.7$"), (2.0, ACCENT, "$a=2$"), (4.0, PURPLE, "$a=4$")):
    ax1.plot(JP, E_of_JP(JP, a) / E0, color=c, lw=1.8, label=lab)

ax1.set_xlim(1.0, 0.45)
ax1.set_ylim(0.85, 8.4)
ax1.set_yticks([1, 2, 3, 4, 6, 8])
ax1.set_xticks([1.0, 0.9, 0.8, 0.7, 0.6, 0.5])
ax1.set_xlabel("塑性体积比 $J_P$")
ax1.set_ylabel("$E/E_0$")
clean(ax1, spines=("left", "bottom"))
ax1.legend(loc="upper left", bbox_to_anchor=(0.02, 0.99), handlelength=1.8,
           borderaxespad=0.0, labelspacing=0.35, fontsize=8.4)

ax1.text(0.985, 5.35, "松散雪", fontsize=8, color=MUTED, ha="left", va="center")
ax1.text(0.505, 2.05, "压实雪", fontsize=8, color=MUTED, ha="right", va="center")

# ---------- (b) 一维压缩的应力 ----------
for a, c, lab in ((0.0, MUTED, "$a=0$（不硬化）"), (0.7, GREEN, "$a=0.7$"),
                  (3.0, ACCENT, "$a=3$")):
    s, sg = compress_1d(a)
    ax2.plot(s, sg, color=c, lw=1.9, label=lab)
    print("a=%.1f  sigma(压缩 0.5) = %.2f kPa" % (a, sg[-1]))

ax2.set_xlim(0, 0.52)
ax2.set_ylim(0, 17.5)
ax2.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
ax2.set_yticks([0, 5, 10, 15])
ax2.set_xlabel("压缩量 $1-J$")
ax2.set_ylabel("压应力（kPa）")
clean(ax2, spines=("left", "bottom"))
ax2.legend(loc="upper left", bbox_to_anchor=(0.02, 0.99), handlelength=1.8,
           borderaxespad=0.0, labelspacing=0.35, fontsize=8.0)

ax2.annotate("屈服点 $\\theta_c=0.025$", xy=(0.032, 3.15), xytext=(0.115, 1.35),
             fontsize=8, color=MUTED, ha="left", va="center",
             arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8,
                             shrinkA=2, shrinkB=2, mutation_scale=7,
                             connectionstyle="arc3,rad=-0.25"))
save(fig, "06", "fig06-01")


# ============================================================
# 图 6-2  泡沫的屈服（真实公式）
#   (a) Herschel-Bulkley: tau = tau0 + K gamma^n     式 (6.7)
#   (b) 表观黏度 tau/gamma                           式 (6.8)(6.9)
# ============================================================
TAU0 = 50.0     # 屈服应力 (Pa)
K = 80.0        # 稠度系数

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.15),
                               gridspec_kw=dict(wspace=0.27, bottom=0.175,
                                                top=0.955, left=0.085, right=0.985))

g = np.logspace(-3, 2, 500)

# ---------- (a) 流动曲线 ----------
for n, c, lab in ((0.4, GREEN, "$n=0.4$"), (1.0, ACCENT, "$n=1.0$（Bingham）"),
                  (1.6, PURPLE, "$n=1.6$")):
    ax1.loglog(g, TAU0 + K * g ** n, color=c, lw=1.9, label=lab)
ax1.loglog(g, K * g ** 1.0, color=BLUE, lw=1.1, ls=(0, (4, 2.5)),
           label="纯幂律 $K\\dot\\gamma^{\\,n}$")

ax1.axhline(TAU0, color=FAINT, lw=0.8, ls=(0, (2, 3)), zorder=1)
ax1.set_xlim(1e-3, 1e2)
ax1.set_ylim(0.5, 3e5)
ax1.set_xlabel("剪切速率 $\\dot\\gamma$（1/s）")
ax1.set_ylabel("剪应力 $\\tau$（Pa）")
clean(ax1, spines=("left", "bottom"))
ax1.legend(loc="upper left", bbox_to_anchor=(0.015, 0.99), handlelength=1.6,
           borderaxespad=0.0, labelspacing=0.32, fontsize=8.0)
ax1.text(1.3e-3, TAU0 * 1.35, "$\\tau_0=50$ Pa", fontsize=8, color=MUTED,
         ha="left", va="bottom")

# ---------- (b) 表观黏度 ----------
ax2.loglog(g, TAU0 / g + K, color=ACCENT, lw=1.9, label="Bingham（式 6.8）")
for m, c in ((10.0, GREEN), (100.0, PURPLE)):
    mu_reg = TAU0 * (1.0 - np.exp(-m * g)) / g + K
    ax2.loglog(g, mu_reg, color=c, lw=1.7, ls=(0, (5, 2.5)),
               label="$m=%d$ s" % int(m))
    print("m=%3d  低剪切率极限 tau0*m+K = %.0f Pa·s, 在 1e-3 处 %.0f"
          % (m, TAU0 * m + K, mu_reg[0]))

ax2.set_xlim(1e-3, 1e2)
ax2.set_ylim(60, 2e5)
ax2.set_xlabel("剪切速率 $\\dot\\gamma$（1/s）")
ax2.set_ylabel("表观黏度 $\\mu_{\\mathrm{app}}$（Pa·s）")
clean(ax2, spines=("left", "bottom"))
ax2.legend(loc="upper right", bbox_to_anchor=(0.995, 0.995), handlelength=2.0,
           borderaxespad=0.0, labelspacing=0.32, fontsize=8.0)
save(fig, "06", "fig06-02")
