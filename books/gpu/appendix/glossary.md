# 术语中英对照

| 中文 | 英文 | 说明 |
|---|---|---|
| 带宽受限 | bandwidth-bound | 性能由内存带宽而非算力决定 |
| 计算受限 | compute-bound | 性能由浮点算力决定 |
| 算术强度 | arithmetic intensity | 每读一字节数据做了多少次运算 |
| 屋顶线模型 | roofline model | 用带宽与算力上界刻画性能的模型 |
| 强扩展 | strong scaling | 问题规模不变时增加并行度的加速 |
| 弱扩展 | weak scaling | 每核问题规模不变时增加并行度的效率 |
| 阿姆达尔定律 | Amdahl's law | 串行部分对加速比的限制 |
| 缓存行 | cache line | CPU 一次从内存取回的最小数据块 |
| 假共享 | false sharing | 不同线程写同一缓存行的不同变量 |
| 数组结构体 | structure of arrays (SoA) | 每个字段单独一个数组的布局 |
| 结构体数组 | array of structures (AoS) | 每个元素一个结构体的布局 |
| 合并访问 | coalesced access | 相邻线程访问相邻地址 |
| 分支发散 | branch divergence | 同一 warp 内线程走不同分支 |
| warp | warp | GPU 上一起执行的一组线程 |
| 占用率 | occupancy | 活跃 warp 数与硬件上限之比 |
| 共享内存 | shared memory | 块内线程共享的低延迟存储 |
| bank 冲突 | bank conflict | 共享内存访问落在同一 bank |
| 稀疏网格 | sparse grid | 只为有效区域分配存储的网格 |
| 窄带 | narrow band | 只保留界面附近的稀疏层 |
| 稀疏矩阵-向量乘 | sparse matrix-vector product (SpMV) | Krylov 方法的核心操作 |
| 压缩稀疏行 | compressed sparse row (CSR) | 常用的稀疏矩阵存储格式 |
| 多重网格 | multigrid | 在多层网格间转移残差加速收敛 |
| 红黑高斯-赛德尔 | red-black Gauss-Seidel | 可并行的 Gauss-Seidel 变体 |
| 空间哈希 | spatial hashing | 用网格桶加速邻域查询 |
| 计数排序 | counting sort | 按整数键线性时间排序 |
| 基数排序 | radix sort | 按位分轮排序，适合 GPU |
| 半排序 | partial sorting | 只按网格单元局部排序 |
| 原子操作 | atomic operation | 不可分割的读改写操作 |
| 前缀和 | prefix sum | 并行构造索引的常用原语 |
| 图着色 | graph coloring | 把冲突的写分到不同轮次 |
| 子循环 | subcycling | 不同物理过程用不同步长 |
| 幽灵层 | ghost layer | 区域边界外复制的一层数据 |
| 区域分解 | domain decomposition | 把计算域切块分给不同进程 |
| 检查点 | checkpoint | 定期保存状态以便恢复 |
| 确定性 | determinism | 相同输入产生逐位相同结果 |
| 回滚 | rollback | 恢复历史状态并重算 |
| 定点数 | fixed-point number | 用整数表示小数，便于确定性计算 |
| 核函数 | kernel | GPU 上执行的一次并行函数调用 |
| 精度 | precision | 浮点数的有效位数，如 fp16/fp32/fp64 |
