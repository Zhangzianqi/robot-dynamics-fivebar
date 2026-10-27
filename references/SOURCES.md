# 参考资料与图片来源

资料访问日期：2026-10-27。参考资料用于标准方法、机构背景和引用核验；报告中的机构尺寸、质量、轨迹与仿真指标由本项目设定和计算。

## 报告参考文献

1. Asada H H. *Introduction to Robotics: Chapters 3, 4, 5 and 7*. MIT OpenCourseWare, Course 2.12, Fall 2005. [官方讲义目录](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/pages/lecture-notes/)。用于机构、平面运动学、微分运动及动力学。
2. Lynch K M, Park F C. *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press, 2017. DOI：[10.1017/9781316661239](https://doi.org/10.1017/9781316661239)。[作者预印本入口](https://hades.mech.northwestern.edu/images/7/7f/MR.pdf)；预印本注明个人使用，不重新托管。
3. Liu X-J, Wang J, Pritschow G. Kinematics, singularity and workspace of planar 5R symmetrical parallel mechanisms. *Mechanism and Machine Theory*, 2006, 41(2):145–169. DOI：[10.1016/j.mechmachtheory.2005.05.004](https://doi.org/10.1016/j.mechmachtheory.2005.05.004)。用于五杆机构、模式及工作空间背景。
4. Barnard P. Mechatronics Supports Robotics. Quanser Engineering Blog, 2009-04-06. [制造商原文](https://quanser.blogspot.com/2009/04/mechatronics-supports-robotics.html)。用于实际绘图设备和笔式绘迹场景。
5. Quanser Inc. *2 DOF Planar Robot User Manual*. 2013, draft dated September 6, 2013, Sections 1.1 and 3.1. [制造商原手册的公开镜像](https://www.manualslib.com/manual/1568977/Quanser-2-Dof-Planar-Robot.html)。文档由制造商编写，链接为第三方镜像。
6. I.Elgamal. *Five Bar Mechanism*. Wikimedia Commons, 2020-06-01. [作品页](https://commons.wikimedia.org/wiki/File:Five_bar_mechanism.png)。CC BY-SA 4.0。
7. Denavit J, Hartenberg R S. A kinematic notation for lower-pair mechanisms based on matrices. *Journal of Applied Mechanics*, 1955, 22(2):215–221. DOI：[10.1115/1.4011045](https://doi.org/10.1115/1.4011045)。DH 记号出处。
8. Yoshikawa T. Manipulability of robotic mechanisms. *The International Journal of Robotics Research*, 1985, 4(2):3–9. DOI：[10.1177/027836498500400201](https://doi.org/10.1177/027836498500400201)。[作者存档](https://tsuneo-yoshikawa.my.coocan.jp/PDF-of-Papers/1985-EP2.pdf)。可操作度定义出处。
9. Luh J Y S, Walker M W, Paul R P C. On-line computational scheme for mechanical manipulators. *Journal of Dynamic Systems, Measurement, and Control*, 1980, 102(2):69–76. DOI：[10.1115/1.3149599](https://doi.org/10.1115/1.3149599)。递推 Newton–Euler 方法出处。
10. Gosselin C, Angeles J. Singularity analysis of closed-loop kinematic chains. *IEEE Transactions on Robotics and Automation*, 1990, 6(3):281–290. DOI：[10.1109/70.56660](https://doi.org/10.1109/70.56660)。闭链奇异性分类出处。

## 图片

| 本地文件 | 作者、来源和说明 |
|---|---|
| `images/Five_bar_mechanism_I_Elgamal_2020.png` | I.Elgamal，2020；[Wikimedia Commons 原作品](https://commons.wikimedia.org/wiki/File:Five_bar_mechanism.png)，原图未修改，按 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 使用。 |
| `images/Quanser_2009_2DOF_Planar_Robot_official_blog.jpg` | © Quanser；来源为 Barnard 2009 年[制造商官方工程博客](https://quanser.blogspot.com/2009/04/mechatronics-supports-robotics.html)，原图未修改，作为报告中说明真实设备及其绘图用途的引用图片。未标为开放许可。 |
| `../figures/generated/` | 本项目 Python 代码绘制的模型示意和仿真图；原始数据位于 `../data/`。 |

Quanser 原机在桌面纸上绘图；本报告在相同五杆拓扑基础上研究竖直板面描绘。报告的安装方向、几何尺寸、杆件质量和工具负载均为课程模型，不作为产品原机参数或实体实验结果。

## 全文与元数据

`papers/README.md` 给出官方或作者下载入口。本文未将有个人使用限制或未明确授权再分发的全文纳入公共仓库。MIT 讲义入口采用课程网站原有使用条款；第三方材料遵循其各自版权。`metadata/crossref_*.json` 保留 DOI 注册元数据，下载脚本保留原始公共 URL，未绕过付费访问限制。
