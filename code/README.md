# 平面五杆机器人及 2R 支链：可复现实验

从项目根目录运行：

```powershell
python -m pip install -r code/requirements.txt
python code/run_simulations.py
python code/make_figures.py
python code/scenario_sweeps.py
python code/validate_parallel_christoffel.py
python code/run_figure_qa.py
python code/build_report.py
python code/check_pdf.py
```

所有路径从脚本位置解析，数据写入 `data/`，图写入 `figures/generated/`，验证记录写入 `outputs/validation/`。绘图优先使用微软雅黑，可自行安装中文字体后调整 `make_figures.py` 的字体列表。每张图导出 PDF、SVG 以及 300 dpi PNG，报告优先使用矢量 PDF。

仅修改正文时，运行 `build_report.py` 即可；它连续运行三次 XeLaTeX，生成最终中文 PDF，保持原始 Word 模板不变。`check_pdf.py` 渲染每页用于人工视觉检查，并生成结构检查 JSON。最终 LaTeX 使用 SimSun、SimHei、KaiTi、Times New Roman 以及 TeX Gyre Termes Math 字体。`prepare_template.py` 的输入是项目内已经保留的 Word 只读导出件，普通重编译无需再次启动 Word。

## 模型与约定

- 世界坐标 x 向右、y 向上；重力向量为 (0, -9.81) m/s²，机构处于竖直平面。
- 五杆固定基座 A=(-0.18,0)、B=(0.18,0) m。两侧近杆 0.32 m、0.8 kg，远杆 0.28 m、0.6 kg；均匀细杆惯量 I=m l²/12；集中末端载荷 0.25 kg。
- 2R 关节角 q1 从全局 +x 轴逆时针计算，q2 为相对角。左支链选 q2<0，右支链选 q2>0；五杆正解选双圆交点中 y 较高者，保持同一装配支路。
- 2R 独立开链含一次 0.25 kg 末端质量；并联整机的两支链均不包含该质量，整机末端只加一次。
- 安全轨迹为 p=(0.04 cosφ, 0.38+0.025 sinφ) m；近奇异对照 p=(0.04 cosφ, 0.34+0.035 sinφ) m。φ=2π(10s³-15s⁴+6s⁵)，s=t/4，0≤t≤4 s。
- 工作空间热图只包含“左负肘角、右正肘角、上方双圆交点”的装配子空间；未考虑机械关节限位、杆件碰撞、驱动饱和和结构柔性。灰区包括不可达点及被排除的其他装配支路，不能等同于整机全部几何不可达区。

## 计算与验证

`robot_model.py` 包括正逆运动学、Jacobian/其时间导数、2R 拉格朗日 M/C/g、独立的平面牛顿—欧拉递推、串联机械能、五杆约束矩阵、闭环正解和整机动力学。

并联动力学由每条无载荷支链的逆动力学扭矩通过 J_i^(-T) 投影成笛卡尔广义力，汇总并添加 m_p(p¨−g)，再按 τ=J_p^T F 投影至两主动电机。该方法适用于无奇异、理想无摩擦铰链和刚性杆件。并联整机两电机扭矩不能与单条开链的两关节扭矩一一视作同一对象。

直接动力学回放使用预先给定的解析逆动力学扭矩、无反馈、相同理想模型。DOP853 主算例采用 rtol=1e-10、atol=1e-12、最大步长 0.01 s；RK45 比较固定容差下最大步长递减的敏感性。高精度回放误差只说明模型和数值计算一致，不能视作真实闭环控制精度。

验证包括 500 个固定种子随机状态的拉格朗日/牛顿—欧拉差异、串联中心差分 Jacobian、惯性正定性、Mdot−2C 反对称性、41个采样位置的并联正解中心差分 Jacobian、闭环闭合、逆正解一致性、虚功功率等式及串并联功-能积分检查。轨迹1601点，输出采样间隔0.0025 s，功用复合梯形积分。所有数值均为指定理想模型的计算结果，未使用硬件测量数据。

## 图与数据

1. `fig01_mechanism`：机构、连杆长度和角度定义。
2. `fig02_path_timing`：轨迹和五次相位律。
3. `fig03_serial_kinematics`：串联角度、速度、加速度与条件数。
4. `fig04_serial_singularity`：肘角与行列式/条件数。
5. `fig05_serial_torques`：各关节扭矩分解。
6. `fig06_validation`：正动力学回放、两种动力学差异及功-能平衡；fN·m=10^-15 N·m。
7. `fig07_parallel_workspace`：指定装配子空间及并联条件数。
8. `fig08_parallel_kinematics`：主动角、闭环行列式、驱动传递系数及条件数。
9. `fig09_parallel_dynamics`：完整并联机器人主动电机扭矩及分解。
10. `fig10_singularity_comparison`：安全/近奇异条件数、动态扭矩、固定单位竖直力的纯几何传力增益。两条实际轨迹还存在高度、半径差异，动态峰值比不能严格全部归因于条件数。
11. `fig11_installation_speed`：板面倾角与执行速度对课程模型峰值扭矩的影响。每条轨迹401点，区别于主实验1601点；γ=0为水平、γ=90°为竖直，面内重力按g sinγ；忽略板面法向支撑反力、笔尖接触力与摩擦；虚线是各轨迹的重力静态极限。实物参照为公开Quanser绘图机产品，所有扫参均使用本课程自设参数，不是产品实测或参数复现。

`data/results.json` 保存参数、样例矩阵、静态传力对照和汇总指标；CSV 保存时间序列与工作空间，NPZ 保存所有未舍入数组。多面板对齐记录、PDF字体和碰撞检查位于 `outputs/validation/`；图形审计工具随代码提供。程序无云端服务或私有依赖。
