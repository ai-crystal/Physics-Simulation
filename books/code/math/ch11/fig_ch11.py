import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import matplotlib.ticker as mticker

# ============================================================
# 图 11-1  高斯先验 × 高斯似然 → 高斯后验（真实计算）
#   先验   N(1.00, 0.80^2)
#   似然   5 次测量，单次标准差 0.50，样本均值 1.62 → N(1.62, (0.50/sqrt(5))^2)
#   后验   精度相加：1/s^2 = 1/0.8^2 + 5/0.5^2
# ============================================================
mu0, s0 = 1.00, 0.80
n_obs, s_obs = 5, 0.50
xbar = 1.62

prec = 1.0 / s0**2 + n_obs / s_obs**2
mu_p = (mu0 / s0**2 + xbar * n_obs / s_obs**2) / prec
s_p = 1.0 / np.sqrt(prec)
s_like = s_obs / np.sqrt(n_obs)
print("后验 均值 %.4f 标准差 %.4f；似然标准差 %.4f" % (mu_p, s_p, s_like))

th = np.linspace(-0.75, 2.95, 900)
prior = np.exp(-0.5 * ((th - mu0) / s0)**2) / (s0 * np.sqrt(2 * np.pi))
like = np.exp(-0.5 * ((th - xbar) / s_like)**2) / (s_like * np.sqrt(2 * np.pi))
post = np.exp(-0.5 * ((th - mu_p) / s_p)**2) / (s_p * np.sqrt(2 * np.pi))

fig, ax = new(6.8, 3.8)
clean(ax, grid=True, spines=("left", "bottom"))
ax.set_xlim(-0.75, 2.95)
ax.set_ylim(0, 2.12)

ax.fill_between(th, 0, prior, color=BLUE, alpha=0.10, zorder=2)
ax.plot(th, prior, color=BLUE, lw=1.3, zorder=3,
        label="先验  $\\mu_0=1.00,\\ \\sigma_0=0.80$")

k = 0.62 / like.max()          # 似然只画形状，按峰值缩放到 0.62
ax.plot(th, k * like, color=MUTED, lw=1.2, ls=(0, (5, 3)), zorder=3,
        label="似然（按峰值缩放）$\\bar{x}=1.62,\\ \\sigma=0.50/\\sqrt{5}$")

ax.fill_between(th, 0, post, color=ACCENT, alpha=0.13, zorder=2)
ax.plot(th, post, color=ACCENT, lw=1.8, zorder=4,
        label="后验  $\\mu=%.2f,\\ \\sigma=%.2f$" % (mu_p, s_p))

for v, c in ((mu0, BLUE), (xbar, MUTED), (mu_p, ACCENT)):
    ax.plot([v, v], [0, 1.72], color=c, lw=0.8, ls=":", zorder=1)

ax.set_xlabel("参数 $\\theta$（例如刚度 $k$，N/m）")
ax.set_ylabel("概率密度（任意单位）")
ax.set_yticks([])
ax.legend(loc="upper left", bbox_to_anchor=(0.005, 0.80), fontsize=8.5,
          handlelength=2.2, labelspacing=0.75, borderaxespad=0.2)

ax.text(0.015, 0.975,
        "先验精度 %.3f $\\rightarrow$ 后验精度 %.3f，峰高变为 %.1f 倍"
        % (1 / s0**2, prec, post.max() / prior.max()),
        transform=ax.transAxes, fontsize=8.4, color=INK, va="top")

save(fig, "11", "fig11-01")

# ============================================================
# 图 11-2  线性最小二乘与三次最小二乘：拟合曲线与残差（真实数据）
#   数据  F(x) = k x + beta x^3 + 噪声，k=12 N/m, beta=300 N/m^3,
#         x 在 [0.02, 0.50] m 上取 40 点，噪声 N(0, 0.05^2)，seed=7
# ============================================================
rng = np.random.default_rng(7)
N = 40
x = np.linspace(0.02, 0.50, N)
k_true, b_true, sig = 12.0, 300.0, 0.05
y = k_true * x + b_true * x**3 + sig * rng.standard_normal(N)

A1 = np.column_stack([np.ones(N), x])
A3 = np.column_stack([np.ones(N), x, x**2, x**3])
c1 = np.linalg.lstsq(A1, y, rcond=None)[0]
c3 = np.linalg.lstsq(A3, y, rcond=None)[0]
r1 = y - A1 @ c1
r3 = y - A3 @ c3
print("线性拟合: k=%.2f  F0=%.2f  残差 rms=%.4f" %
      (c1[1], c1[0], np.sqrt((r1**2).mean())))
print("三次拟合: k=%.2f beta=%.1f c2=%.2f  残差 rms=%.4f" %
      (c3[1], c3[3], c3[2], np.sqrt((r3**2).mean())))
print("cond(A1)=%.0f  cond(A3)=%.0f  cond(A3'A3)=%.2e" %
      (np.linalg.cond(A1), np.linalg.cond(A3), np.linalg.cond(A3.T @ A3)))

xs = np.linspace(0.0, 0.52, 400)
y1 = c1[0] + c1[1] * xs
y3 = c3[0] + c3[1] * xs + c3[2] * xs**2 + c3[3] * xs**3

fig, (ax1, ax2) = new(6.9, 3.5, ncols=2, gridspec_kw={"width_ratios": [1.2, 1.0],
                                                       "wspace": 0.30})
for a in (ax1, ax2):
    clean(a, grid=True, spines=("left", "bottom"))

ax1.plot(xs, y3, color=ACCENT, lw=1.7, zorder=3, label="三次模型")
ax1.plot(xs, y1, color=MUTED, lw=1.4, ls=(0, (5, 3)), zorder=3, label="线性模型")
ax1.plot(x, y, "o", ms=3.6, color=INK, mfc="white", mew=0.9, zorder=4, label="测量点")
ax1.set_xlim(0, 0.52)
ax1.set_ylim(-3, 64)
ax1.set_xlabel("位移 $x$ (m)")
ax1.set_ylabel("力 $F$ (N)")
ax1.legend(loc="upper left", fontsize=8.4, handlelength=2.0, borderaxespad=0.3)
ax1.text(0.045, 20.0, "真值 $k=12$，$\\beta=300$", fontsize=8.2, color=FAINT,
         va="bottom", ha="left")
ax1.text(0.035, 33.0, "$\\hat{k}=%.2f$\n$\\hat{\\beta}=%.0f$" % (c3[1], c3[3]),
         fontsize=8.6, color=ACCENT, va="bottom", ha="left")

ax2.axhline(0, color=FAINT, lw=0.9, zorder=1)
ax2.axhspan(-2 * sig, 2 * sig, color=GRID, alpha=0.55, zorder=0)
ax2.plot(x, r1, "o", ms=3.2, color=MUTED, mfc="none", mew=0.9, zorder=3, label="线性模型")
ax2.plot(x, r3, "o", ms=3.6, color=ACCENT, mfc="white", mew=0.9, zorder=4, label="三次模型")
ax2.set_xlim(0, 0.52)
ax2.set_ylim(-7.0, 7.0)
ax2.set_xlabel("位移 $x$ (m)")
ax2.set_ylabel("残差 $F-\\hat{F}$ (N)")
ax2.legend(loc="lower left", fontsize=8.2, handlelength=1.6, labelspacing=0.45,
           borderaxespad=0.4)
ax2.annotate("$\\pm2\\sigma$", xy=(0.505, 0.10), xytext=(0.505, 1.35),
             fontsize=8.0, color=MUTED, ha="right",
             arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))

save(fig, "11", "fig11-02")

# ============================================================
# 图 11-3  Tikhonov 正则化：L 曲线与三个 lambda 下的解（真实计算）
#   A 为高斯核第一类积分算子的离散化，A(s,t)=exp(-(s-t)^2/(2c^2))*h
#   c = 0.05，[0,1] 上 N=80 点，真解 x(t)=1+0.55 exp(-((t-0.36)/0.10)^2)
#   数据 b = A x + 噪声，sigma=0.02，seed=3；罚项 lambda^2 * ||x||^2
# ============================================================
N2 = 80
s = np.linspace(0, 1, N2)
h = s[1] - s[0]
cw = 0.05
A = np.exp(-(s[:, None] - s[None, :])**2 / (2 * cw**2)) * h
x_true = 1.0 + 0.55 * np.exp(-((s - 0.36) / 0.10)**2)
rng = np.random.default_rng(3)
sig_n = 0.02
b = A @ x_true + sig_n * rng.standard_normal(N2)

KtK = A.T @ A
Ktb = A.T @ b
I = np.eye(N2)
lam_all = np.logspace(-7, -0.45, 140)


def tik(lam):
    return np.linalg.solve(KtK + lam**2 * I, Ktb)


res_all, sol_all, err_all = [], [], []
for lm in lam_all:
    xx = tik(lm)
    res_all.append(np.linalg.norm(A @ xx - b))
    sol_all.append(np.linalg.norm(xx))
    err_all.append(np.linalg.norm(xx - x_true))
res_all, sol_all, err_all = map(np.array, (res_all, sol_all, err_all))
i_best = int(np.argmin(err_all))
lam_best = lam_all[i_best]
print("cond(A)=%.2e  最优 lambda=%.4f  相对误差=%.3f"
      % (np.linalg.cond(A), lam_best, err_all[i_best] / np.linalg.norm(x_true)))

pick = [(1.0e-2, "偏小", MUTED), (lam_best, "拐角", ACCENT), (1.0e-1, "偏大", BLUE)]
for lm, tag, _c in pick:
    xx = tik(lm)
    print("  lambda=%.2e [%s]  |x|=%.2f  |Ax-b|=%.4f  相对误差=%.3f"
          % (lm, tag, np.linalg.norm(xx), np.linalg.norm(A @ xx - b),
             np.linalg.norm(xx - x_true) / np.linalg.norm(x_true)))

fig, (ax1, ax2) = new(6.9, 3.5, ncols=2, gridspec_kw={"width_ratios": [1.0, 1.08],
                                                      "wspace": 0.30})
for a in (ax1, ax2):
    clean(a, grid=True, spines=("left", "bottom"))

ax1.loglog(res_all, sol_all, color=INK, lw=1.5, zorder=3)
ax1.set_xticks([0.2, 0.3, 0.5, 1.0, 2.0])
ax1.set_xticklabels(["0.2", "0.3", "0.5", "1.0", "2.0"])
ax1.xaxis.set_minor_locator(mticker.NullLocator())
ax1.xaxis.set_minor_formatter(mticker.NullFormatter())
ax1.set_yticks([1, 10, 100, 1000])
ax1.set_yticklabels(["1", "10", "100", "1000"])
ax1.yaxis.set_minor_locator(mticker.NullLocator())
ax1.yaxis.set_minor_formatter(mticker.NullFormatter())

pos = {}
for lm, tag, c in pick:
    xx = tik(lm)
    rr, sl = np.linalg.norm(A @ xx - b), np.linalg.norm(xx)
    pos[tag] = (rr, sl)

# 只标拐角与 lambda=0.1 两点；lambda=1e-2 落在竖直段上，标了会盖住拐角
for tag, c, ms in (("拐角", ACCENT, 6.2), ("偏大", BLUE, 6.2)):
    ax1.plot([pos[tag][0]], [pos[tag][1]], "o", ms=ms, mfc="white", mew=1.4,
             color=c, zorder=5)

ax1.annotate("$\\lambda=%.2f$（拐角）" % lam_best, xy=pos["拐角"], xytext=(0.28, 26),
             fontsize=8.2, color=ACCENT,
             arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
ax1.annotate("$\\lambda=0.1$", xy=pos["偏大"], xytext=(0.72, 13),
             fontsize=8.2, color=BLUE,
             arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.8))
ax1.set_xlabel("残差 $\\|\\mathbf{Ax}-\\mathbf{b}\\|$")
ax1.set_ylabel("解范数 $\\|\\mathbf{x}\\|$")
ax1.set_xlim(0.15, 2.6)
ax1.set_ylim(0.55, 2.2e3)
ax1.text(0.31, 1.1e3, "$\\lambda$ 减小：解被噪声放大", fontsize=8.2,
         color=MUTED, ha="left", va="top")
ax1.text(0.163, 1.05, "$\\lambda$ 增大：解被压向零", fontsize=8.2,
         color=BLUE, ha="left", va="bottom")

ax2.plot(s, x_true, color=INK, lw=1.8, zorder=5, label="真解")
ax2.plot(s, tik(1.0e-2), color=MUTED, lw=1.2, ls=(0, (4, 2.5)), zorder=4,
         label="$\\lambda=10^{-2}$")
ax2.plot(s, tik(lam_best), color=ACCENT, lw=1.3, zorder=4,
         label="$\\lambda=%.2f$（拐角）" % lam_best)
ax2.plot(s, tik(1.0e-1), color=BLUE, lw=1.4, ls=(0, (1.3, 1.9)), zorder=4,
         label="$\\lambda=0.1$")
ax2.set_xlim(0, 1)
ax2.set_ylim(-0.35, 2.15)
ax2.set_xlabel("$t$")
ax2.set_ylabel("$x(t)$")
ax2.legend(loc="upper right", fontsize=8.2, handlelength=2.3, labelspacing=0.55,
           borderaxespad=0.3)
ax2.text(0.03, -0.28, "$N=80$，噪声 $\\sigma=0.02$", fontsize=8.0, color=MUTED,
         ha="left", va="bottom")

save(fig, "11", "fig11-03")
