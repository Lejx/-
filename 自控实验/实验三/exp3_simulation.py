"""
实验三：控制系统串联校正
- 原系统: G0(s) = 4 / (s(s+1))
- 超前校正: Gc(s) = (0.624s + 1) / (0.26s + 1), a=2.44, T=0.26
- 滞后校正: Gc(s) = (10s + 1) / (83.33s + 1), b=0.12, T=83.33
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 系统定义 ====================
# 原系统前向通道传递函数 G0(s) = 4 / (s*(s+1))
num0 = [4]
den0 = [1, 1, 0]
G0 = ctrl.TransferFunction(num0, den0)

# 单位反馈 H(s) = 1
H = ctrl.TransferFunction([1], [1])

# 无校正闭环系统 (Gc = 1)
sys_no_correction = ctrl.feedback(G0, H)

# 超前校正装置 Gc(s) = (0.624s + 1) / (0.26s + 1)
num_lead = [0.624, 1]
den_lead = [0.26, 1]
Gc_lead = ctrl.TransferFunction(num_lead, den_lead)
G_lead_open = ctrl.series(Gc_lead, G0)
sys_lead = ctrl.feedback(G_lead_open, H)

# 滞后校正装置 Gc(s) = (10s + 1) / (83.33s + 1)
num_lag = [10, 1]
den_lag = [83.33, 1]
Gc_lag = ctrl.TransferFunction(num_lag, den_lag)
G_lag_open = ctrl.series(Gc_lag, G0)
sys_lag = ctrl.feedback(G_lag_open, H)

print("=" * 60)
print("实验三：控制系统串联校正")
print("=" * 60)
print(f"\n原系统开环传递函数: G0(s) = 4/(s(s+1))")
print(f"超前校正: Gc(s) = (0.624s+1)/(0.26s+1)")
print(f"滞后校正: Gc(s) = (10s+1)/(83.33s+1)")

# ==================== 1. 单位阶跃响应 ====================
t = np.linspace(0, 20, 1000)

# 阶跃响应 - 使用 control.step_response
t_no, y_no_corr = ctrl.step_response(sys_no_correction, t)
t_lead, y_lead = ctrl.step_response(sys_lead, t)
t_lag, y_lag = ctrl.step_response(sys_lag, t)

# 将输出展平为一维数组
y_no_corr = y_no_corr.flatten()
y_lead = y_lead.flatten()
y_lag = y_lag.flatten()

# 计算时域性能指标
def step_info(y, t):
    """计算阶跃响应性能指标"""
    # 稳态值（取最后10%的平均）
    steady_state = np.mean(y[-int(len(y)*0.1):])
    # 超调量
    overshoot = (np.max(y) - steady_state) / steady_state * 100
    # 峰值时间
    peak_idx = np.argmax(y)
    peak_time = t[peak_idx]
    # 调节时间 (2%误差带)
    settle_mask = np.abs(y - steady_state) > 0.02 * steady_state
    if np.any(settle_mask):
        settling_time = t[np.where(settle_mask)[0][-1]]
    else:
        settling_time = t[-1]
    # 上升时间 (10% -> 90%)
    idx_10 = np.where(y >= 0.1 * steady_state)[0]
    idx_90 = np.where(y >= 0.9 * steady_state)[0]
    if len(idx_10) > 0 and len(idx_90) > 0:
        rise_time = t[idx_90[0]] - t[idx_10[0]]
    else:
        rise_time = float('inf')
    
    return {
        'steady_state': steady_state,
        'overshoot': overshoot,
        'peak_time': peak_time,
        'settling_time': settling_time,
        'rise_time': rise_time
    }

info_no = step_info(y_no_corr, t_no)
info_lead = step_info(y_lead, t_lead)
info_lag = step_info(y_lag, t_lag)

print("\n" + "=" * 60)
print("一、单位阶跃响应性能指标")
print("=" * 60)
print(f"\n{'指标':<15} {'无校正':<18} {'超前校正':<18} {'滞后校正':<18}")
print("-" * 70)
print(f"{'稳态值':<15} {info_no['steady_state']:<18.4f} {info_lead['steady_state']:<18.4f} {info_lag['steady_state']:<18.4f}")
print(f"{'超调量(%)':<15} {info_no['overshoot']:<18.2f} {info_lead['overshoot']:<18.2f} {info_lag['overshoot']:<18.2f}")
print(f"{'峰值时间(s)':<15} {info_no['peak_time']:<18.4f} {info_lead['peak_time']:<18.4f} {info_lag['peak_time']:<18.4f}")
print(f"{'调节时间(s)':<15} {info_no['settling_time']:<18.4f} {info_lead['settling_time']:<18.4f} {info_lag['settling_time']:<18.4f}")
print(f"{'上升时间(s)':<15} {info_no['rise_time']:<18.4f} {info_lead['rise_time']:<18.4f} {info_lag['rise_time']:<18.4f}")

# 绘制阶跃响应曲线
fig1, ax1 = plt.subplots(figsize=(12, 7))
ax1.plot(t_no, y_no_corr, 'b-', linewidth=2, label='无校正')
ax1.plot(t_lead, y_lead, 'r-', linewidth=2, label='超前校正')
ax1.plot(t_lag, y_lag, 'g-', linewidth=2, label='滞后校正')
ax1.axhline(y=1, color='k', linestyle='--', alpha=0.5, label='期望值')
ax1.set_xlabel('时间 t (s)', fontsize=13)
ax1.set_ylabel('输出 y(t)', fontsize=13)
ax1.set_title('实验三：串联校正系统单位阶跃响应对比', fontsize=15, fontweight='bold')
ax1.legend(loc='best', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 20])
ax1.set_ylim([-0.5, 2.5])
plt.tight_layout()
fig1.savefig('/Users/ljx/ee_review/自控实验/exp3_step_response.png', dpi=150, bbox_inches='tight')
print("\n✓ 阶跃响应图已保存: exp3_step_response.png")

# ==================== 2. Bode图与稳定裕度 ====================
print("\n" + "=" * 60)
print("二、Bode图与稳定裕度")
print("=" * 60)

# 计算稳定裕度
gm_no, pm_no, wgc_no, wpc_no = ctrl.margin(G0)
gm_lead, pm_lead, wgc_lead, wpc_lead = ctrl.margin(G_lead_open)
gm_lag, pm_lag, wgc_lag, wpc_lag = ctrl.margin(G_lag_open)

# gm是绝对值，需要转换为dB
gm_no_dB = 20 * np.log10(gm_no)
gm_lead_dB = 20 * np.log10(gm_lead)
gm_lag_dB = 20 * np.log10(gm_lag)

print(f"\n{'指标':<20} {'无校正':<20} {'超前校正':<20} {'滞后校正':<20}")
print("-" * 85)
print(f"{'幅值裕度(dB)':<20} {gm_no_dB:<20.4f} {gm_lead_dB:<20.4f} {gm_lag_dB:<20.4f}")
print(f"{'相位裕度(°)':<20} {pm_no:<20.4f} {pm_lead:<20.4f} {pm_lag:<20.4f}")
print(f"{'截止频率(rad/s)':<20} {wpc_no:<20.4f} {wpc_lead:<20.4f} {wpc_lag:<20.4f}")
print(f"{'相位穿越频率(rad/s)':<20} {wgc_no:<20.4f} {wgc_lead:<20.4f} {wgc_lag:<20.4f}")

# 绘制Bode图
fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(14, 9))

# 幅频特性
mag_no, phase_no, omega_no = ctrl.bode_plot(G0, dB=True, plot=False)
mag_lead, phase_lead, omega_lead = ctrl.bode_plot(G_lead_open, dB=True, plot=False)
mag_lag, phase_lag, omega_lag = ctrl.bode_plot(G_lag_open, dB=True, plot=False)

ax2a.semilogx(omega_no, 20*np.log10(mag_no), 'b-', linewidth=2, label='无校正')
ax2a.semilogx(omega_lead, 20*np.log10(mag_lead), 'r-', linewidth=2, label='超前校正')
ax2a.semilogx(omega_lag, 20*np.log10(mag_lag), 'g-', linewidth=2, label='滞后校正')
ax2a.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax2a.set_ylabel('幅值 (dB)', fontsize=13)
ax2a.set_title('实验三：串联校正系统Bode图', fontsize=15, fontweight='bold')
ax2a.legend(loc='best', fontsize=11)
ax2a.grid(True, which='both', alpha=0.3)
ax2a.set_xlim([1e-2, 1e3])

# 相频特性
ax2b.semilogx(omega_no, phase_no, 'b-', linewidth=2, label='无校正')
ax2b.semilogx(omega_lead, phase_lead, 'r-', linewidth=2, label='超前校正')
ax2b.semilogx(omega_lag, phase_lag, 'g-', linewidth=2, label='滞后校正')
ax2b.axhline(y=-180, color='k', linestyle='--', alpha=0.5, label='-180°线')
ax2b.set_xlabel('频率 ω (rad/s)', fontsize=13)
ax2b.set_ylabel('相位 (°)', fontsize=13)
ax2b.legend(loc='best', fontsize=11)
ax2b.grid(True, which='both', alpha=0.3)
ax2b.set_xlim([1e-2, 1e3])

plt.tight_layout()
fig2.savefig('/Users/ljx/ee_review/自控实验/exp3_bode_plot.png', dpi=150, bbox_inches='tight')
print("✓ Bode图已保存: exp3_bode_plot.png")

# ==================== 3. 数据汇总表格 ====================
print("\n" + "=" * 60)
print("三、实验数据汇总")
print("=" * 60)

data_summary = f"""
┌───────────────────┬────────────┬────────────┬────────────┐
│      指标         │   无校正   │  超前校正  │  滞后校正  │
├───────────────────┼────────────┼────────────┼────────────┤
│ 超调量 σ%         │  {info_no['overshoot']:>6.2f}%  │  {info_lead['overshoot']:>6.2f}%  │  {info_lag['overshoot']:>6.2f}%  │
│ 调节时间 ts(s)    │  {info_no['settling_time']:>8.4f}  │  {info_lead['settling_time']:>8.4f}  │  {info_lag['settling_time']:>8.4f}  │
│ 峰值时间 tp(s)    │  {info_no['peak_time']:>8.4f}  │  {info_lead['peak_time']:>8.4f}  │  {info_lag['peak_time']:>8.4f}  │
│ 相位裕度 γ(°)     │  {pm_no:>8.4f}  │  {pm_lead:>8.4f}  │  {pm_lag:>8.4f}  │
│ 幅值裕度 GM(dB)   │  {gm_no_dB:>8.4f}  │  {gm_lead_dB:>8.4f}  │  {gm_lag_dB:>8.4f}  │
│ 截止频率 ωc(rad/s)│  {wpc_no:>8.4f}  │  {wpc_lead:>8.4f}  │  {wpc_lag:>8.4f}  │
└───────────────────┴────────────┴────────────┴────────────┘
"""
print(data_summary)

plt.show()
print("\n实验三仿真完成！")
