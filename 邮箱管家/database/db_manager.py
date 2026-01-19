# -*- coding: utf-8 -*-
"""
数据库管理模块 - SQLite本地存储
"""

import sqlite3
import os
import sys
from datetime import datetime


def get_app_dir():
    """获取程序所在目录，兼容打包后的exe"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe，使用exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，使用源码目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DatabaseManager:
    def __init__(self, db_path=None):
        # 数据库保存在程序所在目录的 data 文件夹下
        if db_path is None:
            base_dir = get_app_dir()
            db_path = os.path.join(base_dir, 'data', 'emails.db')
        
        self.db_path = db_path
        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 邮箱账号表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                group_name TEXT DEFAULT '默认分组',
                status TEXT DEFAULT '未检测',
                account_type TEXT DEFAULT '普通',
                imap_server TEXT,
                imap_port INTEGER DEFAULT 993,
                smtp_server TEXT,
                smtp_port INTEGER DEFAULT 465,
                client_id TEXT,
                refresh_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check TIMESTAMP
            )
        ''')
        
        # 检查并添加缺失的列（兼容旧数据库）
        cursor.execute("PRAGMA table_info(accounts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'client_id' not in columns:
            cursor.execute('ALTER TABLE accounts ADD COLUMN client_id TEXT')
        if 'refresh_token' not in columns:
            cursor.execute('ALTER TABLE accounts ADD COLUMN refresh_token TEXT')
        if 'has_aws_code' not in columns:
            cursor.execute('ALTER TABLE accounts ADD COLUMN has_aws_code INTEGER DEFAULT 0')
        if 'remark' not in columns:
            cursor.execute('ALTER TABLE accounts ADD COLUMN remark TEXT')
        
        # 设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # 默认设置
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('font_size', '13')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('language', 'zh')")
        
        # 分组表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 邮件缓存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                uid TEXT,
                sender TEXT,
                subject TEXT,
                date TIMESTAMP,
                body TEXT,
                is_read INTEGER DEFAULT 0,
                folder TEXT DEFAULT 'INBOX',
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )
        ''')
        
        # 插入默认分组
        cursor.execute("INSERT OR IGNORE INTO groups (name) VALUES ('默认分组')")
        
        conn.commit()
        conn.close()
    
    # ========== 账号管理 ==========
    def add_account(self, email, password, group='默认分组', imap_server=None, imap_port=993,
                    client_id=None, refresh_token=None):
        """添加邮箱账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 自动识别邮箱服务器
            if not imap_server:
                imap_server, smtp_server = self.detect_server(email)
            else:
                smtp_server = imap_server.replace('imap', 'smtp')
            
            # 判断账号类型
            account_type = 'OAuth2' if client_id and refresh_token else '普通'
            
            cursor.execute('''
                INSERT INTO accounts (email, password, group_name, imap_server, imap_port, 
                                      smtp_server, client_id, refresh_token, account_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password, group, imap_server, imap_port, smtp_server, 
                  client_id, refresh_token, account_type))
            conn.commit()
            return True, "添加成功"
        except sqlite3.IntegrityError:
            return False, "邮箱已存在"
        finally:
            conn.close()
    
    def detect_server(self, email):
        """根据邮箱后缀自动识别服务器"""
        domain = email.split('@')[-1].lower()
        servers = {
            'outlook.com': ('imap-mail.outlook.com', 'smtp-mail.outlook.com'),
            'hotmail.com': ('imap-mail.outlook.com', 'smtp-mail.outlook.com'),
            'gmail.com': ('imap.gmail.com', 'smtp.gmail.com'),
            'qq.com': ('imap.qq.com', 'smtp.qq.com'),
            '163.com': ('imap.163.com', 'smtp.163.com'),
            '126.com': ('imap.126.com', 'smtp.126.com'),
            'sina.com': ('imap.sina.com', 'smtp.sina.com'),
            'yahoo.com': ('imap.mail.yahoo.com', 'smtp.mail.yahoo.com'),
        }
        return servers.get(domain, (f'imap.{domain}', f'smtp.{domain}'))
    
    def get_all_accounts(self):
        """获取所有账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts ORDER BY id DESC')
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def get_accounts_by_group(self, group_name):
        """按分组获取账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE group_name = ?', (group_name,))
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def get_account_by_email(self, email):
        """根据邮箱地址获取账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE email = ?', (email,))
        account = cursor.fetchone()
        conn.close()
        return account
    
    def update_account_oauth(self, account_id, client_id, refresh_token):
        """更新账号的 OAuth2 凭据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts 
            SET client_id = ?, refresh_token = ?, account_type = 'OAuth2'
            WHERE id = ?
        ''', (client_id, refresh_token, account_id))
        conn.commit()
        conn.close()
    
    def update_account_status(self, account_id, status):
        """更新账号状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts SET status = ?, last_check = ? WHERE id = ?
        ''', (status, datetime.now(), account_id))
        conn.commit()
        conn.close()
    
    def delete_account(self, account_id):
        """删除账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        cursor.execute('DELETE FROM emails WHERE account_id = ?', (account_id,))
        conn.commit()
        conn.close()
    
    def update_account_group(self, account_id, group_name):
        """更新账号分组"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET group_name = ? WHERE id = ?', (group_name, account_id))
        conn.commit()
        conn.close()
    
    # ========== 分组管理 ==========
    def get_all_groups(self):
        """获取所有分组"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups')
        groups = cursor.fetchall()
        conn.close()
        return groups
    
    def add_group(self, name):
        """添加分组"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO groups (name) VALUES (?)', (name,))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def delete_group(self, name):
        """删除分组"""
        if name == '默认分组':
            return False
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET group_name = ? WHERE group_name = ?', ('默认分组', name))
        cursor.execute('DELETE FROM groups WHERE name = ?', (name,))
        conn.commit()
        conn.close()
        return True
    
    def rename_group(self, old_name, new_name):
        """重命名分组"""
        if old_name == '默认分组':
            return False
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE groups SET name = ? WHERE name = ?', (new_name, old_name))
            cursor.execute('UPDATE accounts SET group_name = ? WHERE group_name = ?', (new_name, old_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_account_count(self):
        """获取账号总数"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM accounts')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # ========== AWS验证码标记 ==========
    def update_aws_code_status(self, account_id, has_code):
        """更新账号的AWS验证码状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET has_aws_code = ? WHERE id = ?', (1 if has_code else 0, account_id))
        conn.commit()
        conn.close()
    
    def update_account_remark(self, account_id, remark):
        """更新账号备注"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET remark = ? WHERE id = ?', (remark, account_id))
        conn.commit()
        conn.close()
    
    # ========== 设置管理 ==========
    def get_setting(self, key, default=None):
        """获取设置值"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key, value):
        """保存设置值"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
    
    def get_all_accounts_sorted(self, sort_by='id', sort_order='DESC'):
        """获取排序后的所有账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        valid_columns = ['id', 'email', 'group_name', 'status', 'account_type', 'has_aws_code']
        if sort_by not in valid_columns:
            sort_by = 'id'
        order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
        cursor.execute(f'SELECT * FROM accounts ORDER BY {sort_by} {order}')
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def get_accounts_by_group_sorted(self, group_name, sort_by='id', sort_order='DESC'):
        """按分组获取排序后的账号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        valid_columns = ['id', 'email', 'group_name', 'status', 'account_type', 'has_aws_code']
        if sort_by not in valid_columns:
            sort_by = 'id'
        order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
        cursor.execute(f'SELECT * FROM accounts WHERE group_name = ? ORDER BY {sort_by} {order}', (group_name,))
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    

