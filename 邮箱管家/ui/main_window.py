# -*- coding: utf-8 -*-
"""
主窗口模块 - Microsoft Fluent Design 风格
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QComboBox, QMessageBox, QHeaderView,
    QFrame, QFileDialog, QCheckBox, QTextEdit,
    QGraphicsDropShadowEffect, QAbstractItemView, QMenu, QShortcut
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QColor, QDragEnterEvent, QDropEvent, QPainter, QPen, QBrush, QKeySequence

from database.db_manager import DatabaseManager
from ui.dialogs import ImportDialog, EmailViewDialog, BatchSendDialog, create_email_client, MENU_STYLE_LIGHT, MENU_STYLE_DARK, ManualOAuth2Dialog, AccountDetailDialog, FluentMessageBox
from ui.sidebar import Sidebar
from ui.theme import ThemeManager, LIGHT_THEME, DARK_THEME
from ui.system_tray import SystemTrayManager
from core.i18n import tr, set_language, get_language


class StatusCheckThread(QThread):
    """状态检测线程"""
    status_updated = pyqtSignal(int, str)
    aws_updated = pyqtSignal(int, bool)  # 新增：AWS 状态更新信号
    progress_updated = pyqtSignal(int, int)  # 新增：进度信号 (current, total)
    finished_all = pyqtSignal()
    
    def __init__(self, accounts, db):
        super().__init__()
        self.accounts = accounts
        self.db = db
        self._stop_flag = False  # 停止标志
    
    def stop(self):
        """请求停止检测"""
        self._stop_flag = True
    
    def run(self):
        total = len(self.accounts)
        for i, account in enumerate(self.accounts):
            # 检查是否需要停止
            if self._stop_flag:
                break
            
            # 发送进度信号
            self.progress_updated.emit(i + 1, total)
            
            client = create_email_client(account, self.db)  # 传入db以便自动更新refresh_token
            status, _ = client.check_status()
            self.db.update_account_status(account[0], status)
            self.status_updated.emit(account[0], status)
            
            # 检测 AWS 验证码邮件
            if status == '正常' and not self._stop_flag:
                try:
                    has_aws, _ = client.check_aws_verification_emails(limit=30)
                    self.db.update_aws_code_status(account[0], has_aws)
                    self.aws_updated.emit(account[0], has_aws)
                except:
                    pass
        
        self.finished_all.emit()


class FluentCheckBox(QCheckBox):
    """自定义复选框 - 支持明暗主题"""
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setFixedSize(24, 24)  # 增大容器尺寸确保完整显示
    
    def set_dark_mode(self, is_dark):
        """设置深色模式"""
        self.is_dark = is_dark
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制边框和背景 - 居中显示 (24x24 容器，绘制 16x16)
        rect = QRect(4, 4, 16, 16)
        
        if self.is_dark:
            # 深色主题
            bg_color = '#0d1117'
            border_color = '#484f58'
            check_color = '#3fb950'
            focus_color = '#58a6ff'
        else:
            # 浅色主题
            bg_color = '#FFFFFF'
            border_color = '#9CA3AF'  # 加深边框颜色确保清晰
            check_color = '#2563EB'
            focus_color = '#2563EB'
        
        # 焦点状态下的边框颜色
        if self.hasFocus():
            border_color = focus_color
            painter.setPen(QPen(QColor(border_color), 1.5))
        else:
            painter.setPen(QPen(QColor(border_color), 1.5))  # 固定较粗的边框
            
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawRoundedRect(rect, 3, 3)
        
        # 如果选中，绘制勾选标记
        if self.isChecked():
            # 选中状态下填充背景色
            painter.setBrush(QBrush(QColor(check_color)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, 3, 3)
            # 绘制白色勾选
            painter.setPen(QPen(Qt.white, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(7, 12, 10, 15)
            painter.drawLine(10, 15, 17, 8)
        
        painter.end()


class FluentButton(QPushButton):
    """Fluent Design 按钮 - 支持明暗主题"""
    def __init__(self, text, btn_type='default', parent=None, is_dark=False):
        super().__init__(text, parent)
        self.btn_type = btn_type
        self.is_dark = is_dark
        self.setup_style()
        
    def setup_style(self):
        theme_data = DARK_THEME if self.is_dark else LIGHT_THEME
        key_map = {
            'primary': 'button_primary',
            'success': 'button_success',
            'warning': 'button_warning',
            'danger': 'button_danger',
            'subtle': 'button_subtle',
            'default': 'button_default'
        }
        theme_key = key_map.get(self.btn_type, 'button_default')
        style = theme_data.get(theme_key, theme_data['button_default'])
        self.setStyleSheet(style)

    def set_dark_mode(self, is_dark):
        """切换深色模式"""
        self.is_dark = is_dark
        self.setup_style()


class FluentCard(QFrame):
    """Fluent Design 卡片 - 支持明暗主题"""
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._apply_style()
        self._apply_shadow()
    
    def _apply_style(self):
        if self.is_dark:
            self.setStyleSheet("""
                QFrame {
                    background-color: #161b22;
                    border: none;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                }
            """)
    
    def _apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        if self.is_dark:
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 60))
            shadow.setOffset(0, 4)
        else:
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def set_dark_mode(self, is_dark):
        """切换深色模式"""
        self.is_dark = is_dark
        self._apply_style()
        self._apply_shadow()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_group = '全部'
        self.sort_by = 'id'
        self.sort_order = 'DESC'
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager(self.db, self)
        self.theme_manager.load_theme()
        
        self.load_settings()
        self.init_ui()
        self.setup_shortcuts()  # 设置快捷键
        self.load_accounts()
        
        # 初始化系统托盘
        self.tray_manager = SystemTrayManager(self)
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否是 txt 文件
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.txt'):
                    event.acceptProposedAction()
                    # 显示拖拽提示
                    self.show_drag_overlay(True)
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.show_drag_overlay(False)
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.show_drag_overlay(False)
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.txt'):
                self.import_from_dropped_file(file_path)
                break
        
        event.acceptProposedAction()
    
    def show_drag_overlay(self, show):
        """显示/隐藏拖拽提示覆盖层"""
        if not hasattr(self, 'drag_overlay'):
            self.drag_overlay = QLabel(self)
            self.drag_overlay.setAlignment(Qt.AlignCenter)
        
        is_dark = self.theme_manager.is_dark()
        if is_dark:
            self.drag_overlay.setStyleSheet("""
                QLabel {
                    background-color: rgba(35, 134, 54, 0.9);
                    color: white;
                    font-size: 24px;
                    font-weight: 600;
                    border: 3px dashed white;
                    border-radius: 16px;
                }
            """)
        else:
            self.drag_overlay.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 120, 212, 0.9);
                    color: white;
                    font-size: 24px;
                    font-weight: 600;
                    border: 3px dashed white;
                    border-radius: 16px;
                }
            """)
        self.drag_overlay.setText('📥 释放以导入账号')
        
        if show:
            self.drag_overlay.setGeometry(50, 50, self.width() - 100, self.height() - 100)
            self.drag_overlay.raise_()
            self.drag_overlay.show()
        else:
            self.drag_overlay.hide()
    
    def import_from_dropped_file(self, file_path):
        """从拖拽的文件导入账号"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                QMessageBox.warning(self, tr('warning'), '文件内容为空')
                return
            
            # 打开导入对话框，预填充内容
            dialog = ImportDialog(self.db, self, 
                                  default_group=None if self.current_group == '全部' else self.current_group)
            dialog.text_edit.setText(content)
            
            if dialog.exec_():
                self.load_accounts()
                self.load_group_filter()
                self.sidebar.load_groups()
                
        except Exception as e:
            QMessageBox.warning(self, tr('warning'), f'读取文件失败: {e}')
    
    def load_settings(self):
        """加载设置"""
        # 加载语言设置
        lang = self.db.get_setting('language', 'zh')
        set_language(lang)
        
        # 加载字体大小
        self.font_size = int(self.db.get_setting('font_size', '13'))
    
    def init_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # 应用全局样式
        self._apply_global_style()
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 侧边栏
        self.sidebar = Sidebar(self.db, is_dark=self.theme_manager.is_dark())
        self.sidebar.group_selected.connect(self.on_group_selected)
        self.sidebar.theme_changed.connect(self.set_theme)
        self.sidebar.language_changed.connect(self.refresh_language)
        self.sidebar.settings_clicked.connect(self.open_settings)
        self.sidebar.dashboard_clicked.connect(self.open_stats_dialog)
        self.sidebar.oauth_clicked.connect(self.open_oauth2_dialog)
        main_layout.addWidget(self.sidebar)
        
        # 内容区 - 保存引用以便主题切换
        self.content = QWidget()
        self._apply_content_style()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(28, 28, 28, 28)
        content_layout.setSpacing(20)
        
        # 标题区
        self.create_header(content_layout)
        # 工具栏
        self.create_toolbar(content_layout)
        # 表格
        self.create_table(content_layout)
        
        main_layout.addWidget(self.content, 1)
        self.load_group_filter()
    
    def _apply_global_style(self):
        """应用全局样式 - 支持明暗主题"""
        is_dark = self.theme_manager.is_dark()
        
        if is_dark:
            self.setStyleSheet(f"""
                QMainWindow {{ 
                    background: #0d1117;
                }}
                QWidget {{ 
                    font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif; 
                    font-size: {self.font_size}px; 
                }}
                QCheckBox {{
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid #30363d;
                    border-radius: 3px;
                    background: #0d1117;
                }}
                QCheckBox::indicator:hover {{
                    border-color: #58a6ff;
                }}
                QCheckBox::indicator:checked {{
                    background: #238636;
                    border-color: #238636;
                }}
                QToolTip {{
                    background-color: #21262d;
                    color: #e6edf3;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-size: 12px;
                }}
                QScrollBar:vertical {{
                    background: #0d1117;
                    width: 10px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: #30363d;
                    min-height: 30px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: #484f58;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{ 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #F8F9FA, stop:1 #E9ECEF);
                }}
                QWidget {{ 
                    font-family: 'Segoe UI', 'Microsoft YaHei UI', sans-serif; 
                    font-size: {self.font_size}px; 
                }}
                QCheckBox {{
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid #C0C0C0;
                    border-radius: 3px;
                    background: #FFFFFF;
                }}
                QCheckBox::indicator:hover {{
                    border-color: #0078D4;
                }}
                QCheckBox::indicator:checked {{
                    background: #0078D4;
                    border-color: #0078D4;
                }}
                QToolTip {{
                    background-color: #FFFFFF;
                    color: #333333;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-size: 12px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 10px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: #C0C0C0;
                    min-height: 30px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: #A0A0A0;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
    
    def _apply_content_style(self):
        """应用内容区样式"""
        if self.theme_manager.is_dark():
            self.content.setStyleSheet("""
                background: #0d1117;
                border-top-left-radius: 16px;
            """)
        else:
            self.content.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #FFFFFF, stop:1 #FAFBFC);
                border-top-left-radius: 16px;
            """)

    def create_header(self, layout):
        """创建标题区"""
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(self.header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        title_area = QVBoxLayout()
        self.title_label = QLabel(tr('email_management'))
        self.title_label.setStyleSheet(f"font-size: 28px; font-weight: 600; color: {self.theme_manager.get_color('text')};")
        self.subtitle_label = QLabel(tr('manage_all_accounts'))
        self.subtitle_label.setStyleSheet(f"font-size: 14px; color: {self.theme_manager.get_color('text_secondary')}; margin-top: 4px;")
        title_area.addWidget(self.title_label)
        title_area.addWidget(self.subtitle_label)
        
        h_layout.addLayout(title_area)
        h_layout.addStretch()
        
        is_dark = self.theme_manager.is_dark()
        
        # 右侧按钮容器 - 用于在设置页面时隐藏
        self.header_buttons = QWidget()
        self.header_buttons.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(self.header_buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        
        # 统计卡片
        self.stats_card = FluentCard(is_dark=is_dark)
        self.stats_card.setFixedSize(160, 60)
        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.setContentsMargins(12, 8, 12, 8)
        stats_layout.setSpacing(2)
        
        self.stats_count = QLabel('0')
        self.stats_count.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('accent')};")
        self.stats_text = QLabel(tr('current_group'))
        self.stats_text.setStyleSheet(f"font-size: 11px; color: {self.theme_manager.get_color('text_secondary')};")
        stats_layout.addWidget(self.stats_count)
        stats_layout.addWidget(self.stats_text)
        buttons_layout.addWidget(self.stats_card)
        
        h_layout.addWidget(self.header_buttons)
        layout.addWidget(self.header_widget)

    def create_toolbar(self, layout):
        """创建工具栏"""
        is_dark = self.theme_manager.is_dark()
        self.toolbar = FluentCard(is_dark=is_dark)
        self.toolbar.setFixedHeight(64)
        t_layout = QHBoxLayout(self.toolbar)
        t_layout.setContentsMargins(16, 12, 16, 12)
        t_layout.setSpacing(12)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍 ' + tr('search_email'))
        self.search_input.setFixedWidth(280)
        self.search_input.setStyleSheet(self.theme_manager.get_theme()['input'])
        self.search_input.textChanged.connect(self.filter_accounts)
        t_layout.addWidget(self.search_input)
        
        # 分组筛选
        self.group_filter = QComboBox()
        self.group_filter.setFixedWidth(140)
        self.group_filter.setStyleSheet(self.theme_manager.get_theme()['combo'])
        self.group_filter.currentTextChanged.connect(self.on_group_filter_changed)
        t_layout.addWidget(self.group_filter)
        
        # 排序按钮
        self.btn_sort = FluentButton(tr('sort_by'), 'default', is_dark=is_dark)
        self.btn_sort.clicked.connect(self.show_sort_menu)
        t_layout.addWidget(self.btn_sort)
        
        t_layout.addStretch()
        
        # 按钮组
        self.btn_import = FluentButton(tr('import_email'), 'default', is_dark=is_dark)
        self.btn_import.clicked.connect(self.import_accounts)
        self.btn_export = FluentButton(tr('export_backup'), 'default', is_dark=is_dark)
        self.btn_export.clicked.connect(self.export_accounts)
        self.btn_move = FluentButton(tr('move_group'), 'default', is_dark=is_dark)
        self.btn_move.clicked.connect(self.batch_move_group)
        self.btn_send = FluentButton(tr('batch_send'), 'default', is_dark=is_dark)
        self.btn_send.clicked.connect(self.batch_send_email)
        self.btn_check = FluentButton(tr('batch_check'), 'default', is_dark=is_dark)
        self.btn_check.clicked.connect(self.batch_check_status)
        self.btn_delete = FluentButton(tr('batch_delete'), 'default', is_dark=is_dark)
        self.btn_delete.clicked.connect(self.batch_delete)
        
        t_layout.addWidget(self.btn_import)
        t_layout.addWidget(self.btn_export)
        t_layout.addWidget(self.btn_move)
        t_layout.addWidget(self.btn_send)
        t_layout.addWidget(self.btn_check)
        t_layout.addWidget(self.btn_delete)
        
        layout.addWidget(self.toolbar)

    def create_table(self, layout):
        """创建表格"""
        is_dark = self.theme_manager.is_dark()
        self.table_card = FluentCard(is_dark=is_dark)
        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # 移除备注列
        self.table.setHorizontalHeaderLabels([
            tr('col_checkbox'), tr('col_index'), tr('col_email'), tr('col_password'),
            tr('col_group'), tr('col_status'), tr('col_type'), tr('col_aws'), 
            tr('col_operation')
        ])
        
        # 应用表格样式
        self.table.setStyleSheet(self.theme_manager.get_theme()['table'])
        
        # 设置表头对齐方式
        for i in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        
        # 双击编辑备注
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        # 右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # 列宽设置
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        
        # 复选框和序号固定宽度
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # 复选框
        header.setSectionResizeMode(1, QHeaderView.Fixed)      # 序号
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # 邮箱
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # 密码
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # 分组
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # 状态
        header.setSectionResizeMode(6, QHeaderView.Interactive)  # 类型
        header.setSectionResizeMode(7, QHeaderView.Fixed)        # AWS
        header.setSectionResizeMode(8, QHeaderView.Interactive)  # 操作
        
        self.table.setColumnWidth(0, 44)   # 复选框 (增大以适应新尺寸)
        self.table.setColumnWidth(1, 50)   # 序号
        self.table.setColumnWidth(7, 60)   # AWS
        
        table_layout.addWidget(self.table)
        
        # 底部信息
        self.table_bottom = QWidget()
        self._apply_table_bottom_style()
        bottom_layout = QHBoxLayout(self.table_bottom)
        bottom_layout.setContentsMargins(20, 14, 20, 14)
        
        # 拖拽提示
        self.drag_hint = QLabel('💡 提示：可直接拖拽 TXT 文件到窗口导入账号')
        self._apply_drag_hint_style()
        bottom_layout.addWidget(self.drag_hint)
        
        bottom_layout.addStretch()
        
        self.page_info = QLabel(tr('total_records', 0))
        self._apply_page_info_style()
        bottom_layout.addWidget(self.page_info)
        
        table_layout.addWidget(self.table_bottom)
        layout.addWidget(self.table_card, 1)
    
    def _apply_table_bottom_style(self):
        """应用表格底部样式"""
        if self.theme_manager.is_dark():
            self.table_bottom.setStyleSheet("""
                background: #161b22;
                border-top: 1px solid #30363d;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            """)
        else:
            self.table_bottom.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FAFBFC, stop:1 #F3F4F6);
                border-top: 1px solid #E5E7EB;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            """)
    
    def _apply_drag_hint_style(self):
        """应用拖拽提示样式"""
        if self.theme_manager.is_dark():
            self.drag_hint.setStyleSheet("color: #6e7681; font-size: 12px;")
        else:
            self.drag_hint.setStyleSheet("color: #9CA3AF; font-size: 12px;")
    
    def _apply_page_info_style(self):
        """应用页面信息样式"""
        if self.theme_manager.is_dark():
            self.page_info.setStyleSheet("color: #8b949e; font-size: 13px; font-weight: 500;")
        else:
            self.page_info.setStyleSheet("color: #6B7280; font-size: 13px; font-weight: 500;")

    def load_group_filter(self):
        # 暂时断开信号，避免触发跳转
        self.group_filter.blockSignals(True)
        
        current_group = self.current_group  # 保存当前分组
        self.group_filter.clear()
        self.group_filter.addItem(tr('all_groups'))
        for group in self.db.get_all_groups():
            self.group_filter.addItem(group[1])
        
        # 恢复选中状态
        if current_group != '全部':
            index = self.group_filter.findText(current_group)
            if index >= 0:
                self.group_filter.setCurrentIndex(index)
        
        # 重新连接信号
        self.group_filter.blockSignals(False)

    def load_accounts(self):
        if self.current_group == '全部':
            accounts = self.db.get_all_accounts_sorted(self.sort_by, self.sort_order)
        else:
            accounts = self.db.get_accounts_by_group_sorted(self.current_group, self.sort_by, self.sort_order)
        
        self.table.setRowCount(len(accounts))
        
        # 获取主题颜色（移到循环外部提高性能）
        is_dark = self.theme_manager.is_dark()
        text_color = self.theme_manager.get_color('text')
        text_secondary = self.theme_manager.get_color('text_secondary')
        text_muted = self.theme_manager.get_color('text_muted')
        accent_color = self.theme_manager.get_color('accent')
        success_color = self.theme_manager.get_color('success')
        danger_color = self.theme_manager.get_color('danger')
        
        # 密码列表
        font_bold = self.font()
        font_bold.setBold(True)
        
        for row, acc in enumerate(accounts):
            self.table.setRowHeight(row, 44)
            
            # 复选框 - 使用自定义样式
            cb = FluentCheckBox(is_dark=is_dark)
            cb.setProperty('account_id', acc[0])
            cb_widget = QWidget()
            cb_widget.setStyleSheet("background: transparent; border: none;")
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(cb)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, cb_widget)
            
            # 序号
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setForeground(QColor(text_muted))
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, num_item)
            
            # 邮箱 + 复制按钮
            email_widget = QWidget()
            email_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
            email_layout = QHBoxLayout(email_widget)
            email_layout.setContentsMargins(4, 0, 4, 0)
            email_layout.setSpacing(4)
            
            email_label = QLabel(acc[1])
            email_label.setStyleSheet(f"QLabel {{ color: {text_color}; font-size: 13px; background: transparent; }}")
            email_layout.addWidget(email_label, 1)
            
            btn_copy_email = QPushButton(tr('copy'))
            btn_copy_email.setFixedWidth(36)
            btn_copy_email.setCursor(Qt.PointingHandCursor)
            copy_btn_style = f"QPushButton{{border:none;background:transparent;color:{'#8b949e' if is_dark else '#666'};font-size:11px;border-radius:3px;padding:2px 4px;}}QPushButton:hover{{background:{'#30363d' if is_dark else '#f0f0f0'};color:{'#58a6ff' if is_dark else '#0078D4'};}}"
            btn_copy_email.setStyleSheet(copy_btn_style)
            btn_copy_email.setProperty('copy_text', acc[1])
            btn_copy_email.clicked.connect(self.copy_text)
            email_layout.addWidget(btn_copy_email)
            
            self.table.setCellWidget(row, 2, email_widget)
            
            # 密码 + 显示/隐藏 + 复制按钮
            pwd_widget = QWidget()
            pwd_widget.setStyleSheet("QWidget { background: transparent; border: none; }")
            pwd_layout = QHBoxLayout(pwd_widget)
            pwd_layout.setContentsMargins(4, 0, 4, 0)
            pwd_layout.setSpacing(4)
            
            pwd_label = QLabel('••••••••')
            pwd_label.setStyleSheet(f"QLabel {{ color: {text_secondary}; font-size: 13px; background: transparent; }}")
            pwd_label.setProperty('real_password', acc[2])
            pwd_label.setProperty('is_hidden', True)
            pwd_layout.addWidget(pwd_label, 1)
            
            btn_toggle_pwd = QPushButton(tr('show'))
            btn_toggle_pwd.setFixedWidth(36)
            btn_toggle_pwd.setCursor(Qt.PointingHandCursor)
            btn_toggle_pwd.setStyleSheet(copy_btn_style)
            btn_toggle_pwd.setProperty('pwd_label', pwd_label)
            btn_toggle_pwd.clicked.connect(self.toggle_password)
            pwd_layout.addWidget(btn_toggle_pwd)
            
            btn_copy_pwd = QPushButton(tr('copy'))
            btn_copy_pwd.setFixedWidth(36)
            btn_copy_pwd.setCursor(Qt.PointingHandCursor)
            btn_copy_pwd.setStyleSheet(copy_btn_style)
            btn_copy_pwd.setProperty('copy_text', acc[2])
            btn_copy_pwd.clicked.connect(self.copy_text)
            pwd_layout.addWidget(btn_copy_pwd)
            
            self.table.setCellWidget(row, 3, pwd_widget)
            
            # 分组
            group_item = QTableWidgetItem(acc[3])
            group_item.setForeground(QColor(text_color))
            group_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            group_item.setData(Qt.UserRole, acc[0])  # 存储 account_id
            self.table.setItem(row, 4, group_item)
            
            # 状态 - 使用徽章样式
            status_text = acc[4]
            status_widget = QWidget()
            status_widget.setStyleSheet("background: transparent; border: none;")
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            status_badge = QLabel(status_text)
            status_badge.setAlignment(Qt.AlignCenter)
            
            # 根据状态选择样式
            badge_style_key = 'badge_info'
            if status_text == '正常':
                badge_style_key = 'badge_success'
            elif status_text in ['异常', '封禁', '失败']:
                badge_style_key = 'badge_error'
            elif status_text in ['验证中', '验证']:
                badge_style_key = 'badge_warning'
                
            status_badge.setStyleSheet(self.theme_manager.get_theme().get(badge_style_key, ''))
            status_layout.addWidget(status_badge)
            self.table.setCellWidget(row, 5, status_widget)
            
            # 类型
            type_item = QTableWidgetItem(acc[5])
            type_item.setForeground(QColor(text_secondary))
            type_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.table.setItem(row, 6, type_item)
            
            # AWS 标记 - 检查 has_aws_code 字段 (索引14)
            has_aws = acc[14] if len(acc) > 14 else 0
            aws_item = QTableWidgetItem(tr('has_aws_code') if has_aws else tr('no_aws_code'))
            aws_item.setTextAlignment(Qt.AlignCenter)
            if has_aws:
                aws_item.setForeground(QColor(success_color))
            else:
                aws_item.setForeground(QColor(text_muted))
            self.table.setItem(row, 7, aws_item)
            
            # 操作按钮 - 图标样式
            ops_widget = QWidget()
            ops_widget.setStyleSheet("background: transparent; border: none;")
            ops_layout = QHBoxLayout(ops_widget)
            ops_layout.setContentsMargins(0, 0, 0, 0)
            ops_layout.setSpacing(6)
            ops_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # 查看
            btn_view = QPushButton('👁')
            btn_view.setFixedSize(28, 28)
            btn_view.setCursor(Qt.PointingHandCursor)
            view_color = '#58a6ff' if is_dark else '#0078D4'
            view_bg = 'rgba(88,166,255,0.1)' if is_dark else 'rgba(0,120,212,0.1)'
            btn_view.setStyleSheet(f"QPushButton{{color:{view_color};background:transparent;border:none;border-radius:4px;font-size:14px;}}QPushButton:hover{{background:{view_bg};}}")
            btn_view.setToolTip(tr('view'))
            btn_view.setProperty('account_id', acc[0])
            btn_view.clicked.connect(self.view_emails)
            
            # 删除
            btn_del = QPushButton('🗑')
            btn_del.setFixedSize(28, 28)
            btn_del.setCursor(Qt.PointingHandCursor)
            del_color = '#f85149' if is_dark else '#D13438'
            del_bg = 'rgba(248,81,73,0.1)' if is_dark else 'rgba(209,52,56,0.1)'
            btn_del.setStyleSheet(f"QPushButton{{color:{del_color};background:transparent;border:none;border-radius:4px;font-size:14px;}}QPushButton:hover{{background:{del_bg};}}")
            btn_del.setToolTip(tr('delete'))
            account_id = acc[0]
            btn_del.clicked.connect(lambda checked, aid=account_id: self.delete_single_account(aid))

            # 更多
            btn_more = QPushButton('⋮')
            btn_more.setFixedSize(28, 28)
            btn_more.setCursor(Qt.PointingHandCursor)
            more_color = '#8b949e' if is_dark else '#666'
            more_hover_bg = '#30363d' if is_dark else '#f0f0f0'
            btn_more.setStyleSheet(f"QPushButton{{color:{more_color};background:transparent;border:none;border-radius:4px;font-size:16px;font-weight:bold;}}QPushButton:hover{{background:{more_hover_bg};}}")
            btn_more.setToolTip('更多操作')
            btn_more.setProperty('row', row)
            btn_more.clicked.connect(self.show_more_menu)
            
            ops_layout.addWidget(btn_view)
            ops_layout.addWidget(btn_del)
            ops_layout.addWidget(btn_more)
            self.table.setCellWidget(row, 8, ops_widget)
        
        # 右上角显示当前分组数量
        current_count = len(accounts)
        self.stats_count.setText(str(current_count))
        self.page_info.setText(tr('total_records', current_count))
        
        # 调整列宽
        self.adjust_column_widths()

    def on_group_selected(self, group_name):
        self.current_group = group_name
        # 隐藏设置页面，显示表格
        self.hide_settings_page()
        self.load_accounts()

    def on_group_filter_changed(self, group_name):
        all_groups_text = tr('all_groups')
        self.current_group = '全部' if group_name == all_groups_text else group_name
        self.load_accounts()
    
    def show_sort_menu(self):
        """显示排序菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        
        action_default = menu.addAction(tr('sort_default'))
        action_email = menu.addAction(tr('sort_by_email'))
        action_status = menu.addAction(tr('sort_by_status'))
        action_aws = menu.addAction(tr('sort_by_aws'))
        
        action = menu.exec_(self.btn_sort.mapToGlobal(self.btn_sort.rect().bottomLeft()))
        
        if action == action_default:
            self.sort_by = 'id'
            self.sort_order = 'DESC'
        elif action == action_email:
            self.sort_by = 'email'
            self.sort_order = 'ASC'
        elif action == action_status:
            self.sort_by = 'status'
            self.sort_order = 'ASC'
        elif action == action_aws:
            self.sort_by = 'has_aws_code'
            self.sort_order = 'DESC'
        else:
            return
        
        self.load_accounts()
    
    def open_settings(self):
        """显示设置页面 - 在右侧内容区显示"""
        # 隐藏表格区域，显示设置页面
        self.show_settings_page()
    
    def show_settings_page(self):
        """显示设置页面"""
        # 如果设置页面不存在，创建它
        if not hasattr(self, 'settings_page'):
            self.create_settings_page()
        
        # 隐藏工具栏、表格卡片、标题区右侧按钮和其他页面
        self.toolbar.hide()
        self.table_card.hide()
        self.header_buttons.hide()
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.hide()
        if hasattr(self, 'oauth_page'):
            self.oauth_page.hide()
        self.settings_page.show()
        
        # 更新标题
        self.title_label.setText(tr('settings'))
        self.subtitle_label.setText(tr('settings_desc'))
    
    def hide_settings_page(self):
        """隐藏设置页面，显示表格"""
        if hasattr(self, 'settings_page'):
            self.settings_page.hide()
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.hide()
        if hasattr(self, 'oauth_page'):
            self.oauth_page.hide()
        
        # 显示工具栏、表格和标题区右侧按钮
        self.toolbar.show()
        self.table_card.show()
        self.header_buttons.show()
        
        # 恢复标题
        self.title_label.setText(tr('email_management'))
        self.subtitle_label.setText(tr('manage_all_accounts'))
    
    def create_settings_page(self):
        """创建设置页面 - 简洁设计"""
        from core.i18n import tr, get_language, set_language
        
        is_dark = self.theme_manager.is_dark()
        self.settings_page = QWidget()
        
        # 设置无边框背景
        if is_dark:
            self.settings_page.setStyleSheet("background: #0d1117; border: none;")
        else:
            self.settings_page.setStyleSheet("background: #FFFFFF; border: none;")
        
        # 添加到内容区布局
        content_layout = self.content.layout()
        content_layout.addWidget(self.settings_page)
        
        page_layout = QVBoxLayout(self.settings_page)
        page_layout.setContentsMargins(32, 32, 32, 32)
        page_layout.setSpacing(32)
        
        # 主题设置区域
        theme_section = self.create_theme_section()
        page_layout.addWidget(theme_section)
        
        # 常规设置区域
        general_section = self.create_general_section()
        page_layout.addWidget(general_section)
        
        page_layout.addStretch()
        
        # 初始隐藏
        self.settings_page.hide()
    
    def create_theme_section(self):
        """创建主题设置区域 - 精美卡片式设计"""
        from core.i18n import tr
        
        is_dark = self.theme_manager.is_dark()
        
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 区域标题
        self.theme_section_title = QLabel(tr('theme_settings'))
        self.theme_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        layout.addWidget(self.theme_section_title)
        
        self.theme_section_desc = QLabel(tr('theme_settings_desc'))
        self.theme_section_desc.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text_secondary')}; background: transparent;")
        layout.addWidget(self.theme_section_desc)
        
        layout.addSpacing(8)
        
        # 主题选择按钮容器
        theme_row = QHBoxLayout()
        theme_row.setSpacing(16)
        
        # 浅色主题按钮
        self.theme_light_btn = self.create_theme_button('☀️', tr('light_theme'), not is_dark, '#0078D4')
        self.theme_light_btn.clicked.connect(lambda: self.on_theme_select('light'))
        theme_row.addWidget(self.theme_light_btn.container)
        
        # 深色主题按钮
        self.theme_dark_btn = self.create_theme_button('🌙', tr('dark_theme'), is_dark, '#1a1b3c')
        self.theme_dark_btn.clicked.connect(lambda: self.on_theme_select('dark'))
        theme_row.addWidget(self.theme_dark_btn.container)
        
        theme_row.addStretch()
        layout.addLayout(theme_row)
        
        return section
    
    def create_theme_button(self, icon, text, selected=False, icon_bg='#0078D4'):
        """创建主题选择按钮 - 精美设计"""
        is_light = icon == '☀️'
        
        # 外层容器
        container = QWidget()
        container.setFixedSize(100, 120)
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 按钮
        btn = QPushButton()
        btn.setFixedSize(100, 120)
        btn.setCheckable(True)
        btn.setChecked(selected)
        btn.setCursor(Qt.PointingHandCursor)
        
        # 创建按钮内容
        btn_layout = QVBoxLayout(btn)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 16, 0, 12)
        
        # 图标容器 - 精美渐变背景
        icon_container = QLabel()
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignCenter)
        
        if is_light:
            # 浅色主题 - 蓝色渐变背景 + 太阳图标
            icon_container.setText('☀')
            icon_container.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #60A5FA, stop:1 #3B82F6);
                border-radius: 12px;
                font-size: 22px;
                color: white;
            """)
        else:
            # 深色主题 - 深蓝紫色背景 + 月亮图标
            icon_container.setText('🌙')
            icon_container.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1b4b, stop:1 #312e81);
                border-radius: 12px;
                font-size: 20px;
            """)
        
        btn_layout.addWidget(icon_container, 0, Qt.AlignCenter)
        
        # 文本标签
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text')}; background: transparent; font-weight: 500;")
        btn_layout.addWidget(text_label)
        
        # 选中标记 - 蓝色圆形背景 + 白色勾号
        check_label = QLabel('✓')
        check_label.setFixedSize(20, 20)
        check_label.setAlignment(Qt.AlignCenter)
        check_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #60A5FA, stop:1 #3B82F6);
            color: white;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
        """)
        check_label.setVisible(selected)
        
        # 保存引用以便更新
        btn.icon_container = icon_container
        btn.text_label = text_label
        btn.check_label = check_label
        btn.container = container
        btn.is_light = is_light
        
        self._apply_theme_btn_style(btn, selected)
        
        container_layout.addWidget(btn)
        
        # 将选中标记放在右上角
        check_label.setParent(container)
        check_label.move(76, 6)
        check_label.raise_()
        
        return btn
    
    def _apply_theme_btn_style(self, btn, selected=False):
        """应用主题按钮样式 - 精美设计"""
        is_dark = self.theme_manager.is_dark()
        
        if is_dark:
            if selected:
                btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(59, 130, 246, 0.15);
                        border: 2px solid #3B82F6;
                        border-radius: 16px;
                    }
                    QPushButton:hover {
                        background: rgba(59, 130, 246, 0.2);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        border-radius: 16px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.05);
                    }
                """)
        else:
            if selected:
                btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(59, 130, 246, 0.08);
                        border: 2px solid #3B82F6;
                        border-radius: 16px;
                    }
                    QPushButton:hover {
                        background: rgba(59, 130, 246, 0.12);
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        border-radius: 16px;
                    }
                    QPushButton:hover {
                        background: rgba(0, 0, 0, 0.03);
                    }
                """)
    
    def on_theme_select(self, theme):
        """主题选择"""
        self.set_theme(theme)
        # 更新按钮状态
        is_dark = theme == 'dark'
        self.theme_light_btn.setChecked(not is_dark)
        self.theme_dark_btn.setChecked(is_dark)
        self._apply_theme_btn_style(self.theme_light_btn, not is_dark)
        self._apply_theme_btn_style(self.theme_dark_btn, is_dark)
        # 更新选中标记
        if hasattr(self.theme_light_btn, 'check_label'):
            self.theme_light_btn.check_label.setVisible(not is_dark)
        if hasattr(self.theme_dark_btn, 'check_label'):
            self.theme_dark_btn.check_label.setVisible(is_dark)
    
    def create_general_section(self):
        """创建常规设置区域 - 精美设计"""
        from core.i18n import tr, get_language
        import os
        
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        
        # 区域标题
        self.general_section_title = QLabel(tr('general_settings'))
        self.general_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        layout.addWidget(self.general_section_title)
        
        self.general_section_desc = QLabel(tr('general_settings_desc'))
        self.general_section_desc.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text_secondary')}; background: transparent;")
        layout.addWidget(self.general_section_desc)
        
        layout.addSpacing(8)
        
        # 字体大小设置行
        self.font_label = QLabel(tr('font_size'))
        self.font_label.setFixedSize(100, 32)
        self.font_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        
        self.settings_font_combo = QComboBox()
        self.settings_font_combo.addItems(['11', '12', '13', '14', '15', '16', '18', '20'])
        self.settings_font_combo.setFixedSize(120, 32)
        self.settings_font_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        current_font = self.db.get_setting('font_size', '13')
        index = self.settings_font_combo.findText(current_font)
        if index >= 0:
            self.settings_font_combo.setCurrentIndex(index)
        self.settings_font_combo.currentTextChanged.connect(self.on_settings_font_changed)
        
        font_row = QHBoxLayout()
        font_row.setSpacing(24)
        font_row.addWidget(self.font_label)
        font_row.addWidget(self.settings_font_combo)
        font_row.addStretch()
        layout.addLayout(font_row)
        
        layout.addSpacing(8)
        
        # 语言设置行
        self.lang_label = QLabel(tr('language'))
        self.lang_label.setFixedSize(100, 32)
        self.lang_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        
        self.settings_lang_combo = QComboBox()
        self.settings_lang_combo.addItem(tr('chinese'), 'zh')
        self.settings_lang_combo.addItem(tr('english'), 'en')
        self.settings_lang_combo.setFixedSize(120, 32)
        self.settings_lang_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        current_lang = get_language()
        for i in range(self.settings_lang_combo.count()):
            if self.settings_lang_combo.itemData(i) == current_lang:
                self.settings_lang_combo.setCurrentIndex(i)
                break
        self.settings_lang_combo.currentIndexChanged.connect(self.on_settings_lang_changed)
        
        lang_row = QHBoxLayout()
        lang_row.setSpacing(24)
        lang_row.addWidget(self.lang_label)
        lang_row.addWidget(self.settings_lang_combo)
        lang_row.addStretch()
        layout.addLayout(lang_row)
        
        layout.addSpacing(8)
        
        # 数据存储位置
        self.data_label = QLabel(tr('data_location'))
        self.data_label.setFixedSize(100, 28)
        self.data_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        
        db_path = os.path.abspath('data/emails.db')
        self.data_path_label = QLabel(db_path)
        self.data_path_label.setFixedHeight(28)
        self.data_path_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; background: transparent; font-size: 13px;")
        
        self.btn_open_data = QPushButton(tr('open_folder'))
        self.btn_open_data.setFixedHeight(28)
        self.btn_open_data.setCursor(Qt.PointingHandCursor)
        self._apply_link_btn_style(self.btn_open_data)
        self.btn_open_data.clicked.connect(self.open_data_folder)
        
        data_row = QHBoxLayout()
        data_row.setSpacing(24)
        data_row.addWidget(self.data_label)
        data_row.addWidget(self.data_path_label)
        data_row.addWidget(self.btn_open_data)
        data_row.addStretch()
        layout.addLayout(data_row)
        
        # 关于区域
        layout.addSpacing(24)
        self.about_section_title = QLabel(tr('about'))
        self.about_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        layout.addWidget(self.about_section_title)
        
        layout.addSpacing(8)
        
        self.version_label = QLabel(f"{tr('app_name')} v1.2.9")
        self.version_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        layout.addWidget(self.version_label)
        
        self.copyright_label = QLabel("© 2025 邮箱管家. All rights reserved.")
        self.copyright_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; background: transparent; font-size: 12px;")
        layout.addWidget(self.copyright_label)
        
        return section
    
    def _apply_link_btn_style(self, btn):
        """应用链接按钮样式"""
        is_dark = self.theme_manager.is_dark()
        if is_dark:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #58a6ff;
                    border: none;
                    font-size: 13px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #0078D4;
                    border: none;
                    font-size: 13px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
    
    def open_data_folder(self):
        """打开数据存储文件夹"""
        import os
        import subprocess
        data_path = os.path.abspath('data')
        if os.path.exists(data_path):
            subprocess.Popen(f'explorer "{data_path}"')
    
    def on_settings_font_changed(self, font_size_str):
        """设置页面字体大小改变"""
        font_size = int(font_size_str)
        self.db.set_setting('font_size', font_size_str)
        self.refresh_font_size(font_size)
    
    def on_settings_lang_changed(self, index):
        """设置页面语言改变 - 同步更新侧边栏"""
        from core.i18n import set_language
        lang = self.settings_lang_combo.currentData()
        self.db.set_setting('language', lang)
        set_language(lang)
        # 刷新主界面语言
        self.refresh_language()
        # 刷新设置页面文本
        self.refresh_settings_page_text()
        # 同步更新侧边栏语言按钮
        self.sidebar._update_lang_btn_text()
    
    def refresh_settings_page_text(self):
        """刷新设置页面文本"""
        from core.i18n import tr, get_language
        
        if not hasattr(self, 'settings_page'):
            return
        
        # 更新主标题（设置页面使用主标题区域）
        self.title_label.setText(tr('settings'))
        self.subtitle_label.setText(tr('settings_desc'))
        
        # 更新主题区域
        self.theme_section_title.setText(tr('theme_settings'))
        self.theme_section_desc.setText(tr('theme_settings_desc'))
        
        # 更新主题按钮文本
        if hasattr(self.theme_light_btn, 'text_label'):
            self.theme_light_btn.text_label.setText(tr('light_theme'))
        if hasattr(self.theme_dark_btn, 'text_label'):
            self.theme_dark_btn.text_label.setText(tr('dark_theme'))
        
        # 更新常规设置区域
        self.general_section_title.setText(tr('general_settings'))
        self.general_section_desc.setText(tr('general_settings_desc'))
        self.font_label.setText(tr('font_size'))
        self.lang_label.setText(tr('language'))
        
        # 更新数据和关于区域
        if hasattr(self, 'data_label'):
            self.data_label.setText(tr('data_location'))
        if hasattr(self, 'btn_open_data'):
            self.btn_open_data.setText(tr('open_folder'))
        if hasattr(self, 'about_section_title'):
            self.about_section_title.setText(tr('about'))
        if hasattr(self, 'version_label'):
            self.version_label.setText(f"{tr('app_name')} v1.2.9")
        
        # 更新语言下拉框
        current_data = self.settings_lang_combo.currentData()
        self.settings_lang_combo.blockSignals(True)
        self.settings_lang_combo.clear()
        self.settings_lang_combo.addItem(tr('chinese'), 'zh')
        self.settings_lang_combo.addItem(tr('english'), 'en')
        for i in range(self.settings_lang_combo.count()):
            if self.settings_lang_combo.itemData(i) == current_data:
                self.settings_lang_combo.setCurrentIndex(i)
                break
        self.settings_lang_combo.blockSignals(False)
    
    def _update_settings_page_theme(self):
        """更新设置页面主题样式"""
        if not hasattr(self, 'settings_page'):
            return
        
        is_dark = self.theme_manager.is_dark()
        
        # 更新设置页面背景
        if is_dark:
            self.settings_page.setStyleSheet("background: #0d1117; border: none;")
        else:
            self.settings_page.setStyleSheet("background: #FFFFFF; border: none;")
        
        # 更新主题区域样式
        self.theme_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        self.theme_section_desc.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text_secondary')}; background: transparent;")
        
        # 更新常规设置区域样式
        self.general_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        self.general_section_desc.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text_secondary')}; background: transparent;")
        self.font_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        self.lang_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        
        # 更新数据和关于区域样式
        if hasattr(self, 'data_label'):
            self.data_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        if hasattr(self, 'data_path_label'):
            self.data_path_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; background: transparent; font-size: 13px;")
        if hasattr(self, 'btn_open_data'):
            self._apply_link_btn_style(self.btn_open_data)
        if hasattr(self, 'about_section_title'):
            self.about_section_title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {self.theme_manager.get_color('text')}; background: transparent;")
        if hasattr(self, 'version_label'):
            self.version_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; background: transparent; font-size: 14px;")
        if hasattr(self, 'copyright_label'):
            self.copyright_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; background: transparent; font-size: 12px;")
        
        # 更新下拉框样式
        self.settings_font_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        self.settings_lang_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        
        # 更新主题按钮状态
        self.theme_light_btn.setChecked(not is_dark)
        self.theme_dark_btn.setChecked(is_dark)
        self._apply_theme_btn_style(self.theme_light_btn, not is_dark)
        self._apply_theme_btn_style(self.theme_dark_btn, is_dark)
        
        # 更新选中标记
        if hasattr(self.theme_light_btn, 'check_label'):
            self.theme_light_btn.check_label.setVisible(not is_dark)
        if hasattr(self.theme_dark_btn, 'check_label'):
            self.theme_dark_btn.check_label.setVisible(is_dark)
        
        # 更新主题按钮内的文本颜色
        if hasattr(self.theme_light_btn, 'text_label'):
            self.theme_light_btn.text_label.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text')}; background: transparent; font-weight: 500;")
        if hasattr(self.theme_dark_btn, 'text_label'):
            self.theme_dark_btn.text_label.setStyleSheet(f"font-size: 13px; color: {self.theme_manager.get_color('text')}; background: transparent; font-weight: 500;")
    
    def open_oauth2_dialog(self):
        """显示手动授权页面 - 在右侧内容区显示"""
        self.show_oauth_page()
    
    def show_oauth_page(self):
        """显示手动授权页面"""
        from core.i18n import tr
        
        # 如果页面不存在，创建它
        if not hasattr(self, 'oauth_page'):
            self.create_oauth_page()
        
        # 隐藏其他页面
        self.toolbar.hide()
        self.table_card.hide()
        self.header_buttons.hide()
        if hasattr(self, 'settings_page'):
            self.settings_page.hide()
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.hide()
        self.oauth_page.show()
        
        # 更新标题
        self.title_label.setText('手动授权')
        self.subtitle_label.setText('通过浏览器手动登录获取 OAuth2 授权')
    
    def create_oauth_page(self):
        """创建手动授权页面"""
        from core.i18n import tr
        from ui.dialogs import ManualOAuth2Thread
        
        is_dark = self.theme_manager.is_dark()
        self.oauth_page = QWidget()
        
        if is_dark:
            self.oauth_page.setStyleSheet("background: #0d1117; border: none;")
        else:
            self.oauth_page.setStyleSheet("background: #FFFFFF; border: none;")
        
        content_layout = self.content.layout()
        content_layout.addWidget(self.oauth_page)
        
        page_layout = QVBoxLayout(self.oauth_page)
        page_layout.setContentsMargins(32, 32, 32, 32)
        page_layout.setSpacing(20)
        
        # 说明区域
        desc_label = QLabel('点击"开始授权"后，浏览器会打开微软登录页面。\n'
                           '请手动登录您的 Outlook 账号，登录成功后程序会自动获取授权信息。')
        desc_label.setStyleSheet(f"color: {self.theme_manager.get_color('text_secondary')}; font-size: 13px; line-height: 1.6;")
        desc_label.setWordWrap(True)
        page_layout.addWidget(desc_label)
        
        # 分组选择行
        group_row = QHBoxLayout()
        group_label = QLabel('导入到分组:')
        group_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; font-size: 14px;")
        group_row.addWidget(group_label)
        
        self.oauth_group_combo = QComboBox()
        self.oauth_group_combo.setFixedSize(160, 32)
        self.oauth_group_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        for group in self.db.get_all_groups():
            self.oauth_group_combo.addItem(group[1])
        group_row.addWidget(self.oauth_group_combo)
        group_row.addStretch()
        page_layout.addLayout(group_row)
        
        # 提示
        tip_label = QLabel('💡 提示：登录完成后请等待页面自动跳转，不要手动关闭浏览器')
        tip_label.setStyleSheet("color: #E67E22; font-size: 12px; padding: 8px 0;")
        page_layout.addWidget(tip_label)
        
        # 进度状态
        self.oauth_progress_label = QLabel('准备就绪')
        self.oauth_progress_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; font-size: 14px; font-weight: 500;")
        page_layout.addWidget(self.oauth_progress_label)
        
        # 结果区域
        result_title = QLabel('授权结果:')
        result_title.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; font-size: 14px; font-weight: 500;")
        page_layout.addWidget(result_title)
        
        self.oauth_result_text = QTextEdit()
        self.oauth_result_text.setReadOnly(True)
        self.oauth_result_text.setMaximumHeight(200)
        if is_dark:
            self.oauth_result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    background: #161b22;
                    color: #c9d1d9;
                    font-size: 12px;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    padding: 12px;
                }
            """)
        else:
            self.oauth_result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background: #FAFAFA;
                    color: #1A1A1A;
                    font-size: 12px;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    padding: 12px;
                }
            """)
        page_layout.addWidget(self.oauth_result_text)
        
        # 按钮区域
        btn_row = QHBoxLayout()
        
        self.oauth_btn_start = FluentButton('开始授权', 'primary', is_dark=is_dark)
        self.oauth_btn_start.clicked.connect(self._start_oauth)
        btn_row.addWidget(self.oauth_btn_start)
        
        self.oauth_btn_stop = FluentButton('停止', 'default', is_dark=is_dark)
        self.oauth_btn_stop.clicked.connect(self._stop_oauth)
        self.oauth_btn_stop.setEnabled(False)
        btn_row.addWidget(self.oauth_btn_stop)
        
        btn_row.addStretch()
        page_layout.addLayout(btn_row)
        
        page_layout.addStretch()
        
        # 初始化状态
        self.oauth_is_processing = False
        self.oauth_thread = None
        self.oauth_success_count = 0
        
        self.oauth_page.hide()
    
    def _start_oauth(self):
        """开始手动授权"""
        from ui.dialogs import ManualOAuth2Thread
        
        if self.oauth_is_processing:
            return
        
        self.oauth_is_processing = True
        self.oauth_btn_start.setEnabled(False)
        self.oauth_btn_stop.setEnabled(True)
        
        self.oauth_progress_label.setText('正在打开浏览器...')
        
        group = self.oauth_group_combo.currentText()
        self.oauth_thread = ManualOAuth2Thread(self.db, group)
        self.oauth_thread.progress.connect(self._on_oauth_progress)
        self.oauth_thread.finished_signal.connect(self._on_oauth_finished)
        self.oauth_thread.start()
    
    def _stop_oauth(self):
        """停止授权"""
        if self.oauth_thread:
            self.oauth_thread.stop()
        self.oauth_is_processing = False
        self.oauth_btn_start.setEnabled(True)
        self.oauth_btn_stop.setEnabled(False)
        self.oauth_progress_label.setText('已停止')
    
    def _on_oauth_progress(self, message):
        """授权进度更新"""
        self.oauth_progress_label.setText(message)
    
    def _on_oauth_finished(self, email, client_id, refresh_token, error):
        """授权完成"""
        self.oauth_is_processing = False
        self.oauth_btn_start.setEnabled(True)
        self.oauth_btn_stop.setEnabled(False)
        
        if error:
            self.oauth_progress_label.setText('授权失败')
            self.oauth_result_text.append(f'❌ 失败: {error}')
        else:
            self.oauth_progress_label.setText('授权成功!')
            self.oauth_result_text.append(f'✅ {email} - 授权成功，已添加到数据库')
            self.oauth_success_count += 1
            # 刷新账号列表
            self.load_accounts()
            self.sidebar.load_groups()
    
    def _update_oauth_page_theme(self):
        """更新手动授权页面主题"""
        if not hasattr(self, 'oauth_page'):
            return
        
        is_dark = self.theme_manager.is_dark()
        
        if is_dark:
            self.oauth_page.setStyleSheet("background: #0d1117; border: none;")
            self.oauth_result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    background: #161b22;
                    color: #c9d1d9;
                    font-size: 12px;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    padding: 12px;
                }
            """)
        else:
            self.oauth_page.setStyleSheet("background: #FFFFFF; border: none;")
            self.oauth_result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background: #FAFAFA;
                    color: #1A1A1A;
                    font-size: 12px;
                    font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                    padding: 12px;
                }
            """)
        
        self.oauth_group_combo.setStyleSheet(self.theme_manager.get_theme()['combo'])
        self.oauth_progress_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; font-size: 14px; font-weight: 500;")
        self.oauth_btn_start.set_dark_mode(is_dark)
        self.oauth_btn_stop.set_dark_mode(is_dark)
    
    def on_batch_oauth2_completed(self, success_count, fail_count):
        """批量 OAuth2 授权完成"""
        self.load_accounts()
        self.sidebar.load_groups()
    
    def on_oauth2_completed(self, email, client_id, refresh_token):
        """OAuth2 授权完成，导入账号"""
        if not email or not refresh_token:
            return
        
        # 检查账号是否已存在
        existing = self.db.get_account_by_email(email)
        if existing:
            # 更新现有账号的 token
            reply = QMessageBox.question(
                self, '账号已存在',
                f'账号 {email} 已存在，是否更新其 OAuth2 凭据？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db.update_account_oauth(existing[0], client_id, refresh_token)
                QMessageBox.information(self, '成功', f'已更新账号 {email} 的 OAuth2 凭据')
                self.load_accounts()
        else:
            # 添加新账号
            self.db.add_account(
                email=email,
                password='',  # OAuth2 不需要密码
                group_name='默认分组',
                account_type='outlook',
                client_id=client_id,
                refresh_token=refresh_token
            )
            QMessageBox.information(self, '成功', f'已添加账号 {email}')
            self.load_accounts()
            self.sidebar.load_groups()

    def filter_accounts(self, text):
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 2)  # 邮箱在第2列
            if widget:
                label = widget.findChild(QLabel)
                if label:
                    self.table.setRowHidden(row, text.lower() not in label.text().lower())

    def import_accounts(self):
        # 传递当前分组，如果是"全部"则传None使用默认分组
        default_group = None if self.current_group == '全部' else self.current_group
        dialog = ImportDialog(self.db, self, default_group=default_group)
        if dialog.exec_():
            self.load_accounts()
            self.load_group_filter()
            self.sidebar.load_groups()

    def export_accounts(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self, tr('export_backup'), '', 
            'Excel文件 (*.xlsx);;文本文件 (*.txt)'
        )
        if path:
            accounts = self.db.get_all_accounts()
            
            if path.endswith('.xlsx') or 'xlsx' in selected_filter:
                # 导出为 Excel 格式
                self.export_to_xlsx(path, accounts)
            else:
                # 导出为 TXT 格式（与导入格式一致，用 $ 分隔）
                self.export_to_txt(path, accounts)
            
            QMessageBox.information(self, tr('success'), tr('exported_accounts', len(accounts)))
    
    def export_to_xlsx(self, path, accounts):
        """导出为 Excel 格式"""
        try:
            import openpyxl
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws.title = '邮箱账号'
            
            # 表头 - 添加备注列
            headers = ['邮箱', '密码', '分组', '状态', '类型', 'Client ID', 'Refresh Token', '备注']
            ws.append(headers)
            
            # 数据行
            for acc in accounts:
                row = [
                    acc[1],   # email
                    acc[2],   # password
                    acc[3],   # group_name
                    acc[4],   # status
                    acc[5],   # account_type
                    acc[10] if len(acc) > 10 else '',  # client_id
                    acc[11] if len(acc) > 11 else '',  # refresh_token
                    acc[15] if len(acc) > 15 and acc[15] else '',  # remark
                ]
                ws.append(row)
            
            # 调整列宽
            ws.column_dimensions['A'].width = 35
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 10
            ws.column_dimensions['E'].width = 10
            ws.column_dimensions['F'].width = 40
            ws.column_dimensions['G'].width = 50
            ws.column_dimensions['H'].width = 30  # 备注列
            
            wb.save(path)
        except ImportError:
            # 如果没有 openpyxl，提示用户
            QMessageBox.warning(self, tr('warning'), '需要安装 openpyxl 库才能导出 Excel 格式\n请运行: pip install openpyxl')
    
    def export_to_txt(self, path, accounts):
        """导出为 TXT 格式（与导入格式一致）
        格式：邮箱----密码----client_id----refresh_token$邮箱----密码----client_id----refresh_token
        """
        with open(path, 'w', encoding='utf-8') as f:
            parts = []
            for acc in accounts:
                email = acc[1]
                password = acc[2]
                client_id = acc[10] if len(acc) > 10 and acc[10] else ''
                refresh_token = acc[11] if len(acc) > 11 and acc[11] else ''
                
                # 构建账号字符串
                if client_id or refresh_token:
                    # OAuth2 账号，包含所有字段
                    part = f'{email}----{password}----{client_id}----{refresh_token}'
                else:
                    # 普通账号，只包含邮箱和密码
                    part = f'{email}----{password}'
                
                parts.append(part)
            
            # 用 $ 分隔多个账号
            f.write('$'.join(parts))
    
    def batch_move_group(self):
        """批量移动分组"""
        selected = self.get_selected_accounts()
        if not selected:
            QMessageBox.warning(self, tr('warning'), tr('please_select_account'))
            return
        
        groups = [g[1] for g in self.db.get_all_groups()]
        
        menu = QMenu(self)
        menu.setStyleSheet(MENU_STYLE)
        
        for group in groups:
            menu.addAction(group)
        
        action = menu.exec_(self.btn_move.mapToGlobal(self.btn_move.rect().bottomLeft()))
        if action:
            target_group = action.text()
            for aid in selected:
                self.db.update_account_group(aid, target_group)
            self.load_accounts()
            self.sidebar.load_groups()
            FluentMessageBox.success(self, tr('success'), tr('moved_to_group', len(selected), target_group))

    def get_selected_accounts(self):
        selected = []
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.isChecked():
                    selected.append(cb.property('account_id'))
        return selected

    def batch_check_status(self):
        # 如果正在检测，点击则停止
        if hasattr(self, 'check_thread') and self.check_thread and self.check_thread.isRunning():
            self.check_thread.stop()
            self.btn_check.setText('停止中...')
            self.btn_check.setEnabled(False)
            return
        
        selected = self.get_selected_accounts()
        accounts = [acc for acc in self.db.get_all_accounts() if acc[0] in selected] if selected \
                   else self.db.get_all_accounts()
        
        if not accounts:
            QMessageBox.warning(self, tr('warning'), tr('no_accounts_to_check'))
            return
        
        self._check_total = len(accounts)
        self.btn_check.setText(f'检测中 0/{self._check_total} (点击停止)')
        
        self.check_thread = StatusCheckThread(accounts, self.db)
        self.check_thread.status_updated.connect(self.on_status_updated)
        self.check_thread.aws_updated.connect(self.on_aws_updated)
        self.check_thread.progress_updated.connect(self.on_check_progress)
        self.check_thread.finished_all.connect(self.on_check_finished)
        self.check_thread.start()
    
    def on_check_progress(self, current, total):
        """更新检测进度"""
        self.btn_check.setText(f'检测中 {current}/{total} (点击停止)')

    def on_status_updated(self, account_id, status):
        """状态更新回调"""
        is_dark = self.theme_manager.is_dark()
        success_color = '#3fb950' if is_dark else '#107C10'
        danger_color = '#f85149' if is_dark else '#D13438'
        
        # 1. 更新表格（如果存在）
        if hasattr(self, 'table'):
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 0)
                if widget:
                    cb = widget.findChild(QCheckBox)
                    if cb and cb.property('account_id') == account_id:
                        # 更新状态徽章 (列5)
                        status_widget = self.table.cellWidget(row, 5)
                        if status_widget:
                            # 重新创建 badge (或者如有引用直接更新，这里简化直接重新load_accounts的逻辑太重，
                            # 所以我们只更新文字和样式，但之前使用的是 setCellWidget 里的 QLabel)
                            # 查找 QLabel
                            badge = status_widget.findChild(QLabel)
                            if badge:
                                badge.setText(status)
                                # 更新样式
                                badge_style_key = 'badge_info'
                                if status == '正常':
                                    badge_style_key = 'badge_success'
                                elif status in ['异常', '封禁', '失败']:
                                    badge_style_key = 'badge_error'
                                elif status in ['验证中', '验证']:
                                    badge_style_key = 'badge_warning'
                                badge.setStyleSheet(self.theme_manager.get_theme().get(badge_style_key, ''))
                        break
        
        # 2. 如果仪表盘可见，实时更新仪表盘数据
        if hasattr(self, 'dashboard_page') and self.dashboard_page.isVisible():
            self.refresh_dashboard_realtime()

    def refresh_dashboard_realtime(self):
        """实时刷新仪表盘数据 (不重建页面)"""
        # 获取最新统计数据
        total = self.db.get_account_count()
        accounts = self.db.get_all_accounts()
        normal_count = sum(1 for acc in accounts if acc[4] == '正常')
        error_count = sum(1 for acc in accounts if acc[4] == '异常')
        unchecked_count = sum(1 for acc in accounts if acc[4] not in ['正常', '异常'])
        
        # 更新卡片数值
        if hasattr(self, 'dashboard_stat_labels') and len(self.dashboard_stat_labels) >= 4:
            self.dashboard_stat_labels[0].setText(str(total))
            self.dashboard_stat_labels[1].setText(str(normal_count))
            self.dashboard_stat_labels[2].setText(str(error_count))
            self.dashboard_stat_labels[3].setText(str(unchecked_count))
            
        # 更新图表数据
        group_data = self._get_group_data()
        status_data = self._get_status_data()
        
        is_dark = self.theme_manager.is_dark()
        # 饼图颜色
        if is_dark:
            colors = ['#58a6ff', '#3fb950', '#f85149', '#d29922', '#a371f7', '#39c5cf', '#ff7b72', '#79c0ff']
        else:
            colors = ['#0078D4', '#107C10', '#D13438', '#FFB900', '#8764B8', '#00B7C3', '#E74856', '#0099BC']

        # 更新分组图表
        if hasattr(self, 'group_pie_chart'):
            self.group_pie_chart.data = group_data
            self.group_pie_chart.update() # 重绘
        if hasattr(self, 'group_legend_layout'):
            self._update_legend(self.group_legend_layout, group_data, colors)
            
        # 更新状态图表
        if hasattr(self, 'status_pie_chart'):
            self.status_pie_chart.data = status_data
            self.status_pie_chart.update() # 重绘
        if hasattr(self, 'status_legend_layout'):
            self._update_legend(self.status_legend_layout, status_data, colors)

    
    def on_aws_updated(self, account_id, has_aws):
        """更新 AWS 标记列"""
        is_dark = self.theme_manager.is_dark()
        success_color = '#3fb950' if is_dark else '#107C10'
        muted_color = '#6e7681' if is_dark else '#999999'
        
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 0)
            if widget:
                cb = widget.findChild(QCheckBox)
                if cb and cb.property('account_id') == account_id:
                    aws_item = self.table.item(row, 7)
                    if aws_item:
                        aws_item.setText(tr('has_aws_code') if has_aws else tr('no_aws_code'))
                        if has_aws:
                            aws_item.setForeground(QColor(success_color))
                        else:
                            aws_item.setForeground(QColor(muted_color))
                    break

    def on_check_finished(self):
        self.btn_check.setEnabled(True)
        self.btn_check.setText(tr('batch_check'))
        FluentMessageBox.success(self, tr('success'), tr('check_complete'))

    def batch_delete(self):
        selected = self.get_selected_accounts()
        if not selected:
            FluentMessageBox.warning(self, tr('warning'), tr('please_select_account'))
            return
        
        if FluentMessageBox.question(self, tr('confirm'), tr('confirm_delete', len(selected))):
            for aid in selected:
                self.db.delete_account(aid)
            self.load_accounts()
    
    def batch_send_email(self):
        """批量发送邮件"""
        selected = self.get_selected_accounts()
        if not selected:
            FluentMessageBox.warning(self, tr('warning'), tr('please_select_send_account'))
            return
        
        # 获取选中的账号信息
        accounts = [acc for acc in self.db.get_all_accounts() if acc[0] in selected]
        
        dialog = BatchSendDialog(accounts, self)
        dialog.exec_()

    def view_emails(self):
        btn = self.sender()
        account_id = btn.property('account_id')
        for acc in self.db.get_all_accounts():
            if acc[0] == account_id:
                dialog = EmailViewDialog(acc, self.db, self)
                dialog.exec_()
                # 关闭对话框后刷新列表（更新 AWS 标记）
                self.load_accounts()
                break

    def delete_single_account(self, account_id=None):
        """删除单个账号"""
        try:
            # 如果没有传入 account_id，从按钮属性获取
            if account_id is None:
                btn = self.sender()
                if btn:
                    account_id = btn.property('account_id')
            
            if not account_id:
                return
            
            if FluentMessageBox.question(self, tr('confirm'), tr('confirm_delete_single')):
                self.db.delete_account(account_id)
                self.load_accounts()
                self.sidebar.load_groups()  # 刷新侧边栏分组计数
        except Exception as e:
            FluentMessageBox.error(self, '错误', f'删除账号时出错: {str(e)}')
    
    def show_more_menu(self):
        """显示更多操作菜单"""
        btn = self.sender()
        row = btn.property('row')
        
        menu = QMenu(self)
        
        # 根据当前主题选择样式
        is_dark = self.theme_manager.is_dark()
        menu.setStyleSheet(MENU_STYLE_DARK if is_dark else MENU_STYLE_LIGHT)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50 if is_dark else 30))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        action_check_this = menu.addAction(tr('check_this_row'))
        action_check_from = menu.addAction(tr('check_from_row'))
        menu.addSeparator()
        action_check_all = menu.addAction(tr('check_all'))
        action_uncheck_all = menu.addAction(tr('uncheck_all'))
        
        action = menu.exec_(btn.mapToGlobal(btn.rect().bottomLeft()))
        
        if action == action_check_this:
            self.check_row(row)
        elif action == action_check_from:
            self.check_from_row(row)
        elif action == action_check_all:
            self.check_all_rows()
        elif action == action_uncheck_all:
            self.uncheck_all_rows()
    
    def get_row_checkbox(self, row):
        """获取指定行的复选框"""
        widget = self.table.cellWidget(row, 0)
        return widget.findChild(QCheckBox) if widget else None
    
    def set_rows_checked(self, rows, checked=True):
        """设置多行的勾选状态"""
        for row in rows:
            cb = self.get_row_checkbox(row)
            if cb:
                cb.setChecked(checked)
    
    def check_row(self, row):
        """勾选指定行"""
        self.set_rows_checked([row], True)
    
    def check_from_row(self, start_row):
        """从指定行开始勾选N个"""
        from PyQt5.QtWidgets import QInputDialog
        total = self.table.rowCount() - start_row
        n, ok = QInputDialog.getInt(self, tr('check_count_title'), tr('check_count_msg', start_row + 1, total), 
                                    value=min(10, total), min=1, max=total)
        if ok:
            self.set_rows_checked(range(start_row, min(start_row + n, self.table.rowCount())), True)
    
    def check_all_rows(self):
        """勾选全部"""
        self.set_rows_checked(range(self.table.rowCount()), True)
    
    def uncheck_all_rows(self):
        """取消全部勾选"""
        self.set_rows_checked(range(self.table.rowCount()), False)
    
    def copy_text(self):
        """复制文本到剪贴板"""
        btn = self.sender()
        text = btn.property('copy_text')
        if text:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            self.show_toast(tr('copied'))
    
    def toggle_password(self):
        """切换密码显示/隐藏"""
        btn = self.sender()
        pwd_label = btn.property('pwd_label')
        if pwd_label:
            is_hidden = pwd_label.property('is_hidden')
            real_password = pwd_label.property('real_password')
            if is_hidden:
                pwd_label.setText(real_password)
                pwd_label.setProperty('is_hidden', False)
                btn.setText(tr('hide'))
            else:
                pwd_label.setText('••••••••')
                pwd_label.setProperty('is_hidden', True)
                btn.setText(tr('show'))
    
    def show_toast(self, message):
        """显示简短提示"""
        from PyQt5.QtWidgets import QToolTip
        from PyQt5.QtCore import QPoint
        QToolTip.showText(self.mapToGlobal(QPoint(self.width()//2, 50)), message, self, self.rect(), 1500)
    
    def resizeEvent(self, event):
        """窗口大小改变时按比例调整列宽"""
        super().resizeEvent(event)
        self.adjust_column_widths()
    
    def showEvent(self, event):
        """窗口显示时调整列宽"""
        super().showEvent(event)
        self.adjust_column_widths()
    
    def adjust_column_widths(self):
        """按比例调整列宽 (邮箱:密码:分组:状态:类型:操作)"""
        # 计算可用宽度（减去复选框、序号列、AWS列和滚动条）
        available = self.table.viewport().width() - 44 - 50 - 60 - 20
        if available <= 0:
            return
        
        # 比例 3.5:2:1.2:1:1:1.5 = 10.2份
        unit = available / 10.2
        
        self.table.setColumnWidth(2, int(unit * 3.5))   # 邮箱 3.5份
        self.table.setColumnWidth(3, int(unit * 2))     # 密码 2份
        self.table.setColumnWidth(4, int(unit * 1.2))   # 分组 1.2份
        self.table.setColumnWidth(5, int(unit * 1))     # 状态 1份
        self.table.setColumnWidth(6, int(unit * 1))     # 类型 1份
        self.table.setColumnWidth(8, int(unit * 1.5))   # 操作 1.5份

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+A - 全选
        QShortcut(QKeySequence('Ctrl+A'), self, self.check_all_rows)
        
        # Delete - 删除选中
        QShortcut(QKeySequence('Delete'), self, self.on_delete_shortcut)
        
        # Escape - 取消选择
        QShortcut(QKeySequence('Escape'), self, self.uncheck_all_rows)
        
        # Ctrl+F - 聚焦搜索框
        QShortcut(QKeySequence('Ctrl+F'), self, self.focus_search)
        
        # Ctrl+N - 导入
        QShortcut(QKeySequence('Ctrl+N'), self, self.import_accounts)
        
        # Ctrl+Shift+V - 从剪贴板快捷导入
        QShortcut(QKeySequence('Ctrl+Shift+V'), self, self.quick_import_from_clipboard)
    
    def quick_import_from_clipboard(self):
        """从剪贴板快捷导入账号"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text or not text.strip():
            self.show_toast('剪贴板为空')
            return
        
        # 检查是否包含邮箱格式
        if '@' not in text or '----' not in text:
            self.show_toast('剪贴板内容格式不正确')
            return
        
        # 打开导入对话框并预填充剪贴板内容
        dialog = ImportDialog(self.db, self, 
                              default_group=None if self.current_group == '全部' else self.current_group)
        dialog.text_edit.setText(text)
        
        if dialog.exec_():
            self.load_accounts()
            self.load_group_filter()
            self.sidebar.load_groups()
    
    def on_delete_shortcut(self):
        """Delete 快捷键处理"""
        selected = self.get_selected_accounts()
        if selected:
            self.batch_delete()
    
    def focus_search(self):
        """聚焦搜索框"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def toggle_theme(self):
        """切换主题"""
        theme = self.theme_manager.toggle_theme()
        self.apply_theme(theme)
    
    def set_theme(self, theme_name):
        """设置指定主题（由侧边栏调用）"""
        if theme_name == 'light' and self.theme_manager.is_dark():
            self.toggle_theme()
        elif theme_name == 'dark' and not self.theme_manager.is_dark():
            self.toggle_theme()
    
    def refresh_language(self):
        """刷新界面语言 - 立即生效"""
        # 保存语言设置到数据库
        from core.i18n import get_language
        self.db.set_setting('language', get_language())
        
        # 更新窗口标题
        self.setWindowTitle(tr('app_title'))
        
        # 更新标题区
        self.title_label.setText(tr('email_management'))
        self.subtitle_label.setText(tr('manage_all_accounts'))
        self.stats_text.setText(tr('current_group'))
        
        # 更新按钮文本
        self.btn_sort.setText(tr('sort_by'))
        self.btn_import.setText(tr('import_email'))
        self.btn_export.setText(tr('export_backup'))
        self.btn_move.setText(tr('move_group'))
        self.btn_send.setText(tr('batch_send'))
        self.btn_check.setText(tr('batch_check'))
        self.btn_delete.setText(tr('batch_delete'))
        
        # 更新搜索框占位符
        self.search_input.setPlaceholderText('🔍 ' + tr('search_email'))
        
        # 更新表格表头
        self.table.setHorizontalHeaderLabels([
            tr('col_checkbox'), tr('col_index'), tr('col_email'), tr('col_password'),
            tr('col_group'), tr('col_status'), tr('col_type'), tr('col_aws'), 
            tr('col_operation')
        ])
        
        # 更新分组筛选
        self.load_group_filter()
        
        # 重新加载账号列表以更新所有文本
        self.load_accounts()
        
        # 更新侧边栏语言
        self.sidebar.refresh_language()
        
        # 同步更新设置页面的语言下拉框（如果存在）
        if hasattr(self, 'settings_lang_combo'):
            current_lang = get_language()
            self.settings_lang_combo.blockSignals(True)
            for i in range(self.settings_lang_combo.count()):
                if self.settings_lang_combo.itemData(i) == current_lang:
                    self.settings_lang_combo.setCurrentIndex(i)
                    break
            self.settings_lang_combo.blockSignals(False)
        
        # 如果设置页面可见，刷新设置页面文本
        if hasattr(self, 'settings_page') and self.settings_page.isVisible():
            self.refresh_settings_page_text()
    
    def refresh_font_size(self, font_size):
        """刷新界面字体大小 - 立即生效"""
        self.font_size = font_size
        # 重新应用全局样式（包含字体大小）
        self._apply_global_style()
    
    def apply_theme(self, theme):
        """应用主题到界面"""
        is_dark = self.theme_manager.is_dark()
        
        # 更新全局样式（包括复选框、滚动条、工具提示等）
        self._apply_global_style()
        
        # 更新内容区背景
        self._apply_content_style()
        
        # 更新侧边栏
        self.sidebar.apply_theme(is_dark)
        
        # 更新标题颜色
        self.title_label.setStyleSheet(f"font-size: 28px; font-weight: 600; color: {theme['colors']['text']};")
        self.subtitle_label.setStyleSheet(f"font-size: 14px; color: {theme['colors']['text_secondary']}; margin-top: 4px;")
        
        # 更新统计卡片颜色
        self.stats_count.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {theme['colors']['accent']};")
        self.stats_text.setStyleSheet(f"font-size: 11px; color: {theme['colors']['text_secondary']};")
        
        # 更新搜索框样式
        self.search_input.setStyleSheet(theme['input'])
        
        # 更新分组筛选样式
        self.group_filter.setStyleSheet(theme['combo'])
        
        # 更新表格样式
        self.table.setStyleSheet(theme['table'])
        
        # 更新所有按钮
        for btn in [self.btn_sort, self.btn_import, self.btn_export, self.btn_move,
                    self.btn_send, self.btn_check, self.btn_delete]:
            btn.set_dark_mode(is_dark)
        
        # 更新卡片
        self.stats_card.set_dark_mode(is_dark)
        self.toolbar.set_dark_mode(is_dark)
        self.table_card.set_dark_mode(is_dark)
        
        # 更新设置页面（如果存在）
        if hasattr(self, 'settings_page'):
            self._update_settings_page_theme()
        
        # 更新仪表盘页面（如果存在）
        self._update_dashboard_theme()
        
        # 更新表格底部
        self._apply_table_bottom_style()
        self._apply_drag_hint_style()
        self._apply_page_info_style()
        
        # 刷新表格数据以应用新颜色
        self.load_accounts()
    
    def open_stats_dialog(self):
        """显示仪表盘页面 - 在右侧内容区显示"""
        self.show_dashboard_page()
    
    def show_dashboard_page(self):
        """显示仪表盘页面"""
        from core.i18n import tr
        
        # 如果仪表盘页面不存在，创建它
        if not hasattr(self, 'dashboard_page'):
            self.create_dashboard_page()
        else:
            # 更新数据
            self._update_dashboard_data()
        
        # 隐藏工具栏、表格卡片和标题区右侧按钮
        self.toolbar.hide()
        self.table_card.hide()
        self.header_buttons.hide()
        if hasattr(self, 'settings_page'):
            self.settings_page.hide()
        if hasattr(self, 'oauth_page'):
            self.oauth_page.hide()
        self.dashboard_page.show()
        
        # 更新标题
        self.title_label.setText(tr('dashboard'))
        self.subtitle_label.setText(tr('dashboard_desc'))
    
    def hide_dashboard_page(self):
        """隐藏仪表盘页面"""
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.hide()
    
    def create_dashboard_page(self):
        """创建仪表盘页面 - 精美设计"""
        from core.i18n import tr
        from ui.dialogs import PieChartWidget
        
        is_dark = self.theme_manager.is_dark()
        self.dashboard_page = QWidget()
        
        # 设置无边框背景
        if is_dark:
            self.dashboard_page.setStyleSheet("background: #0d1117; border: none;")
        else:
            self.dashboard_page.setStyleSheet("background: #FFFFFF; border: none;")
        
        # 添加到内容区布局
        content_layout = self.content.layout()
        content_layout.addWidget(self.dashboard_page)
        
        page_layout = QVBoxLayout(self.dashboard_page)
        page_layout.setContentsMargins(32, 32, 32, 32)
        page_layout.setSpacing(24)
        
        # 顶部统计卡片区域
        self._create_stats_cards(page_layout)
        
        # 图表区域
        self._create_charts_section(page_layout)
        
        page_layout.addStretch()
        
        # 初始隐藏
        self.dashboard_page.hide()
    
    def _create_stats_cards(self, parent_layout):
        """创建顶部统计卡片"""
        is_dark = self.theme_manager.is_dark()
        
        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(16)
        
        # 获取统计数据
        total = self.db.get_account_count()
        accounts = self.db.get_all_accounts()
        normal_count = sum(1 for acc in accounts if acc[4] == '正常')
        error_count = sum(1 for acc in accounts if acc[4] == '异常')
        unchecked_count = sum(1 for acc in accounts if acc[4] not in ['正常', '异常'])
        
        # 创建统计卡片
        cards_data = [
            ('📊', '总账号数', str(total), '#0078D4' if not is_dark else '#58a6ff'),
            ('✅', '正常账号', str(normal_count), '#107C10' if not is_dark else '#3fb950'),
            ('⚠️', '异常账号', str(error_count), '#D13438' if not is_dark else '#f85149'),
            ('❓', '未检测', str(unchecked_count), '#FFB900' if not is_dark else '#d29922'),
        ]
        
        self.dashboard_stat_labels = []
        
        for icon, title, value, color in cards_data:
            card = self._create_stat_card(icon, title, value, color)
            cards_layout.addWidget(card)
            
        cards_layout.addStretch()
        parent_layout.addWidget(cards_widget)
    
    def _create_stat_card(self, icon, title, value, color):
        """创建单个统计卡片"""
        is_dark = self.theme_manager.is_dark()
        
        card = QFrame()
        card.setFixedSize(160, 100)
        
        if is_dark:
            card.setStyleSheet(f"""
                QFrame {{
                    background: #161b22;
                    border: none;
                    border-radius: 12px;
                }}
            """)
        else:
            card.setStyleSheet(f"""
                QFrame {{
                    background: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                }}
            """)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 20 if not is_dark else 40))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # 图标和标题行
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px; background: transparent;")
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_color = '#8b949e' if is_dark else '#616161'
        title_label.setStyleSheet(f"font-size: 12px; color: {title_color}; background: transparent;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        layout.addStretch()
        
        # 数值
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: 600; color: {color}; background: transparent;")
        layout.addWidget(value_label)
        
        # 保存引用以便更新
        self.dashboard_stat_labels.append(value_label)
        
        return card
    
    def _create_charts_section(self, parent_layout):
        """创建图表区域"""
        from ui.dialogs import PieChartWidget
        
        is_dark = self.theme_manager.is_dark()
        
        # 图表容器
        charts_widget = QWidget()
        charts_widget.setStyleSheet("background: transparent;")
        charts_layout = QHBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(24)
        
        # 分组分布图表
        group_data = self._get_group_data()
        self.group_chart_panel = self._create_chart_panel('分组分布', group_data)
        charts_layout.addWidget(self.group_chart_panel)
        
        # 状态分布图表
        status_data = self._get_status_data()
        self.status_chart_panel = self._create_chart_panel('状态分布', status_data)
        charts_layout.addWidget(self.status_chart_panel)
        
        charts_layout.addStretch()
        parent_layout.addWidget(charts_widget)
    
    def _create_chart_panel(self, title, data):
        """创建图表面板"""
        from ui.dialogs import PieChartWidget
        
        is_dark = self.theme_manager.is_dark()
        
        # 饼图颜色
        if is_dark:
            colors = ['#58a6ff', '#3fb950', '#f85149', '#d29922', '#a371f7', '#39c5cf', '#ff7b72', '#79c0ff']
        else:
            colors = ['#0078D4', '#107C10', '#D13438', '#FFB900', '#8764B8', '#00B7C3', '#E74856', '#0099BC']
        
        panel = QFrame()
        panel.setFixedSize(320, 360)
        
        if is_dark:
            panel.setStyleSheet("""
                QFrame {
                    background: #161b22;
                    border: none;
                    border-radius: 16px;
                }
            """)
        else:
            panel.setStyleSheet("""
                QFrame {
                    background: #FFFFFF;
                    border: none;
                    border-radius: 16px;
                }
            """)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15 if not is_dark else 30))
        shadow.setOffset(0, 4)
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel(title)
        title_color = '#c9d1d9' if is_dark else '#1A1A1A'
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {title_color}; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 饼图
        pie_widget = PieChartWidget(data, colors)
        pie_widget.setFixedSize(160, 160)
        layout.addWidget(pie_widget, 0, Qt.AlignCenter)
        
        # 保存饼图引用以便更新
        if title == '分组分布':
            self.group_pie_chart = pie_widget
            self.group_legend_layout = None # 将在下面初始化
        else:
            self.status_pie_chart = pie_widget
            self.status_legend_layout = None
            
        # 图例容器
        legend_widget = QWidget()
        legend_widget.setStyleSheet("background: transparent;")
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(0, 8, 0, 0)
        legend_layout.setSpacing(6)
        
        # 保存图例布局引用
        if title == '分组分布':
            self.group_legend_layout = legend_layout
        else:
            self.status_legend_layout = legend_layout
        
        # 初始化图例
        self._update_legend(legend_layout, data, colors)
        
        layout.addWidget(legend_widget)
        layout.addStretch()
        
        return panel

    def _update_legend(self, layout, data, colors):
        """更新图例内容"""
        # 清除旧内容
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        is_dark = self.theme_manager.is_dark()
        total = sum(data.values()) if data else 1
        
        for i, (name, count) in enumerate(data.items()):
            color = colors[i % len(colors)]
            percent = count / total * 100 if total > 0 else 0
            
            item_widget = QWidget()
            item_widget.setStyleSheet("background: transparent;")
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(8)
            
            # 颜色块
            color_block = QLabel()
            color_block.setFixedSize(10, 10)
            color_block.setStyleSheet(f"background: {color}; border-radius: 2px;")
            item_layout.addWidget(color_block)
            
            # 名称
            name_label = QLabel(name)
            name_color = '#c9d1d9' if is_dark else '#1A1A1A'
            name_label.setStyleSheet(f"color: {name_color}; font-size: 12px; background: transparent;")
            item_layout.addWidget(name_label)
            
            item_layout.addStretch()
            
            # 数量和百分比
            value_label = QLabel(f'{count} ({percent:.1f}%)')
            value_color = '#8b949e' if is_dark else '#616161'
            value_label.setStyleSheet(f"color: {value_color}; font-size: 12px; background: transparent;")
            item_layout.addWidget(value_label)
            
            layout.addWidget(item_widget)
    
    def _get_group_data(self):
        """获取分组统计数据"""
        groups = self.db.get_all_groups()
        data = {}
        for group in groups:
            count = len(self.db.get_accounts_by_group(group[1]))
            if count > 0:
                data[group[1]] = count
        return data
    
    def _get_status_data(self):
        """获取状态统计数据"""
        accounts = self.db.get_all_accounts()
        data = {'正常': 0, '异常': 0, '未检测': 0}
        for acc in accounts:
            status = acc[4]
            if status in data:
                data[status] += 1
            else:
                data['未检测'] += 1
        return {k: v for k, v in data.items() if v > 0}
    
    def _update_dashboard_data(self):
        """更新仪表盘数据"""
        # 重新创建仪表盘页面以更新数据
        if hasattr(self, 'dashboard_page'):
            self.dashboard_page.deleteLater()
            delattr(self, 'dashboard_page')
        self.create_dashboard_page()
        self.dashboard_page.show()
    
    def _update_dashboard_theme(self):
        """更新仪表盘主题"""
        if hasattr(self, 'dashboard_page'):
            # 重新创建以应用新主题
            was_visible = self.dashboard_page.isVisible()
            self.dashboard_page.deleteLater()
            delattr(self, 'dashboard_page')
            if was_visible:
                self.create_dashboard_page()
                self.dashboard_page.show()

    def closeEvent(self, event):
        """关闭事件 - 直接退出程序"""
        # 隐藏托盘图标
        if self.tray_manager and self.tray_manager.tray_icon:
            self.tray_manager.tray_icon.hide()
        event.accept()

    def show_table_context_menu(self, pos):
        """显示表格右键菜单"""
        # 使用 rowAt 而不是 itemAt，这样即使点击的是包含 widget 的单元格也能正常工作
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        
        # 获取账号信息
        group_item = self.table.item(row, 4)
        if not group_item:
            return
        
        account_id = group_item.data(Qt.UserRole)
        
        # 创建右键菜单
        from PyQt5.QtWidgets import QMenu, QWidgetAction
        menu = QMenu(self)
        
        is_dark = self.theme_manager.is_dark()
        danger_color = '#f85149' if is_dark else '#E53935'
        
        if is_dark:
            menu.setStyleSheet(f"""
                QMenu {{
                    background: #21262d;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 4px;
                }}
                QMenu::item {{
                    padding: 10px 40px 10px 16px;
                    color: #c9d1d9;
                    border-radius: 6px;
                    margin: 2px 6px;
                    font-size: 13px;
                }}
                QMenu::item:selected {{
                    background: #30363d;
                    color: #FFFFFF;
                }}
                QMenu::item[data-danger="true"] {{
                    color: {danger_color};
                }}
                QMenu::separator {{
                    height: 1px;
                    background: #30363d;
                    margin: 6px 16px;
                }}
            """)
        else:
            menu.setStyleSheet(f"""
                QMenu {{
                    background: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 4px;
                }}
                QMenu::item {{
                    padding: 10px 40px 10px 16px;
                    color: #333333;
                    border-radius: 6px;
                    margin: 2px 6px;
                    font-size: 13px;
                }}
                QMenu::item:selected {{
                    background: #F0F0F0;
                    color: #333333;
                }}
                QMenu::separator {{
                    height: 1px;
                    background: #EEEEEE;
                    margin: 6px 16px;
                }}
            """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50 if is_dark else 30))
        shadow.setOffset(0, 6)
        menu.setGraphicsEffect(shadow)
        
        # 详情
        action_detail = menu.addAction('⊙  详情')
        action_detail.triggered.connect(lambda: self.show_account_detail(account_id))
        
        # 查看邮件
        action_view = menu.addAction('✉  查看邮件')
        action_view.triggered.connect(lambda: self.view_account_emails(account_id))
        
        # 导出信息
        action_export = menu.addAction('📋  导出信息')
        action_export.triggered.connect(lambda: self.export_single_account(account_id))
        
        menu.addSeparator()
        
        # 删除 - 使用自定义 widget 实现红色
        delete_widget = QWidget()
        delete_widget.setStyleSheet("background: transparent;")
        delete_layout = QHBoxLayout(delete_widget)
        delete_layout.setContentsMargins(16, 10, 40, 10)
        delete_label = QLabel(f'<span style="color:{danger_color};">🗑  删除</span>')
        delete_label.setStyleSheet(f"color: {danger_color}; font-size: 13px; background: transparent;")
        delete_layout.addWidget(delete_label)
        
        delete_action = QWidgetAction(menu)
        delete_action.setDefaultWidget(delete_widget)
        
        # 保存 account_id 到局部变量，避免闭包问题
        delete_account_id = account_id
        
        def do_delete():
            menu.close()
            self.delete_single_account(delete_account_id)
        
        delete_action.triggered.connect(do_delete)
        
        # 让 widget 可点击
        delete_widget.mousePressEvent = lambda e: do_delete()
        delete_widget.setCursor(Qt.PointingHandCursor)
        
        menu.addAction(delete_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(pos))
    
    def show_account_detail(self, account_id):
        """显示账号详情对话框"""
        # 获取账号信息
        accounts = self.db.get_all_accounts()
        account = None
        for acc in accounts:
            if acc[0] == account_id:
                account = acc
                break
        
        if not account:
            QMessageBox.warning(self, '错误', '账号不存在')
            return
        
        # 创建详情对话框
        dialog = AccountDetailDialog(account, self.theme_manager, self)
        dialog.exec_()
    
    def export_single_account(self, account_id):
        """导出单个账号信息到剪贴板"""
        # 获取账号信息
        accounts = self.db.get_all_accounts()
        account = None
        for acc in accounts:
            if acc[0] == account_id:
                account = acc
                break
        
        if not account:
            QMessageBox.warning(self, '错误', '账号不存在')
            return
        
        # 格式：邮箱地址----邮箱密码----client_id----refresh_token
        email = account[1] if len(account) > 1 else ''
        password = account[2] if len(account) > 2 else ''
        client_id = account[10] if len(account) > 10 and account[10] else ''
        refresh_token = account[11] if len(account) > 11 and account[11] else ''
        
        export_text = f"{email}----{password}----{client_id}----{refresh_token}"
        
        # 复制到剪贴板
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(export_text)
        
        QMessageBox.information(self, '提示', '账号信息已复制到剪贴板')
    
    def view_account_emails(self, account_id):
        """查看账号邮件"""
        accounts = self.db.get_all_accounts()
        account = None
        for acc in accounts:
            if acc[0] == account_id:
                account = acc
                break
        
        if account:
            from ui.dialogs import EmailViewDialog
            dialog = EmailViewDialog(account, self.db, self)
            dialog.exec_()

    def on_cell_double_clicked(self, row, col):
        """双击单元格"""
        if col == 8:  # 备注列
            self.edit_remark(row)
    
    def edit_remark(self, row):
        """编辑备注"""
        item = self.table.item(row, 8)
        if not item:
            return
        
        current_remark = item.text()
        account_id = item.data(Qt.UserRole)
        
        # 创建内联编辑器 - 使用主题感知样式
        editor = QLineEdit(self.table)
        editor.setText(current_remark)
        editor.setProperty('row', row)
        editor.setProperty('account_id', account_id)
        editor.setProperty('original', current_remark)
        
        is_dark = self.theme_manager.is_dark()
        if is_dark:
            editor.setStyleSheet("""
                QLineEdit {
                    padding: 4px 8px;
                    border: 2px solid #58a6ff;
                    border-radius: 4px;
                    background: #0d1117;
                    color: #c9d1d9;
                    font-size: 13px;
                }
            """)
        else:
            editor.setStyleSheet("""
                QLineEdit {
                    padding: 4px 8px;
                    border: 2px solid #0078D4;
                    border-radius: 4px;
                    background: #FFFFFF;
                    color: #1A1A1A;
                    font-size: 13px;
                }
            """)
        
        # 按 Enter 保存，按 Escape 取消
        editor.returnPressed.connect(lambda: self.save_remark(editor))
        editor.installEventFilter(self)
        
        self.table.setCellWidget(row, 8, editor)
        editor.setFocus()
        editor.selectAll()
    
    def save_remark(self, editor):
        """保存备注"""
        row = editor.property('row')
        account_id = editor.property('account_id')
        new_remark = editor.text().strip()
        
        # 保存到数据库
        self.db.update_account_remark(account_id, new_remark)
        
        # 移除编辑器，更新表格显示
        self.table.removeCellWidget(row, 8)
        
        is_dark = self.theme_manager.is_dark()
        text_color = '#8b949e' if is_dark else '#666666'
        
        item = QTableWidgetItem(new_remark)
        item.setForeground(QColor(text_color))
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item.setToolTip('双击编辑备注')
        item.setData(Qt.UserRole, account_id)
        self.table.setItem(row, 8, item)
        
        self.show_toast(tr('remark_saved'))
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理备注编辑器的 Escape 键"""
        from PyQt5.QtCore import QEvent
        if isinstance(obj, QLineEdit) and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                # 取消编辑，恢复原值
                row = obj.property('row')
                account_id = obj.property('account_id')
                original = obj.property('original')
                
                self.table.removeCellWidget(row, 8)
                
                is_dark = self.theme_manager.is_dark()
                text_color = '#8b949e' if is_dark else '#666666'
                
                item = QTableWidgetItem(original)
                item.setForeground(QColor(text_color))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setToolTip('双击编辑备注')
                item.setData(Qt.UserRole, account_id)
                self.table.setItem(row, 8, item)
                return True
        return super().eventFilter(obj, event)
