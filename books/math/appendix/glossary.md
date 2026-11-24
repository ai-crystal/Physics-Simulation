# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 变形梯度 | deformation gradient | 参考构型到当前构型的局部线性映射，记作 $\mathbf{F}$ |
| 右柯西-格林应变 | right Cauchy-Green strain | $\mathbf{C}=\mathbf{F}^{\top}\mathbf{F}$，对刚体旋转不变 |
| 小应变张量 | infinitesimal strain tensor | $\boldsymbol{\varepsilon}=\tfrac12(\nabla\mathbf{u}+\nabla\mathbf{u}^{\top})$，只在小变形下成立 |
| 柯西应力 | Cauchy stress | 当前构型上单位面积的内力 |
| 第一类皮奥拉-基尔霍夫应力 | first Piola-Kirchhoff stress | 参考构型面积上的力，与 $\mathbf{F}$ 共轭 |
| 第二类皮奥拉-基尔霍夫应力 | second Piola-Kirchhoff stress | 完全定义在参考构型上的对称应力 |
| 客观性 | frame indifference | 本构关系不随刚体旋转改变 |
| 超弹性 | hyperelasticity | 应力由应变能密度对变形的导数给出 |
| 粘弹性 | viscoelasticity | 应力同时依赖变形与变形速率 |
| 塑性 | plasticity | 超过屈服后产生不可恢复的变形 |
| 增量势 | incremental potential | 隐式时间步对应的最小化目标函数 |
| 绝对稳定域 | region of absolute stability | 步长与特征值落在其中时数值解不增长 |
| A-稳定 | A-stability | 稳定域包含整个左半平面 |
| L-稳定 | L-stability | 对极刚性分量能迅速衰减 |
| 刚性方程 | stiff equation | 特征值尺度相差很大的方程 |
| 辛积分 | symplectic integrator | 保持相空间体积的积分格式 |
| 局部截断误差 | local truncation error | 单步近似与精确解之差 |
| 全局误差 | global error | 累积到某一时刻的总误差 |
| 收敛阶 | order of accuracy | 步长减半时误差下降的幂次 |
| 条件数 | condition number | 相对误差放大倍数的上界 |
| 预条件 | preconditioner | 改善条件数的近似逆算子 |
| 共轭梯度 | conjugate gradient | 对称正定系统的 Krylov 迭代法 |
| GMRES | generalized minimal residual | 非对称系统的 Krylov 迭代法 |
| 多重网格 | multigrid | 在多层网格间转移残差以加速收敛 |
| 限制算子 | restriction | 把细网格残差投到粗网格 |
| 延拓算子 | prolongation | 把粗网格修正插回细网格 |
| 矩阵自由 | matrix-free | 只实现矩阵-向量乘，不显式组装矩阵 |
| 牛顿法 | Newton's method | 用雅可比线性化后迭代求解非线性方程 |
| 雅可比矩阵 | Jacobian | 非线性映射的偏导矩阵 |
| 线搜索 | line search | 沿搜索方向选步长以保证下降 |
| 拟牛顿法 | quasi-Newton | 用近似海森矩阵的牛顿类方法 |
| KKT 条件 | Karush-Kuhn-Tucker conditions | 约束优化的一阶必要条件 |
| 互补条件 | complementarity | 两个非负量至少一个为零 |
| 投影算子 | projection operator | 把点映到可行集上的最近点 |
| 增广拉格朗日 | augmented Lagrangian | 拉格朗日项加罚项的约束处理方法 |
| ADMM | alternating direction method of multipliers | 分裂变量后交替最小化的优化算法 |
| 弱形式 | weak form | 乘测试函数并分部积分后的方程形式 |
| 形函数 | shape function | 单元内插值场量的基函数 |
| 等参单元 | isoparametric element | 几何与场量用同一组形函数插值 |
| 高斯积分 | Gaussian quadrature | 用少量点精确积分多项式的数值积分 |
| 锁死 | locking | 单元在特定极限下表现得过刚 |
| 沙漏模式 | hourglass mode | 减缩积分导致的零能量变形模式 |
| 余切权重 | cotangent weight | 离散拉普拉斯算子在三角网格上的边权 |
| 角亏 | angle defect | $2\pi$ 减去顶点周围夹角和，离散高斯曲率 |
| 离散外微分 | discrete exterior calculus | 在单纯复形上定义微分形式的框架 |
| 不适定问题 | ill-posed problem | 解不唯一或不连续依赖数据的反问题 |
| 正则化 | regularization | 加先验约束使反问题稳定 |
| 伴随法 | adjoint method | 反向解一个线性系统以计算梯度 |
| 卡尔曼滤波 | Kalman filter | 线性高斯系统的最优状态估计 |
| 制造解 | manufactured solution | 人为构造的精确解，用于验证收敛阶 |
