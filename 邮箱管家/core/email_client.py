# -*- coding: utf-8 -*-
"""
邮件客户端模块 - 支持 OAuth2 (Graph API) 和普通 IMAP/SMTP
"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
import requests
import os
import base64
from datetime import datetime


class EmailClient:
    # SMTP 服务器映射
    SMTP_SERVERS = {
        'outlook.com': ('smtp-mail.outlook.com', 587),
        'hotmail.com': ('smtp-mail.outlook.com', 587),
        'live.com': ('smtp-mail.outlook.com', 587),
        'gmail.com': ('smtp.gmail.com', 587),
        'qq.com': ('smtp.qq.com', 465),
        '163.com': ('smtp.163.com', 465),
        '126.com': ('smtp.126.com', 465),
    }
    
    def __init__(self, email_addr, password, imap_server=None, imap_port=993, 
                 client_id=None, refresh_token=None, account_id=None, db_manager=None):
        self.email_addr = email_addr
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.connection = None
        self.account_id = account_id  # 账号ID，用于更新数据库
        self.db_manager = db_manager  # 数据库管理器，用于保存新的refresh_token
        
        if not self.imap_server:
            self.imap_server = self.detect_server(email_addr)
    
    def detect_server(self, email_addr):
        domain = email_addr.split('@')[-1].lower()
        servers = {
            'outlook.com': 'outlook.office365.com',
            'hotmail.com': 'outlook.office365.com',
            'live.com': 'outlook.office365.com',
            'gmail.com': 'imap.gmail.com',
            'qq.com': 'imap.qq.com',
            '163.com': 'imap.163.com',
        }
        return servers.get(domain, f'imap.{domain}')
    
    def is_outlook(self):
        domain = self.email_addr.split('@')[-1].lower()
        return domain in ['outlook.com', 'hotmail.com', 'live.com', 'msn.com']
    
    def use_graph_api(self):
        """判断是否使用 Graph API"""
        return self.is_outlook() and self.client_id and self.refresh_token
    
    def get_api_type(self):
        """根据 token scope 判断使用哪个 API"""
        # 先获取 token 看 scope
        if not self.access_token:
            self.get_oauth2_access_token()
        return getattr(self, '_api_type', 'graph')
    
    def get_oauth2_access_token(self):
        """使用 refresh_token 获取 access_token"""
        if not self.client_id or not self.refresh_token:
            return None, "缺少 client_id 或 refresh_token"
        
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                scope = result.get('scope', '')
                
                # 检查是否返回了新的 refresh_token，如果有则更新
                new_refresh_token = result.get('refresh_token')
                if new_refresh_token and new_refresh_token != self.refresh_token:
                    self.refresh_token = new_refresh_token
                    # 如果有数据库管理器和账号ID，自动保存新的 refresh_token
                    if self.db_manager and self.account_id:
                        try:
                            self.db_manager.update_account_oauth(
                                self.account_id, self.client_id, new_refresh_token
                            )
                        except Exception as e:
                            print(f"保存新 refresh_token 失败: {e}")
                
                # 根据 scope 判断 API 类型
                if 'outlook.office.com' in scope:
                    self._api_type = 'outlook'
                else:
                    self._api_type = 'graph'
                
                return self.access_token, "获取成功"
            else:
                error_data = response.json()
                error = error_data.get('error_description', response.text)
                return None, f"OAuth2 错误: {error}"
        except Exception as e:
            return None, f"网络错误: {str(e)}"
    
    def check_status(self):
        """检测账号状态"""
        if self.use_graph_api():
            token, msg = self.get_oauth2_access_token()
            if token:
                headers = {'Authorization': f'Bearer {token}'}
                try:
                    # 根据 API 类型选择不同的端点
                    if self._api_type == 'outlook':
                        url = 'https://outlook.office.com/api/v2.0/me/mailfolders/inbox/messages?$top=1'
                    else:
                        url = 'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=1'
                    
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        return "正常", "Token 有效"
                    else:
                        return "异常", f"API 错误: {resp.status_code}"
                except Exception as e:
                    return "异常", f"网络错误: {e}"
            else:
                return "异常", msg
        else:
            # 普通 IMAP 检测
            success, msg = self.connect_imap()
            if success:
                self.disconnect()
                return "正常", msg
            return "异常", msg
    
    def connect_imap(self):
        """连接 IMAP 服务器（普通密码认证）"""
        try:
            context = ssl.create_default_context()
            self.connection = imaplib.IMAP4_SSL(
                self.imap_server, self.imap_port, ssl_context=context
            )
            self.connection.login(self.email_addr, self.password)
            return True, "连接成功"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def disconnect(self):
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    # 文件夹映射 - 统一不同API的文件夹名称
    FOLDER_MAP = {
        'graph': {
            'inbox': 'inbox',
            'junk': 'junkemail',
            'sent': 'sentitems',
            'drafts': 'drafts',
            'deleted': 'deleteditems',
        },
        'outlook': {
            'inbox': 'inbox',
            'junk': 'junkemail', 
            'sent': 'sentitems',
            'drafts': 'drafts',
            'deleted': 'deleteditems',
        },
        'imap': {
            'inbox': 'INBOX',
            'junk': 'Junk',  # Outlook IMAP
            'sent': 'Sent',
            'drafts': 'Drafts',
            'deleted': 'Deleted',
        },
        'imap_gmail': {
            'inbox': 'INBOX',
            'junk': '[Gmail]/Spam',
            'sent': '[Gmail]/Sent Mail',
            'drafts': '[Gmail]/Drafts',
            'deleted': '[Gmail]/Trash',
        },
        'imap_qq': {
            'inbox': 'INBOX',
            'junk': 'Junk',
            'sent': 'Sent Messages',
            'drafts': 'Drafts',
            'deleted': 'Deleted Messages',
        },
        'imap_163': {
            'inbox': 'INBOX',
            'junk': '垃圾邮件',
            'sent': '已发送',
            'drafts': '草稿箱',
            'deleted': '已删除',
        }
    }
    
    def get_folder_name(self, folder_key):
        """根据邮箱类型获取实际文件夹名称"""
        if self.use_graph_api():
            api_type = self.get_api_type()
            return self.FOLDER_MAP.get(api_type, self.FOLDER_MAP['graph']).get(folder_key, folder_key)
        else:
            # IMAP - 根据域名选择映射
            domain = self.email_addr.split('@')[-1].lower()
            if 'gmail' in domain:
                mapping = self.FOLDER_MAP['imap_gmail']
            elif 'qq.com' in domain:
                mapping = self.FOLDER_MAP['imap_qq']
            elif '163.com' in domain or '126.com' in domain:
                mapping = self.FOLDER_MAP['imap_163']
            else:
                mapping = self.FOLDER_MAP['imap']
            return mapping.get(folder_key, folder_key)
    
    def fetch_emails(self, folder='inbox', limit=50):
        """获取邮件列表
        folder: inbox, junk, sent, drafts, deleted
        """
        if self.use_graph_api():
            return self.fetch_emails_graph(folder, limit)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.fetch_emails_imap(actual_folder, limit)
    
    def fetch_emails_graph(self, folder='inbox', limit=50):
        """使用 Graph API 或 Outlook REST API 获取邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return [], msg
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 获取实际文件夹名称
        folder_name = self.get_folder_name(folder)
        
        # 根据 API 类型选择不同的端点
        if self._api_type == 'outlook':
            url = f'https://outlook.office.com/api/v2.0/me/mailfolders/{folder_name}/messages'
            params = {
                '$top': limit,
                '$orderby': 'ReceivedDateTime desc',
                '$select': 'Id,Subject,From,ReceivedDateTime,BodyPreview,Body,IsRead,HasAttachments'
            }
        else:
            url = f'https://graph.microsoft.com/v1.0/me/mailFolders/{folder_name}/messages'
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,from,receivedDateTime,bodyPreview,body,isRead,hasAttachments'
            }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                emails = []
                for msg in data.get('value', []):
                    # Outlook API 和 Graph API 字段名大小写不同
                    if self._api_type == 'outlook':
                        from_info = msg.get('From', {}).get('EmailAddress', {})
                        sender = from_info.get('Name', '') or from_info.get('Address', '')
                        date_str = msg.get('ReceivedDateTime', '')
                        subject = msg.get('Subject', '(无主题)')
                        body = msg.get('Body', {}).get('Content', '') or msg.get('BodyPreview', '')
                        uid = msg.get('Id', '')
                    else:
                        from_info = msg.get('from', {}).get('emailAddress', {})
                        sender = from_info.get('name', '') or from_info.get('address', '')
                        date_str = msg.get('receivedDateTime', '')
                        subject = msg.get('subject', '(无主题)')
                        body = msg.get('body', {}).get('content', '') or msg.get('bodyPreview', '')
                        uid = msg.get('id', '')
                    
                    # 解析时间
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        date = None
                    
                    emails.append({
                        'uid': uid,
                        'subject': subject,
                        'sender': sender,
                        'sender_email': from_info.get('address', '') if self._api_type != 'outlook' else from_info.get('Address', ''),
                        'date': date,
                        'body': body,
                        'is_read': msg.get('isRead', True) if self._api_type != 'outlook' else msg.get('IsRead', True),
                        'has_attachments': msg.get('hasAttachments', False) if self._api_type != 'outlook' else msg.get('HasAttachments', False)
                    })
                return emails, "获取成功"
            else:
                return [], f"API 错误: {response.status_code} - {response.text[:200]}"
        except Exception as e:
            return [], f"网络错误: {str(e)}"
    
    def fetch_emails_imap(self, folder='INBOX', limit=50):
        """使用 IMAP 获取邮件"""
        success, msg = self.connect_imap()
        if not success:
            return [], msg
        
        try:
            # 选择文件夹并检查返回状态
            select_status, select_data = self.connection.select(folder)
            if select_status != 'OK':
                return [], f"无法打开文件夹 {folder}: {select_data}"
            
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                return [], "获取邮件失败"
            
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            email_ids.reverse()
            
            emails = []
            for eid in email_ids:
                status, msg_data = self.connection.fetch(eid, '(RFC822 FLAGS)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # 检查是否已读
                    flags = msg_data[0][0].decode() if isinstance(msg_data[0][0], bytes) else str(msg_data[0][0])
                    is_read = '\\Seen' in flags
                    
                    subject = self.decode_str(email_message.get('Subject', ''))
                    sender = self.decode_str(email_message.get('From', ''))
                    date_str = email_message.get('Date', '')
                    
                    try:
                        date = parsedate_to_datetime(date_str)
                    except:
                        date = None
                    
                    body = self.get_email_body(email_message)
                    
                    emails.append({
                        'uid': eid.decode() if isinstance(eid, bytes) else str(eid),
                        'subject': subject,
                        'sender': sender,
                        'sender_email': self.extract_email_address(sender),
                        'date': date,
                        'body': body,
                        'is_read': is_read,
                        'has_attachments': self.has_attachments(email_message)
                    })
            
            return emails, "获取成功"
        except Exception as e:
            return [], f"获取邮件失败: {str(e)}"
    
    def decode_str(self, s):
        if not s:
            return ''
        decoded_parts = decode_header(s)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(charset or 'utf-8', errors='ignore'))
                except:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(part)
        return ''.join(result)
    
    def get_email_body(self, msg):
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except:
                pass
        return body[:5000]
    
    def extract_email_address(self, sender_str):
        """从发件人字符串中提取邮箱地址"""
        import re
        match = re.search(r'<([^>]+)>', sender_str)
        if match:
            return match.group(1)
        # 如果没有尖括号，可能整个字符串就是邮箱
        if '@' in sender_str:
            return sender_str.strip()
        return ''
    
    def has_attachments(self, msg):
        """检查邮件是否有附件"""
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get('Content-Disposition', '')
                if 'attachment' in content_disposition:
                    return True
        return False
    
    def mark_as_read(self, email_id, folder='inbox', is_read=True):
        """标记邮件为已读/未读"""
        if self.use_graph_api():
            return self.mark_as_read_graph(email_id, is_read)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.mark_as_read_imap(email_id, actual_folder, is_read)
    
    def mark_as_read_graph(self, email_id, is_read=True):
        """使用 Graph API 标记邮件已读/未读"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return False, msg
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        if self._api_type == 'outlook':
            url = f'https://outlook.office.com/api/v2.0/me/messages/{email_id}'
            data = {'IsRead': is_read}
        else:
            url = f'https://graph.microsoft.com/v1.0/me/messages/{email_id}'
            data = {'isRead': is_read}
        
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return True, "标记成功"
            else:
                return False, f"标记失败: {response.status_code}"
        except Exception as e:
            return False, f"网络错误: {str(e)}"
    
    def mark_as_read_imap(self, email_id, folder='INBOX', is_read=True):
        """使用 IMAP 标记邮件已读/未读"""
        success, msg = self.connect_imap()
        if not success:
            return False, msg
        
        try:
            self.connection.select(folder)
            flag_action = '+FLAGS' if is_read else '-FLAGS'
            eid = email_id.encode() if isinstance(email_id, str) else email_id
            self.connection.store(eid, flag_action, '\\Seen')
            return True, "标记成功"
        except Exception as e:
            return False, f"标记失败: {str(e)}"
        finally:
            self.disconnect()
    
    def mark_emails_batch(self, email_ids, folder='inbox', is_read=True, progress_callback=None):
        """批量标记邮件已读/未读（优化性能，复用连接）
        email_ids: 邮件ID列表
        folder: 当前文件夹
        is_read: True=标记已读, False=标记未读
        progress_callback: 进度回调函数 (current, total)
        返回: (success_count, fail_count)
        """
        if self.use_graph_api():
            return self.mark_emails_batch_graph(email_ids, is_read, progress_callback)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.mark_emails_batch_imap(email_ids, actual_folder, is_read, progress_callback)
    
    def mark_emails_batch_graph(self, email_ids, is_read=True, progress_callback=None):
        """使用 Graph API 批量标记邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return 0, len(email_ids)
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        if self._api_type == 'outlook':
            base_url = 'https://outlook.office.com/api/v2.0/me/messages'
            data = {'IsRead': is_read}
        else:
            base_url = 'https://graph.microsoft.com/v1.0/me/messages'
            data = {'isRead': is_read}
        
        success_count = 0
        fail_count = 0
        total = len(email_ids)
        
        for i, email_id in enumerate(email_ids):
            try:
                url = f'{base_url}/{email_id}'
                response = requests.patch(url, headers=headers, json=data, timeout=30)
                if response.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
            except:
                fail_count += 1
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return success_count, fail_count
    
    def mark_emails_batch_imap(self, email_ids, folder='INBOX', is_read=True, progress_callback=None):
        """使用 IMAP 批量标记邮件（复用连接）"""
        success, msg = self.connect_imap()
        if not success:
            return 0, len(email_ids)
        
        success_count = 0
        fail_count = 0
        total = len(email_ids)
        flag_action = '+FLAGS' if is_read else '-FLAGS'
        
        try:
            self.connection.select(folder)
            
            for i, email_id in enumerate(email_ids):
                try:
                    eid = email_id.encode() if isinstance(email_id, str) else email_id
                    self.connection.store(eid, flag_action, '\\Seen')
                    success_count += 1
                except:
                    fail_count += 1
                
                if progress_callback:
                    progress_callback(i + 1, total)
            
        except Exception as e:
            return 0, total
        finally:
            self.disconnect()
        
        return success_count, fail_count
    
    def get_attachments(self, email_id, folder='inbox'):
        """获取邮件附件列表"""
        if self.use_graph_api():
            return self.get_attachments_graph(email_id)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.get_attachments_imap(email_id, actual_folder)
    
    def get_attachments_graph(self, email_id):
        """使用 Graph API 获取附件列表"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return [], msg
        
        headers = {'Authorization': f'Bearer {token}'}
        
        if self._api_type == 'outlook':
            url = f'https://outlook.office.com/api/v2.0/me/messages/{email_id}/attachments'
        else:
            url = f'https://graph.microsoft.com/v1.0/me/messages/{email_id}/attachments'
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                attachments = []
                for att in data.get('value', []):
                    if self._api_type == 'outlook':
                        attachments.append({
                            'id': att.get('Id', ''),
                            'name': att.get('Name', ''),
                            'size': att.get('Size', 0),
                            'content_type': att.get('ContentType', ''),
                            'content_bytes': att.get('ContentBytes', '')
                        })
                    else:
                        attachments.append({
                            'id': att.get('id', ''),
                            'name': att.get('name', ''),
                            'size': att.get('size', 0),
                            'content_type': att.get('contentType', ''),
                            'content_bytes': att.get('contentBytes', '')
                        })
                return attachments, "获取成功"
            else:
                return [], f"获取附件失败: {response.status_code}"
        except Exception as e:
            return [], f"网络错误: {str(e)}"
    
    def get_attachments_imap(self, email_id, folder='INBOX'):
        """使用 IMAP 获取附件列表"""
        success, msg = self.connect_imap()
        if not success:
            return [], msg
        
        try:
            self.connection.select(folder)
            eid = email_id.encode() if isinstance(email_id, str) else email_id
            status, msg_data = self.connection.fetch(eid, '(RFC822)')
            
            if status != 'OK':
                return [], "获取邮件失败"
            
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            attachments = []
            for part in email_message.walk():
                content_disposition = part.get('Content-Disposition', '')
                if 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self.decode_str(filename)
                        content = part.get_payload(decode=True)
                        attachments.append({
                            'id': filename,
                            'name': filename,
                            'size': len(content) if content else 0,
                            'content_type': part.get_content_type(),
                            'content_bytes': base64.b64encode(content).decode() if content else ''
                        })
            
            return attachments, "获取成功"
        except Exception as e:
            return [], f"获取附件失败: {str(e)}"
        finally:
            self.disconnect()
    
    def download_attachment(self, attachment):
        """下载附件（返回二进制内容）"""
        content_bytes = attachment.get('content_bytes', '')
        if content_bytes:
            return base64.b64decode(content_bytes)
        return None
    
    def send_email_with_attachments(self, to_addr, subject, body, attachments=None, cc_addr=None):
        """发送带附件的邮件
        attachments: 附件文件路径列表
        """
        if self.use_graph_api():
            return self.send_email_graph_with_attachments(to_addr, subject, body, attachments, cc_addr)
        else:
            return self.send_email_smtp_with_attachments(to_addr, subject, body, attachments, cc_addr)
    
    def send_email_graph_with_attachments(self, to_addr, subject, body, attachments=None, cc_addr=None):
        """使用 Graph API 发送带附件的邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return False, msg
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        to_recipients = [{'emailAddress': {'address': addr.strip()}} 
                        for addr in to_addr.split(',') if addr.strip()]
        
        cc_recipients = []
        if cc_addr:
            cc_recipients = [{'emailAddress': {'address': addr.strip()}} 
                           for addr in cc_addr.split(',') if addr.strip()]
        
        # 构建附件数据
        attachment_data = []
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode()
                    attachment_data.append({
                        '@odata.type': '#microsoft.graph.fileAttachment',
                        'name': os.path.basename(file_path),
                        'contentBytes': content
                    })
        
        if self._api_type == 'outlook':
            url = 'https://outlook.office.com/api/v2.0/me/sendmail'
            email_data = {
                'Message': {
                    'Subject': subject,
                    'Body': {'ContentType': 'Text', 'Content': body},
                    'ToRecipients': [{'EmailAddress': {'Address': addr.strip()}} 
                                    for addr in to_addr.split(',') if addr.strip()],
                    'Attachments': [{'@odata.type': '#Microsoft.OutlookServices.FileAttachment',
                                    'Name': att['name'], 'ContentBytes': att['contentBytes']}
                                   for att in attachment_data]
                }
            }
            if cc_addr:
                email_data['Message']['CcRecipients'] = [
                    {'EmailAddress': {'Address': addr.strip()}} 
                    for addr in cc_addr.split(',') if addr.strip()
                ]
        else:
            url = 'https://graph.microsoft.com/v1.0/me/sendMail'
            email_data = {
                'message': {
                    'subject': subject,
                    'body': {'contentType': 'Text', 'content': body},
                    'toRecipients': to_recipients,
                    'attachments': attachment_data
                }
            }
            if cc_recipients:
                email_data['message']['ccRecipients'] = cc_recipients
        
        try:
            response = requests.post(url, headers=headers, json=email_data, timeout=60)
            if response.status_code in [200, 202]:
                return True, "发送成功"
            else:
                return False, f"发送失败: {response.status_code} - {response.text[:200]}"
        except Exception as e:
            return False, f"网络错误: {str(e)}"
    
    def send_email_smtp_with_attachments(self, to_addr, subject, body, attachments=None, cc_addr=None):
        """使用 SMTP 发送带附件的邮件"""
        smtp_server, smtp_port = self.get_smtp_server()
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            if cc_addr:
                msg['Cc'] = cc_addr
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                       f'attachment; filename="{os.path.basename(file_path)}"')
                        msg.attach(part)
            
            all_recipients = [addr.strip() for addr in to_addr.split(',') if addr.strip()]
            if cc_addr:
                all_recipients.extend([addr.strip() for addr in cc_addr.split(',') if addr.strip()])
            
            if smtp_port == 465:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            server.login(self.email_addr, self.password)
            server.sendmail(self.email_addr, all_recipients, msg.as_string())
            server.quit()
            
            return True, "发送成功"
        except Exception as e:
            return False, f"发送失败: {str(e)}"

    def get_smtp_server(self):
        """获取 SMTP 服务器配置"""
        domain = self.email_addr.split('@')[-1].lower()
        return self.SMTP_SERVERS.get(domain, (f'smtp.{domain}', 587))
    
    def send_email(self, to_addr, subject, body, cc_addr=None):
        """发送邮件
        to_addr: 收件人地址（多个用逗号分隔）
        subject: 邮件主题
        body: 邮件正文
        cc_addr: 抄送地址（可选，多个用逗号分隔）
        """
        if self.use_graph_api():
            return self.send_email_graph(to_addr, subject, body, cc_addr)
        else:
            return self.send_email_smtp(to_addr, subject, body, cc_addr)
    
    def send_email_graph(self, to_addr, subject, body, cc_addr=None):
        """使用 Graph API 或 Outlook REST API 发送邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return False, msg
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 解析收件人
        to_recipients = [{'emailAddress': {'address': addr.strip()}} 
                        for addr in to_addr.split(',') if addr.strip()]
        
        # 解析抄送
        cc_recipients = []
        if cc_addr:
            cc_recipients = [{'emailAddress': {'address': addr.strip()}} 
                           for addr in cc_addr.split(',') if addr.strip()]
        
        # 根据 API 类型选择不同的端点和格式
        if self._api_type == 'outlook':
            url = 'https://outlook.office.com/api/v2.0/me/sendmail'
            email_data = {
                'Message': {
                    'Subject': subject,
                    'Body': {
                        'ContentType': 'Text',
                        'Content': body
                    },
                    'ToRecipients': [{'EmailAddress': {'Address': addr.strip()}} 
                                    for addr in to_addr.split(',') if addr.strip()]
                }
            }
            if cc_addr:
                email_data['Message']['CcRecipients'] = [
                    {'EmailAddress': {'Address': addr.strip()}} 
                    for addr in cc_addr.split(',') if addr.strip()
                ]
        else:
            url = 'https://graph.microsoft.com/v1.0/me/sendMail'
            email_data = {
                'message': {
                    'subject': subject,
                    'body': {
                        'contentType': 'Text',
                        'content': body
                    },
                    'toRecipients': to_recipients
                }
            }
            if cc_recipients:
                email_data['message']['ccRecipients'] = cc_recipients
        
        try:
            response = requests.post(url, headers=headers, json=email_data, timeout=30)
            if response.status_code in [200, 202]:
                return True, "发送成功"
            else:
                return False, f"发送失败: {response.status_code} - {response.text[:200]}"
        except Exception as e:
            return False, f"网络错误: {str(e)}"
    
    def send_email_smtp(self, to_addr, subject, body, cc_addr=None):
        """使用 SMTP 发送邮件"""
        smtp_server, smtp_port = self.get_smtp_server()
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.email_addr
            msg['To'] = to_addr
            msg['Subject'] = subject
            if cc_addr:
                msg['Cc'] = cc_addr
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 收集所有收件人
            all_recipients = [addr.strip() for addr in to_addr.split(',') if addr.strip()]
            if cc_addr:
                all_recipients.extend([addr.strip() for addr in cc_addr.split(',') if addr.strip()])
            
            # 连接 SMTP 服务器
            if smtp_port == 465:
                # SSL 连接
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
            else:
                # STARTTLS 连接
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            
            server.login(self.email_addr, self.password)
            server.sendmail(self.email_addr, all_recipients, msg.as_string())
            server.quit()
            
            return True, "发送成功"
        except smtplib.SMTPAuthenticationError as e:
            return False, f"认证失败: {str(e)}"
        except smtplib.SMTPException as e:
            return False, f"SMTP 错误: {str(e)}"
        except Exception as e:
            return False, f"发送失败: {str(e)}"

    def delete_email(self, email_id, folder='inbox'):
        """删除邮件
        email_id: 邮件ID
        folder: 当前文件夹
        """
        if self.use_graph_api():
            return self.delete_email_graph(email_id)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.delete_email_imap(email_id, actual_folder)
    
    def delete_email_graph(self, email_id):
        """使用 Graph API 删除邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return False, msg
        
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        # 根据 API 类型选择不同的端点
        if self._api_type == 'outlook':
            url = f'https://outlook.office.com/api/v2.0/me/messages/{email_id}'
        else:
            url = f'https://graph.microsoft.com/v1.0/me/messages/{email_id}'
        
        try:
            response = requests.delete(url, headers=headers, timeout=30)
            if response.status_code in [200, 204]:
                return True, "删除成功"
            else:
                return False, f"删除失败: {response.status_code}"
        except Exception as e:
            return False, f"网络错误: {str(e)}"
    
    def delete_email_imap(self, email_id, folder='INBOX'):
        """使用 IMAP 删除邮件"""
        success, msg = self.connect_imap()
        if not success:
            return False, msg
        
        try:
            self.connection.select(folder)
            # 标记为删除
            self.connection.store(email_id.encode() if isinstance(email_id, str) else email_id, 
                                 '+FLAGS', '\\Deleted')
            # 执行删除
            self.connection.expunge()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
        finally:
            self.disconnect()
    
    def delete_emails_batch(self, email_ids, folder='inbox', progress_callback=None):
        """批量删除邮件（优化性能，复用连接）
        email_ids: 邮件ID列表
        folder: 当前文件夹
        progress_callback: 进度回调函数 (current, total)
        返回: (success_count, fail_count)
        """
        if self.use_graph_api():
            return self.delete_emails_batch_graph(email_ids, progress_callback)
        else:
            actual_folder = self.get_folder_name(folder)
            return self.delete_emails_batch_imap(email_ids, actual_folder, progress_callback)
    
    def delete_emails_batch_graph(self, email_ids, progress_callback=None):
        """使用 Graph API 批量删除邮件"""
        token, msg = self.get_oauth2_access_token()
        if not token:
            return 0, len(email_ids)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 根据 API 类型选择端点前缀
        if self._api_type == 'outlook':
            base_url = 'https://outlook.office.com/api/v2.0/me/messages'
        else:
            base_url = 'https://graph.microsoft.com/v1.0/me/messages'
        
        success_count = 0
        fail_count = 0
        total = len(email_ids)
        
        for i, email_id in enumerate(email_ids):
            try:
                url = f'{base_url}/{email_id}'
                response = requests.delete(url, headers=headers, timeout=30)
                if response.status_code in [200, 204]:
                    success_count += 1
                else:
                    fail_count += 1
            except:
                fail_count += 1
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return success_count, fail_count
    
    def check_aws_verification_emails(self, limit=50):
        """检查是否有 AWS/Amazon 验证码邮件（只检查标题）
        返回: (has_aws_code, email_count) - 是否有AWS验证码邮件，以及找到的数量
        """
        # AWS 验证码邮件的标题特征
        aws_keywords = ['aws', 'amazon']
        
        try:
            emails, msg = self.fetch_emails(folder='inbox', limit=limit)
            if not emails:
                return False, 0
            
            aws_count = 0
            for email_data in emails:
                subject = email_data.get('subject', '').lower()
                
                # 只检查标题是否包含 aws 或 amazon
                if any(kw in subject for kw in aws_keywords):
                    aws_count += 1
            
            return aws_count > 0, aws_count
        except Exception as e:
            return False, 0
    
    def delete_emails_batch_imap(self, email_ids, folder='INBOX', progress_callback=None):
        """使用 IMAP 批量删除邮件（复用连接，最后统一 expunge）"""
        success, msg = self.connect_imap()
        if not success:
            return 0, len(email_ids)
        
        success_count = 0
        fail_count = 0
        total = len(email_ids)
        
        try:
            self.connection.select(folder)
            
            # 先标记所有邮件为删除
            for i, email_id in enumerate(email_ids):
                try:
                    eid = email_id.encode() if isinstance(email_id, str) else email_id
                    self.connection.store(eid, '+FLAGS', '\\Deleted')
                    success_count += 1
                except:
                    fail_count += 1
                
                if progress_callback:
                    progress_callback(i + 1, total)
            
            # 最后统一执行删除
            self.connection.expunge()
            
        except Exception as e:
            # 如果整体失败，返回全部失败
            return 0, total
        finally:
            self.disconnect()
        
        return success_count, fail_count
