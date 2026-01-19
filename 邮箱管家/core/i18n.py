# -*- coding: utf-8 -*-
"""
多语言支持模块 - 中英文切换
"""

# 语言包
TRANSLATIONS = {
    'zh': {
        # 主窗口
        'app_title': '邮箱管家',
        'app_name': '邮箱管家',
        'email_management': '邮箱管理',
        'manage_all_accounts': '管理您的所有邮箱账号',
        'current_group': '当前分组',
        'search_email': '搜索邮箱地址...',
        'all_groups': '全部分组',
        'all_emails': '全部邮箱',
        'groups': '分组',
        'import_email': '导入邮箱',
        'export_backup': '导出备份',
        'move_group': '移动分组',
        'batch_send': '批量发信',
        'batch_check': '批量检测',
        'batch_delete': '批量删除',
        'checking': '检测中...',
        'total_records': '共 {0} 条记录',
        'close': '关闭',
        'switch_theme': '切换主题',
        'switch_language': '切换语言',
        
        # 表格列
        'col_checkbox': '',
        'col_index': '#',
        'col_email': '邮箱地址',
        'col_password': '密码',
        'col_group': '分组',
        'col_status': '状态',
        'col_type': '类型',
        'col_aws': 'AWS',
        'col_operation': '操作',
        
        # 操作按钮
        'view': '查看',
        'delete': '删除',
        'copy': '复制',
        'show': '显示',
        'hide': '隐藏',
        'copied': '已复制',
        
        # 更多菜单
        'check_this_row': '勾选本行',
        'check_from_row': '从本行勾选N个',
        'check_all': '勾选全部数据',
        'uncheck_all': '取消全部勾选',
        'check_count_title': '勾选数量',
        'check_count_msg': '从第 {0} 行开始勾选几个？\n(最多 {1} 个)',
        
        # 状态
        'status_normal': '正常',
        'status_error': '异常',
        'status_unchecked': '未检测',
        
        # 排序
        'sort_by': '排序',
        'sort_default': '默认排序',
        'sort_by_email': '按邮箱排序',
        'sort_by_status': '按状态排序',
        'sort_by_aws': '按AWS标记排序',
        
        # 设置
        'settings': '设置',
        'settings_desc': '配置应用程序的外观和行为，修改后即时生效',
        'theme_settings': '主题设置',
        'theme_settings_desc': '选择你喜欢的界面主题',
        'general_settings': '常规设置',
        'general_settings_desc': '配置应用程序的基本选项',
        'font_size': '字体大小',
        'language': '语言',
        'chinese': '中文',
        'english': 'English',
        'save': '保存',
        'cancel': '取消',
        'settings_saved': '设置已保存，部分设置需要重启生效',
        
        # 消息
        'confirm': '确认',
        'success': '成功',
        'error': '错误',
        'warning': '提示',
        'please_select_account': '请先选择账号',
        'confirm_delete': '确定要删除选中的 {0} 个账号吗？',
        'confirm_delete_single': '确定要删除这个账号吗？',
        'no_accounts_to_check': '没有可检测的账号',
        'check_complete': '状态检测完成',
        'moved_to_group': '已将 {0} 个账号移动到 "{1}"',
        'exported_accounts': '已导出 {0} 个账号',
        'please_select_send_account': '请先选择要发送邮件的账号',
        
        # 邮件查看
        'email_title': '邮件 - {0}',
        'folder_inbox': '收件箱',
        'folder_junk': '垃圾邮件',
        'folder_sent': '已发送',
        'folder_drafts': '草稿箱',
        'folder_deleted': '已删除',
        'refresh': '刷新',
        'search_email_placeholder': '搜索邮件...',
        'compose': '写邮件',
        'reply': '回复',
        'forward': '转发',
        'mark': '标记',
        'loading': '加载中...',
        'select_email_to_view': '选择一封邮件查看',
        'no_emails': '{0} 暂无邮件',
        'no_subject': '(无主题)',
        'mark_as_unread': '标为未读',
        'mark_as_read': '标为已读',
        'sender': '发件人',
        'time': '时间',
        'attachment': '附件',
        'save_attachment': '保存附件',
        'attachment_saved': '附件已保存到:\n{0}',
        'download_failed': '无法下载附件',
        'save_failed': '保存失败: {0}',
        
        # 导入对话框
        'import_title': '导入邮箱账号',
        'import_format_hint': '支持格式：每行一个 邮箱----密码，或使用 $ 分隔多个账号',
        'import_placeholder': 'example@outlook.com----password123',
        'import_to_group': '导入到分组:',
        'import_from_file': '从文件导入',
        'import_from_clipboard': '从剪贴板',
        'skip_duplicate': '跳过已存在的邮箱（去重）',
        'import_btn': '导入',
        'import_result': '成功: {0} 个\n失败: {1} 个',
        'import_result_with_skip': '成功: {0} 个\n失败: {1} 个\n跳过(重复): {2} 个',
        'please_input_account': '请输入账号信息',
        'read_failed': '读取失败: {0}',
        'clipboard_empty': '剪贴板为空或没有文本内容',
        'clipboard_format_error': '剪贴板内容格式不正确',
        
        # 侧边栏
        'all_accounts': '全部账号',
        'default_group': '默认分组',
        'add_group': '添加分组',
        'rename_group': '重命名',
        'delete_group': '删除分组',
        'group_name': '分组名称',
        'new_group_name': '新分组名称',
        'group_exists': '分组已存在',
        'cannot_delete_default': '无法删除默认分组',
        'confirm_delete_group': '确定要删除分组 "{0}" 吗？\n该分组下的账号将移动到默认分组。',
        
        # AWS 标记
        'has_aws_code': '有',
        'no_aws_code': '-',
        
        # 主题
        'toggle_theme': '切换主题',
        'light_theme': '浅色模式',
        'dark_theme': '深色模式',
        
        # 仪表盘
        'dashboard': '仪表盘',
        'view_dashboard': '查看仪表盘',
        'dashboard_desc': '查看账号统计数据和分布情况',
        'stats_by_group': '分组分布',
        'stats_by_status': '状态分布',
        'total_accounts': '总账号数',
        'normal_accounts': '正常账号',
        'error_accounts': '异常账号',
        'unchecked_accounts': '未检测',
        
        # 手动授权
        'manual_oauth': '手动授权',
        
        # 备注
        'col_remark': '备注',
        'edit_remark': '编辑备注',
        'remark_saved': '备注已保存',
        
        # 数据和关于
        'data_location': '数据位置',
        'open_folder': '打开文件夹',
        'about': '关于',
    },
    'en': {
        # Main window
        'app_title': 'Email Manager',
        'app_name': 'Email Manager',
        'email_management': 'Email Management',
        'manage_all_accounts': 'Manage all your email accounts',
        'current_group': 'Current Group',
        'search_email': 'Search email address...',
        'all_groups': 'All Groups',
        'all_emails': 'All Emails',
        'groups': 'Groups',
        'import_email': 'Import',
        'export_backup': 'Export',
        'move_group': 'Move Group',
        'batch_send': 'Batch Send',
        'batch_check': 'Check Status',
        'batch_delete': 'Delete',
        'checking': 'Checking...',
        'total_records': 'Total {0} records',
        'close': 'Close',
        'switch_theme': 'Switch Theme',
        'switch_language': 'Switch Language',
        
        # Table columns
        'col_checkbox': '',
        'col_index': '#',
        'col_email': 'Email',
        'col_password': 'Password',
        'col_group': 'Group',
        'col_status': 'Status',
        'col_type': 'Type',
        'col_aws': 'AWS',
        'col_operation': 'Actions',
        
        # Action buttons
        'view': 'View',
        'delete': 'Delete',
        'copy': 'Copy',
        'show': 'Show',
        'hide': 'Hide',
        'copied': 'Copied',
        
        # More menu
        'check_this_row': 'Check this row',
        'check_from_row': 'Check N rows from here',
        'check_all': 'Check all',
        'uncheck_all': 'Uncheck all',
        'check_count_title': 'Check Count',
        'check_count_msg': 'Check how many from row {0}?\n(Max {1})',
        
        # Status
        'status_normal': 'Normal',
        'status_error': 'Error',
        'status_unchecked': 'Unchecked',
        
        # Sort
        'sort_by': 'Sort',
        'sort_default': 'Default',
        'sort_by_email': 'By Email',
        'sort_by_status': 'By Status',
        'sort_by_aws': 'By AWS',
        
        # Settings
        'settings': 'Settings',
        'settings_desc': 'Configure app appearance and behavior, changes take effect immediately',
        'theme_settings': 'Theme Settings',
        'theme_settings_desc': 'Choose your preferred interface theme',
        'general_settings': 'General Settings',
        'general_settings_desc': 'Configure basic application options',
        'font_size': 'Font Size',
        'language': 'Language',
        'chinese': '中文',
        'english': 'English',
        'save': 'Save',
        'cancel': 'Cancel',
        'settings_saved': 'Settings saved. Some changes require restart.',
        
        # Messages
        'confirm': 'Confirm',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'please_select_account': 'Please select accounts first',
        'confirm_delete': 'Delete {0} selected accounts?',
        'confirm_delete_single': 'Delete this account?',
        'no_accounts_to_check': 'No accounts to check',
        'check_complete': 'Status check complete',
        'moved_to_group': 'Moved {0} accounts to "{1}"',
        'exported_accounts': 'Exported {0} accounts',
        'please_select_send_account': 'Please select accounts to send email',
        
        # Email view
        'email_title': 'Email - {0}',
        'folder_inbox': 'Inbox',
        'folder_junk': 'Junk',
        'folder_sent': 'Sent',
        'folder_drafts': 'Drafts',
        'folder_deleted': 'Deleted',
        'refresh': 'Refresh',
        'search_email_placeholder': 'Search emails...',
        'compose': 'Compose',
        'reply': 'Reply',
        'forward': 'Forward',
        'mark': 'Mark',
        'loading': 'Loading...',
        'select_email_to_view': 'Select an email to view',
        'no_emails': 'No emails in {0}',
        'no_subject': '(No Subject)',
        'mark_as_unread': 'Mark Unread',
        'mark_as_read': 'Mark Read',
        'sender': 'From',
        'time': 'Time',
        'attachment': 'Attachment',
        'save_attachment': 'Save Attachment',
        'attachment_saved': 'Attachment saved to:\n{0}',
        'download_failed': 'Failed to download attachment',
        'save_failed': 'Save failed: {0}',
        
        # Import dialog
        'import_title': 'Import Email Accounts',
        'import_format_hint': 'Format: email----password per line, or use $ to separate',
        'import_placeholder': 'example@outlook.com----password123',
        'import_to_group': 'Import to group:',
        'import_from_file': 'From File',
        'import_from_clipboard': 'From Clipboard',
        'skip_duplicate': 'Skip existing emails (deduplicate)',
        'import_btn': 'Import',
        'import_result': 'Success: {0}\nFailed: {1}',
        'import_result_with_skip': 'Success: {0}\nFailed: {1}\nSkipped (duplicate): {2}',
        'please_input_account': 'Please input account info',
        'read_failed': 'Read failed: {0}',
        'clipboard_empty': 'Clipboard is empty',
        'clipboard_format_error': 'Invalid clipboard content format',
        
        # Sidebar
        'all_accounts': 'All Accounts',
        'default_group': 'Default',
        'add_group': 'Add Group',
        'rename_group': 'Rename',
        'delete_group': 'Delete Group',
        'group_name': 'Group Name',
        'new_group_name': 'New Group Name',
        'group_exists': 'Group already exists',
        'cannot_delete_default': 'Cannot delete default group',
        'confirm_delete_group': 'Delete group "{0}"?\nAccounts will be moved to default group.',
        
        # AWS mark
        'has_aws_code': 'Yes',
        'no_aws_code': '-',
        
        # Theme
        'toggle_theme': 'Toggle Theme',
        'light_theme': 'Light Mode',
        'dark_theme': 'Dark Mode',
        
        # Dashboard
        'dashboard': 'Dashboard',
        'view_dashboard': 'View dashboard',
        'dashboard_desc': 'View account statistics and distribution',
        'stats_by_group': 'By Group',
        'stats_by_status': 'By Status',
        'total_accounts': 'Total Accounts',
        'normal_accounts': 'Normal',
        'error_accounts': 'Error',
        'unchecked_accounts': 'Unchecked',
        
        # Manual OAuth
        'manual_oauth': 'Manual Auth',
        
        # Remark
        'col_remark': 'Remark',
        'edit_remark': 'Edit Remark',
        'remark_saved': 'Remark saved',
        
        # Data and About
        'data_location': 'Data Location',
        'open_folder': 'Open Folder',
        'about': 'About',
    }
}

# 当前语言
_current_lang = 'zh'


def set_language(lang):
    """设置当前语言"""
    global _current_lang
    if lang in TRANSLATIONS:
        _current_lang = lang


def get_language():
    """获取当前语言"""
    return _current_lang


def tr(key, *args):
    """翻译函数
    key: 翻译键
    args: 格式化参数
    """
    text = TRANSLATIONS.get(_current_lang, TRANSLATIONS['zh']).get(key, key)
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text
