"""
实验四：采样控制系统研究
- 被控对象: G(s) = 4/(s(s+1))
- D(z) = 1 (单位反馈)
- 采样周期: T = 0.01s, 0.2s, 0.5s, 0.6s
- 研究采样周期对系统稳定性的影响（Z平面特征根）
"""

import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("实验四：采样控制系统研究")
print("=" * 60)

# 原连续系统传递函数 G0(s) = 4 / (s*(s+1))
num_s = [4]
den_s = [1, 1, 0]
G0 = ctrl.TransferFunction(num_s, den_s)

# 不同的采样周期
T_values = [0.01, 0.2, 0.5, 0.6]
colors = ['b', 'r', 'g', 'm']
labels = ['T=0.01s', 'T=0.2s', 'T=0.5s', 'T=0.6s']

# 存储结果
results = {}

for idx, T in enumerate(T_values):
    print(f"\n--- 处理 T = {T}s ---")
    
    # 离散化被控对象 (使用零阶保持器方法)
    Gz = ctrl.c2d(G0, T, method='zoh')
    
    # 单位反馈闭环系统
    sys_clz = ctrl.feedback(Gz, 1)
    
    # 获取离散系统的极点（Z平面特征根）
    poles = ctrl.pole(sys_clz)
    
    # 判断稳定性：所有极点是否都在单位圆内
    is_stable = all(np.abs(p) < 1 for p in poles)
    
    results[T] = {
        'Gz': Gz,
        'sys_clz': sys_clz,
        'poles': poles,
        'is_stable': is_stable
    }
    
    print(f"  开环脉冲传递函数 G(z):")
    print(f"    分子: {Gz.num[0][0]}")
    print(f"    分母: {Gz.den[0][0]}")
    print(f"  闭环极点: {poles}")
    print(f"  极点模值: {[np.abs(p) for p in poles]}")
    print(f"  系统稳定性: {'✓ 稳定' if is_stable else '✗ 不稳定'}")

# ==================== 1. 绘制不同采样周期的阶跃响应 ====================
fig1, ax1 = plt.subplots(figsize=(14, 8))

for idx, T in enumerate(T_values):
    res = results[T]
    if res['is_stable']:
        # 使用匹配采样时间的时间向量
        n_steps = int(20 / T) + 1  # 足够多的步数覆盖20秒
        t_step = np.linspace(0, 20, n_steps)
        try:
            t_out, y_out = ctrl.step_response(res['sys_clz'], t_step)
            y_out = y_out.flatten()
            ax1.plot(t_out, y_out, color=colors[idx], linewidth=2, label=labels[idx])
        except Exception as e:
            print(f"  Warning: 阶跃响应绘制失败 ({labels[idx]}): {e}")
            # 尝试使用默认时间向量
            t_out, y_out = ctrl.step_response(res['sys_clz'])
            y_out = y_out.flatten()
            ax1.plot(t_out, y_out, color=colors[idx], linewidth=2, label=labels[idx])
    else:
        # 不稳定系统 - 绘制短时间内的发散响应
        try:
            n_steps = int(3 / T) + 1
            t_short = np.linspace(0, 3, n_steps)
            t_out, y_out = ctrl.step_response(res['sys_clz'], t_short)
            y_out = y_out.flatten()
            ax1.plot(t_out, y_out, color=colors[idx], linewidth=2, linestyle='--', 
                     label=f"{labels[idx]} (不稳定)")
        except Exception as e:
            ax1.text(0.5, 0.9 - idx*0.08, f"{labels[idx]}: 不稳定，响应发散", 
                    transform=ax1.transAxes, fontsize=11, color=colors[idx])

ax1.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='期望值')
ax1.set_xlabel('时间 t (s)', fontsize=13)
ax1.set_ylabel('输出 y(t)', fontsize=13)
ax1.set_title('实验四：不同采样周期下系统的单位阶跃响应', fontsize=15, fontweight='bold')
ax1.legend(loc='best', fontsize=11)
ax1.grid(True, alpha=0.3)
plt.tight_layout()
fig1.savefig('/Users/ljx/ee_review/自控实验/exp4_step_response.png', dpi=150, bbox_inches='tight')
print("\n✓ 阶跃响应图已保存: exp4_step_response.png")

# ==================== 2. 绘制Z平面特征根分布 ====================
fig2, axes = plt.subplots(2, 2, figsize=(12, 12))

for idx, T in enumerate(T_values):
    ax = axes[idx // 2][idx % 2]
    poles = results[T]['poles']
    is_stable = results[T]['is_stable']
    
    # 绘制单位圆
    theta = np.linspace(0, 2*np.pi, 200)
    ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=1.5, alpha=0.7)
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    # 标记极点
    for i, p in enumerate(poles):
        marker_color = 'green' if is_stable else 'red'
        ax.scatter(p.real, p.imag, s=150, c=marker_color, marker='x', linewidths=3, zorder=5)
        ax.annotate(f'p{i+1}\n({p.real:.4f}{p.imag>=0:+.4f}j)', 
                   (p.real, p.imag), textcoords="offset points", xytext=(10, 10),
                   fontsize=10, fontweight='bold')
    
    ax.set_xlim([-1.6, 1.6])
    ax.set_ylim([-1.4, 1.4])
    ax.set_aspect('equal')
    ax.set_xlabel('实部 Re(z)', fontsize=12)
    ax.set_ylabel('虚部 Im(z)', fontsize=12)
    stability_text = "稳定" if is_stable else "不稳定"
    ax.set_title(f'T = {T}s ({stability_text})', fontsize=14, fontweight='bold',
                color='green' if is_stable else 'red')
    ax.grid(True, alpha=0.3)

plt.suptitle('实验四：不同采样周期下系统的Z平面特征根分布', fontsize=16, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.96])
fig2.savefig('/Users/ljx/ee_review/自控实验/exp4_zplane_poles.png', dpi=150, bbox_inches='tight')
print("✓ Z平面特征根图已保存: exp4_zplane_poles.png")

# ==================== 3. 汇总所有特征根在同一张图上 ====================
fig3, ax3 = plt.subplots(figsize=(10, 10))

# 绘制单位圆
theta = np.linspace(0, 2*np.pi, 200)
ax3.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2, alpha=0.7)
# 填充单位圆内部（稳定区域）
fill_theta = np.linspace(0, 2*np.pi, 100)
ax3.fill_between(np.cos(fill_theta), -np.sin(fill_theta), np.sin(fill_theta), 
                  alpha=0.08, color='green', label='稳定区域')

ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax3.axvline(x=0, color='k', linestyle='-', alpha=0.3)

for idx, T in enumerate(T_values):
    poles = results[T]['poles']
    for i, p in enumerate(poles):
        ax3.scatter(p.real, p.imag, s=180, c=colors[idx], marker='x', linewidths=3, 
                   label=labels[idx] if i == 0 and p == poles[0] else None, zorder=5)

ax3.set_xlim([-2.0, 2.0])
ax3.set_ylim([-2.0, 2.0])
ax3.set_aspect('equal')
ax3.set_xlabel('实部 Re(z)', fontsize=14)
ax3.set_ylabel('虚部 Im(z)', fontsize=14)
ax3.set_title('实验四：Z平面特征根汇总对比\n（×标记为闭环极点）', fontsize=15, fontweight='bold')
ax3.legend(loc='upper right', fontsize=12)
ax3.grid(True, alpha=0.3)
plt.tight_layout()
fig3.savefig('/Users/ljx/ee_review/自控实验/exp4_zplane_summary.png', dpi=150, bbox_inches='tight')
print("✓ Z平面特征根汇总图已保存: exp4_zplane_summary.png")

# ==================== 4. 数据汇总 ====================
print("\n" + "=" * 60)
print("实验数据汇总")
print("=" * 60)
print(f"\n{'采样周期T(s)':<15} {'闭环极点':<45} {'稳定性':<10}")
print("-" * 75)
for T in T_values:
    res = results[T]
    poles_str = ", ".join([f"{p:.4f}" for p in res['poles']])
    stable_str = "稳定" if res['is_stable'] else "不稳定"
    print(f"{T:<15} {poles_str:<45} {stable_str:<10}")

print("\n分析结论:")
print("-" * 50)
stable_T = [T for T in T_values if results[T]['is_stable']]
unstable_T = [T for T in T_values if not results[T]['is_stable']]
if stable_T:
    print(f"• 当 T ∈ {{{', '.join([str(t) for t in stable_T])}}} 时，系统稳定")
if unstable_T:
    print(f"• 当 T ∈ {{{', '.join([str(t) for t in unstable_T])}}} 时，系统不稳定")
print("• 采样周期越大，系统越容易变得不稳定")
print("• 根据香农定理，采样频率应大于信号最高频率的2倍")
print("• 采样周期增大导致Z平面极点向单位圆外移动")

plt.show()
print("\n实验四仿真完成！")
