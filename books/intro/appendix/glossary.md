# 术语中英对照

下表只收录正文里出现、且容易混淆的词。释义按本书的用法写，不追求词典式的完整。

| 中文 | 英文 | 说明 |
|---|---|---|
| 物理模拟 | physics simulation | 用数值方法求解物理方程，得到随时间演化的状态 |
| 刚体 | rigid body | 形状与质量分布不随运动改变的物体，状态由位置与姿态决定 |
| 柔体 | deformable body | 受力后形状会改变的连续介质，状态是位移场 |
| 连续介质 | continuum | 把物质看成处处有定义的场，不追踪单个分子 |
| 离散化 | discretization | 把连续的场或方程换成有限个未知量 |
| 自由度 | degree of freedom | 描述系统状态所需的独立变量个数 |
| 时间步 | time step | 把连续时间切成的小段，记作 $\Delta t$ |
| 显式积分 | explicit integration | 用当前时刻的力直接算出下一时刻的状态 |
| 隐式积分 | implicit integration | 力的取值依赖下一时刻状态，需要解方程 |
| 半隐式欧拉 | semi-implicit Euler | 先更新速度再用新速度更新位置，稳定性和显式不同 |
| 辛积分 | symplectic integrator | 能保持相空间体积的积分器，长期能量行为较好 |
| 刚性方程 | stiff equation | 包含多个差距很大的时间尺度的方程，显式方法步长被最小尺度限制 |
| CFL 条件 | Courant-Friedrichs-Lewy condition | 显式格式的稳定性对步长与网格尺寸的限制 |
| 截断误差 | truncation error | 用有限阶公式近似导数带来的误差 |
| 条件数 | condition number | 输入微小扰动被放大多少的度量 |
| 有限差分 | finite difference | 用网格点上的差商近似导数 |
| 有限体积 | finite volume | 在控制体上积分守恒律，保证通量守恒 |
| 有限元 | finite element method (FEM) | 用形函数在单元内插值，把弱形式化成线性系统 |
| 弱形式 | weak form | 把方程乘测试函数并分部积分后的等价形式，降低对光滑性的要求 |
| 形函数 | shape function | 单元内用节点值插值场量的基函数 |
| 锁死 | locking | 单元在近不可压或细长情况下表现得过刚 |
| 无网格法 | meshfree method | 不依赖固定拓扑连接，用核函数或点集近似场 |
| 光滑粒子流体动力学 | smoothed particle hydrodynamics (SPH) | 用核加权求和近似场量与导数的粒子方法 |
| 物质点法 | material point method (MPM) | 粒子携带物质状态、背景网格求解动量方程的方法 |
| 粒子网格法 | particle-in-cell (PIC) | 粒子与网格之间来回传递量的一类方法 |
| FLIP | fluid-implicit-particle | PIC 的改进，粒子保留速度增量以减少耗散 |
| APIC | affine particle-in-cell | 粒子携带仿射速度场，显著减少角动量损失 |
| 水平集 | level set | 用高维函数的零等值面表示界面 |
| 有向距离场 | signed distance field (SDF) | 每点到界面带符号的距离，负值表示内部 |
| 体积分数 | volume of fluid (VOF) | 用网格内流体所占比例表示界面 |
| 投影 | projection | 把速度场减去压力梯度，使其满足不可压条件 |
| 泊松方程 | Poisson equation | 形如 $\nabla^2 p = f$ 的椭圆型方程，压力求解的核心 |
| 半拉格朗日平流 | semi-Lagrangian advection | 沿速度回溯上一时刻位置并插值，无条件稳定但会耗散 |
| 数值耗散 | numerical dissipation | 离散格式带来的非物理能量损失，表现为细节被抹平 |
| 涡量 | vorticity | 速度场的旋度，描述局部旋转 |
| 涡量约束 | vorticity confinement | 人工补回被耗散掉的小尺度涡 |
| 库仑摩擦 | Coulomb friction | 切向力不超过法向力乘以摩擦系数 |
| 互补条件 | complementarity condition | 接触力与间隙不能同时为正的一类约束关系 |
| 线性互补问题 | linear complementarity problem (LCP) | 接触力学里常见的一类互补问题 |
| 投影高斯-赛德尔 | projected Gauss-Seidel (PGS) | 逐约束迭代并在每步投影到可行域，接触求解常用 |
| 顺序冲量 | sequential impulses | 逐个接触施加冲量并迭代，游戏引擎常用 |
| 位置动力学 | position based dynamics (PBD) | 直接投影位置满足约束，再由位置反推速度 |
| XPBD | extended position based dynamics | 引入柔度参数，使刚度与迭代次数解耦 |
| 投影动力学 | projective dynamics | 把隐式求解拆成局部投影与全局线性求解交替 |
| 局部-全局 | local-global | 先对每个单元独立求解，再全局耦合的一类交替格式 |
| 共轭梯度 | conjugate gradient (CG) | 求解对称正定稀疏系统的迭代法 |
| 多重网格 | multigrid | 在粗细多层网格间转移残差，快速消除低频误差 |
| 预条件 | preconditioning | 把原系统变成条件数更小的等价系统 |
| 子空间模拟 | subspace simulation | 在低维基上求解，用少量自由度近似大幅形变 |
| 连续碰撞检测 | continuous collision detection (CCD) | 在时间区间内检测是否发生穿透，而不只看离散帧 |
| 自碰撞 | self-collision | 同一物体不同部分之间的碰撞，布料与毛发常见 |
| 增量势接触 | incremental potential contact (IPC) | 把接触写成势能并保证不穿透、不翻转的求解框架 |
| 伴随法 | adjoint method | 通过解一个反向方程计算梯度，代价与参数维数无关 |
| 自动微分 | automatic differentiation | 对程序本身做符号求导，得到精确到机器精度的梯度 |
| 可微模拟 | differentiable simulation | 整个时间步进可求导，梯度可穿过求解器 |
| 神经算子 | neural operator | 学习函数到函数的映射，输入输出都是场 |
| 图网络 | graph neural network (GNN) | 在节点与边上做消息传递的网络，适合粒子与网格 |
| 物理约束网络 | physics-informed neural network (PINN) | 把方程残差写进损失函数的网络 |
| 仿真到现实 | sim-to-real | 在仿真里训练、迁移到真实系统的做法 |
