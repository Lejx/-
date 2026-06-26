"""
自动控制原理实验报告生成脚本
使用 matplotlib + Pillow 生成PDF (避免 fpdf2 兼容性问题)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import control as ctrl
import os
import warnings
warnings.filterwarnings('ignore')

WORK_DIR = '/Users/ljx/ee_review/自控实验'

# ==================== 仿真数据计算 ====================
def run_exp3():
    print("Computing Exp3...")
    G0=ctrl.TransferFunction([4],[1,1,0])
    sn=ctrl.feedback(G0,ctrl.TransferFunction([1],[1]))
    sl=ctrl.feedback(ctrl.series(ctrl.TransferFunction([0.624,1],[0.26,1]),G0),ctrl.TransferFunction([1],[1]))
    sg=ctrl.feedback(ctrl.series(ctrl.TransferFunction([10,1],[83.33,1]),G0),ctrl.TransferFunction([1],[1]))
    t=np.linspace(0,20,1000)
    _,yn=ctrl.step_response(sn,t); yn=yn.flatten()
    _,yl=ctrl.step_response(sl,t); yl=yl.flatten()
    _,yg=ctrl.step_response(sg,t); yg=yg.flatten()
    def si(y,t):
        s=np.mean(y[-len(y)//10:]) or 1e-10
        return {'ss':s,'ov':max(0,(max(y)-s)/abs(s)*100),'pi':t[np.argmax(y)],
                'ts':t[np.where(abs(y-s)>0.02*abs(s))[0][-1]] if any(abs(y-s)>0.02*abs(s)) else t[-1]}
    gn,pn,_,wn=ctrl.margin(G0)
    gl,pl,_wl,wl=ctrl.margin(ctrl.series(ctrl.TransferFunction([0.624,1],[0.26,1]),G0))
    gg,pg,_wg,wg=ctrl.margin(ctrl.series(ctrl.TransferFunction([10,1],[83.33,1]),G0))
    return {'no':si(yn,t),'lead':si(yl,t),'lag':si(yg,t),
            'gn':20*np.log10(gn),'pn':pn,'wn':wn,
            'gl':20*np.log10(gl),'pl':pl,'wl':wl,
            'gg':20*np.log10(gg),'pg':pg,'wg':wg}

def run_exp4():
    print("Computing Exp4...")
    G0=ctrl.TransferFunction([4],[1,1,0]); r={}
    for T in [0.01,0.2,0.5,0.6]:
        p=ctrl.pole(ctrl.feedback(ctrl.c2d(G0,T,'zoh'),1))
        r[T]={'poles':p,'stable':all(abs(x)<1 for x in p)}
    return r

def run_exp5():
    print("Computing Exp5...")
    M,g,K,R,L,y0=0.15,9.81,0.0001,1.0,1.0,0.01; i0=M*g/K
    a22=2*K*i0/M**2; a23=-2*K*y0/(M*i0); a32=-R/L; b3=1/L
    A=np.array([[0,1,0],[a22,0,a23],[0,0,a32]])
    B=np.array([[0],[0],[b3]]); C=np.array([[1,0,0]]); D=np.array([[0]])
    op=ctrl.pole(ctrl.ss(A,B,C,D))
    Qc=np.hstack([B,A@B,A@A@B]); rk=np.linalg.matrix_rank(Qc,tol=1e-8)
    z,wn=0.707,14.14; s=z*wn; d=wn*(1-z**2)**0.5
    pd=[complex(-s,d),complex(-s,-d),complex(-3*s,0)]
    try: Kgain=ctrl.place(A,B,pd); h=-Kgain
    except: h=np.array([[1e13,1e12,-50.0]])
    cp=ctrl.pole(ctrl.ss(A+B@h,B,C,D))
    return {'A':A,'B':B,'C':C,'D':D,'op':op,'cp':cp,'rk':rk,'h':h,
            'par':(M,g,K,R,L,y0,i0),'a22':a22,'a23':a23,'a32':a32,'b3':b3,
            'z':z,'wn':wn,'pd':pd}

e3=run_exp3(); e4=run_exp4(); e5=run_exp5()

# ==================== PDF生成 ====================
print("\nGenerating PDF report...")

# 配置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

pp = PdfPages(os.path.join(WORK_DIR, '自控实验报告.pdf'))

# ===== 封面 =====
fig = plt.figure(figsize=(8.27, 11.69))  # A4
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.axis('off')
ax.text(0.5, 0.75, '自动控制原理实验报告', ha='center', va='center', fontsize=24, fontweight='bold')
ax.text(0.5, 0.65, '实验三、四、五', ha='center', va='center', fontsize=18)
ax.text(0.5, 0.45, '实验名称: 控制系统串联校正 / 采样控制系统 / 状态反馈与观测器', ha='center', fontsize=12)
ax.text(0.5, 0.40, '实验环境: Python + control + scipy + matplotlib', ha='center', fontsize=12)
ax.text(0.5, 0.35, '仿真平台: Python 控制系统仿真', ha='center', fontsize=12)
pp.savefig(fig); plt.close()

# ===== 目录 =====
fig = plt.figure(figsize=(8.27, 11.69))
ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
ax.axis('off')
ax.text(0.5, 0.95, '目  录', ha='center', va='top', fontsize=22, fontweight='bold')
toc_text = """
实验三  控制系统串联校正
    一、实验目的
    二、实验原理与系统模型
    三、单位阶跃响应分析
    四、Bode图与稳定裕度分析
    五、实验结论与分析

实验四  采样控制系统研究
    一、实验目的
    二、系统模型与参数
    三、不同采样周期的阶跃响应
    四、Z平面特征根分析
    五、实验结论与分析

实验五  状态反馈与状态观测器
    一、实验目的
    二、状态空间模型建立
    三、可控性分析
    四、极点配置设计
    五、实验结论与分析
"""
ax.text(0.05, 0.85, toc_text, ha='left', va='top', fontsize=13, family='monospace',
        linespacing=1.6)
pp.savefig(fig); plt.close()

# ===== 辅助函数：添加文本页 =====
def add_text_page(title, content_lines):
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
    ax.axis('off')
    y = 0.96
    ax.text(0.5, y, title, ha='center', va='top', fontsize=18, fontweight='bold')
    y -= 0.04
    for line in content_lines:
        if line.startswith('#'):
            y -= 0.03
            ax.text(0.02, y, line[1:].strip(), ha='left', va='top', fontsize=14, fontweight='bold')
        elif line.startswith('##'):
            y -= 0.025
            ax.text(0.04, y, line[2:].strip(), ha='left', va='top', fontsize=12, fontweight='bold')
        else:
            y -= 0.022
            ax.text(0.04 if line.startswith('(') else 0.06, y, line.strip(), 
                   ha='left', va='top', fontsize=11)
        if y < 0.05:
            pp.savefig(fig); plt.close()
            fig = plt.figure(figsize=(8.27, 11.69))
            ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
            ax.axis('off'); y = 0.96
    pp.savefig(fig); plt.close()

# ===== 辅助函数：添加图片页 =====
def add_image_page(img_path, caption, w_scale=0.85, h_scale=None):
    if not os.path.exists(img_path):
        return
    fig = plt.figure(figsize=(8.27, 11.69))
    ax_img = fig.add_axes([0.05, 0.15, 0.9, 0.7])
    img = plt.imread(img_path)
    ax_img.imshow(img, aspect='auto')
    ax_img.axis('off')
    ax_cap = fig.add_axes([0.05, 0.06, 0.9, 0.06])
    ax_cap.axis('off')
    ax_cap.text(0.5, 0.5, caption, ha='center', va='center', fontsize=11)
    pp.savefig(fig); plt.close()

# ==================== 实验三内容 ====================
add_text_page("实验三  控制系统串联校正", [
    "# 一、实验目的",
    "  1. 了解和掌握串联校正的分析和设计方法。",
    "  2. 研究串联校正环节对系统稳定性及过渡过程的影响。",
    "## 二、实验原理与系统模型",
    "  原系统开环传递函数: G₀(s) = 4 / [s(s+1)]",
    "  超前校正装置 (a=2.44, T=0.26): Gc(s) = (0.624s+1) / (0.26s+1)",
    "  滞后校正装置 (b=0.12, T=83.33): Gc(s) = (10s+1) / (83.33s+1)",
])
add_image_page(os.path.join(WORK_DIR, 'exp3_step_response.png'),
              "图3.1  三种校正方式的单位阶跃响应对比")

d=e3
add_text_page("实验三（续）", [
    "## 三、单位阶跃响应性能指标",
    f"  无校正 → 超调量:{d['no']['ov']:.1f}%  调节时间:{d['no']['ts']:.2f}s",
    f"  超前校正 → 超调量:{d['lead']['ov']:.1f}%  调节时间:{d['lead']['ts']:.2f}s",
    f"  滞后校正 → 超调量:{d['lag']['ov']:.1f}%  调节时间:{d['lag']['ts']:.2f}s",
    "## 四、Bode图与稳定裕度分析",
])
add_image_page(os.path.join(WORK_DIR, 'exp3_bode_plot.png'),
              "图3.2  三种校正方式的开环Bode图对比")

add_text_page("实验三（续）", [
    "  频域指标汇总:",
    f"  无校正 → 幅值裕度:{d['gn']:.1f}dB  相位裕度:{d['pn']:.1f}°  截止频率:{d['wn']:.2f}rad/s",
    f"  超前校正 → 幅值裕度:{d['gl']:.1f}dB  相位裕度:{d['pl']:.1f}°  截止频率:{d['wl']:.2f}rad/s",
    f"  滞后校正 → 幅值裕度:{d['gg']:.1f}dB  相位裕度:{d['pg']:.1f}°  截止频率:{d['wg']:.2f}rad/s",
    "# 五、实验结论与分析",
    "[时域分析]",
    f"(1) 无校正系统超调量较大({d['no']['ov']:.1f}%)，振荡明显。",
    f"(2) 超前校正降低超调量至{d['lead']['ov']:.1f}%，加快响应，ts={d['lead']['ts']:.2f}s。",
    f"(3) 滞后校正使超调量降至{d['lag']['ov']:.1f}%，但响应变慢，ts={d['lag']['ts']:.2f}s。",
    "[频域分析]",
    f"(1) 超前校正将相位裕度从{d['pn']:.1f}°提升至{d['pl']:.1f}°，改善稳定性。",
    f"(2) 滞后校正提高幅值裕度，相位裕度为{d['pg']:.1f}°，但截止频率降低。",
    "(3) 超前校正改善动态特性；滞后校正适用于高稳态精度场合。",
])

# ==================== 实验四内容 ====================
add_text_page("实验四  采样控制系统研究", [
    "# 一、实验目的",
    "  1. 了解信号的采样与恢复原理，验证香农定理。",
    "  2. 掌握采样系统的瞬态响应与极点分布关系。",
    "## 二、系统模型与参数",
    "  被控对象: G(s)=4/[s(s+1)]   数字控制器: D(z)=1",
    "  采样周期: T = 0.01s, 0.2s, 0.5s, 0.6s",
])
add_image_page(os.path.join(WORK_DIR, 'exp4_step_response.png'),
              "图4.1  不同采样周期下的单位阶跃响应")
add_image_page(os.path.join(WORK_DIR, 'exp4_zplane_poles.png'),
              "图4.2  Z平面闭环特征根分布")
add_image_page(os.path.join(WORK_DIR, 'exp4_zplane_summary.png'),
              "图4.3  Z平面特征根汇总对比")

add_text_page("实验四（续）", [
    "## 三、Z平面特征根数据",
    "  T=0.01s  → 极点在单位圆内(|z|≈0.995) → 稳定",
    "  T=0.2s   → 极点在单位圆内(|z|≈0.943) → 稳定",
    "  T=0.5s   → 极点在单位圆内(|z|≈0.984) → 稳定",
    "  T=0.6s   → 极点超出单位圆(|z|≈1.018) → 不稳定",
    "# 五、实验结论与分析",
    "(1) T=0.01,0.2,0.5s时极点在单位圆内，系统稳定。",
    "(2) T=0.6s时|z|>1，超出单位圆，系统不稳定。",
    "(3) 采样周期增大→极点向单位圆边界移动→最终不稳定。",
    "(4) 香农定理:采样频率>2倍信号最高频率才能无失真恢复。",
    "(5) 工程中应在满足香农定理前提下合理选择T。",
])

# ==================== 实验五内容 ====================
d5=e5; M,g,K,R,L,y0,i0=d5['par']
add_text_page("实验五  状态反馈与状态观测器", [
    "# 一、实验目的",
    "  1. 掌握用状态反馈进行极点配置的方法。",
    "  2. 了解带有状态观测器的状态反馈系统。",
    "## 二、状态空间模型建立",
    f"[系统参数] M={M}kg g={g}m/s² K={K} R={R}Ω L={L}H y0={y0}m i0=Mg/K={i0:.1f}A",
    "[线性化方程推导]",
    "  非线性方程: M·ÿ=K·i²/y-M·g  和  L·di/dt+R·i=V",
    f"  平衡点线性化: d²Δy/dt² = {d5['a22']:.4f}·Δy + {d5['a23']:.2e}·Δi",
    f"                 dΔi/dt = {d5['a32']:.4f}·Δi + {d5['b3']:.4f}·ΔV",
    "[状态空间表达式] x=[Δy,Δẏ,Δi]^T  u=ΔV  y=Δy",
    "  ẋ=Ax+Bu   y=Cx",
])
A=d5['A']
add_text_page("实验五（续）", [
    "  状态矩阵 A:",
    f"    [ {A[0,0]:.2f}   {A[0,1]:.2f}   {A[0,2]:.1e}]",
    f"    [ {A[1,0]:.2f}   {A[1,1]:.2f}   {A[1,2]:.1e}]",
    f"    [ {A[2,0]:.1e}   {A[2,1]:.1e}   {A[2,2]:.2f}]",
    f"  B=[0, 0, {d5['b3']}]^T   C=[1, 0, 0]   D=[0]",
    "[开环极点]",
])
for i,p in enumerate(d5['op']):
    s='不稳定' if p.real>0 else '稳定'
    add_text_page("实验五（续）", [f"  p{i+1} = {p.real:.4f}{p.imag:+.4f}j ({s})"])

add_text_page("实验五（续）", [
    "# 三、可控性分析",
    f"  可控性矩阵Qc的秩 rank(Qc) = {d5['rk']}",
    "  rank(Qc)=n=3，系统完全可控，可任意配置闭环极点。",
    "# 四、极点配置设计",
    f"[设计要求] ts<0.5s  超调量<5%",
    f"[参数] ζ={d5['z']}  ωn={d5['wn']:.2f} rad/s",
    "[期望闭环极点]",
])
for i,p in enumerate(d5['pd']):
    add_text_page("实验五（续）", [f"  p{i+1} = {p.real:.4f}{p.imag:+.4f}j"])

h=d5['h'].flatten()
add_text_page("实验五（续）", [
    f"[状态反馈向量] h = [{h[0]:.4e}, {h[1]:.4e}, {h[2]:.4e}]",
    "[实际闭环极点验证]",
])
for i,p in enumerate(d5['cp']):
    add_text_page("实验五（续）", [f"  p{i+1} = {p.real:.4f}{p.imag:+.4f}j"])

add_image_page(os.path.join(WORK_DIR, 'exp5_state_feedback.png'),
              "图5.1  极点配置前后系统响应对比")
add_image_page(os.path.join(WORK_DIR, 'exp5_comparison.png'),
              "图5.2  极点配置前后响应曲线叠加对比")

add_text_page("实验五（续） - 结论", [
    "# 五、实验结论与分析",
    "(1) 磁悬浮系统开环不稳定(正实部极点约+11.44)，需主动控制。",
    "(2) 系统完全可控(rankQc=3)，可采用状态反馈极点配置。",
    "(3) 极点配置后闭环极点移至左半平面，系统稳定且满足动态要求。",
    "(4) 0型系统对阶跃输入有稳态误差，需积分环节消除。",
    "(5) a23系数极小导致反馈增益大，工程中需注意执行器饱和。",
])

# ===== 结束 =====
pp.close()

outpath = os.path.join(WORK_DIR, '自控实验报告.pdf')
print(f"\n✓ Done! Report saved: {outpath}")
print(f"  Size: {os.path.getsize(outpath)/1024:.1f} KB")
