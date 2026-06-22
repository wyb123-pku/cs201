# RSA-Analyzer

> RSA 公钥参数与 Trial Division 破解耗时的实证分析工具

## 项目背景

本课程项目选题来源于《网络安全 / 密码学》课程中的 RSA 公钥加密算法实验。RSA 的安全性依赖于大整数分解的困难性，而**试除法（Trial Division）**是最直观的因式分解攻击方式。

本项目旨在**通过实验数据验证并可视化**以下核心问题：

1. **破解耗时 `t` 与模数 `n` 的关系是否符合理论预期 `O(√n)`？**
2. **公钥指数 `e` 是否影响 Trial Division 的破解时间？**（理论上无关）
3. **在给定超时阈值下，安全模数 `n` 的临界值（安全边界）大约是多少？**

通过 1000 次随机 RSA 密钥对实验，收集 `(n, e, t, broken)` 数据，并用多种坐标变换和拟合方法对结果进行可视化分析，最终形成五张核心图表。

---

## 核心算法与课程知识点

本项目涉及以下课程核心知识点：

### 1. RSA 密钥生成（`rsa_core.py`）
- **素数生成**：使用欧拉筛法（`eluer_prime`）预计算素数表
- **模数计算**：`n = p × q`，其中 `p`、`q` 为大素数
- **欧拉函数**：`φ(n) = (p-1)(q-1)`
- **公钥/私钥指数**：选取 `e` 满足 `gcd(e, φ(n)) = 1`，计算 `d ≡ e⁻¹ (mod φ(n))`
- **模幂运算**：使用快速模幂（`mod_pow`），时间复杂度 `O(log exponent)`

### 2. Trial Division 破解算法（`rsa_core.py / crack_n`）
- **核心思想**：从 2 到 `√n` 逐个试除，找到 `n` 的非平凡因子
- **时间复杂度**：`O(√n)`，`n` 每增加两个十进制位，耗时约增加 10 倍
- **超时保护**：设置 `timeout` 参数，防止对大 `n` 无限等待

### 3. 数据分析与拟合（`main.py`）
| 图表 | 坐标变换 | 数学原理 | 课程知识点 |
|------|---------|----------|------------|
| 图1 | 双对数 (log-log) | 幂律关系 `t = C·nᵅ` 取对数后变为直线 | 算法复杂度分析 |
| 图2 | 双对数 + 线性拟合 | `log t = α·log n + β`，斜率 `α ≈ 0.5` | 最小二乘法、线性回归 |
| 图3 | `√n` vs `t`（线性） | 若 `t ∝ √n`，则散点呈直线 | 算法验证、假设检验 |
| 图4 | `log₁₀(n)` vs 成功率 | Sigmoid 逻辑回归 `1/(1+e⁻ᵏ⁽ˣ⁻ˣ⁰⁾)` | Logistic 回归、S 型曲线拟合 |
| 图5 | `e` vs `t`（线性） | `R² ≈ 0` 说明两变量无线性相关 | 相关性分析、R² 判定系数 |

### 4. 使用的 Python 库与算法
- **`numpy`**：数组运算、对数变换
- **`scipy.optimize.curve_fit`**：非线性最小二乘拟合（Sigmoid）
- **`scipy.stats.linregress`**：线性回归、斜率与 R² 计算
- **`matplotlib`**：高质量图表生成（支持双对数坐标、Unicode 标签）
---

## 项目结构

```
RSA-Analyzer/
├── src/                  # 核心源代码
│   └── rsa_core.py       # RSA 密钥生成、模幂、Trial Division 破解
├── docs/                 # 文档、演示素材、报告
│   ├── fig1_loglog_overview.png      # 图1：双对数全图
│   ├── fig2_powerlaw_loglog.png     # 图2：幂律拟合
│   ├── fig3_sqrt_linear.png        # 图3：√n 线性验证
│   ├── fig4_logistic.png           # 图4：逻辑回归安全边界
│   └── fig5_e_vs_time.png         # 图5：e 与耗时无关验证
├── tests/                # 测试用例
│   └── test_rsa_core.py
├── main.py               # 主程序入口（数据收集 + 绘图）
├── README.md             # 项目说明文档
├── requirements.txt      # Python 依赖清单
└── LICENSE              # MIT 开源协议
```

---

## 运行指南

### 环境要求

- **Python**：3.8 及以上（推荐 3.10+）
- **操作系统**：Windows / macOS / Linux（已针对 Windows 中文字体优化）

### 安装依赖

```bash
# 使用 venv（推荐）
python -m venv venv
# Windows
venv\Scripts\pip install -r requirements.txt
# macOS / Linux
source venv/bin/pip install -r requirements.txt

# 或直接使用系统 Python
pip install -r requirements.txt
```

### 运行主程序

```bash
python main.py
```

运行流程：
1. 程序自动生成 1000 个随机 RSA 密钥对
2. 对每个 `(n, e)` 执行 Trial Division 破解（超时阈值 1ms）
3. 收集 `(n, e, 破解耗时, 是否破解)` 数据
4. 自动生成 5 张分析图，保存至 `docs/` 目录

> ⏱️ 预计运行时间：2~5 分钟（取决于 CPU 性能）

### 预期输出

```
正在运行 1000 次 RSA 测试，请稍等...
  200/1000
  400/1000
  ...

已破解: 292  |  超时(安全): 708

saved docs/fig1_loglog_overview.png
saved docs/fig2_powerlaw_loglog.png
saved docs/fig3_sqrt_linear.png
saved docs/fig4_logistic.png
saved docs/fig5_e_vs_time.png
安全阈值 n₀ ≈ 6.2e+08

全部完成。
```

---

## 核心结论

| 问题 | 实验结论 |
|------|----------|
| `t` 与 `n` 的关系 | 双对数拟合斜率 `α ≈ 0.52`（理论值 0.5），**验证 `O(√n)` 成立** |
| `e` 是否影响破解时间 | 图5 线性拟合 `R² ≈ 0.003`（接近 0），**证明 `e` 对 Trial Division 无影响** |
| 安全边界（`TIMEOUT=1ms`） | 逻辑回归得出临界值 **`n₀ ≈ 6.2 × 10⁸`**（约 29 位二进制）|

> ⚠️ **注意**：以上 `n₀` 是针对 Trial Division + 1ms 超时的结果。实际 RSA 安全标准要求 `n` 至少为 **2048 位**（约 617 位十进制），Trial Division 在实用场景中完全不可行。

---

## AI 工具使用声明

本项目开发过程中使用了 **WorkBuddy（AI 编程助手）** 进行辅助，具体说明如下：

| 环节 | 本人独立完成 | AI 辅助部分 |
|------|------------|------------|
| RSA 核心算法（`rsa_core.py`） | ✅ 独立实现 | 无 |
| 数据分析思路设计 | ✅ 独立设计实验方案 | 讨论坐标选择（双对数 vs 线性） |
| `main.py` 绘图代码 | 框架由 AI 生成 | ✅ 调整图表参数、标注格式 |
|  README 文档 | 内容大纲由本人设计 | ✅ AI 辅助排版与措辞 |
| 目录结构整理 | ✅ 按作业要求独立规划 | AI 执行文件移动与文档生成 |

**核心回溯算法（Trial Division）与课程知识点对应分析由本人独立完成。**

---

## 作者与课程信息

- **课程**：cs201数据结构与算法
- **项目仓库**：[https://github.com/](https://github.com/wyb123-pku/cs201)
- **Python 版本**：3.13.12
- **最后更新**：2026-06-22

---

## 参考文献

1. Rivest, R. L., Shamir, A., & Adleman, L. (1978). *A method for obtaining digital signatures and public-key cryptosystems*. Communications of the ACM, 21(2), 120-126.
2. Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. （幂律分析、最小二乘法）
3. Menezes, A. J., et al. (1996). *Handbook of Applied Cryptography*. CRC Press. （RSA 安全性分析）
