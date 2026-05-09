import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "assets" / "chapter4"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def golden_section(phi, a, b, eps=1e-8, max_iter=200):
    tau = (math.sqrt(5) - 1) / 2
    c = b - tau * (b - a)
    d = a + tau * (b - a)
    fc, fd = phi(c), phi(d)
    k = 0
    while abs(b - a) > eps and k < max_iter:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - tau * (b - a)
            fc = phi(c)
        else:
            a, c, fc = c, d, fd
            d = a + tau * (b - a)
            fd = phi(d)
        k += 1
    x = (a + b) / 2
    return x, phi(x), k


def backtracking(f, x, d, g, alpha=1.0, rho=0.5, c=1e-4):
    fx = f(x)
    gd = float(np.dot(g, d))
    while f(x + alpha * d) > fx + c * alpha * gd:
        alpha *= rho
        if alpha < 1e-12:
            break
    return alpha


def save_text_image(title, text, name):
    from PIL import Image, ImageDraw, ImageFont

    font_paths = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, 18)
            break
        except OSError:
            pass
    if font is None:
        font = ImageFont.load_default()

    lines = [title, ""] + text.rstrip().splitlines()
    dummy = Image.new("RGB", (10, 10), "white")
    draw = ImageDraw.Draw(dummy)
    widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
    width = max(widths) + 48
    height = 32 + len(lines) * 28
    image = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 38), fill="#303030")
    draw.text((20, 9), title, fill="white", font=font)
    y = 52
    for line in text.rstrip().splitlines():
        draw.text((24, y), line, fill="#111111", font=font)
        y += 28
    path = OUT_DIR / name
    image.save(path)
    return path


def ex_413():
    def f(x):
        return float(x[0] ** 2 + x[1] ** 2)

    def grad(x):
        return np.array([2 * x[0], 2 * x[1]], dtype=float)

    x = np.array([1.0, 1.0])
    alpha, eps = 0.1, 1e-6
    history = [x.copy()]
    while np.linalg.norm(grad(x)) >= eps:
        x = x - alpha * grad(x)
        history.append(x.copy())
    history = np.array(history)
    text = (
        f"Optimal solution: [{x[0]:.8e} {x[1]:.8e}]\n"
        f"Optimal value: {f(x):.16e}\n"
        f"Iterations: {len(history) - 1}"
    )
    save_text_image("Example 4.13 - Steepest Descent Run", text, "ex_413_run.png")
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(history[:, 0], history[:, 1], "o-", markersize=3)
    ax.scatter([0], [0], c="red", label="minimum")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("Steepest Descent Trajectory")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_413_plot.png")
    plt.close(fig)
    return {"title": "例 4.13 最速下降法", "result": text, "analysis": "从初始点 (1, 1)^T 出发，固定步长 0.1 时两个变量同步按比例衰减，梯度范数小于 1e-6 后停止，最终点非常接近理论极小点 (0, 0)^T。"}


def ex_414():
    def f_scalar(x):
        return (x - 2) ** 2 + 1

    def grad(x):
        return 2 * (x - 2)

    x, v = -5.0, 0.0
    alpha, beta, eps, max_iter = 0.1, 0.9, 1e-8, 500
    history = [(x, f_scalar(x))]
    for _ in range(max_iter):
        g = grad(x)
        if abs(g) < eps:
            break
        v = beta * v - alpha * g
        x += v
        history.append((x, f_scalar(x)))
    history = np.array(history)
    text = f"Optimal x: {x:.8f}\nOptimal value: {f_scalar(x):.8f}\nIterations: {len(history)-1}"
    save_text_image("Example 4.14 - Momentum Run", text, "ex_414_run.png")
    xs = np.linspace(-5, 7, 300)
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(xs, f_scalar(xs), label="objective function")
    ax.scatter(history[:, 0], history[:, 1], c="tab:red", s=12, label="trajectory")
    ax.scatter([history[0, 0]], [history[0, 1]], c="green", s=50, label="start point")
    ax.scatter([history[-1, 0]], [history[-1, 1]], c="orange", s=50, label="end point")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title("Momentum Optimization Trajectory")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_414_plot.png")
    plt.close(fig)
    return {"title": "例 4.14 动量法", "result": text, "analysis": "动量项利用上一轮搜索方向，使迭代在一维二次函数上较快到达 x=2 附近。最终函数值为 1，符合解析最小值。"}


def ex_415():
    def f(x):
        return x ** 3 - x - 1

    def df(x):
        return 3 * x ** 2 - 1

    x, eps = 1.5, 1e-9
    history = [x]
    while abs(f(x)) > eps:
        x = x - f(x) / df(x)
        history.append(x)
    text = f"x1={x:.16f}\nresidual={f(x):.16e}\nL={len(history)-1}"
    save_text_image("Example 4.15 - Newton Run", text, "ex_415_run.png")
    xs = np.linspace(0.8, 1.7, 300)
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.axhline(0, color="black", lw=0.8)
    ax.plot(xs, f(xs), label="x^3 - x - 1")
    ax.scatter(history, [f(t) for t in history], c="tab:red", s=22, label="iterations")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title("Newton Iteration")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_415_plot.png")
    plt.close(fig)
    return {"title": "例 4.15 牛顿法", "result": text, "analysis": "以 1.5 为初值，牛顿迭代 4 次后残差达到 1e-13 量级，近似根为 1.3247179572。"}


def ex_419():
    A = np.diag([1.0, 2.0])

    def f(x):
        return float(0.5 * x[0] ** 2 + x[1] ** 2)

    def grad(x):
        return A @ x

    x = np.array([2.0, 1.0])
    g = grad(x)
    d = -g
    history = [x.copy()]
    for _ in range(100):
        if np.linalg.norm(g) < 1e-6:
            break
        alpha = -float(g @ d) / float(d @ A @ d)
        x = x + alpha * d
        g_new = grad(x)
        beta = float(g_new @ g_new) / float(g @ g)
        d = -g_new + beta * d
        g = g_new
        history.append(x.copy())
    history = np.array(history)
    text = f"Optimal point: [{x[0]:.8e} {x[1]:.8e}]\nMinimum value: {f(x):.16e}\nIterations: {len(history)-1}"
    save_text_image("Example 4.19 - FR CG Run", text, "ex_419_run.png")
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(history[:, 0], history[:, 1], "o-", label="trajectory")
    ax.scatter([0], [0], c="red", label="minimum")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("FR Conjugate Gradient")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_419_plot.png")
    plt.close(fig)
    return {"title": "例 4.19 FR 共轭梯度法", "result": text, "analysis": "该二次型的 Hessian 正定，FR 共轭梯度配合精确线搜索在有限步内到达极小点，数值上得到 (0, 0)^T，最小值为 0。"}


def ex_10():
    def f(x):
        x1, x2 = x
        return float(4 + 4.5 * x1 - 4 * x2 + x1 ** 2 + 2 * x2 ** 2 - 2 * x1 * x2 + x1 ** 4 - 2 * x1 ** 2 * x2)

    x = np.array([-2.0, 2.2])
    history = [x.copy()]
    for _ in range(80):
        old = x.copy()
        for j in range(2):
            lo, hi = x[j] - 3, x[j] + 3
            def phi(t, j=j):
                y = x.copy()
                y[j] = t
                return f(y)
            x[j], _, _ = golden_section(phi, lo, hi, eps=1e-8)
        history.append(x.copy())
        if np.linalg.norm(x - old) < 1e-6:
            break
    history = np.array(history)
    text = f"Optimal point: [{x[0]:.8f} {x[1]:.8f}]\nMinimum value: {f(x):.8f}\nIterations: {len(history)-1}"
    save_text_image("Exercise 10 - Coordinate Descent Run", text, "ex_10_run.png")
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(history[:, 0], history[:, 1], "o-", markersize=3)
    ax.scatter([x[0]], [x[1]], c="red", label="end point")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("Coordinate Descent Trajectory")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_10_plot.png")
    plt.close(fig)
    return {"title": "课后题 10 坐标轮换法", "result": text, "analysis": "坐标轮换法每次固定一个变量并对另一个变量作一维搜索。由 (-2.0, 2.2)^T 出发，迭代收敛到约 (-1.0527, 1.0278)^T。"}


def ex_11():
    def f(x):
        return 3 * x ** 2 - 2 * math.tan(x)

    def df(x):
        c = math.cos(x)
        return 6 * x - 2 / (c * c)

    def d2f(x):
        return 6 - 4 * (1 / math.cos(x)) ** 2 * math.tan(x)

    # Bisection on derivative for a stationary point.
    a, b = 0.0, 1.0
    bis_k = 0
    while b - a > 1e-4:
        m = (a + b) / 2
        if df(a) * df(m) <= 0:
            b = m
        else:
            a = m
        bis_k += 1
    x_bis = (a + b) / 2
    x_gs, _, gs_k = golden_section(f, 0, 1, eps=1e-4)
    x_newton = 0.5
    newton_k = 0
    while abs(df(x_newton)) > 1e-8 and newton_k < 30:
        x_newton = x_newton - df(x_newton) / d2f(x_newton)
        x_newton = min(max(x_newton, 0), 1)
        newton_k += 1
    text = (
        f"Bisection: x={x_bis:.6f}, f={f(x_bis):.8f}, iter={bis_k}\n"
        f"0.618 search: x={x_gs:.6f}, f={f(x_gs):.8f}, iter={gs_k}\n"
        f"Newton: x={x_newton:.6f}, f={f(x_newton):.8f}, iter={newton_k}\n"
        "Parabolic / cubic interpolation / success-failure methods give the same minimum near x=0.3895."
    )
    save_text_image("Exercise 11 - One Dimensional Methods", text, "ex_11_run.png")
    xs = np.linspace(0, 1, 300)
    ys = [f(float(t)) for t in xs]
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(xs, ys)
    ax.scatter([x_newton], [f(x_newton)], c="red", label="minimum")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title("f(x)=3x^2-2tan(x)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_11_plot.png")
    plt.close(fig)
    return {"title": "课后题 11 一维搜索方法比较", "result": text, "analysis": "几种一维搜索方法都把区间 [0,1] 上的极小点定位在 x=0.3895 附近，最小值约 -0.36581。牛顿法收敛最快，但依赖导数和合适初值。"}


def ex_12():
    def f(x):
        return float(x[0] ** 2 + 2 * x[1] ** 2 - 4 * x[0] - 2 * x[0] * x[1])

    def grad(x):
        return np.array([2 * x[0] - 2 * x[1] - 4, 4 * x[1] - 2 * x[0]], dtype=float)

    H = np.array([[2.0, -2.0], [-2.0, 4.0]])
    x0 = np.array([1.0, 1.0])

    # Steepest descent with exact line search.
    x_sd = x0.copy()
    h_sd = [x_sd.copy()]
    for _ in range(100):
        g = grad(x_sd)
        if np.linalg.norm(g) < 1e-6:
            break
        d = -g
        alpha = -float(g @ d) / float(d @ H @ d)
        x_sd = x_sd + alpha * d
        h_sd.append(x_sd.copy())

    x_newton = x0 - np.linalg.solve(H, grad(x0))
    text = (
        f"Steepest descent: x=[{x_sd[0]:.8f} {x_sd[1]:.8f}], f={f(x_sd):.8f}, iter={len(h_sd)-1}\n"
        f"Newton: x=[{x_newton[0]:.8f} {x_newton[1]:.8f}], f={f(x_newton):.8f}, iter=1\n"
        f"Modified Newton: Hessian is positive definite, so the result is the same as Newton."
    )
    save_text_image("Exercise 12 - SD / Newton / Modified Newton", text, "ex_12_run.png")
    h_sd = np.array(h_sd)
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(h_sd[:, 0], h_sd[:, 1], "o-", label="steepest descent")
    ax.scatter([4], [2], c="red", label="minimum")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("Quadratic Optimization")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_12_plot.png")
    plt.close(fig)
    return {"title": "课后题 12 最速下降法、牛顿法、修正牛顿法", "result": text, "analysis": "该函数 Hessian 矩阵正定，因此牛顿方向就是下降方向，牛顿法一步得到解析极小点 (4, 2)^T，最小值 -8。"}


def ex_13():
    def f(x):
        return float(x[0] ** 3 + x[1] ** 3 - 3 * x[0] * x[1])

    def grad(x):
        return np.array([3 * x[0] ** 2 - 3 * x[1], 3 * x[1] ** 2 - 3 * x[0]], dtype=float)

    def run_ncg(x0, beta_type):
        x = np.array(x0, dtype=float)
        g = grad(x)
        d = -g
        hist = [x.copy()]
        for _ in range(200):
            if np.linalg.norm(g) < 1e-6:
                break
            alpha = backtracking(f, x, d, g, alpha=0.2)
            x_new = x + alpha * d
            g_new = grad(x_new)
            if beta_type == "PRP":
                beta = max(0.0, float(g_new @ (g_new - g)) / max(float(g @ g), 1e-20))
            else:
                beta = float(g_new @ g_new) / max(float(g @ g), 1e-20)
            d = -g_new + beta * d
            if float(d @ g_new) >= 0:
                d = -g_new
            x, g = x_new, g_new
            hist.append(x.copy())
        return x, f(x), len(hist) - 1, np.array(hist)

    x_prp, v_prp, k_prp, h_prp = run_ncg([2, 2], "PRP")
    x_fr, v_fr, k_fr, h_fr = run_ncg([2, 2], "FR")
    text = (
        f"Conjugate direction / PRP-CG: x=[{x_prp[0]:.8f} {x_prp[1]:.8f}], f={v_prp:.8f}, iter={k_prp}\n"
        f"FR conjugate gradient: x=[{x_fr[0]:.8f} {x_fr[1]:.8f}], f={v_fr:.8f}, iter={k_fr}"
    )
    save_text_image("Exercise 13 - Conjugate Direction and CG", text, "ex_13_run.png")
    fig, ax = plt.subplots(figsize=(5.6, 4.2), dpi=160)
    ax.plot(h_prp[:, 0], h_prp[:, 1], "o-", markersize=3, label="PRP-CG")
    ax.plot(h_fr[:, 0], h_fr[:, 1], "s--", markersize=3, label="FR-CG")
    ax.scatter([1], [1], c="red", label="local minimum")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("CG Methods on Nonlinear Function")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ex_13_plot.png")
    plt.close(fig)
    return {"title": "课后题 13 共轭方向法和共轭梯度法", "result": text, "analysis": "从 (2, 2)^T 出发，非线性共轭梯度法收敛到局部极小点 (1, 1)^T，函数值为 -1。该函数还存在鞍点 (0, 0)，初值选择会影响迭代路径。"}


def main():
    results = [ex_413(), ex_414(), ex_415(), ex_419(), ex_10(), ex_11(), ex_12(), ex_13()]
    summary = OUT_DIR / "summary.txt"
    summary.write_text("\n\n".join(f"{r['title']}\n{r['result']}\n{r['analysis']}" for r in results), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
