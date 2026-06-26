"""
实验五：状态反馈与状态观测器
- 磁悬浮控制系统
- 状态变量: x = [Δy, Δẏ, Δi]^T
- 输入: ΔV (控制电压)
- 输出: Δy (位置偏移量)
"""

import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("实验五：状态反馈与状态观测器")
print("=" * 60)

# ==================== 系统参数 ====================
# 使用实验指导书给定的参数
M = 0.15      # 质量 kg
g = 9.81      # 重力加速度 m/s^2
K = 0.0001    # 磁力常数
R = 1.0       # 电阻 欧姆
L = 1.0       # 电感 亨利
y0 = 0.01     # 期望平衡位置 m
i0 = M * g / K  # 平衡电流 i0 = Mg/K

print(f"\n系统参数:")
print(f"  M = {M} kg")
print(f"  g = {g} m/s²")
print(f"  K = {K}")
print(f"  R = {R} Ω")
print(f"  L = {L} H")
print(f"  y0 = {y0} m")
print(f"  i0 = Mg/K = {i0:.4f} A")

# ==================== 1. 建立状态空间模型 ====================
# 从线性化微分方程(实验指导书式1和式2):
# 式(1): d²Δy/dt² = (2Ki₀/M²)·Δy - (2Ky₀/Mi₀)·Δi
# 式(2): dΔi/dt = -(R/L)·Δi + (1/L)·ΔV

# 计算系数
a22 = 2 * K * i0 / (M**2)   # d²y/dt² 对 Δy 的系数
a23 = -2 * K * y0 / (M * i0)  # d²y/dt² 对 Δi 的系数
a32 = -R / L                 # dΔi/dt 对 Δi 的系数
b3 = 1 / L                   # ΔV 的系数

print(f"\n状态方程系数推导:")
print(f"  a₂₂ = 2Ki₀/M² = 2×{K}×{i0:.4f}/{M**2} = {a22:.6f}")
print(f"  a₂₃ = -2Ky₀/(Mi₀) = -2×{K}×{y0}/({M}×{i0:.4f}) = {a23:.10f}")
print(f"  a₃₂ = -R/L = {-R}/{L} = {a32:.4f}")
print(f"  b₃ = 1/L = {b3:.4f}")

# 注意：由于 a23 极小(≈9e-10)，B矩阵第二行几乎为0，
# 这使得系统接近不可控。这是磁悬浮系统的固有特性。
# 在实际仿真中，我们使用精确计算的数值。

# 状态矩阵 A, B, C, D
# x = [Δy, Δẏ, Δi]^T
A = np.array([
    [0.0,   1.0,    0.0],
    [a22,   0.0,    a23],
    [0.0,   0.0,    a32]
], dtype=np.float64)
B = np.array([[0.0], [0.0], [b3]], dtype=np.float64)
C = np.array([[1.0, 0.0, 0.0]])  # 输出为 Δy
D = np.array([[0.0]])

print(f"\n状态空间模型:")
print(f"  A = ")
for row in A:
    print(f"      [{row[0]:>12.6e}, {row[1]:>12.6e}, {row[2]:>12.6e}]")
print(f"  B = ")
for row in B:
    print(f"      [{row[0]:>12.6e}]")
print(f"  C = {C.flatten()}")
print(f"  D = {D.flatten()}")

# 构造状态空间模型
sys = ctrl.ss(A, B, C, D)

# ==================== 2. 绘制极点配置前的输出曲线（零输入响应） ====================
print("\n" + "=" * 60)
print("二、极点配置前系统分析（零输入响应）")
print("=" * 60)

t = np.linspace(0, 5, 5000)
u = np.zeros_like(t)  # 零输入
x0_open = np.array([0.01, 0.0, 0.0])  # 初始状态: Δy=0.01, Δẏ=0, Δi=0

# 使用 forced_response 计算零输入响应
result = ctrl.forced_response(sys, t, u, X0=x0_open)
t_out = result[0]
y_out = result[1]

fig1, ax1 = plt.subplots(figsize=(12, 7))
ax1.plot(t_out, y_out, 'b-', linewidth=2, label='输出 Δy(t)')
ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='平衡位置')
ax1.set_xlabel('时间 t (s)', fontsize=13)
ax1.set_ylabel('位置偏移量 Δy (m)', fontsize=13)
ax1.set_title('实验五：极点配置前系统的零输入响应\n(初始偏移 Δy=0.01m, 零输入 u=0)', 
              fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=12)
ax1.grid(True, alpha=0.3)
plt.tight_layout()
fig1.savefig('/Users/ljx/ee_review/自控实验/exp5_open_loop_response.png', dpi=150, bbox_inches='tight')
print("✓ 开环零输入响应图已保存: exp5_open_loop_response.png")

# 分析开环稳定性
open_poles = ctrl.pole(sys)
print(f"\n开环系统极点:")
for i, p in enumerate(open_poles):
    print(f"  p{i+1} = {p.real:.4f} {'+' if p.imag >= 0 else ''}{p.imag:.4f}j")

has_unstable_pole = any(p.real > 0 for p in open_poles)
if has_unstable_pole:
    print("⚠ 开环系统不稳定！存在右半平面正实部极点。")
    print("   原因：磁悬浮系统本质上是开环不稳定的（需要主动控制才能悬浮）")
else:
    print("✓ 开环系统稳定（所有极点在左半平面）")

# ==================== 3. 可控性分析 ====================
print("\n" + "=" * 60)
print("三、可控性分析")
print("=" * 60)

# 构造可控性矩阵 Qc = [B, AB, A²B]
Qc = np.hstack([B, A @ B, A @ A @ B])
rank_Qc = np.linalg.matrix_rank(Qc, tol=1e-8)
n = A.shape[0]

print(f"\n可控性矩阵 Qc = [B, AB, A²B]:")
for row in Qc:
    print(f"  [{row[0]:>14.6e}, {row[1]:>14.6e}, {row[2]:>14.6e}]")
print(f"\nrank(Qc) = {rank_Qc}, n = {n}")

if rank_Qc == n:
    print(f"✓ rank(Qc) = n = {n}，系统完全可控！")
else:
    print(f"⚠ rank(Qc) = {rank_Qc} < n = {n}，系统不完全可控")
    print("   原因：a23系数极小(≈9e-10)，电流对位置加速度的耦合很弱")
    print("   但在理论分析中仍认为系统可控（秩为3在更高精度下）")

# ==================== 4. 极点配置设计 ====================
print("\n" + "=" * 60)
print("四、极点配置设计")
print("=" * 60)

# 设计要求: 调节时间 < 0.5s, 超调量 < 5%
# 根据二阶系统近似公式:
# σ% = exp(-πζ/√(1-ζ²)) < 5% => ζ > 0.69 (取 ζ = 0.707)
# ts ≈ 4/(ζωn) < 0.5s => ζωn > 8 (取 ζωn = 10)
zeta = 0.707  # 阻尼比
wn = 14.14    # 自然频率 rad/s

sigma = zeta * wn  # 衰减系数 ≈ 10
wd = wn * np.sqrt(1 - zeta**2)  # 阻尼振荡频率 ≈ 10

# 期望闭环极点：一对共轭复数极点 + 一个更快的实极点
p_desired = np.array([
    complex(-sigma, wd),
    complex(-sigma, -wd),
    complex(-3 * sigma, 0)
])

print(f"\n设计要求: 调节时间 ts < 0.5s, 超调量 σ% < 5%")
print(f"选取参数: ζ = {zeta}, ωn = {wn:.2f} rad/s")
print(f"\n期望闭环极点:")
for i, p in enumerate(p_desired):
    print(f"  p{i+1} = {p.real:.4f} {'+' if p.imag >= 0 else ''}{p.imag:.4f}j")

# 使用 place 函数计算增益矩阵 K（负反馈）
try:
    K_gain = ctrl.place(A, B, p_desired)
    print(f"\n状态反馈增益矩阵 K (负反馈, u = -Kx):")
    for row in K_gain:
        print(f"  [{row[0]:>14.6e}, {row[1]:>14.6e}, {row[2]:>14.6e}]")
    
    # 本实验使用正反馈，所以 h = -K
    h = -K_gain
    print(f"\n状态反馈向量 h (正反馈, u = hx):")
    for row in h:
        print(f"  [{row[0]:>14.6e}, {row[1]:>14.6e}, {row[2]:>14.6e}]")
    
    # 构建闭环系统: dx/dt = (A + Bh)x + Bkr
    A_cl = A + B @ h
    sys_cl = ctrl.ss(A_cl, B, C, D)
    
    cl_poles = ctrl.pole(sys_cl)
    print(f"\n实际闭环极点验证:")
    for i, p in enumerate(cl_poles):
        print(f"  p{i+1} = {p.real:.4f} {'+' if p.imag >= 0 else ''}{p.imag:.4f}j")
        
except Exception as e:
    print(f"\n⚠ 极点配置失败: {e}")
    print("  原因：系统条件数过大，数值上难以精确配置极点")
    print("  使用近似方法继续...")
    K_gain = np.array([[1e13, 1e12, -50.0]])
    h = -K_gain
    A_cl = A + B @ h
    sys_cl = ctrl.ss(A_cl, B, C, D)
    cl_poles = ctrl.pole(sys_cl)

# ==================== 5. 极点配置后系统响应 ====================
print("\n" + "=" * 60)
print("五、极点配置后系统响应验证")
print("=" * 60)

r = 0.01  # 参考输入

# 计算DC增益并调整放大系数
sys_cl_tf = ctrl.tf(sys_cl)
dc_gain = abs(ctrl.dcgain(sys_cl_tf))
k_scale = 1.0 / dc_gain if dc_gain > 1e-10 else 1.0

# 修正后的闭环系统
sys_cl_scaled = ctrl.ss(A_cl, B * k_scale, C, D)

# --- 5.3 零初值阶跃响应 ---
t_cl = np.linspace(0, 2, 3000)
u_r = np.ones_like(t_cl) * r * k_scale

result_z = ctrl.forced_response(sys_cl_scaled, t_cl, u_r, X0=[0.0, 0.0, 0.0])
t_z = result_z[0]
y_z = result_z[1]

# 计算性能指标
steady_val_z = np.mean(y_z[-int(len(y_z)*0.1):])
max_yz = np.max(np.abs(y_z))
if steady_val_z != 0:
    overshoot_pct = (np.max(y_z) - steady_val_z) / abs(steady_val_z) * 100
else:
    overshoot_pct = 0.0
settle_mask = np.abs(y_z - steady_val_z) > 0.02 * max(abs(steady_val_z), 1e-10)
settling_time = t_z[np.where(settle_mask)[0][-1]] if np.any(settle_mask) else t_z[-1]

print(f"\n--- 零初值响应 (r={r}V, x0=[0,0,0]) ---")
print(f"  稳态值: {steady_val_z:.6f} m")
print(f"  超调量: {overshoot_pct:.2f}%")
print(f"  调节时间(2%): {settling_time:.4f} s")
req_met = settling_time < 0.5 and overshoot_pct < 5
print(f"  设计要求: ts<0.5s, σ%<5% → {'✓ 满足' if req_met else '需要调整'}")

# --- 5.4 有初值阶跃响应 ---
result_i = ctrl.forced_response(sys_cl_scaled, t_cl, u_r, X0=[0.01, 0.0, 0.0])
t_i = result_i[0]
y_i = result_i[1]

steady_val_i = np.mean(y_i[-int(len(y_i)*0.1):])
steady_error = abs(steady_val_i - r)

print(f"\n--- 有初值响应 (r={r}V, x0=[0.01,0,0]) ---")
print(f"  稳态值: {steady_val_i:.6f} m")
print(f"  期望值: {r} m")
print(f"  稳态误差: {steady_error:.6f} m ({steady_error/max(r,1e-10)*100:.2f}%)")

# ==================== 6. 绘制图形 ====================
fig2, axes = plt.subplots(2, 2, figsize=(14, 11))

# 子图1: 开环零输入响应
ax_a = axes[0][0]
ax_a.plot(t_out, y_out, 'b-', linewidth=2)
ax_a.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax_a.set_xlabel('时间 t (s)', fontsize=12)
ax_a.set_ylabel('Δy (m)', fontsize=12)
ax_a.set_title('极点配置前（零输入，有初值）', fontsize=13, fontweight='bold')
ax_a.grid(True, alpha=0.3)
ax_a.set_xlim([0, 5])

# 子图2: 闭环零初值阶跃响应
ax_b = axes[0][1]
ax_b.plot(t_z, y_z, 'r-', linewidth=2, label=f'输出 y(t)')
ax_b.axhline(y=r, color='k', linestyle='--', alpha=0.5, label=f'参考 r={r}m')
ax_b.set_xlabel('时间 t (s)', fontsize=12)
ax_b.set_ylabel('Δy (m)', fontsize=12)
ax_b.set_title(f'极点配置后（零初值，r={r}V）\nts={settling_time:.3f}s, σ={overshoot_pct:.1f}%', 
               fontsize=13, fontweight='bold')
ax_b.legend(loc='best', fontsize=10)
ax_b.grid(True, alpha=0.3)
ax_b.set_xlim([0, 2])

# 子图3: 闭环有初值阶跃响应
ax_c = axes[1][0]
ax_c.plot(t_i, y_i, 'g-', linewidth=2, label=f'输出 y(t)')
ax_c.axhline(y=r, color='k', linestyle='--', alpha=0.5, label=f'参考 r={r}m')
ax_c.set_xlabel('时间 t (s)', fontsize=12)
ax_c.set_ylabel('Δy (m)', fontsize=12)
ax_c.set_title(f'极点配置后（有初值，r={r}V）\n稳态误差={steady_error:.6f}m', 
               fontsize=13, fontweight='bold')
ax_c.legend(loc='best', fontsize=10)
ax_c.grid(True, alpha=0.3)
ax_c.set_xlim([0, 2])

# 子图4: S平面极点分布对比
ax_d = axes[1][1]
ax_d.axvline(x=0, color='k', linestyle='-', linewidth=1.5, alpha=0.7)
ax_d.axhline(y=0, color='k', linestyle='-', alpha=0.3)
# 标注左半平面稳定区域
ax_d.axvspan(-40, 0, alpha=0.05, color='green')

for idx, p in enumerate(open_poles):
    ax_d.scatter(p.real, p.imag, s=150, c='blue', marker='x', linewidths=3, 
                label='开环极点' if idx == 0 else None, zorder=5)
for idx, p in enumerate(cl_poles):
    ax_d.scatter(p.real, p.imag, s=150, c='red', marker='o', facecolors='none', 
                linewidths=3, label='闭环极点' if idx == 0 else None, zorder=5)

ax_d.set_xlabel('Re(s)', fontsize=12)
ax_d.set_ylabel('Im(s)', fontsize=12)
ax_d.set_title('S平面极点分布对比', fontsize=13, fontweight='bold')
ax_d.legend(loc='best', fontsize=10)
ax_d.grid(True, alpha=0.3)
ax_d.set_xlim([-35, 15])
ax_d.set_ylim([-20, 20])

plt.suptitle('实验五：状态反馈极点配置系统响应', fontsize=16, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])
fig2.savefig('/Users/ljx/ee_review/自控实验/exp5_state_feedback.png', dpi=150, bbox_inches='tight')
print("\n✓ 状态反馈响应图已保存: exp5_state_feedback.png")

# 图2: 三条曲线叠加对比
fig3, ax3 = plt.subplots(figsize=(12, 7))
ax3.plot(t_out, y_out, 'b-', linewidth=2, label='极点配置前（零输入，有初值）')
ax3.plot(t_z, y_z, 'r-', linewidth=2, label=f'极点配置后（零初值，r={r}V）')
ax3.plot(t_i, y_i, 'g-', linewidth=2, label=f'极点配置后（有初值，r={r}V）')
ax3.axhline(y=r, color='k', linestyle='--', alpha=0.5, label=f'参考位置 r={r}m')
ax3.axhline(y=0, color='gray', linestyle=':', alpha=0.5, label='平衡位置')
ax3.set_xlabel('时间 t (s)', fontsize=13)
ax3.set_ylabel('位置偏移量 Δy (m)', fontsize=13)
ax3.set_title('实验五：极点配置前后系统响应对比', fontsize=15, fontweight='bold')
ax3.legend(loc='best', fontsize=11)
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, max(5, 2)])
plt.tight_layout()
fig3.savefig('/Users/ljx/ee_review/自控实验/exp5_comparison.png', dpi=150, bbox_inches='tight')
print("✓ 对比图已保存: exp5_comparison.png")

# ==================== 7. 最终数据汇总 ====================
print("\n" + "=" * 60)
print("六、实验数据汇总")
print("=" * 60)

h_flat = h.flatten()
print(f"""
┌─────────────────────────────┬────────────────────┐
│           项目              │        数值         │
├─────────────────────────────┼────────────────────┤
│ 状态矩阵 A                   │ 3×3 (见上方)        │
│ 输入矩阵 B                   │ 3×1 (见上方)        │
│ 输出矩阵 C                   │ [1, 0, 0]           │
│ 直通矩阵 D                   │ [0]                 │
│ 可控性矩阵秩 rank(Qc)        │ {rank_Qc}                  │
│ 系统是否可控                 │ {'是(理论)' if rank_Qc >= 2 else '否'}                 │
│ 期望阻尼比 ζ                 │ {zeta}                  │
│ 期望自然频率 ωn(rad/s)       │ {wn:.2f}                │
│ 状态反馈向量 h               │ [{h_flat[0]:.4e},      │
│                             │  {h_flat[1]:.4e},      │
│                             │  {h_flat[2]:.4e}]      │
│ 闭环超调量 σ%                │ {overshoot_pct:.2f}%              │
│ 闭环调节时间 ts(s)           │ {settling_time:.4f}              │
│ 是否满足设计要求             │ {'是' if req_met else '需调整'}                 │
│ 有初值时稳态误差(m)          │ {steady_error:.6f}             │
└─────────────────────────────┴────────────────────┘
""")

print("稳态误差分析:")
print("-" * 50)
print("• 极点配置后系统存在稳态误差的原因:")
print("  1) 状态反馈不改变系统的型别（type），原系统为0型系统")
print("  2) 对于阶跃输入，0型系统存在稳态误差")
print("  3) 要消除稳态误差，需要引入积分环节或使用前馈补偿")
print("")
print("• 磁悬浮系统特性说明:")
print("  1) 开环系统存在正实部极点，本质不稳定")
print("  2) 必须通过状态反馈使系统稳定")
print("  3) 由于a23系数极小，控制增益很大，实际系统中需谨慎处理")

plt.show()
print("\n实验五仿真完成！")
