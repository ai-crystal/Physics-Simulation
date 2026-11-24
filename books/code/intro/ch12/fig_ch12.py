import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *


# ---------------------------------------------------------------- 图 12-1
def fig01():
    fig, ax = canvas(6.9, 4.4)

    cols = ["刚体", "布料薄壳", "颗粒", "流体", "断裂多相"]
    rows = ["学习型", "约束与位置", "粒子-网格混合", "欧拉网格", "拉格朗日粒子"]
    cells = [
        ["GNS", "MeshGraph", "GNS 沙", "FNO / 卷积", "—"],
        ["顺序冲量", "PBD / XPBD", "—", "PBF", "—"],
        ["—", "—", "MPM / DEM", "FLIP", "MPM 相变"],
        ["—", "—", "—", "Stable Fluids", "水平集"],
        ["—", "质点弹簧", "DEM", "SPH", "—"],
    ]
    row_tint = [SOFT[3], SOFT[2], SOFT[0], SOFT[1], SOFT[4]]

    x0, y0 = 0.245, 0.055
    w, h = 0.730, 0.775
    cw, ch = w / len(cols), h / len(rows)

    for i, c in enumerate(cols):
        label(ax, x0 + (i + 0.5) * cw, y0 + h + 0.045, c, fs=8.8, color=INK)
    for j, r in enumerate(rows):
        label(ax, x0 - 0.016, y0 + h - (j + 0.5) * ch, r, fs=8.6, color=INK, ha="right")

    for j in range(len(rows)):
        for i in range(len(cols)):
            ax.add_patch(Rectangle((x0 + i * cw, y0 + h - (j + 1) * ch), cw, ch,
                                   facecolor=row_tint[j], edgecolor="white", lw=1.4, zorder=1))
            txt = cells[j][i]
            if txt == "—":
                label(ax, x0 + (i + 0.5) * cw, y0 + h - (j + 0.5) * ch, "—",
                      fs=9, color="#D1D5DB")
            else:
                label(ax, x0 + (i + 0.5) * cw, y0 + h - (j + 0.5) * ch, txt,
                      fs=8.0, color=INK)

    label(ax, x0 + w / 2, 0.018, "物质类型", fs=8.6, color=MUTED)
    label(ax, 0.014, y0 + h / 2, "方法家族", fs=8.4, color=MUTED, rot=90)
    save(fig, "12", "fig12-01")


# ---------------------------------------------------------------- 图 12-2
def fig02():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("工程成熟度")
    ax.set_ylabel("需求强度")
    ax.set_xticks([])
    ax.set_yticks([])
    clean(ax)

    ax.add_patch(Rectangle((0, 0.55), 0.58, 0.45, facecolor=SOFT[0], edgecolor="none",
                           alpha=0.75, zorder=0))
    ax.add_patch(Rectangle((0, 0.55), 0.58, 0.45, facecolor="none", edgecolor=ACCENT,
                           hatch="///", lw=0.7, alpha=0.35, zorder=1))
    label(ax, 0.035, 0.985, "需求强、成熟度不够", fs=8.4, color=ACCENT, ha="left", va="top")

    solved = [(0.860, 0.880, "烟雾"), (0.760, 0.755, "离线布料"),
              (0.940, 0.600, "刚体堆叠"), (0.680, 0.500, "雪与沙"),
              (0.820, 0.675, "GPU 百万粒子")]
    hard = [(0.335, 0.945, "实时高保真流体"), (0.455, 0.825, "可微接触"),
            (0.235, 0.715, "艺术可控"), (0.375, 0.625, "跨尺度耦合"),
            (0.195, 0.495, "结果验证"), (0.295, 0.375, "统一框架")]

    for x, y, t in solved:
        ax.scatter([x], [y], s=52, marker="s", color=GREEN, alpha=0.85, zorder=4,
                   linewidths=0)
        label(ax, x - 0.020, y, t, fs=8.2, color=GREEN, ha="right")
    for x, y, t in hard:
        ax.scatter([x], [y], s=52, color=ACCENT, alpha=0.85, zorder=4, linewidths=0)
        if t == "跨尺度耦合":
            label(ax, x - 0.020, y, t, fs=8.2, color=ACCENT, ha="right")
        else:
            label(ax, x + 0.020, y, t, fs=8.2, color=ACCENT, ha="left")

    ax.scatter([0.06], [0.10], s=52, marker="s", color=GREEN, alpha=0.85, linewidths=0)
    label(ax, 0.09, 0.10, "已经够用", fs=8.4, color=GREEN, ha="left")
    ax.scatter([0.06], [0.045], s=52, color=ACCENT, alpha=0.85, linewidths=0)
    label(ax, 0.09, 0.045, "仍然缺方法", fs=8.4, color=ACCENT, ha="left")
    save(fig, "12", "fig12-02")


# ---------------------------------------------------------------- 图 12-3
def fig03():
    fig, ax = canvas(6.9, 3.5)

    heads = ["游戏", "影视", "机器人", "科研"]
    cols = [
        ["位置动力学\nPBD / XPBD", "顺序冲量\n与子步", "确定性与\n回滚", "预算与休眠"],
        ["现成解算器\nVellum / FLIP", "缓存与分层", "引导与控制力", "局部重算"],
        ["MuJoCo / Isaac", "域随机化", "接触与\n系统辨识", "并行与可微"],
        ["复现一篇", "换边界\n找失效场景", "设计验证", "提出新方法"],
    ]
    colors = [BLUE, ACCENT, GREEN, PURPLE]
    tints = [SOFT[1], SOFT[0], SOFT[2], SOFT[3]]

    bw, bh = 0.200, 0.130
    xs = [0.145, 0.385, 0.625, 0.865]
    ys = [0.720, 0.520, 0.320, 0.120]

    for k, (hd, col, c, tn) in enumerate(zip(heads, cols, colors, tints)):
        label(ax, xs[k], 0.930, hd, fs=9.6, color=c, weight="bold")
        for i, txt in enumerate(col):
            box(ax, xs[k] - bw / 2, ys[i], bw, bh, txt, fc=tn if i == 0 else "white",
                ec=c, fs=8.4)
            if i:
                arrow(ax, (xs[k], ys[i - 1]), (xs[k], ys[i] + bh), color=c, lw=1.0,
                      alpha=0.55)
    label(ax, 0.505, 0.045, "每列由上到下：先做什么，最后补什么", fs=8.2, color=MUTED)
    save(fig, "12", "fig12-03")


fig01()
fig02()
fig03()
