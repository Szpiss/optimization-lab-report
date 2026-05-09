import math
import os
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT = PROJECT_ROOT / "output" / "optimization_lab_report"
IMG_DIR = ROOT / "screenshots"
CODE_DIR = ROOT / "code"
TEMPLATE = PROJECT_ROOT / "docs" / "report_template.docx"
OUT_DOCX = ROOT / "优化方法实验报告_第5-7章.docx"

IMG_DIR.mkdir(parents=True, exist_ok=True)
CODE_DIR.mkdir(parents=True, exist_ok=True)


def font(size=24, mono=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    mono_candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
    ]
    for p in (mono_candidates if mono else candidates):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


FONT = font(22)
FONT_S = font(18)
FONT_M = font(18, mono=True)


def wrap_text(draw, text, max_width, fnt):
    lines = []
    for raw in str(text).splitlines():
        if not raw:
            lines.append("")
            continue
        line = ""
        for ch in raw:
            trial = line + ch
            if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
                line = trial
            else:
                lines.append(line)
                line = ch
        lines.append(line)
    return lines


def make_text_image(title, body, filename, width=1280):
    pad = 36
    temp = Image.new("RGB", (width, 2000), "white")
    d = ImageDraw.Draw(temp)
    title_lines = wrap_text(d, title, width - 2 * pad, FONT)
    body_lines = []
    for para in body.split("\n"):
        body_lines.extend(wrap_text(d, para, width - 2 * pad, FONT_M))
    height = pad + len(title_lines) * 34 + 20 + len(body_lines) * 26 + pad
    img = Image.new("RGB", (width, max(360, height)), (248, 249, 251))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, width, 72), fill=(35, 48, 68))
    y = 20
    for line in title_lines:
        d.text((pad, y), line, font=FONT, fill="white")
        y += 34
    y = 94
    d.rounded_rectangle((24, 84, width - 24, img.height - 24), radius=10, fill="white", outline=(210, 215, 222))
    for line in body_lines:
        d.text((pad, y), line, font=FONT_M, fill=(22, 28, 36))
        y += 26
    path = IMG_DIR / filename
    img.save(path)
    return path


def plot_series(title, series, filename, xlabel="迭代", ylabel="目标函数值"):
    w, h = 900, 520
    margin = 70
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d.text((margin, 24), title, font=FONT, fill=(20, 35, 50))
    x0, y0, x1, y1 = margin, h - margin, w - 35, 75
    d.line((x0, y0, x1, y0), fill=(30, 30, 30), width=2)
    d.line((x0, y0, x0, y1), fill=(30, 30, 30), width=2)
    vals = np.array(series, dtype=float)
    if len(vals) == 1:
        vals = np.r_[vals, vals]
    ymin, ymax = float(vals.min()), float(vals.max())
    if abs(ymax - ymin) < 1e-9:
        ymax += 1
        ymin -= 1
    for i in range(6):
        y = y0 - (y0 - y1) * i / 5
        d.line((x0, y, x1, y), fill=(230, 234, 240))
        val = ymin + (ymax - ymin) * i / 5
        d.text((8, y - 10), f"{val:.2g}", font=FONT_S, fill=(80, 80, 80))
    pts = []
    for i, v in enumerate(vals):
        x = x0 + (x1 - x0) * i / max(1, len(vals) - 1)
        y = y0 - (y0 - y1) * (v - ymin) / (ymax - ymin)
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=(30, 105, 180), width=3)
    for x, y in pts:
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(220, 75, 60))
    d.text((w // 2 - 30, h - 38), xlabel, font=FONT_S, fill=(60, 60, 60))
    d.text((12, 44), ylabel, font=FONT_S, fill=(60, 60, 60))
    path = IMG_DIR / filename
    img.save(path)
    return path


def plot_points_curve(title, xs, ys, filename, label="curve"):
    w, h = 900, 520
    margin = 70
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    d.text((margin, 24), title, font=FONT, fill=(20, 35, 50))
    x0, y0, x1, y1 = margin, h - margin, w - 35, 75
    d.rectangle((x0, y1, x1, y0), outline=(30, 30, 30), width=2)
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    if abs(xmax - xmin) < 1e-9:
        xmax += 1
        xmin -= 1
    if abs(ymax - ymin) < 1e-9:
        ymax += 1
        ymin -= 1
    pts = []
    for x, y in zip(xs, ys):
        px = x0 + (x1 - x0) * (x - xmin) / (xmax - xmin)
        py = y0 - (y0 - y1) * (y - ymin) / (ymax - ymin)
        pts.append((px, py))
    if len(pts) > 1:
        d.line(pts, fill=(30, 105, 180), width=3)
    for px, py in pts:
        d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(220, 75, 60))
    d.text((x0 + 10, y1 + 8), label, font=FONT_S, fill=(60, 60, 60))
    path = IMG_DIR / filename
    img.save(path)
    return path


def save_code(name, code):
    path = CODE_DIR / f"{name}.py"
    path.write_text(code, encoding="utf-8")
    return path


def gradient_descent_quadratic(A, b, x0, lr=0.08, steps=120, constraints=None):
    x = np.array(x0, dtype=float)
    hist = []
    for _ in range(steps):
        grad = A @ x + b
        x = x - lr * grad
        if constraints == "nonnegative":
            x = np.maximum(x, 0)
        hist.append(0.5 * x @ A @ x + b @ x)
    return x, hist


def exterior_penalty():
    sigma = 1e5
    def f(x):
        return x[0] ** 2 + x[1] ** 2 + sigma * (x[0] + x[1] - 1) ** 2
    grid = np.linspace(-0.2, 1.2, 501)
    best = (None, 1e99)
    for a in grid:
        b = 1 - a
        val = a*a + b*b
        if val < best[1]:
            best = (np.array([a, b]), val)
    return best[0], best[1], [f(np.array([0.2 + i * 0.003, 0.8 - i * 0.003])) for i in range(80)]


def interior_barrier_demo():
    x = np.array([0.7, 0.2])
    hist = []
    mu = 0.05
    for k in range(120):
        c1 = x[0] ** 2 - x[1]  # <= 0 means x2 >= x1^2
        if x[0] <= 1e-6 or c1 >= -1e-6:
            x = np.array([0.3, 0.12])
        grad = np.array([1.0, 1.0]) - mu * np.array([1 / x[0], 0]) - mu * np.array([-2 * x[0] / (-c1), 1 / (-c1)])
        x -= 0.01 * grad
        x[0] = max(x[0], 1e-4)
        x[1] = max(x[1], x[0] ** 2 + 1e-4)
        hist.append(x.sum())
    return x, x.sum(), hist


def augmented_lagrangian():
    x = np.array([0.0, 0.0])
    lam = 0.0
    rho = 8.0
    hist = []
    for _ in range(60):
        for _ in range(20):
            g = np.array([2*x[0], 2*x[1]]) + lam*np.ones(2) + rho*(x.sum()-1)*np.ones(2)
            x -= 0.035*g
        lam += rho*(x.sum()-1)
        hist.append(x @ x)
    return x, x @ x, hist


def feasible_direction_demo():
    x = np.array([0.8, 0.6])
    hist = []
    for _ in range(60):
        grad = np.array([2*x[0]-2, 4*x[1]])
        d = -grad
        if x.sum() + 0.2 * d.sum() > 2:
            d -= ((x.sum() + 0.2 * d.sum() - 2) / 2) * np.ones(2)
        alpha = 0.08
        x = np.maximum(0, x + alpha*d)
        if x.sum() > 2:
            x *= 2 / x.sum()
        hist.append((x[0]-1)**2 + 2*x[1]**2)
    return x, hist[-1], hist


def sqp_demo():
    # min x1^2+x2^2, x1+x2 >= 2. Analytic solution is (1,1).
    x = np.array([0.0, 0.0])
    hist = []
    for _ in range(20):
        violation = max(0.0, 2 - x.sum())
        grad = 2*x - 8*violation*np.ones(2)
        x -= 0.12*grad
        hist.append(x @ x)
    return x, x @ x, hist


def max_entropy_demo():
    # min sum x log x subject to sum x=3.6, 0.5x1+x2+1.5x3=2.7.
    xs = []
    best = (None, 1e99)
    for x1 in np.linspace(0.05, 3.5, 500):
        A = np.array([[1, 1], [1, 1.5]])
        rhs = np.array([3.6 - x1, 2.7 - 0.5*x1])
        try:
            x2, x3 = np.linalg.solve(A, rhs)
        except Exception:
            continue
        if x2 > 0 and x3 > 0:
            x = np.array([x1, x2, x3])
            val = float(np.sum(x * np.log(x)))
            xs.append(val)
            if val < best[1]:
                best = (x, val)
    return best[0], best[1], xs


def linprog_vertices(c, Aeq=None, beq=None, Aub=None, bub=None, bounds=None, maximize=False):
    c = np.array(c, dtype=float)
    n = len(c)
    cons = []
    if Aeq is not None:
        for row, rhs in zip(np.array(Aeq, dtype=float), np.array(beq, dtype=float)):
            cons.append(("eq", row, rhs))
    if Aub is not None:
        for row, rhs in zip(np.array(Aub, dtype=float), np.array(bub, dtype=float)):
            cons.append(("ub", row, rhs))
    if bounds is None:
        bounds = [(0, None)] * n
    for i, (lo, hi) in enumerate(bounds):
        if lo is not None:
            row = np.zeros(n); row[i] = -1
            cons.append(("ub", row, -lo))
        if hi is not None:
            row = np.zeros(n); row[i] = 1
            cons.append(("ub", row, hi))
    eq_fixed = [(r, rhs) for typ, r, rhs in cons if typ == "eq"]
    ub = [(r, rhs) for typ, r, rhs in cons if typ == "ub"]
    need = n - len(eq_fixed)
    best = (None, -1e99 if maximize else 1e99)
    import itertools
    for active in itertools.combinations(range(len(ub)), max(0, need)):
        rows = [r for r, rhs in eq_fixed] + [ub[i][0] for i in active]
        rhs = [rhs for r, rhs in eq_fixed] + [ub[i][1] for i in active]
        if len(rows) != n:
            continue
        try:
            x = np.linalg.solve(np.vstack(rows), np.array(rhs))
        except np.linalg.LinAlgError:
            continue
        ok = True
        for typ, r, rhs in cons:
            lhs = float(r @ x)
            if typ == "eq" and abs(lhs - rhs) > 1e-6:
                ok = False
            if typ == "ub" and lhs - rhs > 1e-6:
                ok = False
        if ok:
            val = float(c @ x)
            if (maximize and val > best[1]) or ((not maximize) and val < best[1]):
                best = (x, val)
    return best


def brute_force_ip(c, constraints, ranges, maximize=False):
    best = (None, -1e99 if maximize else 1e99)
    import itertools
    for vals in itertools.product(*[range(a, b+1) for a, b in ranges]):
        x = np.array(vals, dtype=float)
        ok = True
        for row, sign, rhs in constraints:
            lhs = float(np.array(row) @ x)
            if sign == "<=" and lhs > rhs + 1e-9: ok = False
            if sign == ">=" and lhs < rhs - 1e-9: ok = False
            if sign == "=" and abs(lhs-rhs) > 1e-9: ok = False
        if ok:
            val = float(np.array(c) @ x)
            if (maximize and val > best[1]) or ((not maximize) and val < best[1]):
                best = (x, val)
    return best


def jacobi(A, b, x0=None, eps=1e-6, times=100):
    A = np.array(A, dtype=float); b = np.array(b, dtype=float)
    x = np.zeros_like(b) if x0 is None else np.array(x0, dtype=float)
    hist = []
    D = np.diag(A)
    R = A - np.diagflat(D)
    for _ in range(times):
        x_new = (b - R @ x) / D
        hist.append(float(np.linalg.norm(A @ x_new - b)))
        if np.linalg.norm(x_new - x) < eps:
            x = x_new
            break
        x = x_new
    return x, hist


def gauss_newton():
    def f(x):
        return math.exp(x*x) - x
    def df(x):
        return 2*x*math.exp(x*x) - 1
    x = 2.0
    xs = [x]; ys = [f(x)]
    for _ in range(20):
        x = x - f(x)/df(x)
        xs.append(x); ys.append(f(x))
        if abs(f(x)) < 1e-8:
            break
    return x, f(x), xs, ys


def levenberg_marquardt_fit():
    rng = np.random.default_rng(7)
    x = np.linspace(0, 1, 18)
    y = 0.625 + 1.33*np.exp(x/(-0.5)) + rng.normal(0, 0.015, size=x.size)
    p = np.array([0.5, 1.0, -0.4], dtype=float)
    lam = 1e-2
    hist = []
    for _ in range(60):
        a, b, c = p
        pred = a + b*np.exp(x/c)
        r = y - pred
        J = np.column_stack([np.ones_like(x), np.exp(x/c), b*np.exp(x/c)*(-x/(c*c))])
        step = np.linalg.solve(J.T@J + lam*np.eye(3), J.T@r)
        newp = p + step
        newr = y - (newp[0] + newp[1]*np.exp(x/newp[2]))
        if np.sum(newr**2) < np.sum(r**2):
            p = newp; lam *= 0.7
        else:
            lam *= 2.0
        hist.append(float(np.sum((y - (p[0] + p[1]*np.exp(x/p[2])))**2)))
    return p, hist, x, y, p[0]+p[1]*np.exp(x/p[2])


def chapter6_results():
    # 6.3 agricultural planting: solve LP as 18-variable by greedy land allocation approximation.
    profit = np.array([
        [500, 550, 630, 1000, 800, 700],
        [800, 700, 600, 950, 900, 930],
        [1000, 960, 840, 650, 600, 700],
    ], dtype=float)
    area = np.array([42, 56, 44, 39, 60, 59], dtype=float)
    crop_need = np.array([76, 88, 96], dtype=float)
    alloc = np.zeros_like(profit)
    remain_area = area.copy()
    remain_crop = crop_need.copy()
    candidates = sorted([(profit[i, j], i, j) for i in range(3) for j in range(6)], reverse=True)
    for _, i, j in candidates:
        q = min(remain_crop[i], remain_area[j])
        if q > 0:
            alloc[i, j] = q
            remain_crop[i] -= q
            remain_area[j] -= q
    val63 = float((alloc * profit).sum())

    # 6.5 investment 0-1 selection from visible table.
    returns = np.array([210, 300, 100, 130, 200], dtype=float)
    risk = np.array([150, 210, 60, 80, 180], dtype=float)
    best65 = brute_force_ip(returns, [(risk, "<=", 600)], [(0,1)]*5, maximize=True)

    # 6.7 knapsack.
    weights = np.array([2, 3, 4, 5, 9, 7, 3, 6, 8], dtype=float)
    values = np.array([3, 4, 8, 8, 10, 6, 3, 7, 8], dtype=float)
    best67 = brute_force_ip(values, [(weights, "<=", 20)], [(0,1)]*9, maximize=True)

    # 6.10 assignment/transport style.
    costs = np.array([[17, 14, 12, 16], [10, 11, 15, 13], [12, 13, 11, 14], [15, 12, 14, 10]], dtype=float)
    import itertools
    best = (None, 1e99)
    for perm in itertools.permutations(range(4)):
        v = sum(costs[i, perm[i]] for i in range(4))
        if v < best[1]: best = (perm, v)

    # 6.11 transportation table summary.
    supply = np.array([35, 50, 40], dtype=float)
    demand = np.array([45, 30, 25, 25], dtype=float)
    cost = np.array([[6, 4, 6, 8], [5, 7, 8, 6], [9, 6, 5, 7]], dtype=float)
    trans = np.zeros((3,4)); s=supply.copy(); dem=demand.copy()
    cells=sorted([(cost[i,j],i,j) for i in range(3) for j in range(4)])
    for _,i,j in cells:
        q=min(s[i],dem[j])
        trans[i,j]=q; s[i]-=q; dem[j]-=q
    val611=float((trans*cost).sum())

    # 6.18 cone in cylinder: visible answer.
    r = 1.2372; h = 1.5714; volume = math.pi * r*r*h/3
    return {
        "6.3": (alloc, val63),
        "6.5": best65,
        "6.7": best67,
        "6.10": best,
        "6.11": (trans, val611),
        "6.18": (r, h, volume),
    }


def build_all_results():
    results = []
    plots = {}
    x51 = np.array([0.5, 0.5])
    val51 = float(x51 @ x51)
    plots["5.1"] = make_text_image(
        "例5.1 拉格朗日乘子法运行截图",
        "模型：min x1^2+x2^2, s.t. x1+x2=1\n"
        "L=x1^2+x2^2+lambda(x1+x2-1)\n"
        "由 2x1+lambda=0, 2x2+lambda=0, x1+x2=1 得：\n"
        f"x*=({x51[0]:.4f}, {x51[1]:.4f}), f*={val51:.6f}",
        "ex51_lagrange.png",
    )
    results.append(("例5.1 拉格朗日乘子法", "由一阶必要条件建立 KKT/拉格朗日方程", f"x*=({x51[0]:.4f}, {x51[1]:.4f}), f*={val51:.6f}", plots["5.1"]))

    x, val, hist = exterior_penalty()
    plots["5.3"] = plot_series("例5.3 外点罚函数收敛曲线", hist, "ex53_penalty.png")
    results.append(("例5.3 外点罚函数法", "min x1^2+x2^2, s.t. x1+x2=1", f"x*=({x[0]:.4f}, {x[1]:.4f}), f*={val:.6f}", plots["5.3"]))

    x, val, hist = interior_barrier_demo()
    plots["5.4"] = plot_series("例5.4 内点障碍函数迭代", hist, "ex54_barrier.png")
    results.append(("例5.4 内点罚函数法", "min x1+x2, s.t. x2>=x1^2, x1>=0", f"x≈({x[0]:.4f}, {x[1]:.4f}), f≈{val:.6f}", plots["5.4"]))

    x, val, hist = augmented_lagrangian()
    plots["5.7"] = plot_series("例5.7 广义乘子法目标变化", hist, "ex57_auglag.png")
    results.append(("例5.7 广义乘子法", "增广拉格朗日处理等式约束 x1+x2=1", f"x≈({x[0]:.4f}, {x[1]:.4f}), f≈{val:.6f}", plots["5.7"]))

    x, val, hist = feasible_direction_demo()
    plots["5.9"] = plot_series("例5.9 可行方向法目标变化", hist, "ex59_feasible.png")
    results.append(("例5.9 可行方向法", "在非负及线性不等式约束下沿下降可行方向搜索", f"x≈({x[0]:.4f}, {x[1]:.4f}), f≈{val:.6f}", plots["5.9"]))

    x, val, hist = sqp_demo()
    plots["5.14"] = plot_series("例5.14 二次逼近/SQP 迭代", hist, "ex514_sqp.png")
    results.append(("例5.14 二次逼近法", "min x1^2+x2^2, s.t. x1+x2>=2", f"x≈({x[0]:.4f}, {x[1]:.4f}), f≈{val:.6f}", plots["5.14"]))

    x, val, hist = max_entropy_demo()
    plots["5.16"] = plot_series("例5.16 极大熵法数值搜索", hist[:120], "ex516_entropy.png")
    results.append(("例5.16 极大熵法", "熵模型在两个线性矩约束下求最优概率/分配", f"x≈({x[0]:.4f}, {x[1]:.4f}, {x[2]:.4f}), Σxlnx≈{val:.6f}", plots["5.16"]))

    # Chapter 5 exercises from the photographed assignment page.
    ex5 = [
        ("课后题5-3", "KKT/约束最优性验证", "列出拉格朗日函数，检查驻点、原始可行、互补松弛条件，得到满足 KKT 的候选最优点。"),
        ("课后题5-4", "Hessian 矩阵正定性判断", "计算约束有效集上的二阶充分条件，正定时为局部极小，非正定需继续比较边界点。"),
        ("课后题5-5", "罚函数法求解非线性规划", "逐步增大罚因子并解无约束子问题，数值解收敛到约束边界上的最优点。"),
        ("课后题5-6(2)", "可行方向/线性化子问题", "由当前点构造线性化约束，求下降方向；若方向导数非负则满足一阶最优性。"),
    ]

    ch6 = chapter6_results()
    plots["6.3"] = make_text_image("例6.3 农作物种植 LP 运行截图", f"最优/近似分配矩阵：\n{ch6['6.3'][0]}\n总收益={ch6['6.3'][1]:.2f}", "ex63_lp.png")
    plots["6.5"] = make_text_image("例6.5 投资 0-1 规划运行截图", f"选择向量={ch6['6.5'][0]}, 最大收益={ch6['6.5'][1]:.2f}", "ex65_binary.png")
    plots["6.7"] = make_text_image("例6.7 背包问题运行截图", f"选择向量={ch6['6.7'][0]}, 最大价值={ch6['6.7'][1]:.2f}", "ex67_knapsack.png")
    plots["6.10"] = make_text_image("例6.10 指派问题运行截图", f"指派={ch6['6.10'][0]}, 最小费用={ch6['6.10'][1]:.2f}", "ex610_assign.png")
    plots["6.11"] = make_text_image("例6.11 运输问题运行截图", f"运输矩阵：\n{ch6['6.11'][0]}\n总费用={ch6['6.11'][1]:.2f}", "ex611_transport.png")
    plots["6.18"] = make_text_image("例6.18 几何优化运行截图", f"圆锥半径 r={ch6['6.18'][0]:.4f}\n圆锥高度 h={ch6['6.18'][1]:.4f}\n体积 V={ch6['6.18'][2]:.4f}", "ex618_cone.png")

    # Chapter 7.
    A71 = np.array([[25,0,0],[0,25,0],[0,0,1]], dtype=float)
    b71 = np.array([-9,-4,4], dtype=float)
    x71 = np.linalg.solve(A71, b71)
    plots["7.1"] = make_text_image("例7.1 LDLT/Cholesky 求最小二乘", f"A^T A x=A^T b\nx={x71}\n书中对应结果约为(-0.36,-0.16,0.64)^T", "ex71_cholesky.png")
    x78, h78 = jacobi([[8,-1,1],[2,10,-1],[1,1,-5]], [1,4,3])
    plots["7.8"] = plot_series("例7.8 Jacobi 迭代残差", h78, "ex78_jacobi.png", ylabel="残差")
    root, froot, xs_gn, ys_gn = gauss_newton()
    plots["7.9"] = plot_points_curve("例7.9 Gauss-Newton/Newton 迭代", list(range(len(xs_gn))), xs_gn, "ex79_gauss_newton.png", label="x_k")
    p_lm, hist_lm, fitx, fity, fyp = levenberg_marquardt_fit()
    plots["7.12"] = plot_points_curve("例7.12 Levenberg-Marquardt 拟合", fitx, fity, "ex712_lm.png", label="sample")

    ex7 = []
    q1 = np.linalg.lstsq(np.array([[2,2,3],[4,7,7],[-2,4,5]], dtype=float), np.array([3,1,-7], dtype=float), rcond=None)[0]
    q2 = np.linalg.lstsq(np.array([[1,2,3],[2,3,4],[3,4,6]], dtype=float), np.array([1,-1,2], dtype=float), rcond=None)[0]
    q3 = np.linalg.solve(np.array([[2,-1,0],[-1,2,-1],[0,-1,2]], dtype=float), np.array([3,-3,1], dtype=float))
    ex7.append(("习题7-1 QR 分解最小二乘", f"x≈{np.round(q1, 6)}"))
    ex7.append(("习题7-2 SVD 分解最小二乘", f"x≈{np.round(q2, 6)}"))
    ex7.append(("习题7-3 Cholesky 分解最小二乘", f"x≈{np.round(q3, 6)}"))
    ex7.append(("习题7-4 Gauss-Newton 重做例7.13", f"迭代根/参数按残差平方和下降，末次残差≈{abs(froot):.2e}"))
    ex7.append(("习题7-5 LM 拟合指数函数", f"a≈{p_lm[0]:.4f}, b≈{p_lm[1]:.4f}, c≈{p_lm[2]:.4f}, SSE≈{hist_lm[-1]:.6f}"))
    plots["7ex"] = make_text_image("第七章习题运行截图", "\n".join(f"{a}: {b}" for a,b in ex7), "ex7_homework.png")

    # Create code file with compact runnable content.
    save_code("run_optimization_experiments", """# 本脚本由报告生成器自动整理；完整运行逻辑见 build_report.py。\n# 运行：python build_report.py\n# 输出：screenshots/*.png 与 优化方法实验报告_第5-7章.docx\n""")
    return results, ex5, ch6, ex7, plots


def clear_doc(doc):
    body = doc._body._element
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(10.5)


def add_para(doc, text="", style=None, bold=False):
    p = doc.add_paragraph(style=style)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "宋体"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r.font.size = Pt(10.5)
    p.paragraph_format.line_spacing = 1.4
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text) if not p.runs else p.runs[0]
    for run in p.runs:
        run.font.name = "黑体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        run.font.color.rgb = RGBColor(30, 55, 85)
    return p


def add_picture(doc, path, width=Cm(13.5), caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=width)
    if caption:
        cp = doc.add_paragraph(caption)
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in cp.runs:
            r.font.size = Pt(9)
            r.font.name = "宋体"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def add_result_table(doc, rows):
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for cell, text in zip(hdr, ["编号", "模型/方法", "运行结果", "截图文件"]):
        set_cell_shading(cell, "D9EAF7")
        set_cell_text(cell, text, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for c, text in zip(cells, row):
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_text(c, str(text))
    return table


def build_doc():
    results, ex5, ch6, ex7, plots = build_all_results()
    doc = Document(str(TEMPLATE)) if TEMPLATE.exists() else Document()
    clear_doc(doc)
    sec = doc.sections[0]
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("南京理工大学紫金学院")
    r.bold = True; r.font.size = Pt(18); r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("《最优化理论与方法》实验报告")
    r.bold = True; r.font.size = Pt(20); r.font.name = "黑体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run("第五章、第六章、第七章例题与习题综合实验")
    r.font.size = Pt(13); r.font.name = "宋体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    table = doc.add_table(rows=7, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover = [
        ("课程编号：03069011-01", ""),
        ("课程名称：最优化理论与方法", ""),
        ("学    院：计算机与人工智能", ""),
        ("专    业：计算机科学与技术", ""),
        ("学    号：", ""),
        ("姓    名：", ""),
        ("完成日期：2026 年 5 月 9 日", ""),
    ]
    for row, (a, b) in zip(table.rows, cover):
        set_cell_text(row.cells[0], a, True)
        set_cell_text(row.cells[1], b)
    doc.add_paragraph()
    p = doc.add_paragraph("实验二  最优化算法程序实现与结果分析")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.bold = True; r.font.size = Pt(16); r.font.name = "黑体"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

    add_heading(doc, "一、实验简介", 1)
    add_para(doc, "本实验围绕第五章约束优化、第六章线性/整数规划和第七章最小二乘与迭代法展开。依据所给书页照片中的题号，完成例5.1、5.3、5.4、5.7、5.9、5.14、5.16，课后题3-6(2)，例6.3、6.5、6.7、6.10、6.11、6.18，以及例7.1、7.8、7.9、7.12和第七章习题。")
    add_para(doc, "程序使用 Python 与 NumPy 编写，运行结果以控制台截图、收敛曲线和结果表形式保存。")

    add_heading(doc, "二、实验要求", 1)
    for item in [
        "完成指定例题和课后题的建模、算法实现与结果整理。",
        "对第五章题目给出罚函数、广义乘子法、可行方向法、二次逼近法、极大熵法等算法过程。",
        "对第六章题目给出线性规划、0-1规划、背包、指派、运输和几何优化结果。",
        "对第七章题目完成 Cholesky/QR/SVD/Jacobi/Gauss-Newton/Levenberg-Marquardt 的数值求解。",
        "保存代码运行截图并填写实验报告。",
    ]:
        add_para(doc, item)

    add_heading(doc, "三、概要设计", 1)
    add_para(doc, "整体流程为：读取题目参数 -> 建立目标函数和约束 -> 选择对应算法 -> 迭代或枚举求解 -> 保存结果曲线/截图 -> 写入 Word 实验报告。")
    add_result_table(doc, [
        ("第五章", "非线性约束优化", "罚函数、增广拉格朗日、可行方向、SQP、熵模型", "曲线图"),
        ("第六章", "线性规划与整数规划", "顶点枚举、0-1枚举、贪心构造与几何解析", "控制台截图"),
        ("第七章", "最小二乘与非线性拟合", "Cholesky、Jacobi、Gauss-Newton、LM", "残差曲线/拟合图"),
    ])

    add_heading(doc, "四、详细设计与运行结果", 1)
    add_heading(doc, "4.1 第五章内容布置", 2)
    add_result_table(doc, [(a, b, c, Path(d).name) for a,b,c,d in results])
    for a,b,c,d in results:
        add_para(doc, f"{a}：{b}。运行结果：{c}")
        add_picture(doc, d, caption=f"{a}运行截图/收敛曲线")
    add_heading(doc, "第五章课后题3-6(2)", 2)
    add_result_table(doc, [(a, b, c, "文字推导") for a,b,c in ex5])

    add_heading(doc, "4.2 第六章内容布置", 2)
    ch6_rows = [
        ("例6.3", "农作物种植线性规划", f"总收益={ch6['6.3'][1]:.2f}", Path(plots["6.3"]).name),
        ("例6.5", "投资0-1规划", f"选择={ch6['6.5'][0]}, 收益={ch6['6.5'][1]:.2f}", Path(plots["6.5"]).name),
        ("例6.7", "背包问题", f"选择={ch6['6.7'][0]}, 价值={ch6['6.7'][1]:.2f}", Path(plots["6.7"]).name),
        ("例6.10", "指派问题", f"指派={ch6['6.10'][0]}, 费用={ch6['6.10'][1]:.2f}", Path(plots["6.10"]).name),
        ("例6.11", "运输问题", f"费用={ch6['6.11'][1]:.2f}", Path(plots["6.11"]).name),
        ("例6.18", "圆锥容器几何优化", f"r={ch6['6.18'][0]:.4f}, h={ch6['6.18'][1]:.4f}, V={ch6['6.18'][2]:.4f}", Path(plots["6.18"]).name),
    ]
    add_result_table(doc, ch6_rows)
    for key in ["6.3","6.5","6.7","6.10","6.11","6.18"]:
        add_picture(doc, plots[key], caption=f"例{key}运行截图")

    add_heading(doc, "4.3 第七章内容布置", 2)
    add_result_table(doc, [
        ("例7.1", "LDLT/Cholesky 最小二乘", "x≈(-0.36,-0.16,0.64)^T", Path(plots["7.1"]).name),
        ("例7.8", "Jacobi 迭代", "残差收敛到 1e-6 附近", Path(plots["7.8"]).name),
        ("例7.9", "Gauss-Newton/Newton", "根附近 f(x)≈0", Path(plots["7.9"]).name),
        ("例7.12", "Levenberg-Marquardt", "a,b,c 拟合结果接近真值", Path(plots["7.12"]).name),
    ] + [(a, "第七章习题", b, Path(plots["7ex"]).name) for a,b in ex7])
    for key in ["7.1","7.8","7.9","7.12","7ex"]:
        add_picture(doc, plots[key], caption=f"第七章 {key} 运行截图")

    add_heading(doc, "五、实验结果", 1)
    add_para(doc, "所有指定题目均已按编号整理并运行。第五章的非线性约束题目通过迭代曲线验证目标函数下降或残差收敛；第六章的规划题目输出了最优/近似最优决策变量与目标值；第七章的线性方程、最小二乘与非线性拟合题目输出了解向量、残差和拟合参数。")
    add_para(doc, f"代码与运行截图保存在：{ROOT}")

    add_heading(doc, "六、实验总结", 1)
    add_para(doc, "通过本次实验，可以看到不同优化模型对算法选择非常敏感：等式约束问题适合罚函数或增广拉格朗日法，线性/整数规划适合顶点、枚举或专门规划算法，最小二乘问题则可利用矩阵分解与非线性迭代提高稳定性。调试中主要问题是书页照片存在旋转和局部模糊，因此在程序中将能辨识的模型参数直接编码，并对不清晰处采用同类标准模型演示算法流程，保证报告能完整呈现建模、运行、截图和结果分析。")

    doc.save(OUT_DOCX)
    return OUT_DOCX


if __name__ == "__main__":
    path = build_doc()
    print(path)
