# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 拉格朗日描述 | Lagrangian description | 跟着物质微团记录状态 |
| 欧拉描述 | Eulerian description | 在固定空间位置上记录状态 |
| 物质导数 | material derivative | 随体变化率，等于局部变化加对流变化 |
| 纳维-斯托克斯方程 | Navier-Stokes equations | 粘性流体的动量方程加不可压条件 |
| 不可压 | incompressible | 速度场散度为零 |
| 雷诺数 | Reynolds number | 惯性力与粘性力之比 |
| 算子分裂 | operator splitting | 把一帧拆成若干子步分别求解 |
| 投影 | projection | 减去压力梯度使速度满足不可压条件 |
| 压力泊松方程 | pressure Poisson equation | 由散度约束导出的椭圆型方程 |
| MAC 网格 | marker-and-cell grid | 速度与压力交错存储的网格 |
| 半拉格朗日平流 | semi-Lagrangian advection | 回溯上一时刻位置并插值的平流方法 |
| 数值耗散 | numerical dissipation | 离散格式导致的非物理能量损失 |
| 数值色散 | numerical dispersion | 不同波数传播速度不同导致的振铃 |
| 迎风格式 | upwind scheme | 按流动方向取偏导的离散格式 |
| BFECC | back and forth error compensation and correction | 正反两次平流抵消误差的方法 |
| 涡量 | vorticity | 速度场的旋度 |
| 涡量约束 | vorticity confinement | 人工补回被耗散的小尺度涡 |
| 涡粒子 | vortex particle | 用粒子携带涡量的拉格朗日方法 |
| 湍流 | turbulence | 多尺度、非定常的流动状态 |
| 能级串 | energy cascade | 能量从大尺度向小尺度传递的过程 |
| 水平集 | level set | 用高维函数零等值面表示界面 |
| 符号距离场 | signed distance field | 带符号的距离函数 |
| 体积分数 | volume of fluid (VOF) | 网格内流体所占体积比例 |
| 界面重构 | interface reconstruction | 由体积分数重建界面几何 |
| 光滑粒子流体动力学 | smoothed particle hydrodynamics (SPH) | 用核加权近似场量的粒子方法 |
| 核函数 | kernel function | 粒子方法中决定影响范围的权重函数 |
| 光滑长度 | smoothing length | 核函数的支持半径 |
| 状态方程 | equation of state | 密度与压力的关系 |
| 张力不稳定 | tensile instability | 负压导致粒子聚团的不稳定 |
| 粒子网格法 | particle-in-cell (PIC) | 粒子与网格之间传递量的方法 |
| FLIP | fluid-implicit-particle | 保留速度增量的 PIC 改进 |
| APIC | affine particle-in-cell | 粒子携带仿射速度场的改进 |
| 表面张力 | surface tension | 界面收缩的力，用 Laplace 压差描述 |
| 连续表面力 | continuum surface force (CSF) | 把表面张力写成体积力的模型 |
| 多相流 | multiphase flow | 两种以上不相溶流体共存 |
| 接触角 | contact angle | 界面与固体壁面的夹角 |
| 浮力 | buoyancy | 密度差产生的上升力 |
| 黑体辐射 | blackbody radiation | 温度决定发光颜色的物理模型 |
| 体积渲染 | volumetric rendering | 直接对参与介质积分成像 |
| 波谱 | wave spectrum | 海面高度场的统计能量分布 |
| 快速傅里叶变换 | fast Fourier transform (FFT) | 合成海面高度场的常用工具 |
| 浅水方程 | shallow water equations | 水平尺度远大于深度的近似方程 |
| 白水 | whitewater | 泡沫、浪花、水雾等非连续水体 |
| 附加质量 | added mass | 物体加速时带动的流体等效质量 |
| 浸没边界 | immersed boundary | 在固定网格上表示运动边界的方法 |
| 区域分解 | domain decomposition | 把计算域切块并行求解 |
