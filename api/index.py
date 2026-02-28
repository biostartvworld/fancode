import json
import re
import urllib.request
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "https://www.fancode.com/bd/live-now/all-sports"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        try:
            # Fetch the webpage
            response = urllib.request.urlopen(req)
            html = response.read().decode('utf-8')
            
            # Start building the M3U playlist
            playlist = "#EXTM3U\n"
            
            # Fancode uses Next.js. We look for the embedded JSON state.
            next_data_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
            
            if next_data_match:
                # We found the data, but Fancode secures the actual m3u8 links behind an API token.
                # Here is where you would parse the JSON for match names and logos.
                playlist += '#EXTINF:-1 tvg-logo="https://www.fancode.com/favicon.ico" group-title="Fancode Info", ⚠️ Fancode M3U8 Links Require API Tokens\n'
                playlist += 'https://example.com/fancode-streams-are-protected.m3u8\n'
                
                # Note: To get real streams, you would need to reverse-engineer their GraphQL 
                # endpoint (https://www.fancode.com/graphql) and pass valid authorization headers.
            else:
                playlist += '#EXTINF:-1 group-title="Error", Could not load dynamic Fancode data\n'
                playlist += 'https://example.com/error.m3u8\n'

            # Send the correct headers for an IPTV M3U playlist
            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Disposition', 'attachment; filename="fancode.m3u"')
            self.end_headers()
            
            # Output the playlist
            self.wfile.write(playlist.encode('utf-8'))
            
        except Exception as e:
            # Fallback error handling so Vercel doesn't crash
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error: {str(e)}".encode('utf-8'))
