# -*- coding: utf-8 -*-
"""
侧边栏模块 - 支持明暗主题
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QMessageBox, QFrame,
    QDialog, QLineEdit, QMenu, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QColor

# 导入共享样式
from ui.theme import (
    LIGHT_DIALOG_STYLE, LIGHT_INPUT_STYLE, LIGHT_BTN_CANCEL_STYLE, LIGHT_BTN_OK_STYLE, LIGHT_MENU_STYLE,
    DARK_DIALOG_STYLE, DARK_INPUT_STYLE, DARK_BTN_CANCEL_STYLE, DARK_BTN_OK_STYLE, DARK_MENU_STYLE
)

class BaseGroupDialog(QDialog):
    """分组对话框基类"""
    def __init__(self, db, title, label_text, parent=None, initial_value='', is_dark=False):
        super().__init__(parent)
        self.db = db
        self.is_dark = is_dark
        self.setWindowTitle(title)
        self.setFixedSize(380, 220)
        self._apply_theme()
        self._init_ui(label_text, initial_value)
    
    def _apply_theme(self):
        """应用主题样式"""
        if self.is_dark:
            self.setStyleSheet(DARK_DIALOG_STYLE)
            self.input_style = DARK_INPUT_STYLE
            self.btn_cancel_style = DARK_BTN_CANCEL_STYLE
            self.btn_ok_style = DARK_BTN_OK_STYLE
            self.label_color = '#c9d1d9'
            self.error_color = '#f85149'
        else:
            self.setStyleSheet(LIGHT_DIALOG_STYLE)
            self.input_style = LIGHT_INPUT_STYLE
            self.btn_cancel_style = LIGHT_BTN_CANCEL_STYLE
            self.btn_ok_style = LIGHT_BTN_OK_STYLE
            self.label_color = '#1A1A1A'
            self.error_color = '#D13438'
    
    def _init_ui(self, label_text, initial_value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(12)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {self.label_color}; font-size: 13px;")
        layout.addWidget(label)
        layout.addSpacing(4)
        
        self.input = QLineEdit()
        self.input.setFixedHeight(38)
        self.input.setStyleSheet(self.input_style)
        self.input.returnPressed.connect(self.try_accept)
        if initial_value:
            self.input.setText(initial_value)
            self.input.selectAll()
        layout.addWidget(self.input)
        
        self.error_label = QLabel('')
        self.error_label.setFixedHeight(20)
        self.error_label.setStyleSheet(f"color: {self.error_color}; font-size: 12px;")
        layout.addWidget(self.error_label)
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_cancel = QPushButton('取消')
        btn_cancel.setFixedSize(80, 36)
        btn_cancel.setStyleSheet(self.btn_cancel_style)
        btn_cancel.clicked.connect(self.reject)
        
        btn_ok = QPushButton('确定')
        btn_ok.setFixedSize(80, 36)
        btn_ok.setStyleSheet(self.btn_ok_style)
        btn_ok.clicked.connect(self.try_accept)
        
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)
    
    def try_accept(self):
        """子类需要实现验证逻辑"""
        raise NotImplementedError
    
    def get_name(self):
        return self.input.text().strip()


class AddGroupDialog(BaseGroupDialog):
    """添加分组对话框"""
    def __init__(self, db, parent=None, is_dark=False):
        super().__init__(db, '新建分组', '请输入分组名称:', parent, is_dark=is_dark)
    
    def try_accept(self):
        name = self.input.text().strip()
        if not name:
            self.error_label.setText('分组名称不能为空')
            return
        
        existing = [g[1] for g in self.db.get_all_groups()]
        if name in existing:
            self.error_label.setText('分组已存在，请使用其他名称')
            return
        
        self.accept()


class RenameGroupDialog(BaseGroupDialog):
    """重命名分组对话框"""
    def __init__(self, db, old_name, parent=None, is_dark=False):
        self.old_name = old_name
        super().__init__(db, '重命名分组', '请输入新的分组名称:', parent, old_name, is_dark=is_dark)
    
    def try_accept(self):
        name = self.input.text().strip()
        if not name:
            self.error_label.setText('分组名称不能为空')
            return
        
        if name != self.old_name:
            existing = [g[1] for g in self.db.get_all_groups()]
            if name in existing:
                self.error_label.setText('分组已存在，请使用其他名称')
                return
        
        self.accept()


class Sidebar(QWidget):
    group_selected = pyqtSignal(str)
    theme_changed = pyqtSignal(str)  # 主题切换信号
    language_changed = pyqtSignal()  # 语言切换信号
    settings_clicked = pyqtSignal()  # 设置按钮点击信号
    dashboard_clicked = pyqtSignal()  # 仪表盘按钮点击信号
    oauth_clicked = pyqtSignal()  # 手动授权按钮点击信号
    
    def __init__(self, db, is_dark=False):
        super().__init__()
        self.db = db
        self.is_dark = is_dark
        self.init_ui()
        self.load_groups()
    
    def init_ui(self):
        self.setFixedWidth(220)  # 缩短侧边栏宽度
        self._apply_base_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo区域
        self.logo_widget = QWidget()
        self.logo_widget.setFixedHeight(72)
        self.logo_widget.setStyleSheet("background: transparent; border: none;")
        logo_layout = QHBoxLayout(self.logo_widget)
        logo_layout.setContentsMargins(24, 0, 24, 0)
        
        logo_icon = QLabel('📧')
        logo_icon.setStyleSheet('font-size: 28px; border: none; background: transparent;')
        self.logo_text = QLabel('邮箱管家')
        self._apply_logo_style()
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addSpacing(12)
        logo_layout.addWidget(self.logo_text)
        logo_layout.addStretch()
        layout.addWidget(self.logo_widget)
        
        # 分隔线
        self.line = QFrame()
        self.line.setFixedHeight(1)
        self._apply_line_style()
        layout.addWidget(self.line)
        layout.addSpacing(12)
        
        # 导航菜单
        self.btn_all = QPushButton('  📋  全部邮箱')
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self._apply_nav_style()
        self.btn_all.clicked.connect(lambda: self.on_nav_click('全部'))
        layout.addWidget(self.btn_all)
        
        # 分组标题
        self.group_header = QWidget()
        self.group_header.setStyleSheet("background: transparent;")
        gh_layout = QHBoxLayout(self.group_header)
        gh_layout.setContentsMargins(20, 20, 20, 10)
        
        self.group_title = QLabel('分组')
        self._apply_group_title_style()
        gh_layout.addWidget(self.group_title)
        gh_layout.addStretch()
        
        # 添加分组按钮
        self.btn_add = QPushButton('+')
        self.btn_add.setFixedSize(26, 26)
        self._apply_add_btn_style()
        self.btn_add.clicked.connect(self.add_group)
        gh_layout.addWidget(self.btn_add)
        
        layout.addWidget(self.group_header)
        
        # 分组列表
        self.group_list = QListWidget()
        self.group_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.group_list.customContextMenuRequested.connect(self.show_group_menu)
        self._apply_list_style()
        self.group_list.itemClicked.connect(self.on_group_click)
        layout.addWidget(self.group_list)
        
        layout.addStretch()
        
        # 手动授权按钮 - 使用黑色图标
        self.btn_oauth = QPushButton('  🗝  手动授权')
        self.btn_oauth.setCheckable(True)
        self._apply_oauth_btn_style()
        self.btn_oauth.clicked.connect(self.on_oauth_click)
        layout.addWidget(self.btn_oauth)
        
        # 仪表盘按钮 - 使用黑色图标
        self.btn_dashboard = QPushButton('  📈  仪表盘')
        self.btn_dashboard.setCheckable(True)
        self._apply_dashboard_btn_style()
        self.btn_dashboard.clicked.connect(self.on_dashboard_click)
        layout.addWidget(self.btn_dashboard)
        
        # 设置按钮 - 使用黑色图标
        self.btn_settings = QPushButton('  ⚙  设置')
        self.btn_settings.setCheckable(True)
        self._apply_settings_btn_style()
        self.btn_settings.clicked.connect(self.on_settings_click)
        layout.addWidget(self.btn_settings)
        
        # 底部按钮区域 - 两个小图标按钮
        self.bottom_bar = QWidget()
        self.bottom_bar.setStyleSheet("background: transparent;")
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(16, 12, 16, 16)
        bottom_layout.setSpacing(8)
        
        # 主题切换按钮（月亮/太阳图标）
        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(44, 44)
        self._update_theme_btn_icon()
        self._apply_icon_btn_style(self.theme_btn)
        self.theme_btn.clicked.connect(self.show_theme_menu)
        self.theme_btn.setToolTip('切换主题')
        bottom_layout.addWidget(self.theme_btn)
        
        # 语言切换按钮
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedSize(80, 44)
        self._update_lang_btn_text()
        self._apply_lang_btn_style()
        self.lang_btn.clicked.connect(self.show_lang_menu)
        self.lang_btn.setToolTip('切换语言')
        bottom_layout.addWidget(self.lang_btn)
        
        bottom_layout.addStretch()
        
        layout.addWidget(self.bottom_bar)
    
    def _apply_base_style(self):
        """应用基础样式"""
        if self.is_dark:
            self.setStyleSheet("""
                QWidget {
                    background: #161b22;
                    border-right: 1px solid #30363d;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: #F9FAFB;
                    border-right: 1px solid #E5E7EB;
                }
            """)
    
    def _apply_logo_style(self):
        """应用Logo样式"""
        if self.is_dark:
            self.logo_text.setStyleSheet("""
                font-size: 20px; 
                font-weight: 600; 
                color: #c9d1d9;
                font-family: 'Segoe UI', 'Microsoft YaHei UI';
                background: transparent;
            """)
        else:
            self.logo_text.setStyleSheet("""
                font-size: 20px; 
                font-weight: 600; 
                color: #111827;
                font-family: 'Segoe UI', 'Microsoft YaHei UI';
                background: transparent;
            """)
    
    def _apply_line_style(self):
        """应用分隔线样式"""
        if self.is_dark:
            self.line.setStyleSheet("background-color: #30363d;")
        else:
            self.line.setStyleSheet("background-color: #E5E7EB;")
    
    def _apply_nav_style(self):
        """应用导航按钮样式"""
        if self.is_dark:
            self.btn_all.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 12px;
                    border: none;
                    background: transparent;
                    color: #c9d1d9;
                    font-size: 14px;
                    font-weight: 500;
                    height: 40px;
                    margin: 4px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #21262d;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background: #1f6feb33;
                    color: #58a6ff;
                }
            """)
        else:
            self.btn_all.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 12px;
                    border: none;
                    background: transparent;
                    color: #374151;
                    font-size: 14px;
                    font-weight: 500;
                    height: 40px;
                    margin: 4px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #F3F4F6;
                    color: #111827;
                }
                QPushButton:checked {
                    background: #EFF6FF;
                    color: #2563EB;
                    font-weight: 600;
                }
            """)
    
    def _apply_group_title_style(self):
        """应用分组标题样式"""
        if self.is_dark:
            self.group_title.setStyleSheet("""
                background: transparent;
                color: #8b949e;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 2px;
            """)
        else:
            self.group_title.setStyleSheet("""
                background: transparent;
                color: #6B7280;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 2px;
            """)
    
    def _apply_add_btn_style(self):
        """应用添加按钮样式"""
        if self.is_dark:
            self.btn_add.setStyleSheet("""
                QPushButton {
                    color: #8b949e;
                    background: transparent;
                    border: 1px solid #30363d;
                    border-radius: 4px;
                    padding-bottom: 2px;
                }
                QPushButton:hover {
                    color: #58a6ff;
                    border-color: #58a6ff;
                    background: #1f6feb11;
                }
            """)
        else:
            self.btn_add.setStyleSheet("""
                QPushButton {
                    color: #6B7280;
                    background: transparent;
                    border: 1px solid #E5E7EB;
                    border-radius: 4px;
                    padding-bottom: 2px;
                }
                QPushButton:hover {
                    color: #2563EB;
                    border-color: #2563EB;
                    background: #EFF6FF;
                }
            """)
    
    def _apply_common_btn_style(self, btn):
        if self.is_dark:
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 12px;
                    border: none;
                    background: transparent;
                    color: #c9d1d9;
                    font-size: 14px;
                    font-weight: normal;
                    height: 40px;
                    margin: 2px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #21262d;
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background: #1f6feb33;
                    color: #58a6ff;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 12px;
                    border: none;
                    background: transparent;
                    color: #374151;
                    font-size: 14px;
                    font-weight: normal;
                    height: 40px;
                    margin: 2px 12px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #F3F4F6;
                    color: #111827;
                }
                QPushButton:checked {
                    background: #EFF6FF;
                    color: #2563EB;
                    font-weight: 600;
                }
            """)
    
    def _apply_oauth_btn_style(self):
        self._apply_common_btn_style(self.btn_oauth)

    def _apply_dashboard_btn_style(self):
        self._apply_common_btn_style(self.btn_dashboard)

    def _apply_settings_btn_style(self):
        self._apply_common_btn_style(self.btn_settings)

    def _apply_list_style(self):
        """应用列表样式"""
        if self.is_dark:
            self.group_list.setStyleSheet("""
                QListWidget {
                    background: transparent;
                    border: none;
                    outline: none;
                    padding: 4px 12px;
                }
                QListWidget::item {
                    height: 36px;
                    border-radius: 6px;
                    padding-left: 12px;
                    margin-bottom: 2px;
                    color: #8b949e;
                }
                QListWidget::item:hover {
                    background: #21262d;
                    color: #c9d1d9;
                }
                QListWidget::item:selected {
                    background: #1f6feb33;
                    color: #58a6ff;
                }
            """)
        else:
            self.group_list.setStyleSheet("""
                QListWidget {
                    background: transparent;
                    border: none;
                    outline: none;
                    padding: 4px 12px;
                }
                QListWidget::item {
                    height: 36px;
                    border-radius: 6px;
                    padding-left: 12px;
                    margin-bottom: 2px;
                    color: #4B5563;
                }
                QListWidget::item:hover {
                    background: #F3F4F6;
                    color: #111827;
                }
                QListWidget::item:selected {
                    background: #EFF6FF;
                    color: #2563EB;
                    font-weight: 600;
                }
            """)
    
    def _apply_icon_btn_style(self, btn):
        """应用图标按钮样式 - 大圆角"""
        if self.is_dark:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.12);
                    border-color: rgba(88,166,255,0.5);
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.5);
                    border: 1px solid rgba(0,120,212,0.2);
                    border-radius: 16px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.8);
                    border-color: rgba(0,120,212,0.5);
                }
            """)
    
    def _apply_lang_btn_style(self):
        """应用语言按钮样式 - 大圆角"""
        if self.is_dark:
            self.lang_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.08);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                    font-size: 13px;
                    color: #8b949e;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.12);
                    border-color: rgba(88,166,255,0.5);
                    color: #c9d1d9;
                }
            """)
        else:
            self.lang_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.5);
                    border: 1px solid rgba(0,120,212,0.2);
                    border-radius: 16px;
                    font-size: 13px;
                    color: #1A5A8A;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.8);
                    border-color: rgba(0,120,212,0.5);
                    color: #004080;
                }
            """)
    
    def _update_theme_btn_icon(self):
        """更新主题按钮图标"""
        if self.is_dark:
            self.theme_btn.setText('🌙')
        else:
            self.theme_btn.setText('☀️')
    
    def _update_lang_btn_text(self):
        """更新语言按钮文本"""
        from core.i18n import get_language
        lang = get_language()
        if lang == 'zh':
            self.lang_btn.setText('文A 简体')
        else:
            self.lang_btn.setText('文A EN')
    
    def show_theme_menu(self):
        """显示主题选择菜单"""
        menu = QMenu(self)
        # 设置无边框以支持圆角
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setStyleSheet(DARK_MENU_STYLE if self.is_dark else LIGHT_MENU_STYLE)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50 if self.is_dark else 30))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        action_light = menu.addAction('☀️  浅色')
        action_dark = menu.addAction('🌙  深色')
        
        # 标记当前主题
        if self.is_dark:
            action_dark.setEnabled(False)
        else:
            action_light.setEnabled(False)
        
        action = menu.exec_(QCursor.pos())
        
        if action == action_light:
            self.theme_changed.emit('light')
        elif action == action_dark:
            self.theme_changed.emit('dark')
    
    def show_lang_menu(self):
        """显示语言选择菜单"""
        menu = QMenu(self)
        # 设置无边框以支持圆角
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setStyleSheet(DARK_MENU_STYLE if self.is_dark else LIGHT_MENU_STYLE)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50 if self.is_dark else 30))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        from core.i18n import get_language, set_language
        current_lang = get_language()
        
        action_zh = menu.addAction('简体中文')
        action_en = menu.addAction('English')
        
        # 标记当前语言
        if current_lang == 'zh':
            action_zh.setEnabled(False)
        else:
            action_en.setEnabled(False)
        
        action = menu.exec_(QCursor.pos())
        
        if action == action_zh:
            set_language('zh')
            self._update_lang_btn_text()
            self.lang_changed_signal()
        elif action == action_en:
            set_language('en')
            self._update_lang_btn_text()
            self.lang_changed_signal()
    
    def lang_changed_signal(self):
        """语言切换后的处理 - 立即刷新界面"""
        self.language_changed.emit()
    
    def refresh_language(self):
        """刷新侧边栏语言"""
        from core.i18n import tr
        
        # 更新Logo文本
        self.logo_text.setText(tr('app_name'))
        
        # 更新导航按钮
        self.btn_all.setText('  📋  ' + tr('all_emails'))
        
        # 更新分组标题
        self.group_title.setText(tr('groups'))
        
        # 更新手动授权按钮
        self.btn_oauth.setText('  🗝  ' + tr('manual_oauth'))
        
        # 更新仪表盘按钮
        self.btn_dashboard.setText('  📈  ' + tr('dashboard'))
        
        # 更新设置按钮
        self.btn_settings.setText('  ⚙  ' + tr('settings'))
        
        # 更新语言按钮
        self._update_lang_btn_text()
        
        # 更新工具提示
        self.theme_btn.setToolTip(tr('switch_theme'))
        self.lang_btn.setToolTip(tr('switch_language'))
    
    def apply_theme(self, is_dark):
        """应用主题"""
        self.is_dark = is_dark
        self._apply_base_style()
        self._apply_logo_style()
        self._apply_line_style()
        self._apply_nav_style()
        self._apply_group_title_style()
        self._apply_add_btn_style()
        self._apply_oauth_btn_style()
        self._apply_dashboard_btn_style()
        self._apply_settings_btn_style()
        self._apply_list_style()
        self._apply_icon_btn_style(self.theme_btn)
        self._apply_lang_btn_style()
        self._update_theme_btn_icon()

    def load_groups(self):
        """加载分组列表"""
        self.group_list.clear()
        groups = self.db.get_all_groups()
        for group in groups:
            item = QListWidgetItem(f'  📁  {group[1]}')
            item.setData(Qt.UserRole, group[1])
            self.group_list.addItem(item)
    
    def on_nav_click(self, name):
        """导航点击"""
        self.btn_all.setChecked(name == '全部')
        self.btn_settings.setChecked(False)
        self.btn_dashboard.setChecked(False)
        self.btn_oauth.setChecked(False)
        self.group_list.clearSelection()
        self.group_selected.emit('全部')
    
    def on_group_click(self, item):
        """分组点击"""
        self.btn_all.setChecked(False)
        self.btn_settings.setChecked(False)
        self.btn_dashboard.setChecked(False)
        self.btn_oauth.setChecked(False)
        group_name = item.data(Qt.UserRole)
        self.group_selected.emit(group_name)
    
    def on_settings_click(self):
        """设置按钮点击"""
        self.btn_all.setChecked(False)
        self.group_list.clearSelection()
        self.btn_dashboard.setChecked(False)
        self.btn_oauth.setChecked(False)
        self.btn_settings.setChecked(True)
        self.settings_clicked.emit()
    
    def on_dashboard_click(self):
        """仪表盘按钮点击"""
        self.btn_all.setChecked(False)
        self.group_list.clearSelection()
        self.btn_settings.setChecked(False)
        self.btn_oauth.setChecked(False)
        self.btn_dashboard.setChecked(True)
        self.dashboard_clicked.emit()
    
    def on_oauth_click(self):
        """手动授权按钮点击"""
        self.btn_all.setChecked(False)
        self.group_list.clearSelection()
        self.btn_settings.setChecked(False)
        self.btn_dashboard.setChecked(False)
        self.btn_oauth.setChecked(True)
        self.oauth_clicked.emit()
    
    def add_group(self):
        """添加分组"""
        dialog = AddGroupDialog(self.db, self, is_dark=self.is_dark)
        if dialog.exec_():
            name = dialog.get_name()
            if name:
                self.db.add_group(name)
                self.load_groups()
    
    def show_group_menu(self, pos):
        """显示分组右键菜单"""
        item = self.group_list.itemAt(pos)
        if not item:
            return
        
        group_name = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        # 设置无边框以支持圆角
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setStyleSheet(DARK_MENU_STYLE if self.is_dark else LIGHT_MENU_STYLE)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50 if self.is_dark else 30))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        action_rename = menu.addAction('✏️  重命名')
        action_delete = menu.addAction('🗑️  删除')
        
        # 默认分组不能删除
        if group_name == '默认分组':
            action_delete.setEnabled(False)
        
        action = menu.exec_(self.group_list.mapToGlobal(pos))
        
        if action == action_rename:
            self.rename_group(group_name)
        elif action == action_delete:
            self.delete_group(group_name)
    
    def rename_group(self, old_name):
        """重命名分组"""
        dialog = RenameGroupDialog(self.db, old_name, self, is_dark=self.is_dark)
        if dialog.exec_():
            new_name = dialog.get_name()
            if new_name and new_name != old_name:
                self.db.rename_group(old_name, new_name)
                self.load_groups()
                self.group_selected.emit('全部')
    
    def delete_group(self, group_name):
        """删除分组"""
        reply = QMessageBox.question(
            self, '确认删除', 
            f'确定要删除分组 "{group_name}" 吗？\n该分组下的邮箱将移至默认分组。',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_group(group_name)
            self.load_groups()
            self.group_selected.emit('全部')
