"""
简化版社交媒体监控 - 使用Playwright爬取公开数据
支持抖音、小红书、B站三个平台

安装依赖:
pip install playwright
playwright install chromium

功能:
1. 使用Playwright直接访问网页获取数据
2. 支持Cookie保存和管理
3. 小红书需要登录，抖音和B站不需要
4. 保存HTML用于后续数据提取
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import time
import os
from pathlib import Path

class SimpleSocialMediaMonitor:
    """简单的社交媒体数据监控器"""
    
    def __init__(self, mode='get_data'):
        """
        初始化监控器
        mode: 'login' 或 'get_data'
            - 'login': 手动登录模式，用于更新cookies
            - 'get_data': 数据获取模式（默认），使用已保存的cookies
        """
        self.mode = mode
        self.data = {}
        self.cookies_dir = Path('cookies')
        self.html_dir = Path('html_cache')
        
        # 创建必要的目录
        self.cookies_dir.mkdir(exist_ok=True)
        self.html_dir.mkdir(exist_ok=True)
    
    def _save_cookies(self, context, platform):
        """保存cookies到文件"""
        cookies = context.cookies()
        cookie_file = self.cookies_dir / f'{platform}_cookies.json'
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"✓ {platform} cookies已保存到: {cookie_file}")
    
    def _load_cookies(self, platform):
        """从文件加载cookies"""
        cookie_file = self.cookies_dir / f'{platform}_cookies.json'
        if cookie_file.exists():
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            print(f"✓ 已加载 {platform} cookies")
            return cookies
        else:
            print(f"⚠️  未找到 {platform} cookies文件")
            return None
    
    def _save_html(self, content, platform, timestamp=None):
        """保存HTML内容到文件"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = self.html_dir / f'{platform}_{timestamp}.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ HTML已保存到: {html_file}")
        return html_file
    
    def get_douyin_stats(self, user_url):
        """
        获取抖音用户公开数据
        user_url: 抖音用户主页链接
        """
        platform = 'douyin'
        print(f"\n{'='*50}")
        print(f"正在获取抖音数据: {user_url}")
        print(f"{'='*50}")
        
        with sync_playwright() as p:
            # 启动浏览器
            headless = (self.mode == 'get_data')
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 加载cookies（如果存在）
            cookies = self._load_cookies(platform)
            if cookies:
                context.add_cookies(cookies)
            
            page = context.new_page()
            
            try:
                if self.mode == 'login':
                    print("\n" + "="*50)
                    print("  登录模式 - 请在浏览器中手动登录")
                    print("  登录完成后，按回车键继续...")
                    print("="*50 + "\n")
                    
                    page.goto(user_url)
                    input("按回车键继续...")
                    
                    # 保存cookies
                    self._save_cookies(context, platform)
                    print("✓ 抖音登录完成，cookies已保存")
                    
                else:  # get_data mode
                    # 访问用户主页
                    page.goto(user_url, wait_until='domcontentloaded', timeout=60000)
                    time.sleep(3)  # 等待页面完全加载
                    
                    # 保存HTML
                    html_content = page.content()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    self._save_html(html_content, platform, timestamp)
                    
                    # 返回基本信息（HTML已保存，等待后续regex提取）
                    stats = {
                        'url': user_url,
                        'timestamp': timestamp,
                        'html_saved': True,
                        'message': 'HTML已保存，等待数据提取'
                    }
                    
                    print(f"✓ 抖音数据获取成功")
                    return stats
                
            except Exception as e:
                print(f"✗ 抖音数据获取失败: {str(e)}")
                return {'error': str(e)}
            finally:
                browser.close()
    
    def get_xiaohongshu_stats(self, user_url):
        """
        获取小红书用户公开数据（需要登录）
        user_url: 小红书用户主页链接
        """
        platform = 'xiaohongshu'
        print(f"\n{'='*50}")
        print(f"正在获取小红书数据: {user_url}")
        print(f"{'='*50}")
        
        with sync_playwright() as p:
            # 启动浏览器
            headless = (self.mode == 'get_data')
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 加载cookies（如果存在）
            cookies = self._load_cookies(platform)
            if cookies:
                context.add_cookies(cookies)
            
            page = context.new_page()
            
            try:
                if self.mode == 'login':
                    print("\n" + "="*50)
                    print("  登录模式 - 请在浏览器中手动登录小红书")
                    print("  登录完成后，按回车键继续...")
                    print("="*50 + "\n")
                    
                    page.goto(user_url)
                    input("按回车键继续...")
                    
                    # 保存cookies
                    self._save_cookies(context, platform)
                    print("✓ 小红书登录完成，cookies已保存")
                    
                else:  # get_data mode
                    # 访问用户主页
                    page.goto(user_url, wait_until='networkidle')
                    time.sleep(3)  # 等待页面完全加载
                    
                    # 保存HTML
                    html_content = page.content()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    self._save_html(html_content, platform, timestamp)
                    
                    # 返回基本信息（HTML已保存，等待后续regex提取）
                    stats = {
                        'url': user_url,
                        'timestamp': timestamp,
                        'html_saved': True,
                        'message': 'HTML已保存，等待数据提取'
                    }
                    
                    print(f"✓ 小红书数据获取成功")
                    return stats
                
            except Exception as e:
                print(f"✗ 小红书数据获取失败: {str(e)}")
                return {'error': str(e)}
            finally:
                browser.close()
    
    def get_bilibili_stats(self, user_url):
        """
        获取B站用户公开数据
        user_url: B站用户空间链接，例如: https://space.bilibili.com/uid
        """
        platform = 'bilibili'
        print(f"\n{'='*50}")
        print(f"正在获取B站数据: {user_url}")
        print(f"{'='*50}")
        
        with sync_playwright() as p:
            # 启动浏览器
            headless = (self.mode == 'get_data')
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 加载cookies（如果存在）
            cookies = self._load_cookies(platform)
            if cookies:
                context.add_cookies(cookies)
            
            page = context.new_page()
            
            try:
                if self.mode == 'login':
                    print("\n" + "="*50)
                    print("  登录模式 - 请在浏览器中手动登录B站（可选）")
                    print("  登录完成后，按回车键继续...")
                    print("="*50 + "\n")
                    
                    page.goto(user_url)
                    input("按回车键继续...")
                    
                    # 保存cookies
                    self._save_cookies(context, platform)
                    print("✓ B站登录完成，cookies已保存")
                    
                else:  # get_data mode
                    # 访问用户空间
                    page.goto(user_url, wait_until='networkidle')
                    time.sleep(3)  # 等待页面完全加载
                    
                    # 保存HTML
                    html_content = page.content()
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    self._save_html(html_content, platform, timestamp)
                    
                    # 返回基本信息（HTML已保存，等待后续regex提取）
                    stats = {
                        'url': user_url,
                        'timestamp': timestamp,
                        'html_saved': True,
                        'message': 'HTML已保存，等待数据提取'
                    }
                    
                    print(f"✓ B站数据获取成功")
                    return stats
                
            except Exception as e:
                print(f"✗ B站数据获取失败: {str(e)}")
                return {'error': str(e)}
            finally:
                browser.close()
    
    def monitor_all(self, config):
        """
        监控所有平台
        config: 配置字典，包含各平台的用户链接
        """
        print("\n" + "="*50)
        print("  社交媒体数据监控")
        print(f"  模式: {self.mode}")
        print("="*50 + "\n")
        
        # 抖音
        if 'douyin_url' in config:
            self.data['douyin'] = self.get_douyin_stats(config['douyin_url'])
        
        # 小红书
        if 'xiaohongshu_url' in config:
            self.data['xiaohongshu'] = self.get_xiaohongshu_stats(config['xiaohongshu_url'])
        
        # B站
        if 'bilibili_url' in config:
            self.data['bilibili'] = self.get_bilibili_stats(config['bilibili_url'])
        
        print("\n" + "="*50)
        if self.mode == 'login':
            print("  登录完成! Cookies已保存")
        else:
            print("  数据获取完成! HTML已保存")
        print("="*50 + "\n")
        
        return self.data


# ============ 使用示例 ============

if __name__ == '__main__':
    import sys
    
    # 从环境变量获取账号信息
    config = {}
    
    # 抖音用户主页链接
    douyin_url = os.getenv('DOUYIN_URL')
    if douyin_url:
        config['douyin_url'] = douyin_url
    
    # 小红书用户主页链接
    xiaohongshu_url = os.getenv('XIAOHONGSHU_URL')
    if xiaohongshu_url:
        config['xiaohongshu_url'] = xiaohongshu_url
    
    # B站用户空间链接
    bilibili_url = os.getenv('BILIBILI_URL')
    if bilibili_url:
        config['bilibili_url'] = bilibili_url
    
    if not config:
        print("错误: 请设置至少一个平台的URL环境变量")
        print("  DOUYIN_URL - 抖音用户主页链接")
        print("  XIAOHONGSHU_URL - 小红书用户主页链接")
        print("  BILIBILI_URL - B站用户空间链接")
        sys.exit(1)
    
    # 检查命令行参数
    mode = 'get_data'  # 默认模式
    if len(sys.argv) > 1:
        if sys.argv[1] == 'login':
            mode = 'login'
        elif sys.argv[1] == 'get_data':
            mode = 'get_data'
        else:
            print("使用方法:")
            print("  python simple_monitor.py          # 获取数据（默认）")
            print("  python simple_monitor.py login    # 登录模式，更新cookies")
            print("  python simple_monitor.py get_data # 获取数据模式")
            sys.exit(1)
    
    # 创建监控器
    monitor = SimpleSocialMediaMonitor(mode=mode)
    
    # 开始监控
    results = monitor.monitor_all(config)
    
    # 打印结果
    if mode == 'get_data':
        print("\n最终结果:")
        print(json.dumps(results, ensure_ascii=False, indent=2))


"""
使用说明:

1. 安装依赖:
   pip install playwright
   playwright install chromium

2. 设置环境变量:
   export DOUYIN_URL="https://www.douyin.com/user/YOUR_USER_ID"
   export XIAOHONGSHU_URL="https://www.xiaohongshu.com/user/profile/YOUR_USER_ID"
   export BILIBILI_URL="https://space.bilibili.com/YOUR_USER_ID"
   
   至少需要设置一个平台的URL

3. 首次使用 - 登录小红书（必需）:
   python simple_monitor.py login
   
   这会打开浏览器窗口，请手动登录小红书
   登录完成后按回车，cookies会自动保存

4. 获取数据:
   python simple_monitor.py get_data
   或
   python simple_monitor.py
   
   这会使用保存的cookies访问各平台，并保存HTML到 html_cache/ 目录

5. 文件结构:
   cookies/              # 保存的cookies
   ├── douyin_cookies.json
   ├── xiaohongshu_cookies.json
   └── bilibili_cookies.json
   
   html_cache/           # 保存的HTML文件
   ├── douyin_20241112_143022.html
   ├── xiaohongshu_20241112_143025.html
   └── bilibili_20241112_143028.html
   
   social_media_stats.json  # 汇总的统计数据

6. 定时监控:
   - Linux/Mac: 使用 crontab
     crontab -e
    0 12 * * * cd /path/to/monitor && /path/to/daily_update.sh
    
   - Windows: 使用任务计划程序
   
   注意: 确保在crontab或脚本中设置环境变量

注意事项:
- 小红书必须登录才能查看用户数据
- 抖音和B站可以不登录直接获取公开数据
- HTML文件保存后，你可以编写regex来提取所需数据
- 建议不要频繁请求，避免被限流
"""
