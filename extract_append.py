#!/usr/bin/env python3
"""
Extract follower data from cached HTML files and append to JSON history file.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class DataExtractor:
    def __init__(self, html_cache_dir: str = 'html_cache', output_file: str = 'follower_history.json'):
        self.html_cache_dir = Path(html_cache_dir)
        self.output_file = Path(output_file)
        
    def extract_bilibili_followers(self, html_content: str) -> Optional[int]:
        """
        Extract Bilibili follower count from HTML.
        Pattern: <span data-v-8c500df6="" class="nav-statistics__item-text">粉丝数</span><span data-v-8c500df6="" class="nav-statistics__item-num" title="532">532</span>
        """
        pattern = r'<span[^>]*class="nav-statistics__item-text">粉丝数</span><span[^>]*class="nav-statistics__item-num"[^>]*title="(\d+)">(\d+)</span>'
        match = re.search(pattern, html_content)
        if match:
            # Use the title attribute value as it's the raw number
            return int(match.group(1))
        return None
    
    def extract_douyin_followers(self, html_content: str) -> Optional[int]:
        """
        Extract Douyin follower count from HTML.
        Pattern: <div class="Q1A_pjwq ELUP9h2u" data-e2e="user-info-fans"><div class="uvGnYXqn">粉丝</div><div class="C1cxu0Vq">5439</div></div>
        """
        pattern = r'<div[^>]*data-e2e="user-info-fans"[^>]*>.*?<div[^>]*>粉丝</div>.*?<div[^>]*>(\d+)</div>'
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            return int(match.group(1))
        return None
    
    def extract_xiaohongshu_followers(self, html_content: str) -> Optional[int]:
        """
        Extract Xiaohongshu follower count from HTML.
        Pattern: <span class="count" data-v-18b45ae8="">1865</span><span class="shows" data-v-18b45ae8="">粉丝</span>
        """
        pattern = r'<span class="count"[^>]*>(\d+)</span><span class="shows"[^>]*>粉丝</span>'
        match = re.search(pattern, html_content)
        if match:
            return int(match.group(1))
        return None
    
    def extract_timestamp_from_filename(self, filename: str) -> str:
        """
        Extract timestamp from filename like 'bilibili_20251112_154753.html'
        Returns ISO format timestamp
        """
        match = re.search(r'(\d{8})_(\d{6})', filename)
        if match:
            date_str = match.group(1)  # 20251112
            time_str = match.group(2)  # 154753
            # Parse to datetime
            dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            return dt.isoformat()
        return datetime.now().isoformat()
    
    def process_html_file(self, html_file: Path) -> Optional[Dict]:
        """
        Process a single HTML file and extract follower data.
        """
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        platform = None
        followers = None
        
        # Determine platform from filename
        filename = html_file.name.lower()
        if 'bilibili' in filename:
            platform = 'bilibili'
            followers = self.extract_bilibili_followers(html_content)
        elif 'douyin' in filename:
            platform = 'douyin'
            followers = self.extract_douyin_followers(html_content)
        elif 'xiaohongshu' in filename:
            platform = 'xiaohongshu'
            followers = self.extract_xiaohongshu_followers(html_content)
        
        if platform and followers is not None:
            timestamp = self.extract_timestamp_from_filename(filename)
            return {
                'platform': platform,
                'followers': followers,
                'timestamp': timestamp,
                'source_file': html_file.name
            }
        else:
            print(f"⚠️  Could not extract data from {html_file.name}")
            raise Exception(f"Could not extract data from {html_file.name}")
    
    def load_existing_data(self) -> Dict:
        """
        Load existing follower history data.
        """
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading existing data: {e}")
                return {}
        return {}
    
    def save_data(self, data: Dict):
        """
        Save follower history data to JSON file.
        """
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def append_data(self, new_entry: Dict):
        """
        Append new follower data to history grouped by date.
        Structure: { "2025-11-12": { "douyin": 5439, "bilibili": 532, "xiaohongshu": 1865 } }
        """
        # Load existing data
        history = self.load_existing_data()
        
        platform = new_entry['platform']
        timestamp = new_entry['timestamp']
        followers = new_entry['followers']
        
        # Extract date from timestamp (YYYY-MM-DD)
        date = timestamp.split('T')[0]
        
        # Initialize date entry if it doesn't exist
        if date not in history:
            history[date] = {}
        
        # Update platform data for this date (overwrite if exists)
        if platform in history[date]:
            print(f"⚠️  Data for {platform} on {date} already exists, overwriting")
        history[date][platform] = followers
        print(f"✓ Added {platform} data: {followers} followers on {date}")
        
        # Save updated history
        self.save_data(history)
    
    def process_all_html_files(self):
        """
        Process all HTML files in the cache directory.
        """
        if not self.html_cache_dir.exists():
            print(f"✗ HTML cache directory not found: {self.html_cache_dir}")
            return
        
        html_files = list(self.html_cache_dir.glob('*.html'))
        
        if not html_files:
            print(f"⚠️  No HTML files found in {self.html_cache_dir}")
            return
        
        print(f"\n{'='*50}")
        print(f"Processing {len(html_files)} HTML files...")
        print(f"{'='*50}\n")
        
        processed = 0
        for html_file in sorted(html_files):
            print(f"Processing: {html_file.name}")
            entry = self.process_html_file(html_file)
            if entry:
                self.append_data(entry)
                processed += 1
            print()
        
        print(f"{'='*50}")
        print(f"✓ Processed {processed}/{len(html_files)} files successfully")
        print(f"✓ Data saved to: {self.output_file}")
        print(f"{'='*50}\n")
        
        # Display summary
        self.display_summary()
    
    def display_summary(self):
        """
        Display a summary of the collected data.
        """
        history = self.load_existing_data()
        
        if not history:
            print("No data available")
            return
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        
        # Sort dates
        sorted_dates = sorted(history.keys())
        
        print(f"\nTotal dates recorded: {len(sorted_dates)}")
        print(f"Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
        
        # Display data by date
        print("\nData by date:")
        for date in sorted_dates:
            print(f"\n  {date}:")
            platforms = history[date]
            for platform, followers in sorted(platforms.items()):
                print(f"    {platform}: {followers:,} followers")
        
        # Display growth if we have multiple dates
        if len(sorted_dates) > 1:
            print("\nGrowth Analysis:")
            first_date = sorted_dates[0]
            last_date = sorted_dates[-1]
            
            for platform in ['douyin', 'bilibili', 'xiaohongshu']:
                if platform in history[first_date] and platform in history[last_date]:
                    first_count = history[first_date][platform]
                    last_count = history[last_date][platform]
                    growth = last_count - first_count
                    growth_pct = (growth / first_count * 100) if first_count > 0 else 0
                    print(f"  {platform}: {first_count:,} → {last_count:,} ({growth:+,}, {growth_pct:+.2f}%)")
        
        print("\n" + "="*50)


def main():
    extractor = DataExtractor()
    extractor.process_all_html_files()


if __name__ == '__main__':
    main()

