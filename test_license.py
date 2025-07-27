# test_license.py

import os
import sys
import time
from datetime import datetime, timedelta

# 为了能够导入 local_license_tool，需要确保当前目录或其父目录在 Python 路径中
# 如果 local_license_tool.py 在你的当前运行目录下，通常不需要这行
# 如果 local_license_tool.py 在上一级目录，可以尝试：
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# 导入你的 local_license_tool 模块
# 确保你的 local_license_tool.py 文件在可导入的路径中
try:
    import local_license_tool
    # 重新设置 SECRET_SEED 和 CERTIFICATE_VALID_DAYS，以防万一
    # ！！！请确保这里的 SECRET_SEED 和你 local_license_tool.py 中最终使用的保持一致！！！
    # 否则测试结果可能不准确
    local_license_tool.SECRET_SEED = "YOUR_SUPER_SECRET_AND_UNIQUE_LICENSE_SEED_STRING_1234567890ABCD"
    local_license_tool.CERTIFICATE_VALID_DAYS = 2 # 保持与你实际设置一致
except ImportError:
    print("错误: 无法导入 local_license_tool 模块。请确保 local_license_tool.py 存在于当前目录或 Python 路径中。")
    sys.exit(1)
except AttributeError:
    print("警告: 无法设置 local_license_tool.SECRET_SEED 或 CERTIFICATE_VALID_DAYS。请确保它们在模块中定义为变量。")


def run_test_case(name, func, *args):
    """通用测试用例运行器"""
    print(f"\n--- 测试用例: {name} ---")
    try:
        result = func(*args)
        print(f"结果: {result}")
    except Exception as e:
        print(f"发生异常: {e}")
    print("-" * (len(name) + 10))


if __name__ == "__main__":
    # --- 请替换为你的实际 API Key 和你期望的 SECRET_SEED ---
    # 警告: 实际使用中不要将真实的 API Key 硬编码在这里！
    # 这里的 YOUR_DASH_SCOPE_API_KEY 应该是一个真实的、有效的 DashScope API Key
    # 以便测试 check_dashscope_api_key 函数
    TEST_API_KEY = "sk-b547aee5005d4023991f92aa9a585b0a" # <-- 替换为你的真实 DashScope API Key
    
    # 确保 local_license_tool.py 中的 SECRET_SEED 和 CERTIFICATE_VALID_DAYS 与这里一致
    # 否则证书生成和验证会失败

    print(f"测试使用的 SECRET_SEED: {local_license_tool.SECRET_SEED[:10]}...")
    print(f"证书有效期 (天): {local_license_tool.CERTIFICATE_VALID_DAYS}")

    # --- 证书生成测试 ---
    print("\n--- 证书生成测试 ---")
    generated_cert = local_license_tool.generate_certificate(TEST_API_KEY)
    print(f"为 API Key '{TEST_API_KEY[:8]}...' 生成的证书: {generated_cert}")
    print("-" * 20)

    # --- 证书验证测试 ---

    # 1. 验证成功：使用正确的 API Key 和刚生成的证书
    run_test_case(
        "证书验证成功 (正确 API Key, 正确证书)",
        local_license_tool.verify_certificate,
        TEST_API_KEY,
        generated_cert
    )

    # 2. 验证失败：API Key 为空
    run_test_case(
        "证书验证失败 (API Key 为空)",
        local_license_tool.verify_certificate,
        "",
        generated_cert
    )

    # 3. 验证失败：证书为空
    run_test_case(
        "证书验证失败 (证书为空)",
        local_license_tool.verify_certificate,
        TEST_API_KEY,
        ""
    )

    # 4. 验证失败：API Key 不正确（但证书格式正确）
    run_test_case(
        "证书验证失败 (API Key 不正确)",
        local_license_tool.verify_certificate,
        "WRONG_API_KEY_123",
        generated_cert
    )

    # 5. 验证失败：证书不正确（篡改证书）
    corrupted_cert = generated_cert[:-5] + "XXXXX" # 故意破坏证书
    run_test_case(
        "证书验证失败 (证书被篡改)",
        local_license_tool.verify_certificate,
        TEST_API_KEY,
        corrupted_cert
    )
    
    # 6. 验证失败：证书格式不正确
    malformed_cert = "invalid.format.cert"
    run_test_case(
        "证书验证失败 (证书格式不正确)",
        local_license_tool.verify_certificate,
        TEST_API_KEY,
        malformed_cert
    )

    # 7. 验证失败：模拟证书过期
    print("\n--- 模拟证书过期测试 ---")
    # 临时修改 local_license_tool.CERTIFICATE_VALID_DAYS 为一个负数，使其立即过期
    original_valid_days = local_license_tool.CERTIFICATE_VALID_DAYS
    local_license_tool.CERTIFICATE_VALID_DAYS = -1 # 设置为立即过期
    expired_cert = local_license_tool.generate_certificate(TEST_API_KEY)
    local_license_tool.CERTIFICATE_VALID_DAYS = original_valid_days # 恢复原值

    run_test_case(
        "证书验证失败 (模拟证书已过期)",
        local_license_tool.verify_certificate,
        TEST_API_KEY,
        expired_cert
    )
    print("请注意：如果系统时间不向前调整，实际生成的证书不会过期。此测试仅模拟了证书内容表示过期。")
    print("-" * 20)


    # --- DashScope API Key 验证测试 ---
    
    # 8. 验证成功：使用正确的 DashScope API Key
    # 这将实际调用 DashScope API，请确保你的网络连接和 API Key 有效
    run_test_case(
        "DashScope API Key 验证成功 (正确 Key)",
        local_license_tool.check_dashscope_api_key,
        TEST_API_KEY
    )

    # 9. 验证失败：DashScope API Key 不正确或无效
    run_test_case(
        "DashScope API Key 验证失败 (错误 Key)",
        local_license_tool.check_dashscope_api_key,
        "sk-INVALID_DASH_SCOPE_KEY_00000000000000000"
    )

    # 10. 验证失败：DashScope API Key 为空
    run_test_case(
        "DashScope API Key 验证失败 (空 Key)",
        local_license_tool.check_dashscope_api_key,
        ""
    )

    print("\n所有测试用例运行完毕。")