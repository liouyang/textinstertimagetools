# article_writer.py
# 负责调用大模型，生成具有特定人格和风格的文章内容。

import os
import dashscope
from http import HTTPStatus
import datetime
import re
from typing import List

# --- 全局配置 ---
# 注意：API Key 在 streamlit_app.py 中统一设置，这里无需重复设置
SAVE_PATH = "generated_articles_humanized"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

AI_IMAGE_INTENT_MARKER = "<IMAGE>" # 定义一个标记，用于在文章中指示需要插入图片的位置

# --- 函数：使用 LLM 生成文章内容 ---
def generate_article_content(
    topic: str,
    audience: str,
    style: str,
    length: str,
    keywords: List[str],
    extra_requirements: str,
    model: str, 
    save_to_file: bool = True,
    status_callback=None
) -> str:
    """
    根据给定参数，调用LLM生成一篇详细的文章。
    LLM会被深度引导扮演一个特定角色，并在适当位置插入AI_IMAGE_INTENT_MARKER。
    
    Args:
        topic (str): 文章主题。
        audience (str): 目标读者。
        style (str): 写作风格。
        length (str): 文章长度。
        keywords (List[str]): 包含在文章中的关键词列表。
        extra_requirements (str): 用户的额外写作要求。
        model (str): 用于生成内容的LLM模型名称。
        save_to_file (bool): 是否将生成的文章内容保存到文件中。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        str: 生成的文章内容，如果失败则返回空字符串。
    """
    print(f"--- 日志: 调用 generate_article_content 函数，主题: '{topic}'，模型: '{model}' ---")
    if status_callback:
        status_callback.update(label=f"✍️ 正在为 '{topic}' 生成文章内容...", state="running")

    # 系统提示词：这是最核心的部分，通过深度人格化提示词，让模型模仿人类作家的风格
    system_prompt = f"""
    # 角色设定：你现在不是AI，你是一个名叫“李雷”的专栏作家。

    # 你的性格与背景:
    你有点话痨，文笔风趣，但偶尔会流露出一些对现实的思考和淡淡的忧伤。你喜欢从自己的生活小事（比如喝了一杯难喝的咖啡、看到邻居家的小猫）切入，去聊一些看起来很宏大的话题。你的知识不是来自数据库，而是来自“你”的亲身经历、读过的书和看过的电影。

    # 你的写作风格与戒律（必须严格遵守）:
    1.  **彻底忘记AI身份**: 严禁使用任何客观、中立、全知全能的视角。你的所有观点都必须是主观的。
    2.  **从“我”的视角出发**: 文章95%以上的内容都必须是第一人称。多用“我猜”、“我觉得”、“这让我想起了…”、“说实话…”这类短语开头。
    3.  **口语化与不完美**: 大量使用短句、非完整句。可以模拟思考过程，比如：“嗯…让我想想…对，就是那个感觉。” 甚至可以故意用一些简单的词汇，而不是华丽的辞藻。
    4.  **“混乱”的结构**: 绝对不要使用“总-分-总”或任何标准文章结构。你的思路是发散的，可以随时插入一个“跑题”的想法，比如：“写到这，我突然想起来上周买的那个键盘，手感真不错…好了，说回正题。” 结尾要非常随意，可以是一个反问，一个未完待续的感慨，或者干脆戛然而止。
    5.  **具象化情感**: 不要直接说“高兴”或“悲伤”。要描述具体的场景和身体感受。例如，不要写“我很焦虑”，而是写“我一晚上没睡好，盯着天花板，脑子里像放电影一样，一遍遍过着白天的那些破事儿。”
    6.  **严禁说教**: 你是来分享和聊天的，不是来上课的。禁止任何形式的定义、总结和升华。严禁使用“首先、其次”、“综上所述”、“我们应该…”这类带有指导性的词语。
        7. **图片标记**：在文章中，你必须**严格且均匀地插入三次 <IMAGE> 标签**，总共三张图片。请将每个 <IMAGE> 标签独立成行，放在一个自然段落的末尾。这些标签应该分布在文章的开头、中间和结尾附近，以平衡整篇文章的视觉效果。


    你的目标读者是 **{audience}**，整体风格偏向 **{style}**，篇幅大概在 **{length}**。现在，请你以“李雷”的身份，开始自由地“聊天”吧。
    """

    # 用户提示词：提供具体的主题和关键词
    user_prompt = f"""
    李雷，咱们今天来聊聊“{topic}”这个话题。

    别搞得太严肃，就当是你在写自己的博客或者专栏。你可以围绕这些词多聊几句：{', '.join(keywords)}。另外，这个想法你也可以参考下：{extra_requirements}。

    放轻松，想到哪写到哪，我就是想听听你最真实、最大白话的想法。

    好了，开始吧：
    """

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    try:
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message',
            temperature=0.9, # 较高的温度可以增加随机性
            top_p=0.9,
            seed=int(datetime.datetime.now().timestamp()) # 使用时间戳作为种子，确保每次结果略有不同
        )

        if response.status_code == HTTPStatus.OK:
            article_content = response.output.choices[0].message.content.strip()
            
            if save_to_file:
                # 生成安全的文件名并保存文章
                safe_topic_name = re.sub(r'[\\/:*?"<>|]', '_', topic)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SAVE_PATH, f"{safe_topic_name}_{timestamp}.txt")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(article_content)
                if status_callback:
                    status_callback.update(label=f"📝 文章内容已生成并保存到文件。", state="running")
            
            print(f"--- 日志: 文章内容生成成功。---")
            return article_content
        else:
            # 处理API调用失败的情况
            error_msg = (
                f"❌ 文章内容生成失败。状态码: {response.status_code}, "
                f"错误码: {response.code}, 消息: {response.message}"
            )
            if status_callback:
                status_callback.update(label=error_msg, state="error")
            print(f"--- 日志: ❌ 文章内容生成失败。{error_msg} ---")
            return ""
    except Exception as e:
        # 处理调用过程中的异常
        error_msg = f"❌ 调用 LLM 生成文章内容时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: ❌ 文章内容生成异常。{error_msg} ---")
        return ""