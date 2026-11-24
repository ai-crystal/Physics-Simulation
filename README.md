# 物理模拟技术

> 一套八册的中文书：**把连续的世界切成计算机算得动的块**。

游戏里被风吹起的旗子、电影里塌掉的墙、手术训练里会回弹的组织、机器人学会走路之前在仿真里摔的上百万次，背后是同一件事：把物理定律离散化，在有限的时间里算出来，再让它看起来对。这套书从入门讲到可微物理，八册共用一套术语，可以按顺序读，也可以按需要切进去。

作者：**Dr. Dezeming**　·　2026 年 · 第一版

> 📖 **在线阅读**：<https://ai-crystal.github.io/Physics-Simulation/>
>
> 单册直达：`https://ai-crystal.github.io/Physics-Simulation/#/books/intro/chapters/ch01`

![封面](books/intro/images/cover_front.jpg)

## 八册一览

| 册 | 内容 | 章 | 页数 | 在线阅读 | PDF |
|---|---|---|---|---|---|
| **01 入门篇** | 从伽利略的斜面讲到可微求解器：历史、脉络、每类物质的主流方法与边界，不深挖公式。 | 12 | 109 | [阅读](books/intro/chapters/ch01.md) | <a href="output/ps-intro.pdf" target="_blank" rel="noopener">下载</a> |
| **02 数学基础** | 向量与旋转、应变应力、时间积分、稀疏求解、约束优化、有限元弱形式与离散微分几何。 | 12 | 117 | [阅读](books/math/chapters/ch01.md) | <a href="output/ps-math.pdf" target="_blank" rel="noopener">下载</a> |
| **03 刚体与碰撞** | 姿态与惯性张量、GJK、顺序冲量、LCP、摩擦锥、堆叠抖动，以及实时引擎的工程取舍。 | 12 | 100 | [阅读](books/rigid/chapters/ch01.md) | <a href="output/ps-rigid.pdf" target="_blank" rel="noopener">下载</a> |
| **04 柔体、布料与断裂** | 弹簧质点、PBD/XPBD、有限元与材料模型、投影动力学、壳与杆、自碰撞、断裂。 | 12 | — | 即将推出 | — |
| **05 流体、烟火与水面** | 纳维-斯托克斯逐项、投影、平流、涡量、SPH、FLIP/APIC、表面张力、燃烧与海洋。 | 13 | — | 即将推出 | — |
| **06 颗粒、雪与物质点法** | DEM、μ(I) 流变、MPM 与 MLS-MPM、雪与泡沫的本构、隐式 MPM、两相耦合。 | 11 | — | 即将推出 | — |
| **07 高性能实现与 GPU 并行** | 数据布局、稀疏网格、GPU 线性求解、粒子邻域、图着色、确定性与集群。 | 11 | — | 即将推出 | — |
| **08 可微物理与神经模拟** | 自动微分、伴随法、可微刚体/流体/柔体、逆问题、图网络、神经算子与 Sim-to-Real。 | 12 | — | 即将推出 | — |

<a id="下载"></a>

## 下载

- [01 入门篇 PDF](output/ps-intro.pdf)
- [02 数学基础 PDF](output/ps-math.pdf)
- [03 刚体与碰撞 PDF](output/ps-rigid.pdf)

## 怎么读

- **完全新手**：从入门篇开始，一个周末能读完，建立整张地图。
- **要动手写求解器**：数学基础第 4–7 章补积分与线性求解，再挑对应物质的专题册。
- **做游戏**：入门篇第 5、9 章，然后刚体册与高性能册。
- **做影视**：入门篇第 6–8 章，然后柔体册与流体册。
- **做机器人 / 具身智能**：可微物理册与高性能册，配合刚体册的接触部分。
- **做研究**：数学基础第 9–10 章与可微物理册是当前论文最密集的两块。

## 这套书的特点

- 公式用 KaTeX 排版，网页可读，PDF 里可复制。
- 插图全部由代码生成，脚本在 `books/code/<册>/chNN/`，改参数即可重画。
- 每类方法都讲它为什么长成这样、在什么地方会失效，而不只是步骤。
- 涉及性能对比的图只使用有出处的数据；没有可靠来源时明确标注为示意图。

## 仓库结构

```text
index.html  _sidebar.md  _coverpage.md  README.md  .nojekyll
output/                 各册 PDF
books/
  build/                构建脚本、样式、参考文献元数据
  code/figstyle.py      共用绘图风格；books/code/<册>/chNN/ 是各章绘图脚本
  <册>/book.json        书名、副标题、卷号、输出文件名、强调色
  <册>/structure.json   章节顺序（唯一来源）
  <册>/chapters/        正文
  <册>/appendix/        术语、时间线、参考文献
  <册>/images/NN/       插图（正文写 ../images/NN/x.png）
```

## 本地构建

需要 Python 3.10 以上、Chrome 或 Edge。Windows 上双击 `build-intro.bat` 只构建入门篇，`build.bat` 构建全部。
