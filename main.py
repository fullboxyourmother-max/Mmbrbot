import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from bot import bot
import utils.menus  
import adminmember   

class RailwayHealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bale Bot is active and running!")
    def log_message(self, format, *args):
        return  

def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), RailwayHealthCheck)
    print(f"[Railway] Web server started on port {port}")
    server.serve_forever()

async def main():
    print("[Bot] Connecting to @Havijbkbot ...")
    try:
        await bot.start()
    except Exception as e:
        print(f"[Error] Failed to start the bot: {e}")

if __name__ == "__main__":
    web_thread = threading.Thread(target=start_health_server, daemon=True)
    web_thread.start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[Bot] Process stopped.")
