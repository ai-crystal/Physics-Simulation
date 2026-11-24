# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 颗粒物质 | granular material | 由大量离散颗粒组成的物质 |
| 休止角 | angle of repose | 颗粒堆能保持稳定的最大坡角 |
| 粮仓效应 | silo effect | 容器底部压力随深度趋于饱和的现象 |
| 剪切带 | shear band | 颗粒流动集中的狭窄区域 |
| 离散元 | discrete element method (DEM) | 逐颗粒计算接触与运动的数值方法 |
| 接触模型 | contact model | 描述颗粒间法向与切向力的本构 |
| 恢复系数 | coefficient of restitution | 碰撞前后法向速度之比 |
| 滚动阻力 | rolling resistance | 抵抗颗粒滚动的力矩 |
| 惯性数 | inertial number | 剪切时间尺度与约束时间尺度之比 |
| μ(I) 流变 | μ(I) rheology | 摩擦系数随惯性数变化的连续体本构 |
| 屈服面 | yield surface | 应力空间中开始塑性变形的边界 |
| 剪胀 | dilatancy | 剪切时体积膨胀的现象 |
| 物质点法 | material point method (MPM) | 粒子携带物质、网格求解动量的方法 |
| 粒子到网格 | particle-to-grid (P2G) | 把粒子量加权搬到网格 |
| 网格到粒子 | grid-to-particle (G2P) | 把网格结果插值回粒子 |
| 形函数 | shape function | 粒子对网格节点的权重函数 |
| B 样条 | B-spline | 常用的一类紧支撑形函数 |
| 仿射粒子网格法 | affine particle-in-cell (APIC) | 粒子携带仿射速度场的 MPM 变体 |
| MLS-MPM | moving least squares MPM | 用移动最小二乘简化 P2G 的 MPM |
| 变形梯度 | deformation gradient | 描述局部变形与旋转的量 |
| 本构模型 | constitutive model | 应力与变形历史的关系 |
| 压实 | compaction | 颗粒在压力下体积减小的过程 |
| 相变 | phase change | 融化、凝固等物质状态变化 |
| 潜热 | latent heat | 相变时吸收或释放的热量 |
| 两相流 | two-phase flow | 颗粒与流体共同运动 |
| 拖曳力 | drag force | 流体对颗粒的阻力 |
| 孔隙压力 | pore pressure | 流体在颗粒间隙中的压力 |
| 有效应力 | effective stress | 总应力减去孔隙压力 |
| 区域分解 | domain decomposition | 把计算域切块并行 |
| 空间哈希 | spatial hashing | 用网格桶加速邻居查询 |
| 半排序 | partial sorting | 按网格单元对粒子做局部排序 |
| 原子操作 | atomic operation | 并行写入时保证不冲突的操作 |
| 分层细节 | level of detail (LOD) | 按距离或重要性降低精度 |
| 初始堆积 | packing | 生成颗粒初始分布的过程 |
| 泊松盘采样 | Poisson disk sampling | 保证最小间距的随机采样 |
