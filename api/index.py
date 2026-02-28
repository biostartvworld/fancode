import urllib.request
import json
import re
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta, timezone

# FanCode-এর JSON ডাটা থেকে লাইভ ম্যাচ খুঁজে বের করার ফাংশন
def get_matches(data):
    matches = []
    if isinstance(data, dict):
        # স্ট্যাটাস 'LIVE' বা 'isLive' True হলে সেটি লাইভ ম্যাচ
        if data.get('status') in ['LIVE', 'live'] or data.get('isLive') is True:
            if 'name' in data or 'title' in data:
                matches.append(data)
        for k, v in data.items():
            matches.extend(get_matches(v))
    elif isinstance(data, list):
        for i in data:
            matches.extend(get_matches(i))
    return matches

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # বাংলাদেশ টাইমজোন সেট করা
        bd_tz = timezone(timedelta(hours=6))
        current_time = datetime.now(bd_tz).strftime("%A, %d %B %Y %I:%M %p")

        # M3U প্লেলিস্ট এর বেসিক হেডার
        playlist = "#EXTM3U\n"
        playlist += "# Developer: MD. Shinha Sarder\n"
        playlist += "# Telegram : https://t.me/biostartvworld\n"
        playlist += "# Live TV Website: biostar-tv-world.vercel.app\n"
        playlist += f"# Last Updated: {current_time}\n\n"

        # FanCode URL
        url = "https://www.fancode.com/bd/live-now/all-sports"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        })

        try:
            # FanCode এর পেজ রিকোয়েস্ট করা
            res = urllib.request.urlopen(req)
            html = res.read().decode('utf-8')
            
            # পেজের ভেতর থেকে Next.js এর হিডেন JSON ডাটা বের করা
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            
            if match:
                data = json.loads(match.group(1))
                events = get_matches(data)
                ids = set()
                
                # লাইভ ইভেন্টগুলো লুপ করে প্লেলিস্টে যুক্ত করা
                for e in events:
                    eid = str(e.get('id', ''))
                    # ডুপ্লিকেট ইভেন্ট বাদ দেওয়া
                    if not eid or eid in ids:
                        continue
                    ids.add(eid)
                    
                    # ম্যাচের নাম এবং লোগো সেট করা
                    title = e.get('name') or e.get('title') or f"FanCode Live {eid}"
                    logo = "https://www.fancode.com/favicon.ico"
                    
                    if 'media' in e and isinstance(e['media'], dict) and 'imageId' in e['media']:
                        logo = f"https://fancode.com/skillup-uploads/prod-images/{e['media']['imageId']}"
                    elif 'teams' in e and isinstance(e['teams'], list) and len(e['teams']) > 0:
                        if isinstance(e['teams'][0], dict):
                            logo = e['teams'][0].get('logo', logo)
                            
                    # M3U8 লিংক জেনারেট করা (নোট: এটি প্লে করতে ফ্যানকোড টোকেন লাগতে পারে)
                    m3u8 = f"https://streaming-api.fancode.com/hls/live/{eid}/master.m3u8"
                    
                    playlist += f'#EXTINF:-1 tvg-logo="{logo}" group-title="FanCode Live", {title}\n{m3u8}\n'
                    
        except Exception as e:
            playlist += f"# Error fetching from FanCode: {str(e)}\n"

        # ব্রাউজারে টেক্সট হিসেবে দেখানোর জন্য রেসপন্স
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(playlist.encode('utf-8'))
