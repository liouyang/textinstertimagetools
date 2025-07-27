# batch_article_generator.py

import os
import dashscope
from http import HTTPStatus
import re
import datetime
import time 
import json 
from typing import List, Dict, Any
import markdown

# 从现有模块导入功能
from article_writer import generate_article_content
from wanxiangimg import process_article_and_generate_images, generate_image_from_prompt

# --- 全局配置 ---
# 注意：API Key 在 streamlit_app.py 中统一设置，这里无需重复设置
LLM_MODEL_FOR_TITLE_GENERATION = "qwen-turbo" # 指定用于生成标题的模型

OUTPUT_SAVE_PATH = "generated_output"
# 确保输出目录存在
if not os.path.exists(OUTPUT_SAVE_PATH):
    os.makedirs(OUTPUT_SAVE_PATH)


# --- 函数：使用 LLM 生成文章标题列表 ---
def generate_article_titles(main_topic: str, num_titles: int, status_callback=None) -> List[str]:
    """
    根据主课题，调用LLM生成指定数量的文章标题。
    
    Args:
        main_topic (str): 主课题。
        num_titles (int): 需要生成的标题数量。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        List[str]: 生成的文章标题列表，如果失败则返回空列表。
    """
    print(f"\n--- 日志: 开始为主题 '{main_topic}' 生成文章标题 ({num_titles} 个) ---")
    if status_callback:
        status_callback.update(label=f"🔄 正在调用 LLM 生成 {num_titles} 个文章标题...", state="running")

    # 系统提示词：定义LLM的角色和写作风格
    system_prompt = ("你是一个顶级的创意标题生成器，擅长为给定主题生成多个新颖、吸引人且**具有强烈人类写作风格**的文章标题。你的目标是让读者一眼就被吸引，感觉是真实的人在思考和表达。")
    # 用户提示词：包含具体任务和要求
    user_prompt = f"""
    请根据以下主课题，生成 {num_titles} 个独特的、具有吸引力的文章标题。每个标题应该直接作为一篇文章的主题。
    主课题: “{main_topic}”
    **关键要求，请务必遵循，以确保标题更像人写：**
    1.  **避免**过于生硬、机械或总结式的表达。
    2.  **融入**疑问、反思、情感、观点或小小的悬念。
    3.  可以使用**更口语化、更生活化**的词汇，或引发读者共鸣的表达。
    4.  标题要**足够具体**，可以直接作为一篇文章的主题，但又不能缺乏想象力。
    5.  确保标题之间**内容和切入点有明显差异**，风格也可以略有不同，体现多样性。
    6.  每个标题独占一行，标题之间不要有序号或任何额外文字。
    例如，如果主题是“智能家居”，不要只写“智能家居的优势和挑战”。可以尝试：
    - “我家智能音箱突然‘不想上班’了，我该笑还是该哭？”
    - “AI正在‘偷’走我们的家务，这是好事吗？”
    - “你家的智能门锁，真的比你更懂安全吗？”
    请严格按照示例的风格和要求生成：
    """
    messages = [{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]

    try:
        # 调用 DashScope 的文本生成服务
        response = dashscope.Generation.call(
            model=LLM_MODEL_FOR_TITLE_GENERATION, 
            messages=messages, 
            result_format='message', 
            temperature=1.0, 
            top_p=0.9
        )
        if response.status_code == HTTPStatus.OK:
            titles_raw = response.output.choices[0].message.content.strip()
            titles_list = [t.strip() for t in titles_raw.split('\n') if t.strip()]
            if status_callback:
                status_callback.update(label="✅ 文章标题生成成功！", state="running")
            print(f"--- 日志: 标题生成成功。共生成 {len(titles_list)} 个标题。---")
            print(f"生成的标题列表: {titles_list}")
            return titles_list
        else:
            error_msg = f"❌ 标题生成失败。状态码: {response.status_code}, 错误码: {response.code}, 消息: {response.message}"
            if status_callback:
                status_callback.update(label=error_msg, state="error")
            print(f"--- 日志: 标题生成失败。{error_msg} ---")
            return []
    except Exception as e:
        error_msg = f"❌ 调用 LLM 生成标题时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: 标题生成异常。{error_msg} ---")
        return []

# --- 函数：将处理后的JSON数据转换为HTML页面 ---
def convert_json_to_markdown_to_html(
    title: str,
    processed_data: List[Dict[str, Any]],
    output_filename: str,
    status_callback=None
):
    """
    将包含段落和图片的JSON数据结构转换为一个HTML页面。
    
    Args:
        title (str): 文章的标题。
        processed_data (List[Dict[str, Any]]): 包含文章内容的列表，每个元素代表一个段落或一张图片。
        output_filename (str): 输出HTML文件的文件名。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
    """
    print(f"--- 日志: 开始将文章 '{title}' 转换为 HTML 页面 ---")
    if status_callback:
        status_callback.update(label="📜 正在将JSON数据转换为Markdown并生成HTML...", state="running")
    
    html_content = f"<h1>{title}</h1>\n\n"
    for item in processed_data:
        if item['type'] == 'paragraph':
            # 将Markdown格式的段落内容转换为HTML
            paragraph_html = markdown.markdown(item['content'])
            html_content += paragraph_html
        elif item['type'] == 'image' and item.get('base64_image_data'):
            # 如果是图片，则使用Base64数据嵌入到HTML中
            alt_text = item.get('content', "AI生成的图片")
            html_content += f'<img src="{item["base64_image_data"]}" alt="{alt_text}" style="max-width: 100%; height: auto; display: block; margin: 2em auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>\n\n'

    # 构造输出文件的完整路径
    output_filepath = os.path.join(OUTPUT_SAVE_PATH, output_filename)
    # 将生成的HTML内容写入文件
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    if status_callback:
        status_callback.update(label=f"✅ HTML内容已生成到 {output_filepath}", state="running")
    print(f"--- 日志: HTML内容已生成到 {output_filepath} ---")

# --- 主函数：批量生成文章 ---
def batch_generate_articles(
    main_topic: str,
    num_articles: int,
    article_gen_params: dict, 
    delay_between_articles: int = 10,
    status_callback=None
):
    """
    批量生成多篇文章，并为每篇文章配图、生成HTML。
    
    Args:
        main_topic (str): 主课题。
        num_articles (int): 需要生成的文章数量。
        article_gen_params (dict): 包含文章生成细节参数的字典。
        delay_between_articles (int): 每篇文章生成之间的延迟时间（秒）。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
    """
    print(f"\n--- 日志: 批量生成任务开始 (主课题: {main_topic}, 数量: {num_articles}) ---")
    if status_callback:
        status_callback.update(label=f"🎯 正在为主题 '{main_topic}' 准备生成 {num_articles} 篇文章。", state="running")

    # 第一步：为批量生成任务生成所有文章标题
    article_topics = generate_article_titles(main_topic, num_articles, status_callback=status_callback)
    if not article_topics:
        if status_callback:
            status_callback.update(label="❌ 未能生成任何文章标题，批量生成终止。", state="error")
        print("--- 日志: 批量生成终止，未生成任何标题。---")
        return
    
    # 从参数字典中提取模型信息
    llm_model = article_gen_params.get('llm_model', "qwen-plus") 
    image_model = article_gen_params.get('image_model', "wanx-v1") 

    # 循环处理每一篇文章
    for i, topic in enumerate(article_topics):
        current_article_index = i + 1
        total_articles = len(article_topics)
        print(f"\n--- 日志: 开始处理第 {current_article_index}/{total_articles} 篇文章: '{topic}' ---")
        if status_callback:
            status_callback.update(label=f"文章 {current_article_index}/{total_articles}: 正在处理 '{topic}'...", state="running")
            
        # 提取文章生成参数
        current_article_audience = article_gen_params.get('audience', "通用读者")
        current_article_style = article_gen_params.get('style', "科普性")
        current_article_length = article_gen_params.get('length', "中篇（600-900字）")
        current_article_keywords = article_gen_params.get('keywords', [])

        # 组合额外要求和默认要求
        default_extra_requirements = (
            "文章应内容自然流畅，避免AI写作的痕迹。请使用加粗标记强调核心概念。"
            "**如果文章包含小标题或强调句，请务必使用双星号（**内容**）进行加粗，并确保其独立成行，不与正文混杂在同一行。**"
            "**重要提示：在您认为文章的某个自然段落结束后，或者当你认为需要一个视觉元素来增强说明时，请在该自然段落的末尾另起一行并插入标记 <IMAGE>。请确保 <IMAGE> 是该行的唯一内容。**"
        )
        user_defined_extra_reqs = article_gen_params.get('extra_requirements', '')
        current_extra_requirements = (user_defined_extra_reqs + "\n\n" + default_extra_requirements).strip()
        current_extra_requirements = re.sub(r'(\*\*重要提示:.*?<IMAGE>.*?\*\*)\s*\1', r'\1', current_extra_requirements, flags=re.DOTALL)

        # 第二步：生成文章内容
        if status_callback:
            status_callback.update(label=f"文章 {current_article_index}/{total_articles}: 正在生成文章内容...", state="running")
        generated_article_content = generate_article_content(
            topic=topic, 
            audience=current_article_audience, 
            style=current_article_style, 
            length=current_article_length,
            keywords=current_article_keywords, 
            extra_requirements=current_extra_requirements,
            model=llm_model, 
            save_to_file=True, 
            status_callback=status_callback
        )
        if not generated_article_content:
            if status_callback:
                status_callback.update(label=f"❌ 文章 {current_article_index}/{total_articles}: 未能生成内容，跳过。", state="error")
            print(f"--- 日志: ❌ 未能为文章 '{topic}' 生成内容，跳过后续步骤。---")
            continue

        # 第三步：处理文章并生成图片
        if status_callback:
            status_callback.update(label=f"文章 {current_article_index}/{total_articles}: 正在处理配图...", state="running")
        processed_data = process_article_and_generate_images(
            generated_article_content, 
            enable_image_generation=True, 
            image_model=image_model, 
            status_callback=status_callback
        )
        
        # 第四步：生成HTML页面
        if processed_data:
            # 创建安全的文件名
            safe_html_filename_base = re.sub(r'[\\/:*?"<>|]', ' ', topic)[:50].strip().replace(' ', '_')
            output_html_filename = f"{safe_html_filename_base}_{current_article_index}_with_ai_images.html"
            convert_json_to_markdown_to_html(
                topic, 
                processed_data, 
                output_html_filename, 
                status_callback=status_callback
            )
            print(f"--- 日志: 第 {current_article_index} 篇文章已处理完毕。---")
        else:
            if status_callback:
                status_callback.update(label=f"❌ 文章 {current_article_index}/{total_articles}: 未生成图片数据，无法创建HTML页面。", state="error")
            print(f"--- 日志: ❌ 未为文章 '{topic}' 生成任何图片数据，无法创建HTML页面。---")

        # 第五步：保存处理后的JSON数据（可选）
        safe_json_filename_base = re.sub(r'[\\/:*?"<>|]', ' ', topic)[:50].strip().replace(' ', '_')
        output_json_filename = f"{safe_json_filename_base}_{current_article_index}_results.json"
        output_json_filepath = os.path.join(OUTPUT_SAVE_PATH, output_json_filename)
        with open(output_json_filepath, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
        if status_callback:
            status_callback.update(label=f"✅ 文章 {current_article_index}/{total_articles}: 结果数据已保存到 {output_json_filepath}", state="running")
        print(f"--- 日志: 结果数据已保存到 {output_json_filepath} ---")

        # 在处理下一篇文章之前进行延迟
        if i < len(article_topics) - 1:
            print(f"\n--- 日志: 暂停 {delay_between_articles} 秒，准备开始下一篇文章... ---")
            if status_callback:
                status_callback.update(label=f"文章 {current_article_index}/{total_articles}: 暂停 {delay_between_articles} 秒，准备下一篇...", state="running")
            time.sleep(delay_between_articles)

    print("\n--- 日志: 批量生成任务全部完成。---")

# --- 主执行区 (在没有Streamlit运行时，用于本地测试) ---
if __name__ == "__main__":
    # 检查是否存在 API Key 环境变量，并且当前不是在Streamlit中运行
    if os.environ.get("DASHSCOPE_API_KEY") and os.environ.get("STREAMLIT_RUN", "false").lower() != "true":
        main_batch_topic = "未来教育的创新与挑战"
        num_of_articles = 1
        article_generation_parameters = {
            'audience': "教育工作者、学生家长及对教育改革感兴趣的公众", 'style': "深度分析、启发思考，略带未来主义色彩",
            'length': "中篇（700-1000字）", 'keywords': ["未来教育", "AI教育", "个性化学习", "终身学习", "教育技术"],
            'extra_requirements': ("文章应探讨AI、虚拟现实、个性化学习在未来教育中的应用，以及随之而来的伦理、社会挑战。"
                "可以引用一些假想的未来教育场景或案例。" "请使用引人入胜的语言。"),
            'llm_model': 'qwen-plus',
            'image_model': 'wanx-v1'
        }
        batch_generate_articles(
            main_batch_topic, num_of_articles, article_generation_parameters, delay_between_articles=15)