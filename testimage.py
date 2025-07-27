# wanxiang_test.py
import os
import dashscope
import time
import base64
import json
from wanxiangimg import (
    generate_image_prompt_from_paragraph,
    generate_image_from_prompt,
    download_and_encode_image_as_base64
)

def run_wanxiang_test():
    """
    运行文生图模块的端到端测试，从中文段落生成图片到嵌入HTML。
    """
    # 检查 API Key 是否已设置
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：DASHSCOPE_API_KEY 环境变量未设置。请先设置您的 API Key。")
        print("您可以在终端运行：export DASHSCOPE_API_KEY='您的API_KEY' (mac/linux) 或 set DASHSCOPE_API_KEY='您的API_KEY' (windows)")
        return

    print("--- 文生图模块测试开始 ---")
    
    # 1. 定义一个用于测试的中文段落
    test_paragraph = "未来的城市交通会是什么样子？或许是垂直起降的飞行汽车，在摩天大楼之间穿梭，而地面上是宁静的公园和自行车道。"
    print(f"✅ 测试中文段落: '{test_paragraph}'")

    # 2. 调用函数生成英文图片提示词
    print("⏳ 步骤 1/3: 正在从中文段落生成英文提示词...")
    english_prompt = generate_image_prompt_from_paragraph(test_paragraph)
    if not english_prompt:
        print("❌ 错误：未能生成英文提示词。请检查网络或API Key。")
        return
    print(f"✅ 生成的英文提示词: '{english_prompt}'")
    
    time.sleep(5) # 暂停5秒，避免调用过于频繁

    # 3. 调用函数生成图片URL
    print("⏳ 步骤 2/3: 正在调用文生图模型生成图片...")
    image_url = generate_image_from_prompt(english_prompt)
    if not image_url:
        print("❌ 错误：未能生成图片URL。请检查模型调用是否成功。")
        return
    print(f"✅ 生成的图片URL: '{image_url}'")
    
    time.sleep(5)

    # 4. 调用函数下载图片并编码为Base64
    print("⏳ 步骤 3/3: 正在下载图片并进行Base64编码...")
    base64_data = download_and_encode_image_as_base64(image_url)
    if not base64_data:
        print("❌ 错误：未能将图片编码为Base64。请检查下载URL是否有效。")
        return
    print("✅ 图片已成功编码为Base64数据。")

    # 5. 将结果写入一个简单的HTML文件进行验证
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>文生图测试报告</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; margin: 2em; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>文生图测试报告</h1>
        <p>这是一个从以下中文段落生成的图片：</p>
        <blockquote>{test_paragraph}</blockquote>
        <h2>AI生成的图片</h2>
        <img src="{base64_data}" alt="AI生成的测试图片"/>
        <p>如果图片正常显示，说明文生图模块工作正常。</p>
    </body>
    </html>
    """
    
    output_filename = "wanxiang_test_output.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n🎉 测试完成！请打开文件 '{output_filename}' 查看结果。")
    print("--- 文生图模块测试结束 ---")


if __name__ == "__main__":
    run_wanxiang_test()