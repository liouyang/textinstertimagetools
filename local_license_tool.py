import dashscope
import os
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta

# !!! 重要：这个 SECRET_SEED 应该是一个复杂、随机且在你的应用分发后不会改变的字符串。
# !!! 在实际部署中，硬编码 SECRET_SEED 存在逆向工程的风险。
# !!! 更安全的做法是，在构建时通过环境变量或 PyInstaller 的 hooks 注入。
# !!! 但对于本地分发应用，这是一个可行的起点。
SECRET_SEED = "YOUR_SUPER_SECRET_AND_UNIQUE_LICENSE_SEED_STRING_1234567890ABCD" # <-- 请替换为更复杂随机的字符串！

# 定义证书的有效期（例如，365天）
CERTIFICATE_VALID_DAYS = 365 # 保持与你实际设置一致，确保 test_license.py 也一致

def _get_certificate_payload(api_key: str, expiration_timestamp: int) -> str:
    """
    生成用于 HMAC 签名的字符串载荷。
    格式：API_KEY|EXPIRATION_TIMESTAMP
    """
    return f"{api_key}|{expiration_timestamp}"

def generate_certificate(api_key: str) -> str:
    """
    根据 API Key 和秘密种子生成一个带有过期时间的认证证书。
    证书格式：Base64(HMAC_SIGNATURE).Base64(EXPIRATION_TIMESTAMP)
    """
    if not api_key:
        raise ValueError("API Key 不能为空以生成证书。")

    expiration_dt = datetime.now() + timedelta(days=CERTIFICATE_VALID_DAYS)
    expiration_timestamp = int(expiration_dt.timestamp())

    payload = _get_certificate_payload(api_key, expiration_timestamp)

    h = hmac.new(SECRET_SEED.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256)
    signature = base64.urlsafe_b64encode(h.digest()).decode('utf-8')

    encoded_timestamp = base64.urlsafe_b64encode(str(expiration_timestamp).encode('utf-8')).decode('utf-8')

    certificate = f"{signature}.{encoded_timestamp}"
    return certificate

def verify_certificate(api_key: str, certificate_to_verify: str) -> bool:
    """
    验证给定的证书是否是根据提供的 API Key 和秘密种子生成的，并检查其时效性。
    证书格式：BASE64_SIGNATURE.BASE64_EXPIRATION_TIMESTAMP
    """
    if not api_key or not certificate_to_verify:
        print("API Key 或证书字符串为空，无法验证证书。")
        return False

    try:
        parts = certificate_to_verify.split('.')
        if len(parts) != 2:
            print("证书格式不正确。")
            return False

        user_signature = parts[0]
        encoded_timestamp = parts[1]

        try:
            expiration_timestamp = int(base64.urlsafe_b64decode(encoded_timestamp).decode('utf-8'))
        except (ValueError, TypeError):
            print("证书中的时间戳解码失败或格式无效。")
            return False

        current_timestamp = int(time.time())
        if current_timestamp > expiration_timestamp:
            print(f"证书已过期。当前时间: {datetime.fromtimestamp(current_timestamp)}, 过期时间: {datetime.fromtimestamp(expiration_timestamp)}")
            return False

        payload = _get_certificate_payload(api_key, expiration_timestamp)
        h = hmac.new(SECRET_SEED.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256)
        expected_signature = base64.urlsafe_b64encode(h.digest()).decode('utf-8')

        if hmac.compare_digest(user_signature.encode('utf-8'), expected_signature.encode('utf-8')):
            print("证书签名验证通过。")
            return True
        else:
            print("证书签名不匹配。")
            return False

    except Exception as e:
        print(f"验证证书时发生未知错误: {e}")
        return False

def check_dashscope_api_key(api_key: str) -> bool:
    """
    通过尝试对 DashScope 进行一次小型 API 调用来验证 API Key 的有效性。
    """
    if not api_key:
        print("API 密钥为空，无法验证 DashScope API。")
        return False

    # 1. 临时保存当前的 dashscope.api_key 值，如果它已经设置了
    original_dashscope_api_key = dashscope.api_key
    
    # 2. 设置本次验证使用的 API Key
    dashscope.api_key = api_key # <-- 直接赋值给 dashscope.api_key

    try:
        response = dashscope.Generation.call(
            model='qwen-turbo',
            prompt='你好',
            result_format='message'
        )

        if response.status_code == 200:
            print("DashScope API 密钥验证成功。")
            return True
        else:
            print(f"DashScope API 密钥验证失败。状态码: {response.status_code}, 错误信息: {response.message}")
            return False
    except Exception as e:
        print(f"验证 DashScope API 密钥时发生异常: {e}")
        return False
    finally:
        # 3. 恢复 dashscope.api_key 到其原始值
        dashscope.api_key = original_dashscope_api_key

# 这个辅助函数在实际应用中不再暴露给用户
def get_example_certificate_for_key(api_key_for_example: str) -> str:
    """
    提供一个辅助函数，用于演示如何为给定的 API Key 生成证书。
    这个函数不会在主要认证流程中使用，而是可以在一个独立的工具或 UI 区域使用。
    """
    if api_key_for_example:
        try:
            return generate_certificate(api_key_for_example)
        except ValueError as e:
            return f"生成证书失败: {e}"
    return "请输入 API Key 以生成示例证书"