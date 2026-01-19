# -*- coding: utf-8 -*-
"""
主题管理模块 - 支持明暗主题切换
包含共享的样式定义，供其他模块导入使用
"""

# ============ 共享对话框样式 ============

# 浅色主题对话框样式
LIGHT_DIALOG_STYLE = """
    QDialog {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #E8F4FC, stop:1 #D0E8F8);
        font-family: 'Microsoft YaHei UI', sans-serif;
    }
"""

LIGHT_INPUT_STYLE = """
    QLineEdit {
        padding: 8px 12px;
        border: 1px solid #B8D4E8;
        border-radius: 6px;
        background: #FFFFFF;
        font-size: 13px;
        color: #1A1A1A;
    }
    QLineEdit:focus {
        border: 2px solid #0078D4;
    }
"""

LIGHT_BTN_CANCEL_STYLE = """
    QPushButton {
        background: #FFFFFF; color: #1A1A1A; border: 1px solid #C0C0C0;
        border-radius: 6px; font-size: 13px;
    }
    QPushButton:hover { background: #F0F0F0; }
"""

LIGHT_BTN_OK_STYLE = """
    QPushButton {
        background: #0078D4; color: white; border: none;
        border-radius: 6px; font-size: 13px;
    }
    QPushButton:hover { background: #1084D9; }
"""

LIGHT_MENU_STYLE = """
    QMenu {
        background: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 8px 4px;
    }
    QMenu::item {
        padding: 10px 40px 10px 16px;
        color: #333333;
        border-radius: 6px;
        font-size: 13px;
        margin: 2px 6px;
    }
    QMenu::item:selected {
        background: #F0F0F0;
        color: #333333;
    }
    QMenu::item:disabled {
        color: #AAAAAA;
    }
    QMenu::separator {
        height: 1px;
        background: #EEEEEE;
        margin: 6px 16px;
    }
"""

# 深色主题对话框样式
DARK_DIALOG_STYLE = """
    QDialog {
        background: #161b22;
        font-family: 'Microsoft YaHei UI', sans-serif;
    }
"""

DARK_INPUT_STYLE = """
    QLineEdit {
        padding: 8px 12px;
        border: 1px solid #30363d;
        border-radius: 6px;
        background: #0d1117;
        font-size: 13px;
        color: #c9d1d9;
    }
    QLineEdit:focus {
        border: 2px solid #58a6ff;
    }
"""

DARK_BTN_CANCEL_STYLE = """
    QPushButton {
        background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
        border-radius: 6px; font-size: 13px;
    }
    QPushButton:hover { background: #30363d; }
"""

DARK_BTN_OK_STYLE = """
    QPushButton {
        background: #238636; color: white; border: none;
        border-radius: 6px; font-size: 13px;
    }
    QPushButton:hover { background: #2ea043; }
"""

DARK_MENU_STYLE = """
    QMenu {
        background: #21262d;
        border: none;
        border-radius: 12px;
        padding: 8px 4px;
    }
    QMenu::item {
        padding: 10px 40px 10px 16px;
        color: #c9d1d9;
        border-radius: 6px;
        font-size: 13px;
        margin: 2px 6px;
    }
    QMenu::item:selected {
        background: #30363d;
        color: #FFFFFF;
    }
    QMenu::item:disabled {
        color: #6e7681;
    }
    QMenu::separator {
        height: 1px;
        background: #30363d;
        margin: 6px 16px;
    }
"""

# ============ 主题配置 ============

# 浅色主题样式
LIGHT_THEME = {
    'name': 'light',
    'main_window': """
        QMainWindow { 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #F8F9FA, stop:1 #E9ECEF);
        }
    """,
    'content_area': """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
            stop:0 #FFFFFF, stop:1 #FAFBFC);
        border-top-left-radius: 16px;
    """,
    'sidebar': """
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #667eea, stop:0.5 #5a67d8, stop:1 #4c51bf);
    """,
    'card': """
        QFrame {
            background-color: #FFFFFF;
            border: none;
            border-radius: 12px;
        }
    """,
    'table': """
        QTableWidget {
            background-color: #FFFFFF;
            border: 1px solid #F0F0F0;
            border-radius: 12px;
            gridline-color: transparent;
            outline: none;
            padding: 4px;
        }
        QTableWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #F7F9FC;
            color: #333333;
            outline: none;
        }
        QTableWidget::item:selected {
            background-color: #F0F7FF;
            color: #1A1A1A;
        }
        QTableWidget::item:hover:!selected {
            background-color: #FAFAFA;
        }
        QHeaderView::section {
            background: #FFFFFF;
            padding: 16px 12px;
            border: none;
            border-bottom: 2px solid #F0F0F0;
            font-weight: 600;
            font-size: 13px;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        QScrollBar:vertical {
            background: #FFFFFF;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #E5E7EB;
            border-radius: 4px;
            min-height: 40px;
        }
        QScrollBar::handle:vertical:hover {
            background: #D1D5DB;
        }
    """,
    'badge_success': """
        QLabel {
            background-color: #DEF7EC;
            color: #03543F;
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_error': """
        QLabel {
            background-color: #FDE8E8;
            color: #9B1C1C;
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_warning': """
        QLabel {
            background-color: #FEF3C7;
            color: #92400E;
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_info': """
        QLabel {
            background-color: #E1EFFE;
            color: #1E429F;
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'input': """
        QLineEdit {
            padding: 10px 16px;
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            background: #FAFAFA;
            color: #1A1A1A;
        }
        QLineEdit:focus {
            border: 2px solid #0078D4;
            background: #FFFFFF;
        }
    """,
    'combo': """
        QComboBox {
            padding: 10px 12px;
            border: none;
            border-radius: 8px;
            background: #F5F5F5;
            color: #1A1A1A;
        }
        QComboBox:hover { background: #EBEBEB; }
        QComboBox:focus { background: #E8E8E8; }
        QComboBox::drop-down { border: none; width: 24px; }
        QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
            border-right: 5px solid transparent; border-top: 6px solid #666; }
        QComboBox QAbstractItemView {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            selection-background-color: #E5F1FB;
            color: #1A1A1A;
            outline: none;
        }
    """,
    'button_primary': """
        QPushButton {
            background-color: #2563EB;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { 
            background-color: #1D4ED8;
        }
        QPushButton:pressed { background-color: #1E40AF; }
        QPushButton:disabled { background-color: #E5E7EB; color: #9CA3AF; }
    """,
    'button_success': """
        QPushButton {
            background-color: #10B981;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { 
            background-color: #059669;
        }
        QPushButton:pressed { background-color: #047857; }
    """,
    'button_warning': """
        QPushButton {
            background-color: #F59E0B;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { 
            background-color: #D97706;
        }
        QPushButton:pressed { background-color: #B45309; }
    """,
    'button_danger': """
        QPushButton {
            background-color: #EF4444;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { 
            background-color: #DC2626;
        }
        QPushButton:pressed { background-color: #B91C1C; }
    """,
    'button_default': """
        QPushButton {
            background-color: #FFFFFF;
            color: #374151;
            border: 1px solid #D1D5DB;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: normal;
        }
        QPushButton:hover { 
            background-color: #F9FAFB;
            border-color: #9CA3AF;
            color: #111827;
        }
        QPushButton:pressed { background-color: #F3F4F6; }
    """,
    'button_subtle': """
        QPushButton {
            background-color: transparent;
            color: #2563EB;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { background-color: #EFF6FF; }
        QPushButton:pressed { background-color: #DBEAFE; }
    """,
    'colors': {
        'text': '#1A1A1A',
        'text_secondary': '#616161',
        'text_muted': '#999999',
        'accent': '#0078D4',
        'success': '#107C10',
        'danger': '#D13438',
        'border': '#E0E0E0',
        'background': '#FFFFFF',
        'background_alt': '#F8F9FA',
    }
}

# 深色主题样式 - 参考现代深色UI设计
DARK_THEME = {
    'name': 'dark',
    'main_window': """
        QMainWindow { 
            background: #0d1117;
        }
    """,
    'content_area': """
        background: #0d1117;
        border-top-left-radius: 0px;
    """,
    'sidebar': """
        background: #161b22;
        border-right: 1px solid #30363d;
    """,
    'card': """
        QFrame {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
        }
    """,
    'table': """
        QTableWidget {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 12px;
            gridline-color: transparent;
            color: #c9d1d9;
            outline: none;
            padding: 4px;
        }
        QTableWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #21262d;
            color: #c9d1d9;
            outline: none;
        }
        QTableWidget::item:selected {
            background-color: #1f6feb33;
            color: #FFFFFF;
        }
        QTableWidget::item:hover:!selected {
            background-color: #161b22;
        }
        QHeaderView::section {
            background: #0d1117;
            padding: 16px 12px;
            border: none;
            border-bottom: 2px solid #30363d;
            font-weight: 600;
            font-size: 13px;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        QScrollBar:vertical {
            background: #0d1117;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #30363d;
            border-radius: 4px;
            min-height: 40px;
        }
        QScrollBar::handle:vertical:hover {
            background: #484f58;
        }
    """,
    'badge_success': """
        QLabel {
            background-color: rgba(35, 134, 54, 0.2);
            color: #3fb950;
            border: 1px solid rgba(35, 134, 54, 0.4);
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_error': """
        QLabel {
            background-color: rgba(218, 54, 51, 0.2);
            color: #f85149;
            border: 1px solid rgba(218, 54, 51, 0.4);
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_warning': """
        QLabel {
            background-color: rgba(158, 106, 3, 0.2);
            color: #d29922;
            border: 1px solid rgba(158, 106, 3, 0.4);
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'badge_info': """
        QLabel {
            background-color: rgba(56, 139, 253, 0.15);
            color: #58a6ff;
            border: 1px solid rgba(56, 139, 253, 0.4);
            border-radius: 10px;
            padding: 4px 8px;
            font-size: 12px;
            font-weight: 600;
        }
    """,
    'input': """
        QLineEdit {
            padding: 10px 16px;
            border: 1px solid #30363d;
            border-radius: 6px;
            background: #0d1117;
            color: #c9d1d9;
        }
        QLineEdit:focus {
            border: 1px solid #58a6ff;
            background: #0d1117;
        }
        QLineEdit::placeholder {
            color: #6e7681;
        }
    """,
    'combo': """
        QComboBox {
            padding: 10px 12px;
            border: none;
            border-radius: 8px;
            background: #21262d;
            color: #c9d1d9;
        }
        QComboBox:hover { background: #30363d; }
        QComboBox:focus { background: #30363d; }
        QComboBox::drop-down { border: none; width: 24px; }
        QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
            border-right: 5px solid transparent; border-top: 6px solid #8b949e; }
        QComboBox QAbstractItemView {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            selection-background-color: #1f6feb;
            color: #c9d1d9;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            min-height: 28px;
        }
        QComboBox QAbstractItemView::item:hover {
            background: #21262d;
        }
    """,
    'button_primary': """
        QPushButton {
            background: #238636;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { background: #2ea043; }
        QPushButton:pressed { background: #238636; }
        QPushButton:disabled { background: #21262d; color: #484f58; }
    """,
    'button_success': """
        QPushButton {
            background: #238636;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { background: #2ea043; }
        QPushButton:pressed { background: #238636; }
    """,
    'button_warning': """
        QPushButton {
            background: #9e6a03;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { background: #bb8009; }
        QPushButton:pressed { background: #9e6a03; }
    """,
    'button_danger': """
        QPushButton {
            background: #da3633;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover { background: #f85149; }
        QPushButton:pressed { background: #da3633; }
    """,
    'button_default': """
        QPushButton {
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 13px;
        }
        QPushButton:hover { 
            background-color: #30363d; 
            border-color: #8b949e;
        }
        QPushButton:pressed { background-color: #161b22; }
    """,
    'button_subtle': """
        QPushButton {
            background-color: transparent;
            color: #58a6ff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
        }
        QPushButton:hover { background-color: rgba(88,166,255,0.1); }
        QPushButton:pressed { background-color: rgba(88,166,255,0.2); }
    """,
    'colors': {
        'text': '#c9d1d9',
        'text_secondary': '#8b949e',
        'text_muted': '#6e7681',
        'accent': '#58a6ff',
        'success': '#3fb950',
        'danger': '#f85149',
        'warning': '#d29922',
        'border': '#30363d',
        'background': '#0d1117',
        'background_alt': '#161b22',
        'card': '#161b22',
    }
}


class ThemeManager:
    """主题管理器 - 负责明暗主题切换"""
    
    def __init__(self, db, main_window):
        self.db = db
        self.main_window = main_window
        self.current_theme = 'light'
        self._theme_data = LIGHT_THEME
    
    def load_theme(self):
        """从数据库加载主题设置"""
        self.current_theme = self.db.get_setting('theme', 'light')
        self._theme_data = DARK_THEME if self.current_theme == 'dark' else LIGHT_THEME
        return self._theme_data
    
    def toggle_theme(self):
        """切换主题"""
        self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        self._theme_data = DARK_THEME if self.current_theme == 'dark' else LIGHT_THEME
        self.save_theme()
        return self._theme_data
    
    def save_theme(self):
        """保存主题设置到数据库"""
        self.db.set_setting('theme', self.current_theme)
    
    def get_theme(self):
        """获取当前主题数据"""
        return self._theme_data
    
    def is_dark(self):
        """是否为深色主题"""
        return self.current_theme == 'dark'
    
    def get_color(self, color_name):
        """获取主题颜色"""
        return self._theme_data['colors'].get(color_name, '#000000')
