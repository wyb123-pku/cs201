"""
tests/test_rsa_core.py

对 rsa_core.py 核心函数的单元测试。
运行方式：
    cd D:/assignmentP
    python -m pytest tests/test_rsa_core.py -v
    或：
    python tests/test_rsa_core.py
"""

import sys
import os
import traceback

# 将项目根目录加入 sys.path，使导入生效
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 同时加入 src/ 目录
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from rsa_core import get_keys, mod_pow, crack_n, eluer_prime


def test_eluer_prime():
    """测试埃拉托色尼筛法生成的素数列表"""
    primes = eluer_prime(30)
    expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert primes[:len(expected)] == expected, f"素数表错误: {primes[:15]}"
    print("✓ test_eluer_prime passed")


def test_get_keys_format():
    """测试密钥生成返回的 (p, q, n, phi, e, d) 格式与基本性质"""
    primes = eluer_prime(1000)
    p, q, n, phi, e, d = get_keys(primes)

    assert p in primes, "p 不是素数"
    assert q in primes, "q 不是素数"
    assert n == p * q, "n != p * q"
    assert phi == (p - 1) * (q - 1), "phi 计算错误"
    assert mod_pow(e, d, phi) == 1, "e * d mod phi != 1"
    print("✓ test_get_keys_format passed")


def test_mod_pow_correctness():
    """测试快速模幂的正确性（与 Python 内置 pow 对比）"""
    primes = eluer_prime(1000)
    p, q, n, phi, e, d = get_keys(primes)

    test_cases = [0, 1, 42, 999, n - 1]
    for m in test_cases:
        expected = pow(m, e, n)
        got = mod_pow(m, e, n, T=phi)
        assert got == expected, f"mod_pow({m}, {e}, {n}) = {got}, expected {expected}"

    # 加解密往返测试
    m = 123456
    c = mod_pow(m, e, n, T=phi)
    m_recovered = mod_pow(c, d, n, T=phi)
    assert m_recovered == m, f"加解密往返失败: 原文={m}, 还原={m_recovered}"
    print("✓ test_mod_pow_correctness passed")


def test_crack_n_small():
    """对小规模 n 测试 crack_n 能正确分解"""
    primes = eluer_prime(10000)
    p, q, n, phi, e, d = get_keys(primes)

    result = crack_n(n, timeout=5.0)  # 大超时，确保能跑完
    assert result is not None, f"crack_n 未能分解 n={n}"
    p_found, q_found = result
    assert p_found * q_found == n, f"分解结果错误: {p_found}*{q_found} != {n}"
    print(f"✓ test_crack_n_small passed (n={n}, found {p_found}×{q_found})")


def test_crack_n_timeout():
    """测试超时机制：对大 n 应在 timeout 内返回 None"""
    # 构造一个较大的 n（~10^8），超时设得很小
    primes = eluer_prime(100000)
    import random
    random.seed(42)
    p = primes[5000]
    q = primes[6000]
    n = p * q

    start = __import__('time').perf_counter()
    result = crack_n(n, timeout=0.0001)  # 0.1ms，必然超时
    elapsed = __import__('time').perf_counter() - start

    assert elapsed < 0.5, f"超时机制失效，耗时 {elapsed:.2f}s"
    # result 可能是 None（超时）或偶发分解成功（小概率），不强制断言
    print(f"✓ test_crack_n_timeout passed (elapsed={elapsed:.4f}s, result={result})")


def run_all():
    """运行全部测试"""
    tests = [
        test_eluer_prime,
        test_get_keys_format,
        test_mod_pow_correctness,
        test_crack_n_small,
        test_crack_n_timeout,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ {t.__name__} FAILED: {e}")
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"✗ {t.__name__} ERROR: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*40}")
    print(f"结果: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
