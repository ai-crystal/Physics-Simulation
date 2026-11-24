# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 刚体 | rigid body | 形状与质量分布不随运动改变的物体 |
| 自由度 | degree of freedom | 描述状态所需的独立变量个数，空间刚体有六个 |
| 姿态 | orientation | 刚体相对世界坐标系的旋转 |
| 四元数 | quaternion | 四个数表示旋转，需保持单位长度 |
| 万向节锁 | gimbal lock | 欧拉角在特定角度丢失一个自由度 |
| 角速度 | angular velocity | 姿态的变化率，与姿态的导数不是一回事 |
| 惯性张量 | inertia tensor | 描述质量分布对旋转的抵抗，3×3 对称矩阵 |
| 主轴 | principal axis | 惯性张量的特征向量方向 |
| 主惯性矩 | principal moment of inertia | 惯性张量的特征值 |
| 角动量 | angular momentum | $\mathbf{L}=\mathbf{I}\boldsymbol{\omega}$，无外力矩时守恒 |
| 欧拉方程 | Euler's equations | 在体坐标系下描述角速度演化的方程 |
| 冲量 | impulse | 力对时间的积分，直接改变动量 |
| 恢复系数 | coefficient of restitution | 碰撞后法向相对速度与碰撞前的比值 |
| 有效质量 | effective mass | 沿某方向施加单位冲量产生的速度变化 |
| 宽相 | broad phase | 快速筛掉不可能相碰的物体对 |
| 窄相 | narrow phase | 精确计算两个形状是否相交及接触点 |
| 包围盒 | bounding volume | 包住物体的简单形状，如 AABB、OBB |
| 层次包围盒 | bounding volume hierarchy (BVH) | 用树结构加速相交查询 |
| 支撑函数 | support function | 给定方向返回形状上最远的点 |
| 闵可夫斯基差 | Minkowski difference | 两个形状逐点相减得到的集合，用于判交 |
| GJK | Gilbert-Johnson-Keerthi | 在闵可夫斯基差上迭代求最近点的算法 |
| EPA | expanding polytope algorithm | 由 GJK 结果求穿透深度与法向 |
| 线性互补问题 | linear complementarity problem (LCP) | 接触条件的一类标准形式 |
| 互补条件 | complementarity | 力与间隙不能同时为正 |
| 投影高斯-赛德尔 | projected Gauss-Seidel (PGS) | 逐约束更新并截断到可行域的迭代法 |
| 顺序冲量 | sequential impulses | 逐个接触施加冲量并迭代的求解方式 |
| 库仑摩擦 | Coulomb friction | 切向力上限为法向力乘以摩擦系数 |
| 摩擦锥 | friction cone | 三维中所有允许的切向力方向构成的锥 |
| 静摩擦 | static friction | 接触未滑动时的摩擦 |
| 动摩擦 | kinetic friction | 接触滑动时的摩擦 |
| 粘滑 | stick-slip | 静摩擦与动摩擦交替导致的锯齿运动 |
| 摩擦锚点 | friction anchor | 记录接触点初始位置以约束切向漂移 |
| 热启动 | warm starting | 用上一帧的冲量作为本帧迭代初值 |
| 位置修正 | position correction | 直接移动物体以消除穿透 |
| Baumgarte 稳定化 | Baumgarte stabilization | 把位置误差折算成速度修正的稳定化方法 |
| 分裂冲量 | split impulse | 位置修正不进入速度的稳定化方案 |
| 子步 | substep | 把一帧切成多个更小的物理步 |
| 休眠 | sleeping | 让长时间静止的物体停止计算 |
| 约束 | constraint | 对位置或速度施加的等式条件 |
| 雅可比矩阵 | Jacobian | 约束对广义坐标的偏导数矩阵 |
| 软约束 | soft constraint | 允许一定违反量、带柔度的约束 |
| 连续碰撞检测 | continuous collision detection (CCD) | 在时间区间内检测穿透，避免高速漏检 |
| 碰撞时刻 | time of impact (TOI) | 两个物体首次接触的时间 |
| 保守前进 | conservative advancement | 用安全步长逐步逼近碰撞时刻 |
| 耦合 | coupling | 刚体与流体、布料等介质之间的相互作用 |
| 附加质量 | added mass | 物体在流体中加速时带动的流体等效质量 |
| 确定性 | determinism | 相同输入产生逐位相同的结果 |
| 回滚 | rollback | 恢复到历史状态并重算，用于网络同步 |
