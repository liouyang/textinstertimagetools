# wanxiangimg.py
# 负责调用文生图模型，并根据文章内容智能插入图片。

import os
import dashscope
from http import HTTPStatus
import re
import base64
import requests
import time
from typing import Union, List

# --- 配置 ---
# 注意：API Key 在 streamlit_app.py 中统一设置，这里无需重复设置
AI_IMAGE_INTENT_MARKER = "<IMAGE>"
PARAGRAPHS_PER_IMAGE = 3 # 默认每隔3个自然段落插入一张图片
IMAGE_SAVE_PATH = "generated_images"
if not os.path.exists(IMAGE_SAVE_PATH):
    os.makedirs(IMAGE_SAVE_PATH)

# --- 辅助函数：将图片URL下载并编码为Base64 ---
def download_and_encode_image_as_base64(image_url: str, status_callback=None) -> Union[str, None]:
    """
    下载指定URL的图片，并将其编码为Base64字符串，以便直接嵌入HTML。
    
    Args:
        image_url (str): 图片的URL。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        Union[str, None]: Base64编码的图片字符串（带数据类型前缀），如果下载或编码失败则返回None。
    """
    print(f"--- 日志: 开始下载并编码图片: {image_url[:50]}... ---")
    if status_callback:
        status_callback.update(label=f"🖼️ 正在下载并编码图片...", state="running")
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # 根据响应头判断图片类型
        content_type = response.headers.get('Content-Type', 'image/png')
        if 'image/jpeg' in content_type:
            image_type = 'jpeg'
        elif 'image/png' in content_type:
            image_type = 'png'
        else:
            image_type = 'png'

        encoded_image = base64.b64encode(response.content).decode('utf-8')
        print(f"--- 日志: 图片下载并编码成功。---")
        return f"data:image/{image_type};base64,{encoded_image}"
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 下载图片时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: ❌ 图片下载失败。{error_msg} ---")
        return None
    except Exception as e:
        error_msg = f"❌ 编码图片为Base64时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: ❌ 图片编码失败。{error_msg} ---")
        return None

# --- 函数：调用LLM生成图片提示词（英文） ---
def generate_image_prompt_from_paragraph(paragraph_content: str, status_callback=None) -> str:
    """
    根据一段中文内容，调用LLM生成一个适合文生图模型的英文提示词。
    
    Args:
        paragraph_content (str): 用于提炼提示词的中文段落。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        str: 生成的英文提示词，如果失败则返回空字符串。
    """
    print(f"--- 日志: 开始为段落生成图片提示词: '{paragraph_content[:50]}...' ---")
    
    # 在调用API之前检查API Key
    if not dashscope.api_key:
        error_msg = "❌ API Key 未设置，无法调用 LLM 生成提示词。"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: {error_msg} ---")
        return ""

    if status_callback:
        status_callback.update(label=f"✨ 正在为图片生成提示词...", state="running")

    # 系统提示词：定义LLM生成英文提示词的角色
    system_prompt = "你是一个创意图像提示词生成器。你将根据用户提供的中文段落内容，提炼出关键视觉元素和意境，生成一个简洁、富有想象力、适合图像AI（如Stable Diffusion, DALL-E）生成的高质量英文提示词。提示词应直接表达画面内容，无需任何额外说明或对话。"
    # 用户提示词：提供具体的中文段落
    user_prompt = f"""
    请根据以下中文段落内容，生成一个用于图像AI的英文提示词（prompt）。请直接给出英文提示词，不要包含任何其他文字。

    中文段落:
    "{paragraph_content}"

    英文提示词:
    """
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    try:
        response = dashscope.Generation.call(
            model="qwen-turbo",
            messages=messages,
            result_format='message',
            temperature=0.9,
            top_p=0.9
        )
        if response.status_code == HTTPStatus.OK:
            generated_prompt = response.output.choices[0].message.content.strip()
            print(f"--- 日志: 图片提示词生成成功: '{generated_prompt[:50]}...' ---")
            return generated_prompt
        else:
            error_msg = (
                f"❌ 图片提示词生成失败。状态码: {response.status_code}, "
                f"错误码: {response.code}, 消息: {response.message}"
            )
            if status_callback:
                status_callback.update(label=error_msg, state="error")
            print(f"--- 日志: ❌ 图片提示词生成失败。{error_msg} ---")
            return ""
    except Exception as e:
        error_msg = f"❌ 调用 LLM 生成图片提示词时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: ❌ 图片提示词生成异常。{error_msg} ---")
        return ""

# --- 函数：调用文生图模型 (已优化) ---
def generate_image_from_prompt(prompt: str, image_model: str, status_callback=None) -> Union[str, None]:
    """
    根据英文提示词，调用指定的文生图模型生成图片。
    
    Args:
        prompt (str): 英文图片提示词。
        image_model (str): 文生图模型名称。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        Union[str, None]: 生成图片的URL，如果失败则返回None。
    """
    print(f"--- 日志: 开始调用文生图模型 '{image_model}'，提示词: '{prompt[:50]}...' ---")
    if not prompt:
        return None
    
    # 在调用API之前检查API Key
    if not dashscope.api_key:
        error_msg = "❌ API Key 未设置，无法调用文生图模型。"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: {error_msg} ---")
        return None
    
    if status_callback:
        status_callback.update(label=f"🎨 正在调用文生图模型生成图片...", state="running")
    try:
        # 调用 DashScope 的文生图服务
        rsp = dashscope.ImageSynthesis.call(
            model=image_model,
            prompt=prompt,
            n=1,
            size='1280*720',
        )
        print(f"--- 日志: 文生图调用成功，开始处理结果 ---")
        print(f"--- 日志: 文生图调用状态码: {rsp.status_code}, 错误码: {rsp.code}, 消息: {rsp.message} ---")
        print(f"--- 日志: 文生图调用结果: {rsp.output} ---")
        if rsp.status_code == HTTPStatus.OK:
            if rsp.output and rsp.output.results:
                image_url = rsp.output.results[0].url
                print(f"--- 日志: 文生图成功，获取到图片URL: {image_url} ---")
                return image_url
            else:
                error_msg = "❌ API调用成功但未返回图片结果。可能原因：提示词不符合规范、内容违规或超出额度等。"
                if status_callback:
                    status_callback.update(label=error_msg, state="error")
                print(f"--- 日志: ❌ 文生图失败。{error_msg} ---")
                return None
        else:
            error_msg = (
                f"❌ 图片生成失败。状态码: {rsp.status_code}, "
                f"错误码: {rsp.code}, 消息: {rsp.message}"
            )
            if status_callback:
                status_callback.update(label=error_msg, state="error")
            print(f"--- 日志: ❌ 文生图失败。{error_msg} ---")
            return None
    except Exception as e:
        error_msg = f"❌ 调用文生图模型时出错: {e}"
        if status_callback:
            status_callback.update(label=error_msg, state="error")
        print(f"--- 日志: ❌ 调用文生图模型异常。{error_msg} ---")
        return ""

# --- 主要处理函数：解析文章并生成图片 ---
# --- 主要处理函数：解析文章并生成图片 (已修改) ---
def process_article_and_generate_images(
    article_content: str, 
    enable_image_generation: bool = True, 
    image_model: str = "wanx-v1",
    status_callback=None
) -> List[dict]:
    """
    解析文章内容，通过 <IMAGE> 标记进行内容分割，并为每个分割块调用文生图服务。
    
    Args:
        article_content (str): 待处理的文章内容。
        enable_image_generation (bool): 是否启用文生图功能。
        image_model (str): 文生图模型名称。
        status_callback (streamlit.status): 用于在Streamlit UI中更新状态。
        
    Returns:
        List[dict]: 包含处理后的段落和图片信息的列表。
    """
    print(f"--- 日志: 开始按 <IMAGE> 标记处理文章以插入图片。---")
    if status_callback:
        status_callback.update(label="文章图片处理开始...", state="running")

    # 按 <IMAGE> 标记分割文章内容，并保留标记在每个分割块的末尾（除了最后一个）
    # 使用 re.split 可以更灵活地处理标记
    # re.split 会在分隔符两侧都进行分割，所以如果标记在开头或结尾，会产生空字符串
    # 为了简化，我们按标记分割，然后手动处理插入图片的时机
    parts = article_content.split(AI_IMAGE_INTENT_MARKER)
    
    processed_elements = [] # 存储处理后的元素（段落或图片）
    image_inserted_count = 0 # 统计插入的图片数量

    for i, part_content in enumerate(parts):
        # 清理每个分割块的内容
        cleaned_part = part_content.strip()

        # 如果这个块有内容，就添加为一个段落元素
        if cleaned_part:
            processed_elements.append({"type": "paragraph", "content": cleaned_part})
            print(f"--- 日志: 添加段落块: '{cleaned_part[:50]}...' ---")

        # 如果这不是最后一个分割块，意味着后面有一个 <IMAGE> 标记，需要插入图片
        if i < len(parts) - 1 and enable_image_generation:
            # 提取用于生成图片提示词的段落内容
            # 如果当前块有内容，就用当前块；否则，如果前面有段落，用前一个段落；再否则，用默认提示词。
            paragraph_for_image_prompt = cleaned_part if cleaned_part else (
                processed_elements[-1]['content'] if processed_elements and processed_elements[-1]['type'] == 'paragraph' else "相关场景"
            )
            
            # 确保提示词不为空
            if not paragraph_for_image_prompt.strip():
                paragraph_for_image_prompt = "通用场景"

            print(f"--- 日志: 检测到 <IMAGE> 标记，准备为段落 '{paragraph_for_image_prompt[:50]}...' 生成图片。---")

            # 调用“取词器”生成英文提示词
            image_prompt = generate_image_prompt_from_paragraph(paragraph_for_image_prompt, status_callback=status_callback)
            
            # 调用文生图模型生成图片
            image_url = generate_image_from_prompt(image_prompt, image_model, status_callback=status_callback)
            
            base64_image_data = None
            if image_url:
                # 下载并编码图片
                base64_image_data = download_and_encode_image_as_base64(image_url, status_callback=status_callback)
            
            if not isinstance(base64_image_data, str):
                base64_image_data = None
                if status_callback:
                    status_callback.update(label="⚠️ 图片Base64编码失败，将跳过此图片。", state="running")
                print("--- 日志: ⚠️ 警告: 图片Base64编码失败或返回非字符串类型，将存储为None。---")

            # 将图片信息作为元素添加到列表中
            processed_elements.append({
                "type": "image",
                "content": paragraph_for_image_prompt, # 记录用于生成图片的原始中文内容
                "generated_prompt": image_prompt,
                "generated_image_url_original": image_url,
                "base64_image_data": base64_image_data
            })
            if status_callback:
                status_callback.update(label=f"🖼️ 已为段落 '{paragraph_for_image_prompt[:30]}...' 插入图片。", state="running")
            print(f"--- 日志: 已按 <IMAGE> 标记插入图片。---")
            image_inserted_count += 1
            
    if status_callback:
        status_callback.update(label=f"文章处理完成。共 {len(processed_elements)} 个元素 (插入图片: {image_inserted_count})。", state="complete")
    print(f"--- 日志: 文章图片处理完成。共 {len(processed_elements)} 个元素。插入图片总数: {image_inserted_count}。---")
    return processed_elements
