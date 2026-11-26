# 物理模拟技术

> 把连续的世界切成计算机算得动的块

游戏里被风吹起的旗子、电影里塌掉的墙、手术训练里会回弹的组织、机器人学会走路之前在仿真里摔的上百万次，背后是同一件事：把物理定律离散化，在有限的时间里算出来，再让它看起来对。

这套书从入门讲到可微物理，八册共用一套术语。每类方法都讲它为什么长成这样、在什么地方会失效，而不只是步骤。

作者：Dr. Dezeming　·　2026

**在线阅读**：[在线阅读站](https://ai-crystal.github.io/Physics-Simulation/)　·　**仓库**：[GitHub 仓库](https://github.com/ai-crystal/Physics-Simulation)

## 分册

| 册 | 书名 | 一句话 | 页数 | 在线阅读 | PDF |
| --- | --- | --- | ---: | --- | --- |
| 01 | [入门篇](books/intro/README.md) | 从抛物线到可微世界 | 109 | [阅读](books/intro/README.md) | <a href="output/v1-intro.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 02 | [数学基础](books/math/README.md) | 描述运动与变形的语言 | 117 | [阅读](books/math/README.md) | <a href="output/v2-math.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 03 | [刚体与碰撞](books/rigid/README.md) | 让物体撞在一起 | 137 | [阅读](books/rigid/README.md) | <a href="output/v3-rigid.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 04 | [柔体、布料与断裂](books/deform/README.md) | 会皱、会断、会回弹 | 152 | [阅读](books/deform/README.md) | <a href="output/v4-deform.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 05 | [流体、烟火与水面](books/fluid/README.md) | 把连续介质装进格子 | 110 | [阅读](books/fluid/README.md) | <a href="output/v5-fluid.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 06 | [颗粒、雪与物质点法](books/particle/README.md) | 沙、雪、泡沫与岩浆 | 132 | [阅读](books/particle/README.md) | <a href="output/v6-particle.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 07 | [高性能实现与 GPU 并行](books/gpu/README.md) | 一帧十六毫秒的预算 | 92 | [阅读](books/gpu/README.md) | <a href="output/v7-gpu.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |
| 08 | [可微物理与神经模拟](books/diff/README.md) | 让梯度穿过时间 | 103 | [阅读](books/diff/README.md) | <a href="output/v8-diff.pdf" target="_blank" rel="noopener" data-router-ignore>下载</a> |

## 怎么读

- 完全新手：从入门篇开始，一个周末能读完，建立整张地图。
- 要动手写求解器：先补数学基础的积分与线性求解，再挑对应物质的专题册。
- 做游戏：看入门篇的刚体与实时章节，然后刚体册与高性能册。
- 做影视：看柔体册与流体册。
- 做机器人 / 具身智能：看可微物理册与高性能册，配合刚体册的接触部分。

## 许可

本系列文字与插图采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可发布，转载请注明作者与出处。书中引用的论文、数据集与模型归各自作者所有。

---

作者：Dr. Dezeming　·　2026
