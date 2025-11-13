#!/bin/bash
source ~/.bashrc
source ~/miniconda3/etc/profile.d/conda.sh
conda activate monitor

# Export environment variables for URLs
export DOUYIN_URL="${DOUYIN_URL}"
export XIAOHONGSHU_URL="${XIAOHONGSHU_URL}"
export BILIBILI_URL="${BILIBILI_URL}"

# Run simple_monitor.py and check for errors
python simple_monitor.py
if [ $? -ne 0 ]; then
    echo "Error in simple_monitor.py"
    python send_notification.py "Monitor Error - simple_monitor.py" "simple_monitor.py failed during execution. Please check the logs."
    exit 1
fi

# Run extract_append.py and check for errors
python extract_append.py
if [ $? -ne 0 ]; then
    echo "Error in extract_append.py"
    python send_notification.py "Monitor Error - extract_append.py" "extract_append.py failed during execution. Please check the logs."
    exit 1
fi

git add follower_history.json
git commit -m "📊 Update stats - $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
git push
rm -r html_cache