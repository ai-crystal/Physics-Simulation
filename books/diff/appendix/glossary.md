# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 正问题 | forward problem | 给定参数与初值计算状态演化 |
| 反问题 | inverse problem | 由观测反推参数、形状或控制 |
| 自动微分 | automatic differentiation (AD) | 对程序做符号求导，精度到机器精度 |
| 前向模式 | forward mode | 沿计算图正向传播导数 |
| 反向模式 | reverse mode | 先前向再反向传播伴随变量 |
| 计算图 | computational graph | 把计算表示成节点与边的图 |
| 伴随变量 | adjoint variable | 反向传播中表示损失对状态的导数 |
| 伴随法 | adjoint method | 解反向线性系统计算梯度，代价与参数维数无关 |
| 隐函数定理 | implicit function theorem | 由隐式方程求导的数学依据 |
| 检查点 | checkpointing | 只保存部分中间状态，反向时重算 |
| 时间反向传播 | backpropagation through time (BPTT) | 把时间步展开成网络层后求导 |
| 梯度消失 | vanishing gradient | 长链求导中梯度趋零 |
| 梯度爆炸 | exploding gradient | 长链求导中梯度发散 |
| 李雅普诺夫指数 | Lyapunov exponent | 相邻轨迹分离速率的度量 |
| 不适定 | ill-posed | 解不唯一或不连续依赖数据 |
| 正则化 | regularization | 加先验约束使反问题稳定 |
| 可辨识性 | identifiability | 参数能否由观测唯一确定 |
| 参数辨识 | parameter identification | 由观测反推物理参数 |
| 形状优化 | shape optimization | 优化几何以达成目标性能 |
| 模型预测控制 | model predictive control (MPC) | 用模型滚动优化控制序列 |
| 代理模型 | surrogate model | 替代昂贵求解器的近似模型 |
| 图神经网络 | graph neural network (GNN) | 在节点与边上做消息传递的网络 |
| 消息传递 | message passing | 图网络的基本计算单元 |
| 展开训练 | rollout training | 用模型自己的多步输出训练 |
| 暴露偏差 | exposure bias | 训练用真值、推理用自身预测造成的偏差 |
| 神经算子 | neural operator | 学习函数到函数映射的网络 |
| 傅里叶神经算子 | Fourier neural operator (FNO) | 在频域做卷积的算子网络 |
| 物理约束网络 | physics-informed neural network (PINN) | 把方程残差写进损失的网络 |
| 混合模拟 | hybrid simulation | 物理求解器与学习模型结合 |
| 域随机化 | domain randomization | 训练时随机化参数以提升迁移 |
| 仿真到现实 | sim-to-real | 在仿真中训练、迁移到真实系统 |
| 有限差分 | finite difference | 用差分近似导数 |
| 次梯度 | subgradient | 不可导点处的一种广义梯度 |
| 松弛 | relaxation | 把不连续约束替换为光滑近似 |
