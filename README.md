# Social Media Monitor

Monitor follower counts from Douyin, Bilibili, and Xiaohongshu.

## Configuration

Set the following environment variables with your target URLs:

```bash
export DOUYIN_URL="https://www.douyin.com/user/YOUR_USER_ID"
export BILIBILI_URL="https://space.bilibili.com/YOUR_USER_ID"
export XIAOHONGSHU_URL="https://www.xiaohongshu.com/user/profile/YOUR_USER_ID"
```

# Install
conda activate -n monitor python=3.10
pip install -r requirement.txt
playwright install chromium
playwright install-deps

# Update the cookie

``` bash
# First open the X11 Forward in ssh config
ForwardX11 yes
ForwardX11Trusted yes
# sshd config
X11Forwarding yes
X11UseLocalhost no
# sshd config
python simple_monitor.py login
# Douyin 保存登陆信息
# 小红书 B站正常登陆

```

# Set the cron
crontab -e
0 12 * * * cd /path/to/folder && ./daily_update.sh >> /path/to/log 2>&1

# Environment Variables (add these to your shell profile or export before running)
mkdir -p ~/.config/monitor
touch monitor.env
export MAILTO="your-email@example.com"
export MAIL_PASSWD="your-email-authorization-code"
export DOUYIN_URL="https://www.douyin.com/user/YOUR_USER_ID"
export BILIBILI_URL="https://space.bilibili.com/YOUR_USER_ID"
export XIAOHONGSHU_URL="https://www.xiaohongshu.com/user/profile/YOUR_USER_ID"
export https_proxy=http://your.proxy
export http_proxy=http://your.proxy