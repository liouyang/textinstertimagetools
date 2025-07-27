import streamlit as st
import os
import sys
import datetime
import re
import dashscope # 导入 DashScope SDK
from batch_article_generator import batch_generate_articles
from local_license_tool import verify_certificate, check_dashscope_api_key

import platform # 新增导入
import subprocess # 新增导入

# --- 全局变量和路径获取 ---
def get_base_path():
    """获取应用程序的基路径，兼容 PyInstaller 打包和开发模式。"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.realpath(__file__))

def setup_resource_dirs():
    """确保应用程序所需的资源目录存在。"""
    base_path = get_base_path()
    dirs_to_create = [
        os.path.join(base_path, 'generated_images'),
        os.path.join(base_path, 'generated_articles_humanized'),
        os.path.join(base_path, 'generated_output'),
        os.path.join(base_path, 'templates')
    ]
    for d in dirs_to_create:
        if not os.path.exists(d):
            os.makedirs(d)

# 在应用程序启动时确保目录存在
setup_resource_dirs()

def open_file_directory(directory_path):
    """
    打开指定目录。
    兼容 Windows, macOS, Linux。
    """
    # 确保 directory_path 是绝对路径
    abs_directory_path = os.path.abspath(directory_path)
    
    st.info(f"尝试打开目录: `{abs_directory_path}`") # 在 Streamlit UI 中显示，方便用户检查
    print(f"--- DEBUG: 尝试打开的目录 (绝对路径): {abs_directory_path} ---") # 打印到控制台

    if not os.path.exists(abs_directory_path):
        st.error(f"错误：目录不存在: `{abs_directory_path}`。")
        print(f"--- 错误: 尝试打开的目录不存在: {abs_directory_path} ---")
        return

    try:
        current_platform = platform.system()
        if current_platform == "Windows":
            # 在 Windows 上使用 Explorer 打开目录。/select 参数用于打开并选择一个文件，
            # 但如果目标是目录本身，直接传入目录路径即可。
            # 使用 shell=True 可以确保命令在系统的 shell 中执行，有时能解决 PATH 问题
            subprocess.Popen(f'explorer "{abs_directory_path}"', shell=True) 
        elif current_platform == "Darwin": # macOS
            # 在 macOS 上使用 'open' 命令
            subprocess.run(["open", abs_directory_path], check=True)
        else: # Linux (例如 Ubuntu, Debian 等桌面环境)
            # 在 Linux 上使用 'xdg-open' 命令，它会使用默认的文件管理器打开目录
            subprocess.run(["xdg-open", abs_directory_path], check=True)
        
        st.success(f"已请求打开目录。请检查您的文件管理器。")
        print(f"--- DEBUG: 已成功请求打开目录: {abs_directory_path} ---")

    except FileNotFoundError:
        st.error(f"错误：未找到打开目录所需的系统命令。请确保 'explorer', 'open' 或 'xdg-open' 在系统 PATH 中。")
        print(f"--- 错误: 未找到系统命令以打开目录。---")
    except subprocess.CalledProcessError as e:
        st.error(f"打开目录命令执行失败。错误代码: {e.returncode}，输出: {e.stderr.decode()}")
        print(f"--- 错误: 打开目录命令执行失败: {e} ---")
    except Exception as e:
        st.error(f"无法打开目录 {abs_directory_path}: {e}")
        st.exception(e) # 打印完整的异常信息用于调试
        print(f"--- 错误: 打开目录时发生未知异常: {e} ---")


# --- 密钥认证逻辑 ---

# 初始化 session state，用于在 Streamlit 页面刷新时保持状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'api_key' not in st.session_state: # 存储已验证的 DashScope API Key
    st.session_state['api_key'] = ""
if 'certificate_verified' not in st.session_state: # 证书是否通过了验证
    st.session_state['certificate_verified'] = False

def perform_full_authentication(input_api_key, input_certificate):
    """
    执行完整的认证流程：先证书验证，再 DashScope API Key 验证。
    更新 Streamlit session state。
    """
    st.session_state['authenticated'] = False # 每次尝试认证前重置认证状态
    st.session_state['certificate_verified'] = False # 重置证书验证状态

    # 检查输入是否为空
    if not input_api_key or not input_certificate:
        st.error("API 密钥和认证证书都不能为空！")
        return False

    # 步骤 1: 验证证书的有效性（包括时效性和签名匹配）
    st.info("正在验证认证证书...")
    if verify_certificate(input_api_key, input_certificate):
        st.session_state['certificate_verified'] = True
        st.success("认证证书验证成功！")

        # 步骤 2: 如果证书验证成功，则进一步验证 DashScope API Key 的有效性
        st.info("正在验证 DashScope API 密钥的有效性...")
        if check_dashscope_api_key(input_api_key):
            st.session_state['authenticated'] = True # 标记为完全认证通过
            st.session_state['api_key'] = input_api_key # 保存已验证的 API Key
            st.success("DashScope API 密钥验证成功，您已完成全部认证！")
            return True # 返回 True 表示认证成功
        else:
            st.error("DashScope API 密钥不正确或无法连接DashScope服务。请检查您的API Key或网络。")
            return False # 返回 False 表示 DashScope API Key 验证失败
    else:
        # 如果证书验证失败（签名不匹配或已过期），则不进行 API Key 验证
        st.error("认证证书与提供的API密钥不匹配，或证书已过期/无效。请检查您的证书和API密钥。")
        return False # 返回 False 表示证书验证失败

# --- Streamlit 应用的主要 UI 结构 ---
st.set_page_config(
    page_title="文章批量生成与配图工具",
    page_icon="✍️",
    layout="wide",
)

st.title("文章批量生成与配图工具")

# 创建一个占位符，用于在认证状态变化时动态显示或隐藏内容
auth_placeholder = st.empty()

# 如果用户尚未认证，则显示认证表单
if not st.session_state['authenticated']:
    with auth_placeholder.container(): # 将认证表单放在这个容器内
        st.subheader("请先输入您的认证信息以解锁应用功能")

        with st.form("authentication_form"): # 认证表单
            api_key_input = st.text_input("DashScope API 密钥", type="password", help="请输入您的DashScope API Key", key="dashscope_api_key_input")
            certificate_input = st.text_input("认证证书", type="password", help="请输入您的认证证书", key="certificate_input")

            auth_button = st.form_submit_button("验证")

            if auth_button: # 当用户点击“验证”按钮时
                # 如果认证成功，则立即重新运行应用
                if perform_full_authentication(api_key_input, certificate_input):
                    st.rerun() # 强制重新运行，立即跳转

        st.markdown("---")
        st.info("请向您的提供商获取有效的 DashScope API 密钥和认证证书。")
        st.info("认证证书具有时效性，请确保在有效期内使用。")

else:
    # 如果用户已认证，则清除认证表单，并显示主应用内容
    auth_placeholder.empty() # 清除认证容器的内容

    st.sidebar.title("应用菜单")
    st.sidebar.info("您已成功认证并可以开始使用。")
    st.sidebar.info(f"当前使用的API Key (部分): {st.session_state['api_key'][:8]}...") # 在侧边栏显示部分API Key

    # 提供一个注销或重新认证的选项
    if st.sidebar.button("注销并重新认证"):
        st.session_state['authenticated'] = False
        st.session_state['api_key'] = ""
        st.session_state['certificate_verified'] = False
        st.rerun() # 重新运行应用，回到认证页面

    # 主页面功能
    st.markdown("使用 DashScope 大模型自动生成多篇文章，并为每篇文章智能配图。")

    # --- 表单：文章生成参数 ---
    with st.form("article_generator_form"):
        st.header("📝 文章生成参数")
        main_batch_topic = st.text_input(
            "主课题",
            value="人工智能在未来的发展趋势",
            help="例如：新能源汽车的未来、短视频平台的兴起与挑战"
        )
        num_of_articles = st.slider(
            "希望生成的文章数量",
            min_value=1,
            max_value=200,
            value=1,
            help="请注意：生成多篇文章会消耗更多API额度。"
        )
        
        st.subheader("文章生成细节 (可选)")
        
        selected_llm_model = st.selectbox(
            "选择文章生成模型",
            ["qwen-plus", "qwen-turbo", "qwen-max"],
            help="请根据您的需求和API额度选择合适的模型。"
        )
        
        selected_image_model = st.selectbox(
            "选择文生图模型",
            ["wanx-v1", "wanx2.0-t2i-turbo"],
            help="请根据您的需求和API额度选择合适的文生图模型。"
        )
        
        audience = st.selectbox(
            "文章受众", 
            ["通用读者", "行业专家", "学生群体", "科技爱好者", "儿童", "老年人", "投资者", "企业管理者", "创作者"]
        )
        
        style = st.selectbox(
            "写作风格", 
            ["科普性", "深度分析", "新闻报道", "故事叙述", "幽默风趣", "诗意文学", "学术严谨", "口语化", "评论性"]
        )
        
        length = st.selectbox("文章长度", ["短篇（300-500字）", "中篇（600-900字）", "长篇（1000+字）"])
        
        keywords_input = st.text_input(
            "关键词 (可选)", 
            value="AI, 大数据, 未来科技", 
            help="用逗号分隔，例如：AI, 大数据, 未来科技"
        )
        
        extra_requirements_default = (
            "文章应包含对AI技术未来挑战的讨论，如数据隐私、算法偏见等。文风需严谨但不失趣味性。"
        )
        extra_requirements = st.text_area(
            "额外要求 (可选)", 
            value=extra_requirements_default,
            help="可以指定一些特别的写作要求或注意事项"
        )
        
        delay_between_articles = st.slider(
            "每篇文章生成之间的延迟 (秒)",
            min_value=5,
            max_value=60,
            value=15,
            help="为了避免API调用过于频繁，建议设置延迟。"
        )

        submitted = st.form_submit_button("🚀 开始批量生成", type="primary")

    # --- 提交表单后的处理逻辑 ---
    if submitted:
        # 再次检查 API Key 是否已设置（虽然在认证时已设置，但作为双重保障）
        if not st.session_state['api_key']: # 使用 session state 中存储的 key
            st.error("内部错误：DashScope API Key 未设置。请尝试重新认证。")
        else:
            st.info(f"正在为主题 **'{main_batch_topic}'** 批量生成 **{num_of_articles}** 篇文章...")
            
            # 将关键词字符串转换为列表
            keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
            
            # 封装所有文章生成参数
            article_generation_parameters = {
                'audience': audience,
                'style': style,
                'length': length,
                'keywords': keywords,
                'extra_requirements': extra_requirements,
                'llm_model': selected_llm_model, 
                'image_model': selected_image_model 
            }

            # 使用 st.status 显示任务状态，提供实时反馈
            with st.status("正在启动生成...", expanded=True) as status_container:
                try:
                    # 在调用任何需要 DashScope 的函数之前，设置 DashScope API Key
                    # 这里使用 session state 中已验证的 API Key
                    dashscope.api_key = st.session_state['api_key']
                    
                    # 调用核心的批量生成函数
                    batch_generate_articles(
                        main_topic=main_batch_topic,
                        num_articles=num_of_articles,
                        article_gen_params=article_generation_parameters,
                        delay_between_articles=delay_between_articles,
                        status_callback=status_container
                    )
                    
                    # 任务完成后，更新状态为“完成”
                    status_container.update(label="🎉 所有文章生成完毕！", state="complete", expanded=True)
                    
                    # --- 生成完成后，在主页面展示可点击的链接和打开目录按钮 ---
                    output_dir = os.path.join(get_base_path(), "generated_output") # 确保使用绝对路径
                    if os.path.exists(output_dir):
                        st.success(f"文章已生成到：`{os.path.abspath(output_dir)}`")
                        # 添加一个按钮来打开目录
                        # if st.button(f"📂 打开生成文件目录"):
                        #     open_file_directory(output_dir) # 直接传递目录路径
                        
                        st.write("生成的HTML文件列表：")
                        # 获取 generated_output 文件夹中的所有 HTML 文件，并按修改时间倒序排列
                        html_files_relative = sorted([f for f in os.listdir(output_dir) if f.endswith('.html')], 
                                                    key=lambda f: os.path.getmtime(os.path.join(output_dir, f)), reverse=True)
                        
                        if html_files_relative:
                            for html_file in html_files_relative:
                                # 这里只显示文件名，不再是可点击的链接
                                file_path = os.path.join(output_dir, html_file)
                        
                                # 使用两列布局，左边是文件预览链接，右边是打开目录链接
                                col1, col2 = st.columns([0.7, 0.3]) # 调整列宽比例
                                
                                with col1:
                                    # 文件本身的可预览链接
                                    st.markdown(f"[{html_file}](file://{os.path.abspath(file_path)})")
                                
                                with col2:
                                    # 文件所在目录的链接，不会重置页面
                                    # 注意：这里我们链接的是文件所在的目录，而不是文件本身
                                    st.markdown(f"[📂 打开目录](file://{os.path.abspath(output_dir)})")
                        else:
                            st.write("目前还没有生成的文章。")
                    else:
                        st.error("输出目录不存在。请检查文件生成过程。")

                except Exception as e:
                    # 捕获并显示生成过程中的异常
                    status_container.update(label=f"❌ 生成过程中发生错误: {e}", state="error")
                    st.error(f"生成过程中发生错误: {e}")
                    # 打印完整的错误堆栈，方便调试
                    import traceback
                    st.exception(e)