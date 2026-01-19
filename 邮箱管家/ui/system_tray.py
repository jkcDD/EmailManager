# -*- coding: utf-8 -*-
"""
系统托盘模块 - 支持最小化到托盘
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject
import os

# 托盘菜单样式（简化版，不需要完整的主题样式）
TRAY_MENU_STYLE = """
    QMenu {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 4px;
    }
    QMenu::item {
        padding: 8px 20px;
        color: #1A1A1A;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background: #E5F1FB;
        color: #0078D4;
    }
"""


class SystemTrayManager(QObject):
    """系统托盘管理器"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.tray_icon = None
        self.setup_tray()
    
    def setup_tray(self):
        """设置托盘图标和菜单"""
        # 检查系统是否支持托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self.main_window)
        
        # 设置图标 - 尝试加载自定义图标，否则使用系统默认图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用应用程序默认图标
            self.tray_icon.setIcon(self.main_window.style().standardIcon(QStyle.SP_ComputerIcon))
        
        self.tray_icon.setToolTip('邮箱管家')
        
        # 创建右键菜单
        menu = QMenu()
        menu.setStyleSheet(TRAY_MENU_STYLE)
        
        action_show = menu.addAction('显示主窗口')
        action_show.triggered.connect(self.show_window)
        
        menu.addSeparator()
        
        action_quit = menu.addAction('退出')
        action_quit.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
        elif reason == QSystemTrayIcon.Trigger:
            # 单击也显示窗口（Windows 习惯）
            self.show_window()
    
    def show_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.showNormal()  # 如果最小化则恢复
        self.main_window.activateWindow()
        self.main_window.raise_()
    
    def quit_app(self):
        """退出应用"""
        # 先隐藏托盘图标
        if self.tray_icon:
            self.tray_icon.hide()
        # 退出应用
        QApplication.quit()
    
    def hide_to_tray(self):
        """隐藏到托盘"""
        self.main_window.hide()
        if self.tray_icon:
            self.tray_icon.showMessage(
                '邮箱管家',
                '程序已最小化到系统托盘',
                QSystemTrayIcon.Information,
                2000
            )
    
    def is_available(self):
        """检查托盘是否可用"""
        return self.tray_icon is not None and self.tray_icon.isVisible()
