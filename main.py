import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp')

import matplotlib
matplotlib.use('Agg')   # 无界面后端，直接保存文件

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import linregress
from src.rsa_core import get_keys, mod_pow, crack_n, eluer_prime
import time

# ── 中文字体（Windows） ─────────────────────────────
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ── 输出目录（docs/ 子目录） ────────────────────────
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
os.makedirs(OUT, exist_ok=True)


def main():
    import random

    # ── 实验参数 ───────────────────────────────────
    PLAINTEXT = random.randint(10000, 100000)
    NUM_TESTS = 1000
    TIMEOUT   = 0.001          # 1 ms 超时

    results = []
    primes  = eluer_prime(100000)

    # ── 数据收集 ──────────────────────────────────
    print(f"正在运行 {NUM_TESTS} 次 RSA 测试，请稍等...")
    for i in range(NUM_TESTS):
        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{NUM_TESTS}")
        while True:
            p, q, n, phi, e, d = get_keys(primes)
            if n > PLAINTEXT:
                break
        cipher    = mod_pow(PLAINTEXT, e, n, T=phi)
        decrypted = mod_pow(cipher, d, n, T=phi)
        if decrypted != PLAINTEXT:
            continue
        start   = time.perf_counter()
        result  = crack_n(n, timeout=TIMEOUT)
        elapsed = time.perf_counter() - start
        results.append({'n': n, 'e': e, 'time': elapsed, 'broken': result is not None})

    if not results:
        print("无有效数据，退出。")
        return

    # ── 数组准备 ──────────────────────────────────
    all_n      = np.array([r['n']      for r in results])
    all_e      = np.array([r['e']      for r in results])
    all_t      = np.array([r['time']   for r in results])
    all_broken = np.array([r['broken'] for r in results])

    broken_n = all_n[all_broken]
    broken_t = all_t[all_broken]
    broken_e = all_e[all_broken]
    n_broken = len(broken_n)
    n_safe   = len(all_n) - n_broken
    print(f"\n已破解: {n_broken}  |  超时(安全): {n_safe}")

    # ══════════════════════════════════════════════
    # 图1：双对数全图 — n vs 破解耗时（破解 + 超时）
    # ══════════════════════════════════════════════
    fig1, ax1 = plt.subplots(figsize=(9, 5))
    ax1.scatter(all_n[~all_broken], all_t[~all_broken],
                c='#2ca02c', s=18, alpha=0.55, label=f'超时/安全 ({n_safe})')
    ax1.scatter(broken_n, broken_t,
                c='#d62728', s=18, alpha=0.7,  label=f'已破解 ({n_broken})')
    ax1.axhline(y=TIMEOUT, color='steelblue', linestyle='--', linewidth=1.5,
                label=f'超时阈值 = {TIMEOUT*1000:.0f} ms')
    if n_broken > 5:
        C_est = np.median(broken_t / np.sqrt(broken_n))
        n_line = np.logspace(np.log10(all_n.min()), np.log10(all_n.max()), 300)
        ax1.plot(n_line, C_est * np.sqrt(n_line), 'k--', lw=1.2, alpha=0.6,
                 label=f'理论 t~sqrt(n)  C={C_est:.2e}')
    ax1.set_xscale('log'); ax1.set_yscale('log')
    ax1.set_xlabel('n (log scale)'); ax1.set_ylabel('time (s, log scale)')
    ax1.set_title('Fig1  log-log: n vs crack time', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9); ax1.grid(True, which='both', linestyle=':', alpha=0.5)
    fig1.tight_layout()
    fig1.savefig(os.path.join(OUT, 'fig1_loglog_overview.png'), dpi=200)
    print('saved fig1_loglog_overview.png')

    if n_broken < 10:
        print("已破解样本不足 10 个，跳过图 2 / 图 3 / 图 5。")
    else:
        log_n = np.log10(broken_n)
        log_t = np.log10(broken_t)
        slope, intercept, r_val, _, _ = linregress(log_n, log_t)
        r2 = r_val ** 2

        # ══════════════════════════════════════════
        # 图2：双对数幂律拟合（仅破解点）
        # ══════════════════════════════════════════
        fig2, ax2 = plt.subplots(figsize=(9, 5))
        ax2.scatter(broken_n, broken_t, s=14, alpha=0.6, color='#d62728',
                    label='已破解数据点')
        n_fit = np.logspace(log_n.min(), log_n.max(), 300)
        t_fit = 10 ** (intercept + slope * np.log10(n_fit))
        ax2.plot(n_fit, t_fit, 'k-', lw=2,
                 label=f'幂律拟合  t=C*n^a\na={slope:.4f} (期望 0.5)\nR2={r2:.4f}')
        ax2.set_xscale('log'); ax2.set_yscale('log')
        ax2.set_xlabel('n (log scale)'); ax2.set_ylabel('time (s, log scale)')
        ax2.set_title('Fig2  log-log power-law fit: verify O(sqrt(n))',
                      fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10); ax2.grid(True, which='both', linestyle=':', alpha=0.5)
        ax2.annotate(f'slope a={slope:.3f}\n(expect 0.5)',
                     xy=(0.05, 0.85), xycoords='axes fraction', fontsize=11,
                     bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray', alpha=0.8))
        fig2.tight_layout()
        fig2.savefig(os.path.join(OUT, 'fig2_powerlaw_loglog.png'), dpi=200)
        print('saved fig2_powerlaw_loglog.png')

        # ══════════════════════════════════════════
        # 图3：sqrt(n) vs t 线性验证图
        # ══════════════════════════════════════════
        sqrt_n = np.sqrt(broken_n)
        sl3, ic3, rv3, _, _ = linregress(sqrt_n, broken_t)
        r2_3 = rv3 ** 2
        fig3, ax3 = plt.subplots(figsize=(9, 5))
        ax3.scatter(sqrt_n, broken_t, s=14, alpha=0.6, color='#9467bd',
                    label='已破解数据点')
        x_line = np.linspace(sqrt_n.min(), sqrt_n.max(), 300)
        ax3.plot(x_line, sl3 * x_line + ic3, 'k-', lw=2,
                 label=f'线性拟合  t=C*sqrt(n)+b\nC={sl3:.3e}, b={ic3:.3e}\nR2={r2_3:.4f}')
        ax3.set_xlabel('sqrt(n)  (linear)'); ax3.set_ylabel('time (s, linear)')
        ax3.set_title('Fig3  sqrt(n) vs t: direct O(sqrt(n)) check',
                      fontsize=13, fontweight='bold')
        ax3.legend(fontsize=10); ax3.grid(True, linestyle=':', alpha=0.5)
        fig3.tight_layout()
        fig3.savefig(os.path.join(OUT, 'fig3_sqrt_linear.png'), dpi=200)
        print('saved fig3_sqrt_linear.png')

    # ══════════════════════════════════════════════
    # 图4：逻辑回归安全阈值（横轴 log10(n)）
    # ══════════════════════════════════════════════
    def sigmoid(x, k, x0):
        return 1.0 / (1.0 + np.exp(-k * (x - x0)))

    log10_all_n = np.log10(all_n)
    try:
        popt, _ = curve_fit(sigmoid, log10_all_n, all_broken.astype(float),
                            p0=[5.0, np.median(log10_all_n)], maxfev=10000)
        k_fit, x0_fit = popt
        threshold_n = 10 ** x0_fit

        fig4, ax4 = plt.subplots(figsize=(9, 5))
        jitter = np.random.uniform(-0.015, 0.015, size=len(log10_all_n))
        ax4.scatter(log10_all_n, all_broken.astype(float) + jitter,
                    s=10, alpha=0.3, color='#1f77b4',
                    label='实测 (0=超时, 1=破解)')
        x_curve = np.linspace(log10_all_n.min(), log10_all_n.max(), 500)
        ax4.plot(x_curve, sigmoid(x_curve, k_fit, x0_fit),
                 'r-', lw=2.5,
                 label=f'逻辑回归\nk={k_fit:.2f}, n0~{threshold_n:.2e}')
        ax4.axhline(y=0.5, color='gray', linestyle='--', lw=1, alpha=0.6)
        ax4.axvline(x=x0_fit, color='red', linestyle='--', lw=1.5,
                    label=f'安全阈值 n0~{threshold_n:.2e}')
        ax4.set_xlabel('log10(n)'); ax4.set_ylabel('破解成功率')
        ax4.set_title('Fig4  logistic regression: success rate vs log10(n)',
                      fontsize=13, fontweight='bold')
        ax4.set_ylim(-0.1, 1.1); ax4.legend(fontsize=9)
        ax4.grid(True, linestyle=':', alpha=0.5)
        fig4.tight_layout()
        fig4.savefig(os.path.join(OUT, 'fig4_logistic.png'), dpi=200)
        print(f'saved fig4_logistic.png  (安全阈值 n0 ≈ {threshold_n:.3e})')
    except Exception as err:
        print(f'图4 逻辑回归失败: {err}')

    # ══════════════════════════════════════════════
    # 图5：e vs 破解耗时（验证 e 无关）
    # ══════════════════════════════════════════════
    if n_broken >= 10:
        sl5, ic5, rv5, _, _ = linregress(broken_e, broken_t)
        r2_5 = rv5 ** 2
        fig5, ax5 = plt.subplots(figsize=(9, 5))
        ax5.scatter(broken_e, broken_t, s=14, alpha=0.55, color='#ff7f0e',
                    label=f'已破解数据点 ({n_broken})')
        e_line = np.linspace(broken_e.min(), broken_e.max(), 300)
        ax5.plot(e_line, sl5 * e_line + ic5, 'k-', lw=2,
                 label=f'线性拟合  t=a*e+b\na={sl5:.2e}\nR2={r2_5:.4f} (期望 ~0)')
        ax5.set_xlabel('e (linear)'); ax5.set_ylabel('time (s, linear)')
        ax5.set_title('Fig5  e vs crack time: verify e has no effect',
                      fontsize=13, fontweight='bold')
        ax5.annotate(f'R2={r2_5:.4f}\n(~0 means e irrelevant)',
                     xy=(0.55, 0.85), xycoords='axes fraction', fontsize=10,
                     color='navy',
                     bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray', alpha=0.8))
        ax5.legend(fontsize=10); ax5.grid(True, linestyle=':', alpha=0.5)
        fig5.tight_layout()
        fig5.savefig(os.path.join(OUT, 'fig5_e_vs_time.png'), dpi=200)
        print('saved fig5_e_vs_time.png')

    print('\n全部完成。')


if __name__ == "__main__":
    main()
