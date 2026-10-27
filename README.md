# 五杆绘图机器人的串并联运动学与动力学分析

作者：**Zhangzianqi**

四系机器人动力学专选课结课作业，包含五杆机器人仿真代码及相应的项目源文件。以 Quanser 2 DOF Planar Robot 的五杆拓扑与笔式绘迹用途为实物参照，研究竖直板面椭圆轮廓描绘的课程设计模型。尺寸、质量、安装方向与数值结果为课程设计输入和理想刚体仿真，不是商业原机参数或实体测量。

[阅读结课报告 PDF](outputs/机器人动力学基础结课报告_张子安琪_2024079102.pdf)

## 内容

- 2R 串联支链的 DH 建模、正逆运动学、位置雅可比及可操作度。
- 拉格朗日动力学与独立牛顿—欧拉递推、正动力学回放及功—能核验。
- 五杆闭环正逆运动学、工作模式与装配模式、两类奇异性。
- 支链动力学的虚功投影与并联整机逆动力学。
- 工作空间、近奇异轨迹、安装倾角和描绘时间的定量分析。

## 目录

| 目录或文件 | 内容 |
|---|---|
| `code/` | Python 模型、仿真、绘图、独立核验与报告编译脚本 |
| `data/` | CSV 时间序列、NPZ 数组与 JSON 参数及指标 |
| `figures/generated/` | 11 张自绘图的 PDF、SVG、300 dpi PNG |
| `latex/` | 中文报告 LaTeX 正文及封面背景资产 |
| `references/` | BibTeX、图片原件、来源记录与公开资料下载脚本 |
| `outputs/` | 最终报告、数值核验记录及封面重建所需的模板 PDF 导出件 |
| `作业模版.doc` | 课程原始 Word 模板 |

## 数值复现

在仓库根目录依次运行：

```bash
python -m pip install -r code/requirements.txt
python code/run_simulations.py
python code/make_figures.py
python code/scenario_sweeps.py
python code/validate_parallel_christoffel.py
python code/run_figure_qa.py
```

作图脚本读取前一步生成的数组。所有计算采用 SI 单位，主实验每条轨迹 1601 点，场景扫参 401 点；随机检验固定种子。图形输出与核验记录写回相应目录。中文图优先采用 Microsoft YaHei 字体；其他系统可将 `code/make_figures.py` 中的字体替换为本机可用中文字体。

两侧近杆长 0.32 m、质量 0.8 kg，远杆长 0.28 m、质量 0.6 kg；基距 0.36 m，均匀细杆质心惯量 I=ml²/12，末端工具点质量 0.25 kg。左支链相对肘角取负、右支链取正。常规轨迹为 p=(0.04 cosφ, 0.38+0.025 sinφ) m，近奇异对照为 p=(0.04 cosφ, 0.34+0.035 sinφ) m。

## 编译报告

安装支持 `ctex` 的 TeX Live 或其他 XeLaTeX 环境后，在根目录运行：

```bash
python code/build_report.py
python code/check_pdf.py
```

也可直接进入 `latex/`，连续三次执行 `xelatex main.tex` 解析交叉引用。脚本编译会把中间产物放到 `outputs/latex_build/`，最终报告更新到 `outputs/`。当前字体配置为 SimSun、SimHei、KaiTi、Times New Roman、Arial 和 TeX Gyre Termes Math；在其他系统中需安装相应字体，或在 `latex/main.tex` 中选用本机字体。

仓库已包含 `latex/assets/cover_background.pdf`，正常编译无需启动 Word。需要重建封面背景时可运行 `python code/prepare_template.py`，其输入为保留在 `outputs/template_inspection/template.pdf` 的原模板只读 PDF 导出件；原始 Word 文件保持不变。

## 验证与边界

`data/results.json` 保存主仿真及代表位形指标，`data/scenario_sweeps.json` 保存倾角和执行时间扫参。`outputs/validation/numerical_checks.json` 与 `parallel_independent_checks.json` 保留模型一致性检查。两侧并联支链不重复计入工具质量；开链关节力矩与五杆实际主动关节力矩分别定义。工作空间图对应指定工作/装配模式，未处理实体干涉、限位、柔性和笔尖接触。

## 参考资料与图片

来源及使用说明见 [references/SOURCES.md](references/SOURCES.md)。公开仓库保留参考书目、下载入口与必要引用图片，不重新分发仅限个人学习或未明确允许再分发的论文全文。原始文献与图片的署名和许可分别保留，不因本仓库收录而改变。
