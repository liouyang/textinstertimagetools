# # data.py
# import requests
# import json

# # 定义 API URL 和 Token
# API_URL = "https://xingchengstar.com/api/article/getTypeList"
# API_TOKEN = "bc4f4175-69c0-45cd-9d22-4d46c028c9f6" # 请替换为你的实际 Token

# # 用于存储获取到的分类数据
# categories = []

# def fetch_categories():
#     """
#     从 API 请求分类数据并更新全局 categories 列表。
#     """
#     global categories # 声明使用全局变量

#     request_url = f"{API_URL}?token={API_TOKEN}"
#     print(f"正在从 API 请求分类数据: {request_url}")

#     try:
#         response = requests.get(request_url)
#         response.raise_for_status()  # 检查 HTTP 错误 (4xx, 5xx)

#         json_data = response.json()

#         if json_data.get('code') == 1: # 假设 code 1 表示成功
#             fetched_data = json_data.get('data', [])
#             if isinstance(fetched_data, list):
#                 categories.clear() # 清空旧数据
#                 categories.extend(fetched_data) # 添加新数据
#                 print(f"成功获取 {len(categories)} 条分类数据。")
#             else:
#                 print("API 响应中 'data' 字段不是列表类型。")
#                 categories.clear()
#         else:
#             print(f"API 返回业务错误: code={json_data.get('code')}, msg={json_data.get('msg')}")
#             categories.clear() # 清空数据以防错误数据被使用
#     except requests.exceptions.RequestException as e:
#         print(f"请求 API 失败: {e}")
#         categories.clear()
#     except json.JSONDecodeError as e:
#         print(f"解析 JSON 响应失败: {e}")
#         categories.clear()
#     except Exception as e:
#         print(f"发生未知错误: {e}")
#         categories.clear()

# # 在模块加载时立即执行数据获取
# fetch_categories()

# # 如果你想在每次访问页面时都重新获取数据，
# # 那么你需要将 fetch_categories() 的调用移动到 app.py 的 index() 函数中。
# # 但为了保持 data.py 的职责单一性，目前让它在模块加载时执行一次。