from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.fancode.com/bd/live-now/all-sports"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        try:
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, "html.parser")
            playlist = "#EXTM3U\n"
            
            matches = soup.find_all("div", class_=re.compile(r"event-card|match-card|live", re.I))
            
            for idx, match in enumerate(matches):
                title_tag = match.find(["h2", "h3", "span", "div"], class_=re.compile(r"title|name", re.I))
                title = title_tag.text.strip() if title_tag else f"FanCode Live Event {idx+1}"
                
                img_tag = match.find("img")
                logo = img_tag.get("src", "") if img_tag else ""
                
                stream_url = f"https://streaming-api.fancode.com/hls/live/{idx}/master.m3u8"
                
                playlist += f'#EXTINF:-1 tvg-logo="{logo}" group-title="FanCode Live",{title}\n'
                playlist += f"{stream_url}\n"
                
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Content-Disposition', 'attachment; filename="fancode.m3u"')
            self.end_headers()
            self.wfile.write(playlist.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
        return
