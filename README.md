# 最优化方法实验报告仓库

本仓库整理《最优化方法与应用》实验代码、运行截图、生成脚本和 Word 报告。内容覆盖第 4 章到第 7 章，适合作为课程实验提交材料和复现实验结果的索引。

## 内容总览

| 章节 | 目录/脚本 | 主要内容 |
| --- | --- | --- |
| 第 4 章 | `src/chapter4/optimization_lab.py` | 无约束优化、一维搜索、修正牛顿、非线性共轭梯度等 |
| 第 5-7 章 | `src/chapter5_7/build_report.py` | 约束优化、线性/整数规划、最小二乘与迭代法 |
| 截图与曲线 | `assets/`、`output/` | 报告使用的运行截图、图表和中间输出 |
| 最终报告 | `reports/` | 第 4-7 章合并版 Word 报告和阶段报告 |

## 仓库结构

```text
optimization-lab-report/
├── src/
│   ├── chapter4/optimization_lab.py
│   └── chapter5_7/build_report.py
├── assets/
│   ├── chapter4/
│   └── chapter5_7/
├── output/
│   └── optimization_lab_report/
├── reports/
│   ├── 优化方法实验报告_第4-7章合并版.docx
│   └── 优化方法实验报告_第5-7章.docx
├── requirements.txt
└── README.md
```

## 运行方式

建议使用 Python 3.10 及以上版本：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/chapter4/optimization_lab.py
python src/chapter5_7/build_report.py
```

运行后会更新或生成：

- `assets/chapter4/`：第 4 章运行截图与曲线。
- `output/optimization_lab_report/screenshots/`：第 5-7 章截图。
- `output/optimization_lab_report/优化方法实验报告_第5-7章.docx`：第 5-7 章报告。

## 报告说明

最终合并版报告位于：

```text
reports/优化方法实验报告_第4-7章合并版.docx
```

源码按题号和章节组织，运行结果用于支撑报告中的截图、表格和结论。第 5-7 章脚本在没有模板文件时会使用空白 Word 文档生成报告，方便在不同电脑上复现。

## 维护规则

- 同一门最优化课程的后续实验继续放在本仓库。
- 报告、源码、截图和生成脚本同步维护。
- 不提交虚拟环境、缓存和本机临时文件。
