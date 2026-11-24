# -*- coding: utf-8 -*-
"""临时数值核算（不产出图）：n 层一维堆叠的 PGS 残差。"""
import numpy as np

g = 9.81
dt = 1.0 / 60.0


def build(n, m=1.0):
    """n 个箱子摞在无穷质量的地面上。contact 0 = 地面与箱 0。"""
    A = np.zeros((n, n))
    b = np.zeros(n)
    inv = 1.0 / m
    for j in range(n):
        A[j, j] += inv
        if j >= 1:
            A[j, j] += inv          # 与上一个箱子的接触
        if j + 1 < n:
            A[j, j + 1] -= inv
        if j - 1 >= 0:
            A[j, j - 1] -= inv
    b[0] = -g * dt
    return A, b


def pgs(A, b, iters):
    n = len(b)
    lam = np.zeros(n)
    hist = []
    for it in range(iters + 1):
        w = A @ lam + b
        res = np.max(np.abs(np.minimum(lam, w)))
        hist.append(res)
        for j in range(n):
            if A[j, j] == 0:
                continue
            s = b[j] + A[j] @ lam - A[j, j] * lam[j]
            lam[j] = max(0.0, -s / A[j, j])
    return hist, lam.copy()


for n in (1, 2, 3, 5, 10):
    A, b = build(n)
    hist, lam = pgs(A, b, 60)
    exact = np.linalg.solve(A, -b)
    print(f"n={n:2d} res[0..4]={['%.3e' % h for h in hist[:5]]}")
    print(f"      res[10],res[30],res[60]={hist[10]:.3e} {min(hist[30],1):.3e} {hist[60]:.3e}")
    print(f"      lam exact (N)={np.round(exact/dt,2)}  目标={[round((n-j)*m*gv,2) for j in range(n)] if (gv:=1.0) else 0}")

# 单次迭代的中间量（写正文用）
A, b = build(3)
lam = np.zeros(3)
for j in range(3):
    s = b[j] + A[j] @ lam
    lam[j] = max(0.0, -s / A[j, j])
print("one pass lam =", lam, " -> force N =", lam / dt)
w = A @ lam + b
print("one pass w =", w)
