# # desktop_app.py
# import sys
# import threading
# import time
# import socket # 用于查找可用端口

# # 导入 PyQt5 模块
# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
# from PyQt5.QtWebEngineWidgets import QWebEngineView # 导入 Web 浏览器控件
# from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QTimer

# # 导入你的 Flask 应用实例
# from app import app as flask_app # 将 Flask 应用导入为 flask_app

# # 定义 Flask 服务器运行的端口
# FLASK_PORT = 5000
# FLASK_HOST = "127.0.0.1" # 本地主机

# # --- 辅助函数：查找一个可用的端口 ---
# def find_available_port(start_port=FLASK_PORT):
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     for port in range(start_port, start_port + 100): # 尝试 100 个端口
#         try:
#             sock.bind((FLASK_HOST, port))
#             sock.close()
#             return port
#         except OSError:
#             continue
#     raise IOError("没有找到可用的端口。")

# # --- Flask 服务器线程 ---
# class FlaskThread(QThread):
#     # 定义一个信号，用于通知主线程 Flask 服务器已启动
#     started_signal = pyqtSignal(str) # 传递 Flask 服务器的 URL

#     def __init__(self, host, port):
#         super().__init__()
#         self.host = host
#         self.port = port
#         self.server = None # 用于存储 Werkzeug 服务器实例

#     def run(self):
#         # 禁用 Flask 的日志，避免在控制台输出过多信息
#         import logging
#         log = logging.getLogger('werkzeug')
#         log.setLevel(logging.ERROR) # 只显示错误信息

#         try:
#             # 使用 Werkzeug 的 run_simple 来运行 Flask 应用
#             # 这是 Flask app.run() 的底层实现
#             from werkzeug.serving import run_simple
#             self.server = run_simple(
#                 self.host,
#                 self.port,
#                 flask_app,
#                 threaded=True, # 允许 Flask 处理多个请求
#                 use_reloader=False, # 禁用自动重载，因为是在桌面应用中
#                 use_debugger=False # 禁用调试器
#             )
#             print(f"Flask 服务器在 http://{self.host}:{self.port} 启动。")
#             self.started_signal.emit(f"http://{self.host}:{self.port}/")
#         except Exception as e:
#             print(f"Flask 服务器启动失败: {e}")
#             self.started_signal.emit(f"error:{e}") # 发送错误信息
            
#     def stop(self):
#         # 尝试停止 Werkzeug 服务器
#         if self.server:
#             print("正在关闭 Flask 服务器...")
#             self.server.shutdown() # 发送关闭信号
#             self.wait() # 等待线程结束
#             print("Flask 服务器已关闭。")

# # --- 主桌面应用程序窗口 ---
# class DesktopApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Python 桌面应用 - 分类列表")
#         self.setGeometry(100, 100, 1000, 700) # 设置窗口大小

#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout = QVBoxLayout(self.central_widget)

#         self.browser = QWebEngineView() # 创建 Web 浏览器控件
#         self.layout.addWidget(self.browser)

#         self.flask_thread = None
#         self.flask_port = FLASK_PORT

#         self.start_flask_server()

#     def start_flask_server(self):
#         try:
#             # 尝试查找一个可用的端口
#             self.flask_port = find_available_port(FLASK_PORT)
            
#             self.flask_thread = FlaskThread(FLASK_HOST, self.flask_port)
#             self.flask_thread.started_signal.connect(self.on_flask_started)
#             self.flask_thread.start() # 启动 Flask 线程

#             # 设置一个定时器，在 Flask 启动后加载 URL
#             # 给予 Flask 服务器一点时间来启动
#             QTimer.singleShot(1000, lambda: self.browser.load(QUrl(f"http://{FLASK_HOST}:{self.flask_port}/")))

#         except IOError as e:
#             QMessageBox.critical(self, "错误", f"无法启动 Flask 服务器：{e}\n请确保没有其他程序占用端口。")
#             sys.exit(1) # 退出应用

#     def on_flask_started(self, url_or_error):
#         if url_or_error.startswith("error:"):
#             error_msg = url_or_error[6:]
#             QMessageBox.critical(self, "Flask 启动失败", f"Flask 服务器未能启动：{error_msg}")
#             sys.exit(1)
#         else:
#             print(f"桌面应用加载 URL: {url_or_error}")
#             # 浏览器加载 URL 的操作已移到 start_flask_server 中的 QTimer
#             # self.browser.load(QUrl(url_or_error))

#     def closeEvent(self, event):
#         # 窗口关闭事件：在关闭桌面应用时停止 Flask 服务器
#         if self.flask_thread and self.flask_thread.isRunning():
#             self.flask_thread.stop()
#         event.accept() # 接受关闭事件

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = DesktopApp()
#     window.show()
#     sys.exit(app.exec_())