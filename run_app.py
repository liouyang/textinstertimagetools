import os
import sys
import logging # 导入 logging 模块，用于调试

# 尝试导入 Streamlit 的 main_run 函数
try:
    # 推荐使用这种方式导入，因为它更直接地指向 Streamlit 的 Web CLI
    from streamlit.web import cli as streamlit_cli
except ImportError:
    # 如果 streamlit.web.cli 不存在（例如旧版 Streamlit），尝试兼容旧版
    try:
        from streamlit import cli as streamlit_cli
    except ImportError:
        print("错误: 无法导入 Streamlit CLI。请确保 Streamlit 已正确安装。")
        sys.exit(1)


def get_app_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.realpath(__file__))

    app_script_name = "streamlit_app.py"
    # 如果你在 spec 文件中将 streamlit_app.py 放在了 _internal 目录下，
    # 那么这里可能需要调整为 os.path.join(base_path, '_internal', app_script_name)
    # 但由于我们在 spec 文件中将其放在了 '.' (root)，所以当前的 os.path.join(base_path, app_script_name) 是正确的。
    return os.path.join(base_path, app_script_name)

def setup_resource_dirs():
    """确保应用程序所需的资源目录存在"""
    # 假设这些目录应该在打包后应用程序的根目录下
    base_dir = get_app_path() # 获取 Streamlit 应用程序所在的基路径
    # 需要移除文件名部分，只保留目录
    resource_base_dir = os.path.dirname(base_dir)

    paths_to_create = [
        'generated_images',
        'generated_articles_humanized',
        'generated_output',
        'templates'
    ]
    
    for path_name in paths_to_create:
        full_path = os.path.join(resource_base_dir, path_name) # 资源目录应该相对于可执行文件的位置
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"✅ 确保目录存在: {full_path}")
        except Exception as e:
            print(f"⚠️ 目录创建失败 {full_path}: {e}")

if __name__ == "__main__":
    # 配置日志，以便在控制台中看到 Streamlit 的内部输出
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # 1. 确保资源目录被创建
    setup_resource_dirs()

    # # 2. 设置 Streamlit 运行时需要的环境变量
    # os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'true'
    # os.environ['STREAMIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    # os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'true' # 调试时保持为 true
    # os.environ['STREAMLIT_CLIENT_TOOLBAR_MODE'] = 'minimal'
    # os.environ['STREAMLIT_LOG_LEVEL'] = 'debug' # 调试时保持为 debug

    # 3. 准备 Streamlit CLI 期望的命令行参数
    app_script_path = get_app_path()
    sys.argv = [
        "streamlit",
        "run",
        app_script_path,
        #  "--server.port", "8502", 
        # "--server.port", "8502", # 你的目标端口
        # "--server.enableCORS=true",
        # "--server.enableXsrfProtection=false",
        # "--global.developmentMode=false",
        # "--global.developmentMode=true",
        # "--client.toolbarMode=minimal"
    ]

    print(f"--- Streamlit 应用程序准备启动。应用脚本路径: {app_script_path} ---")
    print(f"DEBUG: sys.argv for Streamlit: {sys.argv}")

    # 4. 直接调用 Streamlit 的主运行函数
    try:
        # main_run() 会启动 Streamlit 服务器并接管控制权
        sys.exit(streamlit_cli.main()) # <--- 正确的启动方式
    except SystemExit as e:
        if e.code != 0:
            print(f"⚠️ Streamlit 应用程序异常退出，退出码: {e.code}")
        else:
            print("--- Streamlit 应用程序已正常退出。 ---")
    except Exception as e:
        print(f"❌ 启动 Streamlit 应用程序时发生未知错误: {e}")
        import traceback
        traceback.print_exc() # 打印完整的错误栈信息