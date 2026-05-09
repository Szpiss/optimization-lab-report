# 最优化方法实验报告（第 4-7 章）

本仓库整理了《最优化方法与应用》实验报告相关材料，包括第 4 章无约束优化、第 5 章约束优化、第 6 章线性/整数规划、第 7 章最小二乘与迭代法的源码、运行截图和 Word 报告。

## 目录结构

```text
.
├── src/
│   ├── chapter4/optimization_lab.py      # 第 4 章例题与课后题源码
│   └── chapter5_7/build_report.py        # 第 5-7 章源码、截图与报告生成脚本
├── assets/
│   ├── chapter4/                         # 第 4 章运行截图与曲线
│   └── chapter5_7/                       # 第 5-7 章运行截图与曲线
├── reports/
│   ├── 优化方法实验报告_第4-7章合并版.docx
│   └── 优化方法实验报告_第5-7章.docx
└── output/                               # 原始生成输出备份
```

## 实验内容

- 第 4 章：最速下降法、动量法、牛顿法、FR 共轭梯度法、坐标轮换法、一维搜索、修正牛顿法、非线性共轭梯度法。
- 第 5 章：拉格朗日乘子法、外点罚函数法、内点罚函数法、广义乘子法、可行方向法、二次逼近法、极大熵法。
- 第 6 章：线性规划、0-1 规划、背包问题、指派问题、运输问题、几何优化。
- 第 7 章：Cholesky、QR、SVD、Jacobi、Gauss-Newton、Levenberg-Marquardt 及相关最小二乘实验。

## 运行方式

建议使用 Python 3.10 及以上版本。

```bash
python -m pip install -r requirements.txt
python src/chapter4/optimization_lab.py
python src/chapter5_7/build_report.py
```

运行后会更新：

- `assets/chapter4/`：第 4 章运行截图与曲线。
- `output/optimization_lab_report/screenshots/`：第 5-7 章截图。
- `output/optimization_lab_report/优化方法实验报告_第5-7章.docx`：第 5-7 章报告。

最终合并版报告已整理在：

```text
reports/优化方法实验报告_第4-7章合并版.docx
```

## 说明

源码均按题号组织，运行结果用于支撑实验报告中的截图、表格和结论。第 5-7 章脚本会在没有模板文件时使用空白 Word 文档生成报告，便于在不同电脑上直接复现。
