# # app.py
# from flask import Flask, render_template, request, redirect, url_for
# import requests
# import json
# from data import categories # 从 data.py 导入分类数据

# app = Flask(__name__)

# # --- 文章 API 配置 ---
# BASE_ARTICLE_API_URL = "https://xingchengstar.com/api/article/index"
# API_TOKEN = "bc4f4175-69c0-45cd-9d22-4d46c028c9f6" # <--- 重要：请替换为你的实际 API TOKEN !!!
# DEFAULT_PAGE_SIZE = 10 # 文章列表默认每页显示数量

# # --- 文章获取函数（复用并调整自之前的 Flask 示例） ---
# def fetch_articles_by_type(article_type: int, page: int, page_size: int):
#     """
#     根据指定的文章类型（分类ID）、页码和每页数量从 API 获取文章。
#     返回一个字典，包含文章列表、当前页码、是否有更多数据以及任何错误信息。
#     """
#     url = f"{BASE_ARTICLE_API_URL}?type={article_type}&page={page}&page_size={page_size}&token={API_TOKEN}"
#     print(f"Flask 服务器正在请求文章 API: {url}") # 在 Flask 服务器控制台打印请求 URL，用于调试

#     try:
#         response = requests.get(url)
#         response.raise_for_status() # 如果 HTTP 状态码是 4xx 或 5xx，则抛出异常
#         full_api_response = response.json()

#         if full_api_response.get('code') == 1:
#             articles_list = full_api_response.get('data', [])
#             # 根据你的描述：如果返回的文章数量等于请求的 page_size，则认为可能还有下一页
#             has_more_data = len(articles_list) == page_size

#             return {
#                 'articles': articles_list,
#                 'current_page': page,
#                 'has_more_data': has_more_data,
#                 'error': None
#             }
#         else:
#             error_msg = full_api_response.get('msg', '未知API错误')
#             print(f"文章 API 返回业务错误: code={full_api_response.get('code')}, msg={error_msg}")
#             return {
#                 'articles': [],
#                 'current_page': page,
#                 'has_more_data': False,
#                 'error': f"API 业务错误: {error_msg}"
#             }
#     except requests.exceptions.RequestException as e:
#         print(f"请求文章 API 失败: {e}")
#         return {
#             'articles': [],
#             'current_page': page,
#             'has_more_data': False,
#             'error': f"文章 API 请求失败: {e}"
#         }
#     except json.JSONDecodeError as e:
#         print(f"解析文章 API JSON 响应失败: {e}")
#         return {
#             'articles': [],
#             'current_page': page,
#             'has_more_data': False,
#             'error': f"文章 API JSON 解析失败: {e}"
#         }
#     except Exception as e:
#         print(f"获取文章时发生未知错误: {e}")
#         return {
#             'articles': [],
#             'current_page': page,
#             'has_more_data': False,
#             'error': f"服务器内部错误: {e}"
#         }

# # --- 分类列表页面路由（主页） ---
# @app.route('/')
# def index():
#     # 'categories' 变量包含从 data.py 中获取的数据
#     return render_template('index.html', categories=categories)

# # --- 新的二级文章页面路由 ---
# # <int:category_id> 表示这是一个整数参数，将从 URL 中捕获
# @app.route('/articles/<int:category_id>')
# def articles_page(category_id):
#     # 从 URL 查询参数中获取页码和每页数量，默认为 1 和 DEFAULT_PAGE_SIZE
#     page = request.args.get('page', 1, type=int)
#     page_size = request.args.get('page_size', DEFAULT_PAGE_SIZE, type=int)

#     # 确保页码和每页数量至少为 1
#     if page < 1:
#         page = 1
#     if page_size < 1:
#         page_size = DEFAULT_PAGE_SIZE

#     # 使用 category_id 作为 'type' 参数来获取文章
#     article_data = fetch_articles_by_type(category_id, page, page_size)

#     # 准备传递给模板的数据
#     articles = article_data['articles']
#     current_page = article_data['current_page']
#     has_more_data = article_data['has_more_data']
#     api_error = article_data['error']

#     # 用于“每页显示数量”下拉菜单的选项
#     page_sizes_options = [5, 10, 20, 50]

#     # 查找分类名称以便在页面上显示（可选，但能提供更好的用户体验）
#     category_name = "未知分类"
#     # 'categories' 是从 data.py 导入的全局变量
#     for cat in categories:
#         if cat.get('id') == category_id:
#             category_name = cat.get('name', "未知分类")
#             break

#     return render_template(
#         'articles.html',
#         category_id=category_id, # 将 category_id 传回模板，用于构建分页链接
#         category_name=category_name, # 传递分类名称
#         articles=articles,
#         current_page=current_page,
#         has_more_data=has_more_data,
#         page_size=page_size,
#         page_sizes_options=page_sizes_options,
#         api_error=api_error # 传递错误信息
#     )

# if __name__ == '__main__':
#     app.run(debug=True) # 启动 Flask 开发服务器，debug=True 会自动重新加载代码