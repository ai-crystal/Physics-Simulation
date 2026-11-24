# -*- coding: utf-8 -*-
"""临时数值核算（不产出图）。"""
import numpy as np

def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2])

def qnorm(q):
    return q / np.linalg.norm(q)

def q2R(q):
    w, x, y, z = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)],
        [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)],
        [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])

# ---- 1-3 四元数不归一化 ----
om = np.array([0.3, 0.5, 0.81]); om = 8.0*om/np.linalg.norm(om)
q = qnorm(np.array([0.4, 0.5, -0.3, 0.7]))
dt = 1/60.0
T = 60.0
N = int(round(T/dt))
e = np.linalg.norm(om)*dt/2
q0 = q.copy()
norms = []
for i in range(N):
    q = q + 0.5*dt*qmul(np.array([0.0, *om]), q)
    norms.append(np.linalg.norm(q))
norms = np.array(norms)
print("omega=%.4f rad/s dt=1/60 N=%d" % (np.linalg.norm(om), N))
print("predicted final norm %.3f  actual %.3f" % ((1+e*e)**(N/2), norms[-1]))
print("per-step factor %.6f" % ((norms[1]/norms[0])))
for dts in (1/30, 1/60, 1/120, 1/240, 1/480):
    n = int(round(T/dts)); ee = np.linalg.norm(om)*dts/2
    print("  dt=1/%-4.0f final |q| = %.4g" % (1/dts, (1+ee*ee)**(n/2)))

# ---- 1.5 积分顺序：姿态用旧 ω 还是新 ω ----
def	free_spin(order, dt, T, I_diag, w0):
    I = np.diag(I_diag)
    Iinv = np.diag(1.0/I_diag)
    w = np.array(w0, float)
    q = np.array([1.0, 0, 0, 0])
    n = int(round(T/dt))
    for _ in range(n):
        tau = -np.cross(w, I @ w)
        if order == "old":
            # 先用旧角速度推姿态，再更新角速度
            q = qnorm(q + 0.5*dt*qmul(np.array([0.0, *w]), q))
            w = w + dt*(Iinv @ tau)
        else:
            w = w + dt*(Iinv @ tau)
            q = qnorm(q + 0.5*dt*qmul(np.array([0.0, *w]), q))
    return q, w

I_diag = (1.0, 2.5, 3.5)
w0 = (0.3, 4.0, 0.2)
for dt in (1/60, 1/120, 1/240, 1/480):
    qa, wa = free_spin("old", dt, 10.0, I_diag, w0)
    qb, wb = free_spin("new", dt, 10.0, I_diag, w0)
    d = np.clip(abs(np.dot(qa, qb)), 0, 1)
    ang = 2*np.degrees(np.arccos(d))
    print("dt=1/%-4.0f  姿态差 %.4f deg  角速度差 %.4f rad/s" % (1/dt, ang, np.linalg.norm(wa-wb)))

# 参考解
qa_ref, _ = free_spin("new", 1e-4, 10.0, I_diag, w0)
for dt in (1/60, 1/240):
    qa, _ = free_spin("old", dt, 10.0, I_diag, w0)
    qb, _ = free_spin("new", dt, 10.0, I_diag, w0)
    for name, qq in (("old", qa), ("new", qb)):
        d = np.clip(abs(np.dot(qq, qa_ref)), 0, 1)
        print("  dt=1/%-4.0f %s 相对参考解偏 %.4f deg" % (1/dt, name, 2*np.degrees(np.arccos(d))))
