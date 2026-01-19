# -*- coding: utf-8 -*-
"""
对话框模块 - Microsoft Fluent Design 风格
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QTextBrowser, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QWidget, QFrame, QScrollArea, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from core.email_client import EmailClient
import os


def create_email_client(account, db_manager=None):
    """从账号元组创建 EmailClient 实例
    account: 数据库返回的账号元组 (id, email, password, group, status, type, imap_server, imap_port, smtp_server, smtp_port, client_id, refresh_token, ...)
    db_manager: 数据库管理器，用于自动保存刷新后的 refresh_token
    """
    return EmailClient(
        account[1], account[2],
        account[6], account[7],
        client_id=account[10] if len(account) > 10 else None,
        refresh_token=account[11] if len(account) > 11 else None,
        account_id=account[0],  # 账号ID
        db_manager=db_manager   # 数据库管理器
    )


# 对话框基础样式
DIALOG_STYLE = """
    QDialog {
        background-color: #FFFFFF;
        font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
    }
    QLabel { color: #1A1A1A; font-size: 13px; }
    QLineEdit, QTextEdit {
        padding: 10px 12px;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        background: #FAFAFA;
        font-size: 13px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #0078D4;
        background: #FFFFFF;
    }
    QComboBox {
        padding: 10px 12px;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        background: #FAFAFA;
        font-size: 13px;
        color: #1A1A1A;
    }
    QComboBox:hover { border-color: #B0B0B0; }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #666;
    }
    QComboBox QAbstractItemView {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        selection-background-color: #E5F1FB;
        selection-color: #0078D4;
        outline: none;
    }
    QComboBox QAbstractItemView::item {
        padding: 8px 12px;
        min-height: 32px;
        color: #1A1A1A;
    }
    QComboBox QAbstractItemView::item:hover { background: #F5F5F5; }
"""

BTN_PRIMARY = """
    QPushButton {
        background-color: #0078D4; color: white; border: none;
        padding: 10px 24px; border-radius: 4px; font-size: 14px; font-weight: 500;
    }
    QPushButton:hover { background-color: #1084D9; }
    QPushButton:pressed { background-color: #006CBE; }
"""

BTN_DEFAULT = """
    QPushButton {
        background-color: #FFFFFF; color: #1A1A1A; border: 1px solid #D0D0D0;
        padding: 10px 24px; border-radius: 4px; font-size: 14px;
    }
    QPushButton:hover { background-color: #F5F5F5; }
"""

MENU_STYLE_LIGHT = """
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
        margin: 2px 6px;
        font-size: 13px;
    }
    QMenu::item:selected {
        background: #F0F0F0;
        color: #333333;
    }
    QMenu::separator {
        height: 1px;
        background: #EEEEEE;
        margin: 6px 16px;
    }
"""

MENU_STYLE_DARK = """
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
        margin: 2px 6px;
        font-size: 13px;
    }
    QMenu::item:selected {
        background: #30363d;
        color: #FFFFFF;
    }
    QMenu::separator {
        height: 1px;
        background: #30363d;
        margin: 6px 16px;
    }
"""

# 兼容旧代码
MENU_STYLE = MENU_STYLE_LIGHT


class FluentMessageBox(QDialog):
    """美观的消息提示框 - 圆角设计"""
    
    TYPES = {
        'success': {'icon': '✓', 'color': '#10B981'},
        'warning': {'icon': '!', 'color': '#F59E0B'},
        'error': {'icon': '✕', 'color': '#EF4444'},
        'info': {'icon': 'i', 'color': '#3B82F6'},
        'question': {'icon': '?', 'color': '#8B5CF6'},
    }
    
    def __init__(self, msg_type, title, message, parent=None, show_cancel=False):
        super().__init__(parent)
        self.msg_type = msg_type
        self.show_cancel = show_cancel
        self.result_value = False
        
        self.setWindowTitle(title)
        self.setFixedSize(300, 180 if not show_cancel else 190)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui(title, message)
    
    def init_ui(self, title, message):
        config = self.TYPES.get(self.msg_type, self.TYPES['info'])
        
        # 主容器
        container = QFrame(self)
        container.setGeometry(0, 0, 300, self.height())
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background: white;
                border-radius: 12px;
            }
        """)
        
        # 阴影
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 图标
        icon_label = QLabel(config['icon'])
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background: {config['color']};
            color: white;
            font-size: 24px;
            font-weight: bold;
            border-radius: 25px;
        """)
        
        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon_label)
        icon_row.addStretch()
        layout.addLayout(icon_row)
        
        # 标题
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #1F2937; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        # 消息
        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 13px; color: #6B7280; background: transparent; border: none;")
        layout.addWidget(msg_label)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        if self.show_cancel:
            btn_cancel = QPushButton('取消')
            btn_cancel.setFixedSize(80, 32)
            btn_cancel.setCursor(Qt.PointingHandCursor)
            btn_cancel.setStyleSheet("""
                QPushButton {
                    background: #F3F4F6;
                    color: #4B5563;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #E5E7EB; }
            """)
            btn_cancel.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancel)
        
        btn_ok = QPushButton('确定')
        btn_ok.setFixedSize(80 if self.show_cancel else 260, 32)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: {config['color']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        btn_ok.clicked.connect(self.on_accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)
    
    def on_accept(self):
        self.result_value = True
        self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
    
    @staticmethod
    def success(parent, title, message):
        dialog = FluentMessageBox('success', title, message, parent)
        dialog.exec_()
    
    @staticmethod
    def warning(parent, title, message):
        dialog = FluentMessageBox('warning', title, message, parent)
        dialog.exec_()
    
    @staticmethod
    def error(parent, title, message):
        dialog = FluentMessageBox('error', title, message, parent)
        dialog.exec_()
    
    @staticmethod
    def info(parent, title, message):
        dialog = FluentMessageBox('info', title, message, parent)
        dialog.exec_()
    
    @staticmethod
    def question(parent, title, message):
        dialog = FluentMessageBox('question', title, message, parent, show_cancel=True)
        dialog.exec_()
        return dialog.result_value


# 兼容旧代码
SuccessDialog = lambda title, message, parent=None: FluentMessageBox('success', title, message, parent)


class AccountDetailDialog(QDialog):
    """账号详情对话框"""
    
    def __init__(self, account, theme_manager=None, parent=None):
        super().__init__(parent)
        self.account = account
        self.theme_manager = theme_manager
        self.is_dark = theme_manager.is_dark() if theme_manager else False
        
        self.setWindowTitle('账号详情')
        self.setMinimumSize(500, 480)
        self.resize(520, 520)
        self._apply_style()
        self.init_ui()
    
    def _apply_style(self):
        """应用对话框样式"""
        if self.is_dark:
            self.setStyleSheet("""
                QDialog {
                    background: #161b22;
                    font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                }
            """)
        else:
            self.setStyleSheet(DIALOG_STYLE)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题区域
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 邮箱图标和地址
        email_icon = QLabel('📧')
        email_icon.setStyleSheet("font-size: 28px;")
        header_layout.addWidget(email_icon)
        
        email_info = QVBoxLayout()
        email_info.setSpacing(4)
        
        email_label = QLabel(self.account[1])  # 邮箱地址
        email_color = '#c9d1d9' if self.is_dark else '#1A1A1A'
        email_label.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {email_color};")
        email_info.addWidget(email_label)
        
        # 账号类型和状态
        type_status = QLabel(f"{self.account[5]} · {self.account[4]}")
        type_color = '#8b949e' if self.is_dark else '#666666'
        type_status.setStyleSheet(f"font-size: 13px; color: {type_color};")
        email_info.addWidget(type_status)
        
        header_layout.addLayout(email_info)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line_color = '#30363d' if self.is_dark else '#E0E0E0'
        line.setStyleSheet(f"background-color: {line_color};")
        line.setFixedHeight(1)
        layout.addWidget(line)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        if self.is_dark:
            scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        
        # 基本信息区域
        self._add_section(content_layout, '🔐 基本信息', [
            ('邮箱地址', self.account[1]),
            ('密码', self.account[2]),
            ('分组', self.account[3]),
            ('状态', self.account[4]),
            ('类型', self.account[5]),
        ])
        
        # 服务器信息
        imap_server = self.account[6] if len(self.account) > 6 and self.account[6] else '-'
        imap_port = str(self.account[7]) if len(self.account) > 7 and self.account[7] else '-'
        smtp_server = self.account[8] if len(self.account) > 8 and self.account[8] else '-'
        smtp_port = str(self.account[9]) if len(self.account) > 9 and self.account[9] else '-'
        
        self._add_section(content_layout, '🌐 服务器配置', [
            ('IMAP 服务器', imap_server),
            ('IMAP 端口', imap_port),
            ('SMTP 服务器', smtp_server),
            ('SMTP 端口', smtp_port),
        ])
        
        # OAuth2 凭证信息
        client_id = self.account[10] if len(self.account) > 10 and self.account[10] else '-'
        refresh_token = self.account[11] if len(self.account) > 11 and self.account[11] else '-'
        
        # 如果有 OAuth2 信息，显示 Token 区域
        if client_id != '-' or refresh_token != '-':
            self._add_section(content_layout, '🔑 OAuth2 凭证', [
                ('Client ID', client_id),
                ('Refresh Token', refresh_token if len(refresh_token) <= 50 else refresh_token[:50] + '...'),
            ], copyable=True)
        
        # 其他信息
        created_at = str(self.account[12]) if len(self.account) > 12 and self.account[12] else '-'
        last_check = str(self.account[13]) if len(self.account) > 13 and self.account[13] else '-'
        has_aws = '是' if (len(self.account) > 14 and self.account[14]) else '否'
        remark = self.account[15] if len(self.account) > 15 and self.account[15] else '-'
        
        self._add_section(content_layout, '📋 其他信息', [
            ('创建时间', created_at),
            ('最后检测', last_check),
            ('AWS 验证码', has_aws),
            ('备注', remark),
        ])
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # 复制全部按钮
        btn_copy = QPushButton('复制全部信息')
        if self.is_dark:
            btn_copy.setStyleSheet("""
                QPushButton {
                    background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                    padding: 10px 20px; border-radius: 6px; font-size: 13px;
                }
                QPushButton:hover { background: #30363d; }
            """)
        else:
            btn_copy.setStyleSheet(BTN_DEFAULT)
        btn_copy.clicked.connect(self.copy_all_info)
        btn_layout.addWidget(btn_copy)
        
        # 关闭按钮
        btn_close = QPushButton('关闭')
        if self.is_dark:
            btn_close.setStyleSheet("""
                QPushButton {
                    background: #238636; color: white; border: none;
                    padding: 10px 24px; border-radius: 6px; font-size: 13px; font-weight: 500;
                }
                QPushButton:hover { background: #2ea043; }
            """)
        else:
            btn_close.setStyleSheet(BTN_PRIMARY)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _add_section(self, parent_layout, title, items, copyable=False):
        """添加信息区域"""
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(12)
        
        # 标题
        title_label = QLabel(title)
        title_color = '#c9d1d9' if self.is_dark else '#1A1A1A'
        title_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {title_color}; border: none; background: transparent;")
        section_layout.addWidget(title_label)
        
        # 内容卡片
        card = QFrame()
        if self.is_dark:
            card.setStyleSheet("""
                QFrame {
                    background: #0d1117;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                }
                QFrame QLabel {
                    border: none;
                    background: transparent;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame {
                    background: #FAFAFA;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                }
                QFrame QLabel {
                    border: none;
                    background: transparent;
                }
            """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(10)
        
        for label, value in items:
            row = QHBoxLayout()
            
            # 标签
            lbl = QLabel(label)
            lbl_color = '#8b949e' if self.is_dark else '#666666'
            lbl.setStyleSheet(f"color: {lbl_color}; font-size: 13px; min-width: 90px; border: none; background: transparent;")
            row.addWidget(lbl)
            
            # 值
            val = QLabel(str(value) if value else '-')
            val_color = '#c9d1d9' if self.is_dark else '#1A1A1A'
            val.setStyleSheet(f"color: {val_color}; font-size: 13px; border: none; background: transparent;")
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.addWidget(val, 1)
            
            # 复制按钮（可选）
            if copyable and value and value != '-':
                btn_copy = QPushButton('复制')
                btn_copy.setFixedSize(50, 26)
                if self.is_dark:
                    btn_copy.setStyleSheet("""
                        QPushButton {
                            background: #21262d; color: #58a6ff; border: 1px solid #30363d;
                            border-radius: 4px; font-size: 11px;
                        }
                        QPushButton:hover { background: #30363d; }
                    """)
                else:
                    btn_copy.setStyleSheet("""
                        QPushButton {
                            background: #FFFFFF; color: #0078D4; border: 1px solid #D0D0D0;
                            border-radius: 4px; font-size: 11px;
                        }
                        QPushButton:hover { background: #E5F1FB; }
                    """)
                # 获取完整值用于复制
                full_value = self.account[10] if label == 'Client ID' else (
                    self.account[11] if label == 'Refresh Token' else value
                )
                btn_copy.clicked.connect(lambda checked, v=full_value: self._copy_to_clipboard(v))
                row.addWidget(btn_copy)
            
            card_layout.addLayout(row)
        
        section_layout.addWidget(card)
        parent_layout.addWidget(section)
    
    def _copy_to_clipboard(self, text):
        """复制到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(str(text))
        QMessageBox.information(self, '提示', '已复制到剪贴板')
    
    def copy_all_info(self):
        """复制全部信息"""
        info_lines = [
            f"邮箱地址: {self.account[1]}",
            f"密码: {self.account[2]}",
            f"分组: {self.account[3]}",
            f"状态: {self.account[4]}",
            f"类型: {self.account[5]}",
        ]
        
        if len(self.account) > 6 and self.account[6]:
            info_lines.append(f"IMAP服务器: {self.account[6]}")
        if len(self.account) > 7 and self.account[7]:
            info_lines.append(f"IMAP端口: {self.account[7]}")
        if len(self.account) > 10 and self.account[10]:
            info_lines.append(f"Client ID: {self.account[10]}")
        if len(self.account) > 11 and self.account[11]:
            info_lines.append(f"Refresh Token: {self.account[11]}")
        if len(self.account) > 15 and self.account[15]:
            info_lines.append(f"备注: {self.account[15]}")
        
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(info_lines))
        QMessageBox.information(self, '提示', '已复制全部信息到剪贴板')


class ImportDialog(QDialog):
    """导入邮箱对话框"""
    def __init__(self, db, parent=None, default_group=None):
        super().__init__(parent)
        self.db = db
        self.default_group = default_group
        self.setWindowTitle('导入邮箱')
        self.setFixedSize(520, 520)
        self.setStyleSheet(DIALOG_STYLE)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title = QLabel('导入邮箱账号')
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)
        
        info = QLabel('支持格式：每行一个 邮箱----密码，或使用 $ 分隔多个账号')
        info.setStyleSheet("color: #616161; font-size: 13px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('example@outlook.com----password123')
        self.text_edit.setMinimumHeight(180)
        layout.addWidget(self.text_edit)
        
        group_row = QHBoxLayout()
        group_row.addWidget(QLabel('导入到分组:'))
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(160)
        
        # 加载分组并设置默认选中
        current_index = 0
        for i, group in enumerate(self.db.get_all_groups()):
            self.group_combo.addItem(group[1])
            if self.default_group and group[1] == self.default_group:
                current_index = i
        self.group_combo.setCurrentIndex(current_index)
        
        group_row.addWidget(self.group_combo)
        group_row.addStretch()
        
        btn_file = QPushButton('从文件导入')
        btn_file.setStyleSheet(BTN_DEFAULT)
        btn_file.clicked.connect(self.import_from_file)
        group_row.addWidget(btn_file)
        
        btn_clipboard = QPushButton('从剪贴板')
        btn_clipboard.setStyleSheet(BTN_DEFAULT)
        btn_clipboard.clicked.connect(self.import_from_clipboard)
        group_row.addWidget(btn_clipboard)
        layout.addLayout(group_row)
        
        # 去重选项
        option_row = QHBoxLayout()
        self.skip_duplicate_cb = QCheckBox('跳过已存在的邮箱（去重）')
        self.skip_duplicate_cb.setChecked(True)
        self.skip_duplicate_cb.setStyleSheet("color: #616161; font-size: 12px;")
        option_row.addWidget(self.skip_duplicate_cb)
        option_row.addStretch()
        layout.addLayout(option_row)
        
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton('取消')
        btn_cancel.setStyleSheet(BTN_DEFAULT)
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton('导入')
        btn_ok.setStyleSheet(BTN_PRIMARY)
        btn_ok.clicked.connect(self.do_import)
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)
    
    def import_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择文件', '', '文本文件 (*.txt);;所有文件 (*.*)')
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read())
            except Exception as e:
                QMessageBox.warning(self, '错误', f'读取失败: {e}')
    
    def import_from_clipboard(self):
        """从剪贴板导入"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text and text.strip():
            self.text_edit.setText(text)
        else:
            QMessageBox.warning(self, '提示', '剪贴板为空或没有文本内容')
    
    def do_import(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, '错误', '请输入账号信息')
            return
        
        group = self.group_combo.currentText()
        skip_duplicate = self.skip_duplicate_cb.isChecked()
        
        success, fail, skipped = 0, 0, 0
        
        # 获取已存在的邮箱列表（用于去重检测）
        existing_emails = set()
        if skip_duplicate:
            for acc in self.db.get_all_accounts():
                existing_emails.add(acc[1].lower())  # acc[1] 是邮箱地址
        
        for account_data in self.parse_accounts(text):
            email = account_data.get('email')
            pwd = account_data.get('password')
            client_id = account_data.get('client_id')
            refresh_token = account_data.get('refresh_token')
            
            if email and pwd and '@' in email:
                # 去重检测
                if skip_duplicate and email.lower() in existing_emails:
                    skipped += 1
                    continue
                
                ok, _ = self.db.add_account(email, pwd, group, 
                                            client_id=client_id, 
                                            refresh_token=refresh_token)
                if ok:
                    success += 1
                    existing_emails.add(email.lower())  # 添加到已存在列表，防止同批次重复
                else:
                    fail += 1
            else:
                fail += 1
        
        # 显示结果 - 使用美观的成功提示框
        result_msg = f'成功: {success} 个  |  失败: {fail} 个'
        if skipped > 0:
            result_msg += f'  |  跳过: {skipped} 个'
        
        dialog = SuccessDialog('导入完成', result_msg, self)
        dialog.exec_()
        
        if success > 0:
            self.accept()
    
    def parse_accounts(self, text):
        """解析账号文本，支持 $ 或 $$ 分隔多账号，格式：邮箱----密码----client_id----refresh_token"""
        accounts = []
        
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
        
        # 判断分隔符类型 - 优先用 $$ 分隔
        if '$$' in text:
            parts = text.split('$$')
        elif '\n' in text:
            parts = text.split('\n')
        else:
            # 单条数据或用 $ 分隔（需要智能判断）
            # 检查是否有 $邮箱 的模式（$ 后面紧跟邮箱地址）
            import re
            # 用正则在 $ 后面跟邮箱地址的位置分割
            parts = re.split(r'\$(?=[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 移除末尾的 $
            while part.endswith('$'):
                part = part[:-1]
            
            account_data = {}
            
            # 按 ---- 分割
            if '----' in part:
                p = part.split('----')
                if len(p) >= 2:
                    account_data['email'] = p[0].strip()
                    account_data['password'] = p[1].strip()
                    if len(p) >= 3 and p[2].strip():
                        account_data['client_id'] = p[2].strip()
                    if len(p) >= 4 and p[3].strip():
                        account_data['refresh_token'] = p[3].strip()
            
            if account_data and account_data.get('email') and '@' in account_data.get('email', ''):
                accounts.append(account_data)
        
        return accounts


class FetchEmailThread(QThread):
    """获取邮件线程"""
    finished = pyqtSignal(list, str)
    
    def __init__(self, account, folder='inbox', db_manager=None):
        super().__init__()
        self.account = account
        self.folder = folder
        self.db_manager = db_manager
    
    def run(self):
        client = create_email_client(self.account, self.db_manager)
        emails, msg = client.fetch_emails(folder=self.folder, limit=50)
        client.disconnect()
        self.finished.emit(emails, msg)


class EmailViewDialog(QDialog):
    """邮件查看对话框"""
    
    # 文件夹显示名称映射
    FOLDER_NAMES = {
        'inbox': '收件箱',
        'junk': '垃圾邮件',
        'sent': '已发送',
        'drafts': '草稿箱',
        'deleted': '已删除',
    }
    
    def __init__(self, account, db, parent=None):
        super().__init__(parent)
        self.account = account
        self.db = db
        self.current_folder = 'inbox'
        self.all_emails = []  # 存储所有邮件用于搜索
        self.setWindowTitle(f'邮件 - {account[1]}')
        self.setMinimumSize(1000, 650)
        self.setStyleSheet("QDialog { background-color: #F3F3F3; font-family: 'Segoe UI', 'Microsoft YaHei UI'; }")
        self.init_ui()
        self.fetch_emails()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧邮件列表
        left_panel = QFrame()
        left_panel.setFixedWidth(350)
        left_panel.setStyleSheet("background: #FFFFFF; border-right: 1px solid #E5E5E5;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 工具栏区域
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("background: #FAFAFA; border-bottom: 1px solid #E5E5E5;")
        toolbar_layout = QVBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)
        
        # 第一行：文件夹选择和刷新
        row1 = QHBoxLayout()
        self.folder_combo = QComboBox()
        self.folder_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 10px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: #FAFAFA;
                font-size: 12px;
                color: #1A1A1A;
            }
            QComboBox:hover { border-color: #B0B0B0; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow { image: none; border-left: 4px solid transparent;
                border-right: 4px solid transparent; border-top: 5px solid #666; }
            QComboBox QAbstractItemView {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                selection-background-color: #E5F1FB;
                selection-color: #1A1A1A;
                color: #1A1A1A;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                min-height: 24px;
                color: #1A1A1A;
            }
        """)
        for key, name in self.FOLDER_NAMES.items():
            self.folder_combo.addItem(name, key)
        self.folder_combo.currentIndexChanged.connect(self.on_folder_changed)
        row1.addWidget(self.folder_combo)
        
        self.refresh_btn = QPushButton('刷新')
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: #FFFFFF;
                font-size: 12px;
                padding: 6px 12px;
                color: #1A1A1A;
            }
            QPushButton:hover { background: #F5F5F5; border-color: #0078D4; }
        """)
        self.refresh_btn.clicked.connect(self.fetch_emails)
        row1.addWidget(self.refresh_btn)
        row1.addStretch()
        toolbar_layout.addLayout(row1)
        
        # 第二行：搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索邮件...')
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: #FFFFFF;
                font-size: 12px;
            }
            QLineEdit:focus { border: 2px solid #0078D4; }
        """)
        self.search_input.textChanged.connect(self.filter_emails)
        toolbar_layout.addWidget(self.search_input)
        
        # 第三行：操作按钮
        row3 = QHBoxLayout()
        row3.setSpacing(6)
        
        # 统一按钮样式 - 白底黑字
        toolbar_btn_style = """
            QPushButton {
                background-color: #FFFFFF;
                color: #1A1A1A;
                border: 1px solid #D0D0D0;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #F5F5F5; border-color: #0078D4; }
            QPushButton:disabled { background-color: #F5F5F5; color: #999999; }
        """
        
        self.compose_btn = QPushButton('写邮件')
        self.compose_btn.setStyleSheet(toolbar_btn_style)
        self.compose_btn.clicked.connect(self.open_compose_dialog)
        row3.addWidget(self.compose_btn)
        
        self.reply_btn = QPushButton('回复')
        self.reply_btn.setStyleSheet(toolbar_btn_style)
        self.reply_btn.clicked.connect(self.reply_email)
        self.reply_btn.setEnabled(False)
        row3.addWidget(self.reply_btn)
        
        self.forward_btn = QPushButton('转发')
        self.forward_btn.setStyleSheet(toolbar_btn_style)
        self.forward_btn.clicked.connect(self.forward_email)
        self.forward_btn.setEnabled(False)
        row3.addWidget(self.forward_btn)
        
        self.mark_btn = QPushButton('标记')
        self.mark_btn.setStyleSheet(toolbar_btn_style)
        self.mark_btn.clicked.connect(self.toggle_read_status)
        self.mark_btn.setEnabled(False)
        row3.addWidget(self.mark_btn)
        
        self.delete_btn = QPushButton('删除')
        self.delete_btn.setStyleSheet(toolbar_btn_style)
        self.delete_btn.clicked.connect(self.delete_selected_email)
        self.delete_btn.setEnabled(False)
        row3.addWidget(self.delete_btn)
        
        row3.addStretch()
        toolbar_layout.addLayout(row3)
        
        left_layout.addWidget(toolbar_widget)
        
        # 加载状态标签
        self.loading_label = QLabel('加载中...')
        self.loading_label.setStyleSheet("padding: 20px; color: #666; font-size: 13px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.loading_label)
        
        self.email_list = QListWidget()
        self.email_list.setSelectionMode(QListWidget.ExtendedSelection)  # 支持 Ctrl+A 和 Ctrl+点击多选
        self.email_list.setStyleSheet("""
            QListWidget { 
                background: #FFFFFF; 
                border: none; 
                outline: none;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QListWidget::item { 
                padding: 14px 16px; 
                border-bottom: 1px solid #F0F0F0;
                margin: 0px 8px;
                color: #1A1A1A;
            }
            QListWidget::item:hover { 
                background: #F5F5F5;
            }
            QListWidget::item:selected { 
                background: #FFFFFF;
                color: #1A1A1A;
                border-left: 3px solid #0078D4;
            }
            /* 滚动条 */
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.email_list.itemClicked.connect(self.show_email_content)
        self.email_list.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.email_list)
        layout.addWidget(left_panel)
        
        # 右侧内容区 - 使用浅灰色背景与左侧区分
        right_panel = QWidget()
        right_panel.setStyleSheet("background: #F5F5F5;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(12)
        
        self.subject_label = QLabel('选择一封邮件查看')
        self.subject_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #1A1A1A; background: transparent;")
        self.subject_label.setWordWrap(True)
        
        self.info_label = QLabel('')
        self.info_label.setStyleSheet("color: #616161; font-size: 12px; background: transparent;")
        
        # 附件区域
        self.attachment_widget = QWidget()
        self.attachment_widget.setStyleSheet("background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 4px;")
        self.attachment_widget.hide()
        attachment_layout = QHBoxLayout(self.attachment_widget)
        attachment_layout.setContentsMargins(12, 8, 12, 8)
        self.attachment_label = QLabel('附件:')
        self.attachment_label.setStyleSheet("color: #666; font-size: 12px;")
        attachment_layout.addWidget(self.attachment_label)
        self.attachment_list = QHBoxLayout()
        attachment_layout.addLayout(self.attachment_list)
        attachment_layout.addStretch()
        
        self.content_text = QTextBrowser()
        self.content_text.setReadOnly(True)
        self.content_text.setOpenExternalLinks(True)  # 启用点击链接在浏览器中打开
        self.content_text.setStyleSheet("""
            QTextBrowser { 
                border: 1px solid #E0E0E0; 
                padding: 16px; 
                background: #FFFFFF; 
                font-size: 14px;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                color: #1A1A1A;
            }
            QTextBrowser a {
                color: #0078D4;
                text-decoration: underline;
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        right_layout.addWidget(self.subject_label)
        right_layout.addWidget(self.info_label)
        right_layout.addWidget(self.attachment_widget)
        right_layout.addWidget(self.content_text, 1)
        layout.addWidget(right_panel, 1)
    
    def on_folder_changed(self, index):
        """文件夹切换"""
        self.current_folder = self.folder_combo.currentData()
        self.search_input.clear()
        self.fetch_emails()
    
    def fetch_emails(self):
        self.email_list.clear()
        self.all_emails = []
        self.loading_label.show()
        self.loading_label.setText('加载中...')
        self.subject_label.setText('选择一封邮件查看')
        self.info_label.setText('')
        self.content_text.setText('')
        self.attachment_widget.hide()
        self.reset_buttons()
        
        self.fetch_thread = FetchEmailThread(self.account, self.current_folder, self.db)
        self.fetch_thread.finished.connect(self.on_emails_fetched)
        self.fetch_thread.start()
    
    def reset_buttons(self):
        """重置按钮状态"""
        self.delete_btn.setEnabled(False)
        self.delete_btn.setText('删除')
        self.reply_btn.setEnabled(False)
        self.forward_btn.setEnabled(False)
        self.mark_btn.setEnabled(False)
    
    def on_selection_changed(self):
        """选择变化时更新按钮状态"""
        selected_items = self.email_list.selectedItems()
        count = len(selected_items)
        
        if count == 0:
            self.reset_buttons()
        elif count == 1:
            # 单选时启用所有按钮
            self.delete_btn.setEnabled(True)
            self.delete_btn.setText('删除')
            self.reply_btn.setEnabled(True)
            self.forward_btn.setEnabled(True)
            self.mark_btn.setEnabled(True)
        else:
            # 多选时启用删除和标记按钮
            self.delete_btn.setEnabled(True)
            self.delete_btn.setText(f'删除 ({count})')
            self.reply_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)
            self.mark_btn.setEnabled(True)
            self.mark_btn.setText(f'标记 ({count})')
    
    def on_emails_fetched(self, emails, msg):
        self.loading_label.hide()
        self.all_emails = emails  # 保存所有邮件用于搜索
        
        if not emails:
            folder_name = self.FOLDER_NAMES.get(self.current_folder, self.current_folder)
            self.subject_label.setText(f'{folder_name} 暂无邮件\n{msg}')
            return
        
        self.display_emails(emails)
        
        # 自动检测 AWS 验证码邮件并更新数据库
        if self.current_folder == 'inbox':
            self.check_aws_emails(emails)
    
    def check_aws_emails(self, emails):
        """检测邮件列表中是否有 AWS 验证码邮件（只检查标题）"""
        # AWS 验证码邮件的标题特征
        aws_keywords = [
            'aws',
            'amazon',
        ]
        
        aws_count = 0
        for email_data in emails:
            subject = email_data.get('subject', '').lower()
            
            # 只检查标题是否包含 aws 或 amazon
            if any(kw in subject for kw in aws_keywords):
                aws_count += 1
        
        # 更新数据库
        has_aws = aws_count > 0
        self.db.update_aws_code_status(self.account[0], has_aws)
    
    def display_emails(self, emails):
        """显示邮件列表"""
        self.email_list.clear()
        
        for email_data in emails:
            item = QListWidgetItem()
            sender = email_data.get('sender', '')[:30]
            subject = email_data.get('subject', '(无主题)')[:40]
            date = email_data.get('date')
            date_str = date.strftime('%m/%d %H:%M') if date else ''
            is_read = email_data.get('is_read', True)
            has_attachments = email_data.get('has_attachments', False)
            
            # 附件标记
            att_mark = '📎 ' if has_attachments else ''
            
            # 未读邮件加粗显示
            if not is_read:
                item.setText(f"● {att_mark}{sender}\n{subject}\n{date_str}")
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            else:
                item.setText(f"{att_mark}{sender}\n{subject}\n{date_str}")
            
            item.setData(Qt.UserRole, email_data)
            self.email_list.addItem(item)
    
    def filter_emails(self, text):
        """搜索过滤邮件（只搜索发件人和主题）"""
        if not text:
            self.display_emails(self.all_emails)
            return
        
        text = text.lower()
        filtered = []
        for email_data in self.all_emails:
            sender = email_data.get('sender', '').lower()
            sender_email = email_data.get('sender_email', '').lower()
            subject = email_data.get('subject', '').lower()
            # 只搜索发件人和主题，不搜索正文（正文通常是 HTML，包含太多无关内容）
            if text in sender or text in sender_email or text in subject:
                filtered.append(email_data)
        
        self.display_emails(filtered)
    
    def show_email_content(self, item):
        data = item.data(Qt.UserRole)
        self.current_email = data
        self.current_item = item  # 保存当前选中的列表项
        
        # 启用操作按钮
        self.delete_btn.setEnabled(True)
        self.reply_btn.setEnabled(True)
        self.forward_btn.setEnabled(True)
        self.mark_btn.setEnabled(True)
        
        # 更新标记按钮文字
        is_read = data.get('is_read', True)
        
        # 如果是未读邮件，立即更新 UI 显示为已读
        if not is_read:
            self.mark_btn.setText('标为未读')
            
            # 立即更新列表项显示（移除粗体和圆点）
            sender = data.get('sender', '')[:30]
            subject = data.get('subject', '(无主题)')[:40]
            date = data.get('date')
            date_str = date.strftime('%m/%d %H:%M') if date else ''
            has_attachments = data.get('has_attachments', False)
            att_mark = '📎 ' if has_attachments else ''
            
            item.setText(f"{att_mark}{sender}\n{subject}\n{date_str}")
            font = item.font()
            font.setBold(False)
            item.setFont(font)
            
            # 更新数据
            data['is_read'] = True
            self.current_email['is_read'] = True
            
            # 更新 all_emails 中的数据
            for email_data in self.all_emails:
                if email_data.get('uid') == data.get('uid'):
                    email_data['is_read'] = True
                    break
            
            # 后台发送请求到服务器（不阻塞 UI）
            self.auto_mark_as_read(data.get('uid'))
        else:
            self.mark_btn.setText('标为未读')
        
        self.subject_label.setText(data.get('subject', '(无主题)'))
        date = data.get('date')
        date_str = date.strftime('%Y-%m-%d %H:%M') if date else ''
        self.info_label.setText(f"发件人: {data.get('sender', '')}\n时间: {date_str}")
        
        # 显示邮件内容，支持 HTML 格式（链接可点击）
        body = data.get('body', '')
        if '<html' in body.lower() or '<a ' in body.lower() or '<div' in body.lower():
            # HTML 格式邮件，直接显示
            self.content_text.setHtml(body)
        else:
            # 纯文本邮件，转换为 HTML 以保持格式
            self.content_text.setPlainText(body)
        
        # 处理附件
        has_attachments = data.get('has_attachments', False)
        if has_attachments:
            self.load_attachments(data.get('uid'))
        else:
            self.attachment_widget.hide()
    
    def load_attachments(self, email_id):
        """加载附件列表"""
        self.attachment_thread = GetAttachmentsThread(self.account, email_id, self.current_folder)
        self.attachment_thread.finished.connect(self.on_attachments_loaded)
        self.attachment_thread.start()
    
    def auto_mark_as_read(self, email_id):
        """后台自动标记邮件为已读（不更新 UI，因为已经更新过了）"""
        self.auto_mark_thread = MarkReadThread(self.account, email_id, self.current_folder, True)
        # 不需要处理回调，因为 UI 已经更新了
        self.auto_mark_thread.start()
    
    def on_attachments_loaded(self, attachments, msg):
        """附件加载完成"""
        # 清除旧的附件按钮
        while self.attachment_list.count():
            item = self.attachment_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.current_attachments = attachments  # 保存附件列表
        
        if attachments:
            self.attachment_widget.show()
            
            # 添加每个附件的下载按钮
            for att in attachments:
                btn = QPushButton(f"📄 {att['name']} ({self.format_size(att['size'])})")
                btn.setStyleSheet("""
                    QPushButton {
                        background: #FFFFFF;
                        border: 1px solid #E0E0E0;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 11px;
                        color: #0078D4;
                    }
                    QPushButton:hover { background: #E5F1FB; border-color: #0078D4; }
                """)
                btn.setProperty('attachment', att)
                btn.setToolTip('点击下载此附件')
                btn.clicked.connect(self.download_attachment)
                self.attachment_list.addWidget(btn)
            
            # 如果有多个附件，添加"下载全部"按钮
            if len(attachments) > 1:
                btn_all = QPushButton(f"⬇ 下载全部 ({len(attachments)})")
                btn_all.setStyleSheet("""
                    QPushButton {
                        background: #0078D4;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 12px;
                        font-size: 11px;
                        color: white;
                    }
                    QPushButton:hover { background: #1084D9; }
                """)
                btn_all.setToolTip('下载所有附件到选择的文件夹')
                btn_all.clicked.connect(self.download_all_attachments)
                self.attachment_list.addWidget(btn_all)
        else:
            self.attachment_widget.hide()
    
    def download_all_attachments(self):
        """下载所有附件"""
        if not hasattr(self, 'current_attachments') or not self.current_attachments:
            return
        
        # 选择保存目录
        folder = QFileDialog.getExistingDirectory(self, '选择保存目录')
        if not folder:
            return
        
        success_count = 0
        fail_count = 0
        
        for att in self.current_attachments:
            try:
                content = create_email_client(self.account).download_attachment(att)
                if content:
                    # 处理文件名冲突
                    file_path = os.path.join(folder, att['name'])
                    base, ext = os.path.splitext(file_path)
                    counter = 1
                    while os.path.exists(file_path):
                        file_path = f"{base}_{counter}{ext}"
                        counter += 1
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1
        
        if fail_count == 0:
            QMessageBox.information(self, '成功', f'已成功下载 {success_count} 个附件到:\n{folder}')
        else:
            QMessageBox.warning(self, '部分成功', f'成功: {success_count} 个\n失败: {fail_count} 个')
    
    def format_size(self, size):
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    def download_attachment(self):
        """下载附件"""
        btn = self.sender()
        att = btn.property('attachment')
        if not att:
            return
        
        # 选择保存路径
        path, _ = QFileDialog.getSaveFileName(self, '保存附件', att['name'])
        if path:
            try:
                content = create_email_client(self.account).download_attachment(att)
                
                if content:
                    with open(path, 'wb') as f:
                        f.write(content)
                    QMessageBox.information(self, '成功', f'附件已保存到:\n{path}')
                else:
                    QMessageBox.warning(self, '错误', '无法下载附件')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'保存失败: {e}')
    
    def toggle_read_status(self):
        """切换已读/未读状态（支持批量）"""
        selected_items = self.email_list.selectedItems()
        count = len(selected_items)
        
        if count == 0:
            return
        elif count == 1:
            # 单个标记
            if not hasattr(self, 'current_email') or not self.current_email:
                return
            
            email_id = self.current_email.get('uid')
            is_read = self.current_email.get('is_read', True)
            new_status = not is_read
            
            self.mark_btn.setEnabled(False)
            self.mark_btn.setText('处理中...')
            
            self.mark_thread = MarkReadThread(self.account, email_id, self.current_folder, new_status)
            self.mark_thread.finished.connect(self.on_mark_finished)
            self.mark_thread.start()
        else:
            # 批量标记 - 弹出选择对话框
            from PyQt5.QtWidgets import QMenu
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            from PyQt5.QtGui import QColor
            menu = QMenu(self)
            menu.setStyleSheet(MENU_STYLE_LIGHT)
            
            # 添加阴影效果
            shadow = QGraphicsDropShadowEffect(menu)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 4)
            menu.setGraphicsEffect(shadow)
            
            action_read = menu.addAction(f'全部标为已读 ({count})')
            action_unread = menu.addAction(f'全部标为未读 ({count})')
            
            action = menu.exec_(self.mark_btn.mapToGlobal(self.mark_btn.rect().bottomLeft()))
            
            if action == action_read:
                self.batch_mark_emails(selected_items, True)
            elif action == action_unread:
                self.batch_mark_emails(selected_items, False)
    
    def batch_mark_emails(self, selected_items, is_read):
        """批量标记邮件"""
        email_ids = []
        for item in selected_items:
            data = item.data(Qt.UserRole)
            if data and data.get('uid'):
                email_ids.append(data.get('uid'))
        
        if not email_ids:
            return
        
        self.mark_btn.setEnabled(False)
        self.mark_btn.setText(f'标记中 (0/{len(email_ids)})...')
        
        self.batch_mark_thread = BatchMarkReadThread(self.account, email_ids, self.current_folder, is_read)
        self.batch_mark_thread.progress.connect(self.on_batch_mark_progress)
        self.batch_mark_thread.finished.connect(lambda s, f, t: self.on_batch_mark_finished(s, f, t, is_read))
        self.batch_mark_thread.start()
    
    def on_batch_mark_progress(self, current, total):
        """批量标记进度更新"""
        self.mark_btn.setText(f'标记中 ({current}/{total})...')
    
    def on_batch_mark_finished(self, success_count, fail_count, total, is_read):
        """批量标记完成"""
        self.mark_btn.setText('标记')
        self.mark_btn.setEnabled(True)
        
        status_text = '已读' if is_read else '未读'
        if fail_count == 0:
            QMessageBox.information(self, '成功', f'已将 {success_count} 封邮件标为{status_text}')
        else:
            QMessageBox.warning(self, '部分成功', 
                               f'标记完成\n成功: {success_count} 封\n失败: {fail_count} 封')
        
        self.fetch_emails()  # 刷新列表
    
    def on_mark_finished(self, success, msg):
        if success:
            # 更新当前邮件状态
            self.current_email['is_read'] = not self.current_email.get('is_read', True)
            is_read = self.current_email['is_read']
            self.mark_btn.setText('标为未读' if is_read else '标为已读')
            self.fetch_emails()  # 刷新列表
        else:
            QMessageBox.warning(self, '错误', msg)
        
        self.mark_btn.setEnabled(True)
    
    def reply_email(self):
        """回复邮件"""
        if not hasattr(self, 'current_email') or not self.current_email:
            return
        
        sender_email = self.current_email.get('sender_email', '')
        if not sender_email:
            # 尝试从 sender 字段提取
            sender = self.current_email.get('sender', '')
            import re
            match = re.search(r'<([^>]+)>', sender)
            if match:
                sender_email = match.group(1)
            elif '@' in sender:
                sender_email = sender.strip()
        
        subject = self.current_email.get('subject', '')
        original_body = self.current_email.get('body', '')
        date = self.current_email.get('date')
        date_str = date.strftime('%Y-%m-%d %H:%M') if date else ''
        
        # 构建回复正文
        reply_body = f"\n\n\n-------- 原始邮件 --------\n发件人: {self.current_email.get('sender', '')}\n时间: {date_str}\n\n{original_body}"
        
        dialog = ComposeEmailDialog(
            self.account, self,
            reply_to=sender_email,
            reply_subject=subject,
            reply_body=reply_body
        )
        dialog.exec_()
    
    def forward_email(self):
        """转发邮件"""
        if not hasattr(self, 'current_email') or not self.current_email:
            return
        
        subject = self.current_email.get('subject', '')
        if not subject.startswith('Fwd:') and not subject.startswith('转发:'):
            subject = f'Fwd: {subject}'
        
        original_body = self.current_email.get('body', '')
        date = self.current_email.get('date')
        date_str = date.strftime('%Y-%m-%d %H:%M') if date else ''
        
        # 构建转发正文
        forward_body = f"\n\n\n-------- 转发邮件 --------\n发件人: {self.current_email.get('sender', '')}\n时间: {date_str}\n主题: {self.current_email.get('subject', '')}\n\n{original_body}"
        
        dialog = ComposeEmailDialog(
            self.account, self,
            reply_subject=subject,
            reply_body=forward_body,
            is_forward=True
        )
        dialog.exec_()
    
    def delete_selected_email(self):
        """删除选中的邮件（支持批量删除）"""
        selected_items = self.email_list.selectedItems()
        if not selected_items:
            return
        
        count = len(selected_items)
        
        if count == 1:
            # 单个删除
            if not hasattr(self, 'current_email') or not self.current_email:
                return
            
            reply = QMessageBox.question(self, '确认删除', '确定要删除这封邮件吗？',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
            email_id = self.current_email.get('uid')
            if not email_id:
                QMessageBox.warning(self, '错误', '无法获取邮件ID')
                return
            
            self.delete_btn.setEnabled(False)
            self.delete_btn.setText('删除中...')
            
            self.delete_thread = DeleteEmailThread(self.account, email_id, self.current_folder)
            self.delete_thread.finished.connect(self.on_delete_finished)
            self.delete_thread.start()
        else:
            # 批量删除
            reply = QMessageBox.question(self, '确认批量删除', 
                                         f'确定要删除选中的 {count} 封邮件吗？',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            
            # 收集所有选中邮件的ID
            email_ids = []
            for item in selected_items:
                data = item.data(Qt.UserRole)
                if data and data.get('uid'):
                    email_ids.append(data.get('uid'))
            
            if not email_ids:
                QMessageBox.warning(self, '错误', '无法获取邮件ID')
                return
            
            self.delete_btn.setEnabled(False)
            self.delete_btn.setText(f'删除中 (0/{len(email_ids)})...')
            
            self.batch_delete_thread = BatchDeleteEmailThread(self.account, email_ids, self.current_folder)
            self.batch_delete_thread.progress.connect(self.on_batch_delete_progress)
            self.batch_delete_thread.finished.connect(self.on_batch_delete_finished)
            self.batch_delete_thread.start()
    
    def on_batch_delete_progress(self, current, total):
        """批量删除进度更新"""
        self.delete_btn.setText(f'删除中 ({current}/{total})...')
    
    def on_batch_delete_finished(self, success_count, fail_count, total):
        """批量删除完成"""
        self.delete_btn.setText('删除')
        
        if fail_count == 0:
            QMessageBox.information(self, '成功', f'已成功删除 {success_count} 封邮件')
        else:
            QMessageBox.warning(self, '部分成功', 
                               f'删除完成\n成功: {success_count} 封\n失败: {fail_count} 封')
        
        self.current_email = None
        self.fetch_emails()  # 刷新列表
    
    def on_delete_finished(self, success, msg):
        self.delete_btn.setText('删除')
        
        if success:
            QMessageBox.information(self, '成功', '邮件已删除')
            self.current_email = None
            self.fetch_emails()  # 刷新列表
        else:
            self.delete_btn.setEnabled(True)
            QMessageBox.warning(self, '删除失败', msg)
    
    def open_compose_dialog(self):
        """打开写邮件对话框"""
        dialog = ComposeEmailDialog(self.account, self)
        dialog.exec_()


class DeleteEmailThread(QThread):
    """删除邮件线程"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, account, email_id, folder):
        super().__init__()
        self.account = account
        self.email_id = email_id
        self.folder = folder
    
    def run(self):
        client = create_email_client(self.account)
        success, msg = client.delete_email(self.email_id, self.folder)
        self.finished.emit(success, msg)


class BatchDeleteEmailThread(QThread):
    """批量删除邮件线程"""
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(int, int, int)  # success_count, fail_count, total
    
    def __init__(self, account, email_ids, folder):
        super().__init__()
        self.account = account
        self.email_ids = email_ids
        self.folder = folder
    
    def run(self):
        client = create_email_client(self.account)
        total = len(self.email_ids)
        
        def progress_callback(current, total):
            self.progress.emit(current, total)
        
        success_count, fail_count = client.delete_emails_batch(
            self.email_ids, self.folder, progress_callback
        )
        
        self.finished.emit(success_count, fail_count, total)


class BatchMarkReadThread(QThread):
    """批量标记已读/未读线程"""
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(int, int, int)  # success_count, fail_count, total
    
    def __init__(self, account, email_ids, folder, is_read):
        super().__init__()
        self.account = account
        self.email_ids = email_ids
        self.folder = folder
        self.is_read = is_read
    
    def run(self):
        client = create_email_client(self.account)
        total = len(self.email_ids)
        
        def progress_callback(current, total):
            self.progress.emit(current, total)
        
        success_count, fail_count = client.mark_emails_batch(
            self.email_ids, self.folder, self.is_read, progress_callback
        )
        
        self.finished.emit(success_count, fail_count, total)


class MarkReadThread(QThread):
    """标记已读/未读线程"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, account, email_id, folder, is_read):
        super().__init__()
        self.account = account
        self.email_id = email_id
        self.folder = folder
        self.is_read = is_read
    
    def run(self):
        client = create_email_client(self.account)
        success, msg = client.mark_as_read(self.email_id, self.folder, self.is_read)
        self.finished.emit(success, msg)


class GetAttachmentsThread(QThread):
    """获取附件列表线程"""
    finished = pyqtSignal(list, str)
    
    def __init__(self, account, email_id, folder):
        super().__init__()
        self.account = account
        self.email_id = email_id
        self.folder = folder
    
    def run(self):
        client = create_email_client(self.account)
        attachments, msg = client.get_attachments(self.email_id, self.folder)
        self.finished.emit(attachments, msg)


class SendEmailThread(QThread):
    """发送邮件线程"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, account, to_addr, subject, body, cc_addr=None, attachments=None):
        super().__init__()
        self.account = account
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
        self.cc_addr = cc_addr
        self.attachments = attachments
    
    def run(self):
        client = create_email_client(self.account)
        if self.attachments:
            success, msg = client.send_email_with_attachments(
                self.to_addr, self.subject, self.body, self.attachments, self.cc_addr
            )
        else:
            success, msg = client.send_email(self.to_addr, self.subject, self.body, self.cc_addr)
        self.finished.emit(success, msg)


class ComposeEmailDialog(QDialog):
    """写邮件对话框"""
    def __init__(self, account, parent=None, reply_to=None, reply_subject=None, reply_body=None, is_forward=False):
        super().__init__(parent)
        self.account = account
        self.reply_to = reply_to
        self.reply_subject = reply_subject
        self.reply_body = reply_body or ''
        self.is_forward = is_forward
        self.attachments = []  # 附件文件路径列表
        self.setWindowTitle(f'写邮件 - {account[1]}')
        self.setMinimumSize(650, 550)
        self.setStyleSheet(DIALOG_STYLE)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # 标题
        title_text = '转发邮件' if self.is_forward else ('回复邮件' if self.reply_to else '写邮件')
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)
        
        # 发件人（只读）
        from_row = QHBoxLayout()
        from_label = QLabel('发件人:')
        from_label.setFixedWidth(60)
        self.from_input = QLineEdit(self.account[1])
        self.from_input.setReadOnly(True)
        self.from_input.setStyleSheet("background: #F0F0F0; color: #666;")
        from_row.addWidget(from_label)
        from_row.addWidget(self.from_input)
        layout.addLayout(from_row)
        
        # 收件人
        to_row = QHBoxLayout()
        to_label = QLabel('收件人:')
        to_label.setFixedWidth(60)
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText('多个收件人用逗号分隔')
        if self.reply_to:
            self.to_input.setText(self.reply_to)
        to_row.addWidget(to_label)
        to_row.addWidget(self.to_input)
        layout.addLayout(to_row)
        
        # 抄送
        cc_row = QHBoxLayout()
        cc_label = QLabel('抄送:')
        cc_label.setFixedWidth(60)
        self.cc_input = QLineEdit()
        self.cc_input.setPlaceholderText('可选，多个用逗号分隔')
        cc_row.addWidget(cc_label)
        cc_row.addWidget(self.cc_input)
        layout.addLayout(cc_row)
        
        # 主题
        subject_row = QHBoxLayout()
        subject_label = QLabel('主题:')
        subject_label.setFixedWidth(60)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText('邮件主题')
        if self.reply_subject:
            if self.is_forward:
                self.subject_input.setText(self.reply_subject)
            else:
                prefix = 'Re: ' if not self.reply_subject.startswith('Re:') else ''
                self.subject_input.setText(f'{prefix}{self.reply_subject}')
        subject_row.addWidget(subject_label)
        subject_row.addWidget(self.subject_input)
        layout.addLayout(subject_row)
        
        # 附件区域
        att_row = QHBoxLayout()
        att_label = QLabel('附件:')
        att_label.setFixedWidth(60)
        att_row.addWidget(att_label)
        
        self.att_list_widget = QWidget()
        self.att_list_layout = QHBoxLayout(self.att_list_widget)
        self.att_list_layout.setContentsMargins(0, 0, 0, 0)
        self.att_list_layout.setSpacing(4)
        att_row.addWidget(self.att_list_widget, 1)
        
        btn_add_att = QPushButton('添加附件')
        btn_add_att.setStyleSheet("""
            QPushButton {
                background: #FFFFFF;
                border: 1px solid #0078D4;
                color: #0078D4;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background: #E5F1FB; }
        """)
        btn_add_att.clicked.connect(self.add_attachment)
        att_row.addWidget(btn_add_att)
        layout.addLayout(att_row)
        
        # 正文
        body_label = QLabel('正文:')
        layout.addWidget(body_label)
        
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText('在此输入邮件内容...')
        self.body_input.setMinimumHeight(180)
        if self.reply_body:
            self.body_input.setText(self.reply_body)
            # 将光标移到开头
            cursor = self.body_input.textCursor()
            cursor.setPosition(0)
            self.body_input.setTextCursor(cursor)
        layout.addWidget(self.body_input)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_cancel = QPushButton('取消')
        btn_cancel.setStyleSheet(BTN_DEFAULT)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_send = QPushButton('发送')
        self.btn_send.setStyleSheet(BTN_PRIMARY)
        self.btn_send.clicked.connect(self.send_email)
        
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(self.btn_send)
        layout.addLayout(btn_row)
    
    def add_attachment(self):
        """添加附件"""
        paths, _ = QFileDialog.getOpenFileNames(self, '选择附件', '', '所有文件 (*.*)')
        for path in paths:
            if path and path not in self.attachments:
                self.attachments.append(path)
                self.update_attachment_display()
    
    def update_attachment_display(self):
        """更新附件显示"""
        # 清除旧的
        while self.att_list_layout.count():
            item = self.att_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for path in self.attachments:
            filename = os.path.basename(path)
            btn = QPushButton(f'📎 {filename[:20]}{"..." if len(filename) > 20 else ""} ✕')
            btn.setStyleSheet("""
                QPushButton {
                    background: #F5F5F5;
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    color: #666;
                }
                QPushButton:hover { background: #FFE0E0; border-color: #D13438; color: #D13438; }
            """)
            btn.setProperty('path', path)
            btn.clicked.connect(self.remove_attachment)
            self.att_list_layout.addWidget(btn)
    
    def remove_attachment(self):
        """移除附件"""
        btn = self.sender()
        path = btn.property('path')
        if path in self.attachments:
            self.attachments.remove(path)
            self.update_attachment_display()
    
    def send_email(self):
        to_addr = self.to_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText()
        cc_addr = self.cc_input.text().strip() or None
        
        if not to_addr:
            QMessageBox.warning(self, '错误', '请输入收件人地址')
            return
        
        if not subject:
            QMessageBox.warning(self, '错误', '请输入邮件主题')
            return
        
        # 禁用发送按钮
        self.btn_send.setEnabled(False)
        self.btn_send.setText('发送中...')
        self.status_label.setText('正在发送邮件...')
        
        # 启动发送线程
        self.send_thread = SendEmailThread(
            self.account, to_addr, subject, body, cc_addr,
            self.attachments if self.attachments else None
        )
        self.send_thread.finished.connect(self.on_send_finished)
        self.send_thread.start()
    
    def on_send_finished(self, success, msg):
        self.btn_send.setEnabled(True)
        self.btn_send.setText('发送')
        
        if success:
            self.status_label.setText('')
            QMessageBox.information(self, '成功', '邮件发送成功！')
            self.accept()
        else:
            self.status_label.setText(f'发送失败: {msg}')
            QMessageBox.warning(self, '发送失败', msg)


class BatchSendThread(QThread):
    """批量发送邮件线程"""
    progress = pyqtSignal(int, str, bool, str)  # index, email, success, msg
    finished = pyqtSignal(int, int)  # success_count, fail_count
    
    def __init__(self, accounts, to_addr, subject, body):
        super().__init__()
        self.accounts = accounts
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
    
    def run(self):
        success_count = 0
        fail_count = 0
        
        for i, acc in enumerate(self.accounts):
            client = create_email_client(acc)
            success, msg = client.send_email(self.to_addr, self.subject, self.body)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            self.progress.emit(i, acc[1], success, msg)
        
        self.finished.emit(success_count, fail_count)


class BatchSendDialog(QDialog):
    """批量发送邮件对话框"""
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.accounts = accounts
        self.setWindowTitle(f'批量发送邮件 - {len(accounts)} 个账号')
        self.setMinimumSize(650, 550)
        self.setStyleSheet(DIALOG_STYLE)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel(f'批量发送邮件 ({len(self.accounts)} 个发件账号)')
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)
        
        # 发件账号列表
        accounts_label = QLabel(f'发件账号: {", ".join([acc[1] for acc in self.accounts[:3]])}{"..." if len(self.accounts) > 3 else ""}')
        accounts_label.setStyleSheet("color: #666; font-size: 12px;")
        accounts_label.setWordWrap(True)
        layout.addWidget(accounts_label)
        
        # 收件人
        to_row = QHBoxLayout()
        to_label = QLabel('收件人:')
        to_label.setFixedWidth(60)
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText('所有账号将发送到此地址，多个用逗号分隔')
        to_row.addWidget(to_label)
        to_row.addWidget(self.to_input)
        layout.addLayout(to_row)
        
        # 主题
        subject_row = QHBoxLayout()
        subject_label = QLabel('主题:')
        subject_label.setFixedWidth(60)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText('邮件主题')
        subject_row.addWidget(subject_label)
        subject_row.addWidget(self.subject_input)
        layout.addLayout(subject_row)
        
        # 正文
        body_label = QLabel('正文:')
        layout.addWidget(body_label)
        
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText('在此输入邮件内容...')
        self.body_input.setMinimumHeight(150)
        layout.addWidget(self.body_input)
        
        # 发送进度
        progress_label = QLabel('发送进度:')
        layout.addWidget(progress_label)
        
        self.progress_list = QListWidget()
        self.progress_list.setMaximumHeight(120)
        self.progress_list.setStyleSheet("""
            QListWidget { 
                background: #FAFAFA; 
                border: 1px solid #E0E0E0; 
                border-radius: 4px;
                font-size: 12px;
            }
            QListWidget::item { padding: 4px 8px; }
        """)
        layout.addWidget(self.progress_list)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(self.status_label)
        
        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_cancel = QPushButton('取消')
        btn_cancel.setStyleSheet(BTN_DEFAULT)
        btn_cancel.clicked.connect(self.reject)
        
        self.btn_send = QPushButton(f'发送 ({len(self.accounts)} 封)')
        self.btn_send.setStyleSheet(BTN_PRIMARY)
        self.btn_send.clicked.connect(self.start_send)
        
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(self.btn_send)
        layout.addLayout(btn_row)
    
    def start_send(self):
        to_addr = self.to_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText()
        
        if not to_addr:
            QMessageBox.warning(self, '错误', '请输入收件人地址')
            return
        
        if not subject:
            QMessageBox.warning(self, '错误', '请输入邮件主题')
            return
        
        # 确认发送
        reply = QMessageBox.question(
            self, '确认发送', 
            f'确定要使用 {len(self.accounts)} 个账号发送邮件吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        # 禁用发送按钮
        self.btn_send.setEnabled(False)
        self.btn_send.setText('发送中...')
        self.progress_list.clear()
        self.status_label.setText('正在发送...')
        
        # 启动发送线程
        self.send_thread = BatchSendThread(self.accounts, to_addr, subject, body)
        self.send_thread.progress.connect(self.on_progress)
        self.send_thread.finished.connect(self.on_finished)
        self.send_thread.start()
    
    def on_progress(self, index, email, success, msg):
        status = '✓ 成功' if success else f'✗ 失败: {msg[:30]}'
        item = QListWidgetItem(f'{index + 1}. {email} - {status}')
        if success:
            item.setForeground(Qt.darkGreen)
        else:
            item.setForeground(Qt.red)
        self.progress_list.addItem(item)
        self.progress_list.scrollToBottom()
        self.status_label.setText(f'正在发送... ({index + 1}/{len(self.accounts)})')
    
    def on_finished(self, success_count, fail_count):
        self.btn_send.setEnabled(True)
        self.btn_send.setText(f'发送 ({len(self.accounts)} 封)')
        self.status_label.setText(f'发送完成: 成功 {success_count} 封, 失败 {fail_count} 封')
        
        QMessageBox.information(
            self, '发送完成', 
            f'批量发送完成！\n成功: {success_count} 封\n失败: {fail_count} 封'
        )


class ManualOAuth2Dialog(QDialog):
    """手动 OAuth2 授权对话框 - 打开浏览器手动登录获取 Token"""
    
    # 导入完成信号
    import_completed = pyqtSignal(int, int)  # success_count, fail_count
    
    def __init__(self, db, parent=None, default_group=None):
        super().__init__(parent)
        self.db = db
        self.default_group = default_group
        self.setWindowTitle('手动授权 OAuth2')
        self.setMinimumSize(500, 400)
        self.resize(500, 450)
        self.setStyleSheet(DIALOG_STYLE)
        self.success_count = 0
        self.is_processing = False
        self.manual_thread = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel('🔐 手动授权 OAuth2')
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1A1A1A;")
        layout.addWidget(title)
        
        # 说明
        desc = QLabel('点击"开始授权"后，浏览器会打开微软登录页面。\n'
                      '请手动登录您的 Outlook 账号，登录成功后程序会自动获取授权信息。')
        desc.setStyleSheet("color: #666; font-size: 12px; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # 分组选择
        group_row = QHBoxLayout()
        group_row.addWidget(QLabel('导入到分组:'))
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(160)
        
        current_index = 0
        for i, group in enumerate(self.db.get_all_groups()):
            self.group_combo.addItem(group[1])
            if self.default_group and group[1] == self.default_group:
                current_index = i
        self.group_combo.setCurrentIndex(current_index)
        
        group_row.addWidget(self.group_combo)
        group_row.addStretch()
        layout.addLayout(group_row)
        
        # 提示信息
        tip_label = QLabel('💡 提示：登录完成后请等待页面自动跳转，不要手动关闭浏览器')
        tip_label.setStyleSheet("color: #E67E22; font-size: 11px; padding: 8px 0;")
        layout.addWidget(tip_label)
        
        # 进度区域
        self.progress_label = QLabel('准备就绪')
        self.progress_label.setStyleSheet("color: #0078D4; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.progress_label)
        
        self.current_account_label = QLabel('')
        self.current_account_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.current_account_label)
        
        # 结果区域
        result_label = QLabel('授权结果:')
        result_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #1A1A1A;")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background: #FAFAFA;
                font-size: 12px;
                font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
            }
        """)
        self.result_text.setMinimumHeight(100)
        layout.addWidget(self.result_text, 1)
        
        # 按钮
        btn_row = QHBoxLayout()
        
        self.btn_start = QPushButton('开始授权')
        self.btn_start.setStyleSheet(BTN_PRIMARY)
        self.btn_start.clicked.connect(self.start_manual_auth)
        
        self.btn_stop = QPushButton('停止')
        self.btn_stop.setStyleSheet(BTN_DEFAULT)
        self.btn_stop.clicked.connect(self.stop_auth)
        self.btn_stop.setEnabled(False)
        
        btn_close = QPushButton('关闭')
        btn_close.setStyleSheet(BTN_DEFAULT)
        btn_close.clicked.connect(self.close_dialog)
        
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
    
    def start_manual_auth(self):
        """开始手动授权"""
        if self.is_processing:
            QMessageBox.warning(self, '提示', '正在处理中，请等待完成')
            return
        
        self.is_processing = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        
        self.progress_label.setText('正在打开浏览器...')
        self.current_account_label.setText('请在浏览器中登录您的 Outlook 账号')
        
        # 启动手动授权线程
        group = self.group_combo.currentText()
        self.manual_thread = ManualOAuth2Thread(self.db, group)
        self.manual_thread.progress.connect(self.on_progress)
        self.manual_thread.finished_signal.connect(self.on_finished)
        self.manual_thread.start()
    
    def stop_auth(self):
        """停止授权"""
        if self.manual_thread:
            self.manual_thread.stop()
        self.is_processing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_label.setText('已停止')
    
    def on_progress(self, message):
        """进度更新"""
        self.progress_label.setText(message)
    
    def on_finished(self, email, client_id, refresh_token, error):
        """授权完成"""
        self.is_processing = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        if error:
            self.progress_label.setText('授权失败')
            self.result_text.append(f'❌ 失败: {error}')
        else:
            self.progress_label.setText('授权成功!')
            self.current_account_label.setText(f'已添加: {email}')
            self.result_text.append(f'✅ {email} - 授权成功，已添加到数据库')
            self.success_count += 1
            # 发送信号通知主窗口刷新
            self.import_completed.emit(1, 0)
    
    def close_dialog(self):
        """关闭对话框"""
        if self.is_processing:
            reply = QMessageBox.question(
                self, '确认',
                '正在处理中，确定要停止并关闭吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            self.stop_auth()
        self.accept()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.is_processing:
            self.stop_auth()
        event.accept()


class ManualOAuth2Thread(QThread):
    """手动 OAuth2 授权线程"""
    progress = pyqtSignal(str)  # message
    finished_signal = pyqtSignal(str, str, str, str)  # email, client_id, refresh_token, error
    
    def __init__(self, db, group):
        super().__init__()
        self.db = db
        self.group = group
        self.stop_flag = False
        self.selenium_oauth = None
    
    def run(self):
        try:
            from core.oauth2_helper import SeleniumOAuth2
            
            self.selenium_oauth = SeleniumOAuth2()
            
            # 初始化浏览器
            self.progress.emit('正在初始化浏览器...')
            success, error = self.selenium_oauth.init_driver()
            if not success:
                self.finished_signal.emit('', '', '', f'初始化浏览器失败: {error}')
                return
            
            # 使用半自动模式
            self.progress.emit('浏览器已打开，请手动登录任意 Outlook 账号...')
            
            client_id, refresh_token, error = self.selenium_oauth.authorize_semi_auto(
                email='',  # 不预填邮箱
                progress_callback=lambda msg: self.progress.emit(msg),
                timeout=300  # 5分钟超时
            )
            
            if error:
                self.finished_signal.emit('', '', '', error)
                return
            
            # 获取用户邮箱
            self.progress.emit('正在获取账号信息...')
            email = self.get_user_email(client_id, refresh_token)
            
            if not email:
                self.finished_signal.emit('', '', '', '无法获取邮箱地址')
                return
            
            # 保存到数据库
            self.progress.emit(f'正在保存账号: {email}')
            existing = self.db.get_account_by_email(email)
            if existing:
                # 更新现有账号的 OAuth2 信息
                self.db.update_account_oauth(existing[0], client_id, refresh_token)
            else:
                # 添加新账号（密码留空，因为有 OAuth2）
                self.db.add_account(email, '', self.group, client_id=client_id, refresh_token=refresh_token)
            
            self.finished_signal.emit(email, client_id, refresh_token, '')
            
        except Exception as e:
            self.finished_signal.emit('', '', '', f'授权出错: {str(e)}')
        finally:
            if self.selenium_oauth:
                self.selenium_oauth.close_driver()
    
    def get_user_email(self, client_id, refresh_token):
        """通过 refresh_token 获取用户邮箱"""
        import requests
        
        # 先用 refresh_token 获取 access_token
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            'client_id': client_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'offline_access https://outlook.office.com/IMAP.AccessAsUser.All https://outlook.office.com/SMTP.Send',
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            if response.status_code != 200:
                return None
            
            access_token = response.json().get('access_token')
            if not access_token:
                return None
            
            # 获取用户信息
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # 尝试 Outlook API
            try:
                resp = requests.get('https://outlook.office.com/api/v2.0/me', headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json().get('EmailAddress', '')
            except:
                pass
            
            # 尝试 Graph API
            try:
                resp = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get('mail') or data.get('userPrincipalName', '')
            except:
                pass
            
            return None
        except:
            return None
    
    def stop(self):
        self.stop_flag = True
        if self.selenium_oauth:
            self.selenium_oauth.close_driver()


class PieChartWidget(QWidget):
    """简单饼图组件"""
    
    def __init__(self, data, colors, parent=None):
        super().__init__(parent)
        self.data = data
        self.colors = colors
        self.setMinimumSize(150, 150)
    
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        from PyQt5.QtCore import QRectF
        import math
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算绘制区域
        size = min(self.width(), self.height()) - 20
        x = (self.width() - size) / 2
        y = (self.height() - size) / 2
        rect = QRectF(x, y, size, size)
        
        if not self.data:
            # 无数据时显示灰色圆
            painter.setBrush(QBrush(QColor('#E0E0E0')))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(rect)
            return
        
        total = sum(self.data.values())
        if total == 0:
            return
        
        start_angle = 90 * 16  # 从12点钟方向开始
        
        for i, (name, value) in enumerate(self.data.items()):
            # 计算扇形角度 (Qt 使用 1/16 度为单位)
            span_angle = int(value / total * 360 * 16)
            
            # 设置颜色
            color = QColor(self.colors[i % len(self.colors)])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor('#FFFFFF'), 2))
            
            # 绘制扇形
            painter.drawPie(rect, start_angle, -span_angle)
            
            start_angle -= span_angle
        
        painter.end()
