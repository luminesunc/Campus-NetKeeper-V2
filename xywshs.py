import sys
import json
import time
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QTextEdit, QLabel, QSystemTrayIcon,
                             QMenu, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from playwright.sync_api import sync_playwright
import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径，适配开发环境和 PyInstaller 打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 本地开发时的目录
    return os.path.join(os.path.abspath("."), relative_path)


# ==========================================
# 1. 嗅探器子线程 (你已经测试成功的核心功能)
# ==========================================
class SnifferThread(QThread):
    log_signal = pyqtSignal(str)

    def run(self):
        self.log_signal.emit("正在启动自动化浏览器环境...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, channel="msedge")
                context = browser.new_context(ignore_https_errors=True)
                page = context.new_page()
                captured_data = {}

                def handle_request(request):
                    if request.method == "POST" and request.post_data:
                        captured_data['url'] = request.url
                        captured_data['headers'] = request.headers
                        captured_data['payload'] = request.post_data
                        self.log_signal.emit(f"🔍 捕捉到疑似登录数据包: {request.url[:40]}...")

                page.on("request", handle_request)
                self.log_signal.emit("👉 请在弹出的浏览器中，手动输入账号密码并登录！")
                self.log_signal.emit("⚠️ 登录成功连上网后，请直接关闭该浏览器！")

                try:
                    page.goto("http://www.msftconnecttest.com/connecttest.txt", wait_until="commit")
                except:
                    pass

                page.wait_for_event("close", timeout=0)

                if captured_data:
                    with open("config.json", "w", encoding="utf-8") as f:
                        json.dump(captured_data, f, ensure_ascii=False, indent=4)
                    self.log_signal.emit("✅ 抓包大成功！配置文件已生成: config.json")
                else:
                    self.log_signal.emit("❌ 未能捕捉到登录数据，请重试。")

        except Exception as e:
            self.log_signal.emit(f"抓包过程发生异常: {e}")


# ==========================================
# 2. 守护者子线程 (本次新增的核心逻辑！)
# ==========================================
class GuardianThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def is_connected(self):
        """检测网络连通性"""
        try:
            response = requests.get('http://www.msftconnecttest.com/connecttest.txt', timeout=3)
            return response.status_code == 200 and 'Microsoft Connect Test' in response.text
        except:
            return False

    def run(self):
        # 尝试读取配置文件
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            self.log_signal.emit(f"❌ 读取配置失败，请先执行第一步抓包！错误: {e}")
            return

        url = config.get("url")
        headers = config.get("headers")
        payload = config.get("payload")

        self.log_signal.emit("🛡️ 后台守护进程已启动，开始静默监控...")

        while self.is_running:
            if not self.is_connected():
                self.log_signal.emit("⚠️ 检测到网络断开！准备发送重连请求...")
                try:
                    # 关键：用之前抓包偷到的数据，伪装成浏览器发出去
                    res = requests.post(url, headers=headers, data=payload.encode('utf-8'), timeout=5)
                    self.log_signal.emit(f"✅ 重连包发送完毕！服务器返回状态码: {res.status_code}")
                    time.sleep(5)  # 给网络恢复一点时间
                except Exception as e:
                    self.log_signal.emit(f"❌ 重连请求发送异常: {e}")

            # 把 30 秒的休眠拆成 1 秒 1 秒的，方便用户随时点“停止”按钮中断它
            for _ in range(30):
                if not self.is_running:
                    break
                time.sleep(1)

    def stop(self):
        """提供给主界面调用的停止方法"""
        self.is_running = False


# ==========================================
# 3. 主界面 GUI
# ==========================================
class NetKeeperGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icon = QIcon(resource_path("tubiao.ico"))
        self.guardian = None  # 保存守护线程的引用
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle('校园网守护神 V2.0 - 通用版')
        self.resize(500, 350)
        self.setWindowIcon(self.icon)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel('状态: 🟢 待机中 (请先获取配置)', self)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.status_label)

        self.btn_config = QPushButton('🔍 1. 一键打开浏览器获取登录配置', self)
        self.btn_config.setMinimumHeight(40)
        self.btn_config.clicked.connect(self.on_config_clicked)
        layout.addWidget(self.btn_config)

        self.btn_toggle = QPushButton('▶️ 2. 启动后台网络守护', self)
        self.btn_toggle.setMinimumHeight(40)
        self.btn_toggle.clicked.connect(self.on_toggle_clicked)

        # 检查有没有配置文件，如果有，直接点亮第二个按钮
        import os
        if os.path.exists("config.json"):
            self.btn_toggle.setEnabled(True)
            self.status_label.setText('状态: 🟡 配置已就绪，可随时启动')
        else:
            self.btn_toggle.setEnabled(False)

        layout.addWidget(self.btn_toggle)

        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.log_area.append("欢迎使用通用版校园网守护程序！")
        layout.addWidget(self.log_area)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)
        tray_menu = QMenu()
        show_action = QAction("显示主界面", self)
        show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(show_action)
        quit_action = QAction("完全退出", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("守护神已隐藏", "双击托盘图标可恢复界面。", QSystemTrayIcon.Information, 2000)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()

    def show_normal(self):
        self.show()
        self.activateWindow()

    def quit_app(self):
        if self.guardian:
            self.guardian.stop()
        self.tray_icon.hide()
        QApplication.quit()
        sys.exit()

    def append_log(self, text):
        self.log_area.append(text)
        if "大成功" in text:
            self.btn_toggle.setEnabled(True)
            self.status_label.setText('状态: 🟡 配置已就绪，可随时启动')

    def on_config_clicked(self):
        self.btn_config.setEnabled(False)
        self.log_area.append("准备抓取配置...")
        self.sniffer = SnifferThread()
        self.sniffer.log_signal.connect(self.append_log)
        self.sniffer.finished.connect(lambda: self.btn_config.setEnabled(True))
        self.sniffer.start()

    def on_toggle_clicked(self):
        if "启动" in self.btn_toggle.text():
            # 开启守护逻辑
            self.btn_toggle.setText('⏸️ 2. 暂停后台网络守护')
            self.status_label.setText('状态: 🔵 守护进程运行中...')
            self.btn_config.setEnabled(False)  # 守护期间不让抓包

            self.guardian = GuardianThread()
            self.guardian.log_signal.connect(self.append_log)
            self.guardian.start()
        else:
            # 停止守护逻辑
            self.btn_toggle.setText('▶️ 2. 启动后台网络守护')
            self.status_label.setText('状态: 🟡 守护已暂停')
            self.btn_config.setEnabled(True)

            if self.guardian:
                self.guardian.stop()
                self.log_area.append("已发送停止指令，守护进程安全退出。")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.myproduct")
    gui = NetKeeperGUI()
    gui.show()
    sys.exit(app.exec_())