# -*- coding: utf-8 -*-
"""
OAuth2 授权助手 - 使用 Selenium 手动登录获取 Microsoft refresh_token
"""

import urllib.parse
import requests
import secrets
import time


# Thunderbird 邮件客户端的 Client ID
DEFAULT_CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"

# 授权范围
SCOPES = [
    "offline_access",
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "https://outlook.office.com/SMTP.Send",
]

# 回调地址
REDIRECT_URI = "https://localhost"


class SeleniumOAuth2:
    """使用 Selenium 手动登录获取 OAuth2 Token"""
    
    def __init__(self, client_id=None):
        self.client_id = client_id or DEFAULT_CLIENT_ID
        self.driver = None
    
    def init_driver(self):
        """初始化 Edge WebDriver - 使用无痕模式"""
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options
            
            options = Options()
            options.add_argument('--inprivate')  # 无痕模式
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1280,900')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=options)
            
            return True, None
        except Exception as e:
            return False, f"初始化浏览器失败: {str(e)}"
    
    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def authorize_semi_auto(self, email='', progress_callback=None, timeout=120):
        """
        半自动模式 - 打开授权页面，用户手动登录，程序自动获取授权码
        返回: (client_id, refresh_token, error_msg)
        """
        try:
            # 生成授权 URL
            state = secrets.token_urlsafe(16)
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': REDIRECT_URI,
                'response_mode': 'query',
                'scope': ' '.join(SCOPES),
                'state': state,
            }
            if email:
                params['login_hint'] = email  # 预填邮箱
            
            base_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            if progress_callback:
                progress_callback("打开授权页面，请手动登录...")
            
            self.driver.get(auth_url)
            
            # 等待用户手动完成登录，监控 URL 变化
            if progress_callback:
                progress_callback("等待手动登录完成...")
            
            auth_code = None
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                try:
                    current_url = self.driver.current_url
                    
                    # 检查是否获取到授权码
                    if 'code=' in current_url:
                        parsed = urllib.parse.urlparse(current_url)
                        url_params = urllib.parse.parse_qs(parsed.query)
                        if 'code' in url_params:
                            auth_code = url_params['code'][0]
                            if progress_callback:
                                progress_callback("获取到授权码!")
                            break
                    
                    # 检查是否有错误
                    if 'error=' in current_url:
                        parsed = urllib.parse.urlparse(current_url)
                        url_params = urllib.parse.parse_qs(parsed.query)
                        error_desc = url_params.get('error_description', ['授权失败'])[0]
                        error_desc = urllib.parse.unquote(error_desc)
                        return None, None, f"授权失败: {error_desc}"
                    
                except Exception:
                    # 浏览器可能已关闭
                    return None, None, "浏览器已关闭"
                
                time.sleep(1)
            
            if not auth_code:
                return None, None, "授权超时"
            
            # 换取 tokens
            if progress_callback:
                progress_callback("正在获取 Token...")
            
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            data = {
                'client_id': self.client_id,
                'code': auth_code,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code',
                'scope': ' '.join(SCOPES),
            }
            
            response = requests.post(token_url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                refresh_token = result.get('refresh_token')
                if refresh_token:
                    return self.client_id, refresh_token, None
                else:
                    return None, None, "未获取到 refresh_token"
            else:
                error_data = response.json()
                error = error_data.get('error_description', response.text)
                return None, None, f"获取 Token 失败: {error}"
            
        except Exception as e:
            return None, None, f"授权过程出错: {str(e)}"
