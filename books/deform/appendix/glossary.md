# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 柔体 | deformable body | 形状会随受力改变的连续介质 |
| 弹簧质点模型 | mass-spring system | 用质点与弹簧近似连续体 |
| 结构弹簧 | structural spring | 沿网格边连接相邻质点的弹簧 |
| 剪切弹簧 | shear spring | 连接对角线、抵抗剪切变形的弹簧 |
| 弯曲弹簧 | bending spring | 跨过一个顶点、抵抗弯曲的弹簧 |
| 刚度 | stiffness | 抵抗变形的能力，弹簧模型中的 $k$ |
| 位置动力学 | position based dynamics (PBD) | 直接投影位置满足约束的方法 |
| XPBD | extended position based dynamics | 引入柔度、使刚度与迭代次数解耦的 PBD |
| 柔度 | compliance | 刚度的倒数，XPBD 中的 $\alpha$ |
| 子步 | substep | 一帧内切分的多个物理步 |
| 有限元 | finite element method (FEM) | 用形函数在单元内插值场量的方法 |
| 应变能密度 | strain energy density | 单位参考体积储存的弹性能 |
| 变形梯度 | deformation gradient | 参考构型到当前构型的局部线性映射 |
| 第一类皮奥拉-基尔霍夫应力 | first Piola-Kirchhoff stress | 参考构型上的应力度量，与变形梯度共轭 |
| 超弹性 | hyperelasticity | 应力由应变能对变形的导数给出 |
| 各向同性 | isotropy | 材料性质与方向无关 |
| Neo-Hookean | neo-Hookean | 常用的超弹性模型，大变形下较稳定 |
| St. Venant-Kirchhoff | St. Venant-Kirchhoff (StVK) | 线性应力-应变关系配 Green 应变，压缩时易失稳 |
| 共旋 | corotated | 分离旋转与应变的小变形模型 |
| 粘弹性 | viscoelasticity | 应力同时依赖变形与变形速率 |
| 松弛时间 | relaxation time | 粘弹性材料应力衰减的特征时间 |
| 塑性 | plasticity | 超过屈服后产生不可恢复变形 |
| 屈服面 | yield surface | 应力空间中开始塑性变形的边界 |
| 隐式积分 | implicit integration | 用下一时刻的力反解下一时刻状态 |
| 增量势 | incremental potential | 隐式时间步对应的最小化目标 |
| 牛顿法 | Newton's method | 用切线刚度线性化后迭代求根 |
| 切线刚度 | tangent stiffness | 残差对未知量的雅可比 |
| 线搜索 | line search | 沿搜索方向选择步长以保证能量下降 |
| 投影动力学 | projective dynamics | 局部投影与全局线性求解交替的隐式方法 |
| 局部-全局 | local-global | 先逐单元求解、再全局耦合的交替格式 |
| ADMM | alternating direction method of multipliers | 分裂变量后交替最小化的优化算法 |
| 弯曲刚度 | bending stiffness | 抵抗弯曲的刚度，布料中远小于拉伸刚度 |
| 褶皱 | wrinkle | 压缩失稳产生的面外变形 |
| 各向异性 | anisotropy | 材料性质随方向改变 |
| 离散壳 | discrete shell | 用二面角等离散量描述薄壳弯曲能量 |
| 离散弹性杆 | discrete elastic rod | 用节点与转角描述细长杆的方法 |
| 自碰撞 | self-collision | 同一物体不同部分之间的碰撞 |
| 连续碰撞检测 | continuous collision detection (CCD) | 在时间区间内检测穿透 |
| 空间哈希 | spatial hashing | 用网格桶加速邻域查询 |
| 增量势接触 | incremental potential contact (IPC) | 用障碍势保证无穿透的接触框架 |
| 障碍函数 | barrier function | 距离趋零时趋于无穷的惩罚函数 |
| 断裂 | fracture | 材料分离形成新表面的过程 |
| 应力强度因子 | stress intensity factor | 裂纹尖端应力场强弱的度量 |
| 内聚力模型 | cohesive zone model | 用界面牵引-分离关系描述断裂 |
| 虚拟节点 | virtual node | 允许单元拓扑改变的离散技巧 |
| 边界元 | boundary element method (BEM) | 只在边界上离散的数值方法 |
| 预碎片 | pre-fracture | 预先切好碎片再按需分离 |
| 降维 | model reduction | 用低维子空间近似高维状态 |
| 模态分析 | modal analysis | 用结构的固有振型作为基 |
| 子空间 | subspace | 由少量基向量张成的低维空间 |
